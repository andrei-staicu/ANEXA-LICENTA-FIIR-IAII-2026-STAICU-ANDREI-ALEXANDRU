# L3 — Reasoning VLM (Strat de Rationament Semantic)

Stratul de rationament semantic si contractul executiv al sistemului SAS. Implementeaza o
arhitectura dual-process hibrid: o cale determinista rapida (L3a) si o cale VLM pentru cazuri
ambigue (L3b), ambele validate de un contract executiv formalizat.

## Rol in stiva SAS

L3 traduce instructiunile in limbaj natural ale operatorului in comenzi de navigatie concrete
(ID nod destinatie). Primeste instructiunea de la L4 (interfata OpenClaw), rezolva destinatia
prin L3a sau L3b, valideaza actiunea prin contractul executiv, si trimite obiectivul catre Nav2 (L1).

## Continut

```
L3-Reasoning-VLM/
├── config/
│   ├── policy.yaml                        # Contractul executiv: allowlist actiuni, limite siguranta
│   └── semantic_objects_static.geojson    # 18 POI-uri statice (8 clase), harta de baza L3
├── analysis/
│   └── figures/
│       ├── data_loader.py                 # Citire date experimentale din audits/*.jsonl
│       ├── Fig8.py                        # Timpii VLM in ciclul de invatare (bar chart)
│       ├── Fig9.py                        # Timpii de rezolutie pe categorie (box plot)
│       ├── Fig10.py                       # Speedup L3b → L3a (scala logaritmica)
│       └── Fig11.py                       # Rezultate navigatie (stacked bar)
├── README.md                              # Documentatie sistem SAS (L3-L5)
└── CITATION.cff                           # Referinta preprint arXiv:2605.02525
```

## Arhitectura dual-process

### L3a — Calea determinista (88% din decizii)
Resolver parametric in 7 pasi care gestioneaza instructiuni clare fara apel la VLM:
- Rezolutie exacta: `"du-te la cb204"` → nod 5 (< 0.1 ms)
- Rezolutie din preferinte M3: `"du-te la laborator"` → nod promovat din memorie (0.065 ms medie)

### L3b — Calea VLM (12% din decizii)
Apelata automat pentru instructiuni ambigue semantic (`"du-te undeva unde pot sta"`):
- Model: Qwen 3.5:4b via Ollama (rulat local pe laptop-ul operatorului)
- Timp mediu inferenta: 6,733 ms
- Reductie latenta L3b → L3a dupa promotie in M3: **103,000×**

### Contractul executiv ⟨A, O, V, L⟩
Interfata formalizata intre VLM si stack-ul de navigatie:
- **A** (Action): comanda propusa de VLM
- **O** (Object): nodul tinta
- **V** (Validation): verificari siguranta conform `policy.yaml`
- **L** (Log): inregistrare completa in audit JSONL

## Rezultate cheie

| Metrica | Valoare |
|---|---|
| Rata L3a fast-path | 88% din toate deciziile |
| Timp mediu rezolutie M3 | 0.065 ms |
| Timp mediu inferenta VLM (L3b) | 6,733 ms |
| Acuratete rezolutie semantica (robot nou) | 100% (41/41) |
| Transfer cross-robot fara reantrenare | 33/33 = 100% |

## Publicatie

B. F. Abaza, A.-A. Staicu, C. V. Doicin, "A Semantic Autonomy Framework for VLM-Integrated
Indoor Mobile Robots: Hybrid Deterministic Reasoning and Cross-Robot Adaptive Memory," 2026.
arXiv: [2605.02525](https://arxiv.org/abs/2605.02525)
