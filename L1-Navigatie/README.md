# L1 — Navigatie (Strat Nav2 / MPPI)

Stratul de navigatie autonoma bazat pe stiva ROS2 Nav2. Contine grafurile de navigatie ale
coridorului FIIR (etaj 2) si datele experimentale complete din campania de validare pe trei
platforme robotice.

## Rol in stiva SAS

L1 asigura planificarea globala a traseului (SmacPlannerHybrid) si controlul local al miscarii
(MPPI — Model Predictive Path Integral). Primeste obiective de pozitie de la L3 prin Nav2
action server si publica comenzi de viteza catre L0 prin driverele hardware.

Experimentele din acest strat cuprind atat rulele **baseline** (Test 2 — navigatie pura MPPI,
fara semantica) cat si rulele **adaptive** (Test 3 — cu Route Server semantic de la L2).

## Continut

```
L1-Navigatie/
├── maps/
│   ├── route_graph_fiir.geojson           # Graf de baza (7 noduri, 20 muchii directionate)
│   ├── route_graph_fiir_nav2.geojson      # Versiune Nav2-compatibila (metadate scalare)
│   ├── route_graph_fiir_semantic.geojson  # Graf semantic complet (pentru diagnosticare)
│   └── semantic_objects.geojson           # Harta persistenta de obiecte semantice
└── experiments/
    ├── README.md                          # Documentatie format date + criterii validare
    ├── Xplorer-A/                         # 7 sesiuni, RPi5 single (16 GB)
    │   └── session_YYYY-MM-DD_HH-MM-SS/
    │       ├── session_config.json
    │       ├── summary.json
    │       ├── semantic_snapshot_start.geojson
    │       ├── test1_compute_route.json
    │       ├── test2_run0X_{forward,return}.json  # Baseline MPPI
    │       └── test3_run0X_{forward,return}.json  # Adaptive semantic
    ├── Xplorer-B/                         # 13 sesiuni, RPi5 single (16 GB)
    └── Xplorer-C/                         # 7 sesiuni, RPi5 dual (inferenta YOLO offloaded)
```

## Statistici experimentale

| Robot | Arhitectura | Sesiuni | Curse Baseline | Curse Adaptive |
|---|---|---|---|---|
| Xplorer-A | RPi5 single | 7 | 10 | 22 |
| Xplorer-B | RPi5 single | 13 | 19 | 34 |
| Xplorer-C | RPi5 dual | 7 | 16 | 14 |
| **Total** | | **27** | **45** | **70** |

Rata de succes globala: **97%** (111/115 curse validate). Baseline: 100% (45/45). Adaptive: 94% (66/70).

## Format fisiere per cursa

Fiecare `test{2,3}_runXX_{forward,return}.json` contine: durata, distanta, traiectorie AMCL la 2 Hz,
odometrie la 5 Hz, metrici sistem (CPU, memorie, temperatura), obiecte semantice detectate,
si — pentru Test 3 — istoricul replanificarilor si analiza rutei selectate.
