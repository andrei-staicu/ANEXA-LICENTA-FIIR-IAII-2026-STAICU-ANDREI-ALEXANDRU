# L5 — Memorie Semantica (Operational Intelligence)

Stratul de memorie semantica al sistemului SAS. Implementeaza un cadru cu cinci categorii
de memorie (M1–M5) cu taxonomie explicita a scopului: cunostinte globale de mediu, preferinte
per operator, capabilitati per platforma — permitand invatare cross-sesiune si transfer
cross-robot fara reantrenare.

## Rol in stiva SAS

L5 acumuleaza cunostinte operationale in timp si le pune la dispozitia L3 pentru accelerarea
rezolutiei. Cel mai important mecanism: instructiunile ambigue rezolvate prin VLM (L3b) pot fi
promovate in M3 ca preferinte — transformand o rezolutie de 6,733 ms intr-una de 0.065 ms la
urmatoarea aparitie (speedup 103,000×). Digestul de memorie permite transferul direct al
preferintelor intre platforme fara nicio reantrenare.

## Continut

```
L5-Memorie-Semantica/
└── memory/
    ├── M1_environment.jsonl              # Statistici vizite entitati (frecvente, ore de varf)
    ├── M2_temporal_patterns.jsonl        # Tipare temporale: clustere de observatii scena
    ├── M3_operator_preferences.jsonl     # Preferinte promovate: instructiune → nod (6 intrari)
    ├── M4_platform_capabilities.jsonl    # Capabilitati platforma (template general)
    ├── M4_xplorer-b.jsonl               # Capabilitati specifice Xplorer-B
    ├── M4_xplorer-c.jsonl               # Capabilitati specifice Xplorer-C
    ├── M5_task_history.jsonl             # Rezumat per decizie: destinatie, metoda, outcome
    ├── memory_digest.json                # Digest compilat folosit in Sesiunile B si C (MD5: 97241265)
    └── memory_digest_session_a_final.json # Digest final dupa Sesiunea A
```

## Cele 5 categorii de memorie

| Categorie | Scope | Continut |
|---|---|---|
| **M1** — Mediu | Global | Statistici vizite per entitate (frecventa, ore de varf, prima/ultima vizita) |
| **M2** — Tipare temporale | Global | Clustere de observatii ale scenei: ce obiecte apar impreuna, cand |
| **M3** — Preferinte operator | Per operator | Mappinguri promovate instructiune → nod din interactiuni VLM anterioare |
| **M4** — Capabilitati platforma | Per robot | Viteza maxima, raza de evitare obstacole, senzori disponibili, limitari cunoscute |
| **M5** — Istoric taskuri | Global | Rezumat per decizie: instructiune, metoda rezolutie, nod, outcome, timing |

## Transferul cross-robot

`memory_digest.json` (MD5: 97241265) este artefactul central al transferului: contine cele
6 preferinte M3 promovate in Sesiunea A (Xplorer-C) si folosit direct in Sesiunile B si C
pe Xplorer-B fara nicio reantrenare.

Rezultat: **33/33 = 100%** acuratete transfer (IC 95%: [0.894, 1.000]).

## Promovare M3

Un mapping este promovat din L3b in M3 cand:
1. VLM rezolva cu succes o instructiune ambigua
2. Navigatia se incheie cu `mission_complete`
3. Confirmarea vizuala valideaza destinatia

La urmatoarea aparitie a aceleiasi instructiuni (sau similara), L3a o rezolva direct din M3
fara apel VLM.
