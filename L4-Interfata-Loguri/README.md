# L4 — Interfata si Loguri (OpenClaw / Audit)

Stratul de interfata operator-robot si de inregistrare completa a deciziilor. Contine profilul
agentului OpenClaw (SOUL.md) si datele complete din cele trei sesiuni de validare experimentala:
log-uri de audit JSONL, CSV-uri de monitorizare sistem si imagini per misiune.

## Rol in stiva SAS

L4 este interfata dintre operatorul uman si sistemul autonom. Agentul OpenClaw (SOUL.md)
primeste instructiunile in limbaj natural, le trimite catre L3 prin topic-ul ROS2
`/vlm_instruction`, asteapta rezultatul din log-ul de audit si raporteaza inapoi operatorului.
Toate deciziile sunt inregistrate complet pentru trasabilitate si analiza offline.

## Continut

```
L4-Interfata-Loguri/
├── SOUL.md                            # Profilul agentului OpenClaw: reguli, workflow-uri, POI-uri
├── README.md                          # Documentatie format date experimentale
├── session_a/                         # Sesiunea A — Xplorer-C, 37 decizii (ciclu de invatare M3)
│   ├── audits/                        #   10 fisiere JSONL cu decizii structurate
│   ├── csv_clean/                     #   CSV-uri monitor post-v4.8 (date curate)
│   ├── csv_debug/                     #   CSV-uri pre-v4.8 (incluse pentru transparenta)
│   └── mission_folders/               #   Per misiune: start.jpg, finish.jpg, prompt VLM, raspuns VLM
│       └── YYYYMMDD_HHMMSS/
│           └── mission_N_<destinatie>/
│               ├── start.jpg
│               ├── finish.jpg
│               ├── vlm_confirmation_prompt.txt   # (doar misiuni L3b)
│               └── vlm_confirmation_response.txt
├── session_b/                         # Sesiunea B — Xplorer-B, 41 decizii (transfer cross-robot)
│   ├── audits/                        #   3 fisiere JSONL
│   ├── csv/
│   └── mission_folders/
└── session_c/                         # Sesiunea C — ambele platforme concurente, 4 decizii
    ├── audits/                        #   4 fisiere JSONL (1 per robot per pereche)
    └── mission_folders/
```

## Format log audit (JSONL)

Fiecare intrare de tip `"_type": "decision"` contine:

| Camp | Descriere |
|---|---|
| `instruction` | Instructiunea exacta a operatorului (romana sau engleza) |
| `resolution_method` | `L3a_deterministic`, `L3a_m3_preference` sau `L3b_vlm` |
| `node_id` | ID-ul nodului tinta rezolvat |
| `timing.resolve_ms` | Timp rezolutie L3 (ms) |
| `timing.vlm_ms` | Timp inferenta VLM, daca aplicabil (ms) |
| `timing.nav_total_s` | Durata totala navigatie (s) |
| `nav_outcome` | `mission_complete`, `blocked`, `missed`, `timeout` |
| `confirmation` | Date validare vizuala VLM (imagine, prompt, raspuns) |
| `platform_id` | Identificator robot (xplorer-b, xplorer-c) |

## Sesiuni

| Sesiune | Robot | Decizii | Scop |
|---|---|---|---|
| A | Xplorer-C | 37 | Confirmare preferinte M3 + ciclu invatare S3new |
| B | Xplorer-B | 41 | Validare transfer memorie cross-robot |
| C | Ambele | 4 | Testare operare concurenta |
| **Total** | | **82** | |

## Agentul OpenClaw (SOUL.md)

SOUL.md defineste comportamentul agentului operator: cum trimite instructiuni prin ROS2,
cum citeste rezultatele din audit log, cum raporteaza inapoi, reguli de siguranta si lista
completa a punctelor de interes din coridorul FIIR etaj 2.
