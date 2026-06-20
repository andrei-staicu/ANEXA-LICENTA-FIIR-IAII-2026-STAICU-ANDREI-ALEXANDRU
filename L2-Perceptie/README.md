# Lightweight Semantic-Aware Route Planning on Edge Hardware for Indoor Mobile Robots

**Monocular Camera–2D LiDAR Fusion with Penalty-Weighted Nav2 Route Server Replanning**

[![ROS 2](https://img.shields.io/badge/ROS_2-Jazzy-blue)](https://docs.ros.org/en/jazzy/)
[![Nav2](https://img.shields.io/badge/Nav2-1.3.x-green)](https://docs.nav2.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository contains the ROS 2 packages, configuration files, and experimental data accompanying the manuscript:

> **B. F. Abaza, A.-A. Staicu, and C. V. Doicin**, "[Lightweight Semantic-Aware Route Planning on Edge Hardware for Indoor Mobile Robots: Monocular Camera–2D LiDAR Fusion with Penalty-Weighted Nav2 Route Server Replanning](https://www.mdpi.com/1424-8220/26/7/2232)", *Sensors* (MDPI), 2026.

---

## System Overview

The system extends the ROS 2 / Nav2 navigation stack with a **semantic-aware route planning pipeline**:

1. **YOLO26n detection** (`yolo26_cpp`) — C++ lifecycle node running NCNN inference on RPi5 at ~5.5 FPS
2. **Angular Sector Fusion** (`semantic_localizer`) — projects camera bounding boxes to LiDAR angular sectors, localizes objects in the map frame, and maintains a persistent GeoJSON semantic map
3. **Graph annotation** — annotates Nav2 Route Server edges with penalties and speed limits based on detected objects
4. **Penalty-weighted routing** — Nav2 Route Server selects the lowest-cost route; a replanning loop cancels and recomputes routes when penalties change during navigation

All components run on a **Raspberry Pi 5 (CPU-only, no GPU/NPU)** with ~85% total CPU utilization, or ~48% with YOLO inference offloaded to a second RPi5.

---

## Repository Structure

```
nav2-semantic-route-server/
├── semantic_localizer/          # ASF pipeline + semantic map + test framework
│   ├── semantic_localizer/      #   Python package (node + map manager)
│   ├── config/                  #   Parameter files (semantic_localizer, route_server)
│   ├── launch/                  #   ROS 2 launch file
│   └── scripts/                 #   Test framework + route config
│       ├── test_semantic_navigation_v5_10.py
│       └── route_config.yaml
├── yolo26_cpp/                  # C++ YOLO26 detector (NCNN, lifecycle node)
│   ├── src/                     #   C++ source files
│   ├── include/                 #   Headers
│   └── launch/                  #   Launch with auto configure+activate
├── maps/                        # Navigation graphs (GeoJSON) + semantic objects
│   ├── route_graph_fiir.geojson          # Base graph (7 nodes, 20 edges)
│   ├── route_graph_fiir_nav2.geojson     # Nav2-compatible (scalar metadata only)
│   ├── route_graph_fiir_semantic.geojson # Full semantic graph (diagnostics)
│   └── semantic_objects.geojson          # Persistent semantic object store
├── experiments/                 # Experimental session data (JSON + GeoJSON)
│   ├── Xplorer-A/               #   7 sessions, single RPi5
│   ├── Xplorer-B/               #   13 sessions, single RPi5
│   ├── Xplorer-C/               #   7 sessions, dual RPi5
│   └── README.md
├── CITATION.cff
├── LICENSE                      # MIT
└── README.md                    # This file
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Ubuntu | 24.04 (or 22.04) | ARM64 or x86_64 |
| ROS 2 | Jazzy (or Humble) | `ros-jazzy-desktop` or `ros-jazzy-ros-base` |
| Nav2 | 1.3.x | `ros-jazzy-navigation2` |
| Nav2 Route Server | from source or `nav2_route` package | [Configuration guide](https://docs.nav2.org/configuration/packages/configuring-route-server.html) |
| NCNN | ≥ 20240410 | [github.com/Tencent/ncnn](https://github.com/Tencent/ncnn) — required for `yolo26_cpp` |
| OpenCV | 4.x | `libopencv-dev` |
| Python 3 | ≥ 3.8 | `numpy`, `pyyaml`, `ament_index_python` |

The `semantic_localizer` node additionally requires a robot platform publishing:
- `/scan` (`sensor_msgs/LaserScan`) — any 2D LiDAR
- `/camera/camera_info` (`sensor_msgs/CameraInfo`) — monocular camera
- TF2 transforms: `map → odom → base_link → base_laser`, `base_link → camera_link_optical`
- AMCL localization (or equivalent) publishing the `map → odom` transform

---

## Build

```bash
# Clone into your ROS 2 workspace
cd ~/your_ws/src
git clone https://github.com/bogdan-abaza/nav2-semantic-route-server.git

# Build
cd ~/your_ws
colcon build --packages-select semantic_localizer yolo26_cpp --symlink-install
source install/setup.bash
```

> **Note:** `yolo26_cpp` requires NCNN headers and libraries. Set `NCNN_DIR` if not installed system-wide:
> ```bash
> colcon build --cmake-args -DNCNN_DIR=/path/to/ncnn/build/install/lib/cmake/ncnn
> ```

---

## Launch Sequence

The system requires five components launched in order. The first two (robot stack and Nav2) are platform-specific; the remaining three are provided by this repository.

### Terminal 1 — Robot hardware + drivers

*Platform-specific.* Launch your robot's hardware interface, sensor drivers, odometry, and state estimation:

```bash
# Replace with your robot's bringup launch:
ros2 launch your_robot_bringup robot.launch.py
```

The robot must publish `/scan`, camera topics, TF2 transforms, and `/odom`.

### Terminal 2 — Nav2 navigation stack

*Platform-specific.* Launch AMCL, costmap, planner server, controller server, and behavior server:

```bash
# Replace with your Nav2 launch:
ros2 launch your_nav2_config navigation.launch.py
```

Nav2 must be fully active (AMCL localized, controller ready) before proceeding.

### Terminal 3 — YOLO26 detector

```bash
ros2 launch yolo26_cpp yolo26_cpp_launch.py \
  model_path:=/path/to/yolo26n_ncnn_model \
  image_topic:=/camera/image_raw
```

The launch file automatically transitions the lifecycle node through `configure → activate` after a 4-second delay. To manage the lifecycle manually instead:

```bash
ros2 lifecycle set /yolo26_detector configure
ros2 lifecycle set /yolo26_detector activate
```

Verify detections are publishing:
```bash
ros2 topic echo /yolo26/detections --once
```

### Terminal 4 — Semantic Localizer

```bash
ros2 launch semantic_localizer semantic_localizer_launch.py
```

This starts the ASF pipeline, semantic map manager, and graph annotator. Parameters are loaded from `config/semantic_localizer_params.yaml`. The node auto-configures camera intrinsics and LiDAR geometry from their respective ROS topics at startup.

Verify semantic markers are publishing:
```bash
ros2 topic echo /semantic_markers --once
```

### Terminal 5 — Nav2 Route Server

```bash
ros2 run nav2_route route_server --ros-args \
  --params-file $(ros2 pkg prefix semantic_localizer)/share/semantic_localizer/config/route_server_params.yaml \
  -r plan:=route_plan
```

Then activate the lifecycle:
```bash
ros2 lifecycle set /route_server configure
ros2 lifecycle set /route_server activate
```

> **Important:** The Route Server must be launched as a **standalone lifecycle node**, outside the Nav2 lifecycle manager. This allows independent graph reloading via `set_route_graph` without affecting the navigation stack.

---

## Running the Experiments

The experimental protocol is fully automated by `test_semantic_navigation_v5_10.py` (~2,050 lines). All commands below should be run from the `semantic_localizer/scripts/` directory:

```bash
cd ~/your_ws/src/nav2-semantic-route-server/semantic_localizer/scripts
```

### Test phases

| Phase | Command | Description |
|---|---|---|
| Setup | `--test 0` | Reset semantic map, reinitialize AMCL, regenerate Nav2-compatible graph |
| Route check | `--test 1` | Single ComputeRoute request — validates Route Server is operational |
| Baseline | `--test 2` | NavigateToPose (SmacPlannerHybrid + MPPI), no semantic awareness |
| Adaptive | `--test 3` | Semantic prescan → ComputeRoute → FollowPath with replanning |
| Full suite | `--test all` | Setup → Test 1 → Test 2 → Test 3 in sequence |

### Example commands

```bash
# Validate setup (no navigation, just checks)
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test 0

# ComputeRoute only (verify route selection)
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test 1

# Baseline: 5 forward+return runs
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test 2 --runs 5

# Adaptive: 5 forward+return runs with semantic routing
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test 3 --runs 5

# Full test suite: setup + route check + 5 baseline + 5 adaptive
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test all --runs 5

# Different run counts per condition
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test all \
  --runs-baseline 7 --runs-adaptive 5

# Continue an existing session (append runs)
python3 test_semantic_navigation_v5_10.py --config route_config.yaml --test 3 --runs 5 \
  --session session_2026-03-09_18-24-50
```

### Adapting to your environment

Edit `route_config.yaml` to define your navigation graph:

1. Create a GeoJSON graph file with nodes (Point) and edges (MultiLineString) following the [Nav2 Route Server format](https://docs.nav2.org/configuration/packages/configuring-route-server.html)
2. Set `graph_filepath`, `start_node_id`, `goal_node_id`, `start_yaw_deg`, `goal_yaw_deg`
3. Define `route_alternatives` with intermediate node IDs for each alternative route (used for automatic route classification in the logs)

---

## Experimental Data

The `experiments/` directory contains 115 navigation legs across 27 sessions on three robot platforms:

| Robot | Architecture | Sessions | Baseline legs | Adaptive legs |
|---|---|---|---|---|
| Xplorer-A | Single RPi5, 16 GB | 7 | 10 | 22 |
| Xplorer-B | Single RPi5, 16 GB | 13 | 19 | 34 |
| Xplorer-C | Dual RPi5 (inference offload) | 7 | 16 | 14 |
| **Total** | | **27** | **45** | **70** |

Each session directory contains per-run JSON files with navigation metrics, trajectories, semantic snapshots, and system telemetry. See [`experiments/README.md`](experiments/README.md) for the data format.

> **Note:** One file (`Xplorer-B/session_2026-03-09_12-51-24/test3_run02_forward.json`) is truncated due to an aborted session. This file was not included in the 115-leg analysis.

---

## Key Configuration Files

| File | Purpose |
|---|---|
| `semantic_localizer/config/semantic_localizer_params.yaml` | ASF pipeline parameters (rate, thresholds, frames, persistence paths) |
| `semantic_localizer/config/route_server_params.yaml` | Nav2 Route Server scoring (PenaltyScorer weight=5.0, DistanceScorer weight=1.0) |
| `semantic_localizer/scripts/route_config.yaml` | Experiment configuration (graph, terminals, route alternatives, validation criteria) |
| `maps/route_graph_fiir.geojson` | Base navigation graph (7 nodes, 20 directed edges) |

---

## Citation

```bibtex
@article{abaza2026semantic,
  title     = {Lightweight Semantic-Aware Route Planning on Edge Hardware for Indoor
               Mobile Robots: Monocular Camera--2D LiDAR Fusion with Penalty-Weighted
               Nav2 Route Server Replanning},
  author    = {Abaza, Bogdan Felician and Staicu, Andrei-Alexandru and Doicin, Cristian Vasile},
  journal   = {Sensors},
  volume    = {26},
  number    = {7},
  pages     = {2232},
  year      = {2026},
  doi       = {10.3390/s26072232},
  url       = {https://www.mdpi.com/1424-8220/26/7/2232},
  publisher = {MDPI},
}
```

---

## Authors

- **Bogdan Felician Abaza** — system architecture, ASF pipeline, semantic routing, experimental framework, manuscript ([bogdan.abaza@upb.ro](mailto:bogdan.abaza@upb.ro))
- **Andrei-Alexandru Staicu** — software implementation, ROS 2 integration, data collection
- **Cristian Vasile Doicin** — validation, formal analysis, writing-review, supervision

Faculty of Industrial Engineering and Robotics (FIIR), National University of Science and Technology POLITEHNICA Bucharest

---

## License

This project is released under the [MIT License](LICENSE).
