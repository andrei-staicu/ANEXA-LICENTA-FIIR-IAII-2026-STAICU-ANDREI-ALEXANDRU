# L2 — Perceptie (Strat Semantic-Aware)

Stratul de perceptie si planificare semantica a rutelor. Implementeaza detectia obiectelor prin
camera monoculara (YOLO26n), fuziunea cu datele LiDAR 2D si constructia hartii semantice
persistente GeoJSON care annoteza graful Nav2 cu penalitati si limite de viteza.

## Rol in stiva SAS

L2 transforma perceptia bruta (bounding boxes YOLO + scan LiDAR) in cunostinte spatiale
structurate: obiecte localizate in frame-ul hartii, muchii ale grafului de navigatie annotate
dinamic. Aceste informatii sunt consumate de Route Server (Nav2) pentru selectia rutei cu cel
mai mic cost si de L3 pentru rezolutia semantica a instructiunilor.

## Continut

```
L2-Perceptie/
├── yolo26_cpp/                         # Detector YOLO26n — C++ lifecycle node ROS2
│   ├── src/                            #   Sursa C++ (inferenta NCNN)
│   ├── include/                        #   Headere
│   ├── launch/                         #   Launch cu auto configure+activate (delay 4s)
│   ├── CMakeLists.txt
│   └── package.xml
├── semantic_localizer/                  # Pipeline ASF + server rute semantice
│   ├── semantic_localizer/             #   Pachet Python (nod ROS2 + map manager)
│   ├── config/
│   │   ├── semantic_localizer_params.yaml        # Parametri pipeline ASF
│   │   ├── semantic_localizer_params_route.yaml  # Varianta cu Route Server
│   │   └── route_server_params.yaml              # Scorare Nav2 Route Server
│   ├── launch/
│   │   └── semantic_localizer_launch.py
│   ├── scripts/
│   │   ├── test_semantic_navigation_v5_10.py     # Framework test automat (~2050 linii)
│   │   └── route_config.yaml                     # Configurare experiment (graf, noduri, validare)
│   ├── package.xml
│   └── setup.py
├── README.md                            # Documentatie sistem + instructiuni build/launch
└── CITATION.cff                         # Referinta publicatie Sensors 2026
```

## Pipeline de perceptie (Angular Sector Fusion)

1. **YOLO26n** detecteaza obiecte in imaginea camerei → bounding boxes cu clasa si confidenta
2. **Proiectie angulara** — bounding boxes mapate pe sectoare unghiulare LiDAR
3. **Fuziune camera + LiDAR** — distanta estimata prin scanul LiDAR in sectorul corespunzator
4. **Localizare in harta** — coordonate `(x, y)` in frame-ul `map` prin transform TF2
5. **Harta semantica GeoJSON** — obiecte persistate si actualizate intre sesiuni
6. **Anotare graf** — muchiile Nav2 Route Server primesc penalitati si limite de viteza

## Performante

- **~5.5 FPS** pe RPi5 single (CPU-only, fara GPU/NPU)
- **~48% CPU** cu inferenta YOLO offlodata pe al doilea RPi5 (Xplorer-C)
- **~85% CPU** cu toate componentele pe un singur RPi5

## Publicatie

B. F. Abaza, A.-A. Staicu, C. V. Doicin, "Lightweight Semantic-Aware Route Planning on Edge
Hardware for Indoor Mobile Robots," *Sensors* (MDPI), vol. 26, nr. 7, p. 2232, 2026.
DOI: [10.3390/s26072232](https://doi.org/10.3390/s26072232)
