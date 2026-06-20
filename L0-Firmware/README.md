# L0 — Firmware (Strat Hardware)

Firmware-ul ESP32 pentru platforma robotica DummyBot. Implementeaza controlul de nivel jos al
actuatoarelor si citirea senzorilor, expunand o interfata seriala catre stratul ROS2 de deasupra.

## Rol in stiva SAS

L0 este baza fizica a intregului sistem: primeste comenzi de viteza de la driverele ROS2 (L1),
executa controlul PID al motoarelor si returneaza valorile encoderelor pentru odometrie.

## Continut

```
L0-Firmware/
└── esp32/
    ├── DummyBot_ESP32_Bridge.ino   # Program principal: loop serial + update PID la 30 Hz
    ├── config.h                    # Configurare centralizata: pini GPIO, parametri roti/encodere, PID
    ├── commands.h                  # Definitii protocol serial ASCII
    ├── motor_driver_l298n.h/.ino   # Driver 2x L298N dual H-bridge (skid-steer: FL+RL / FR+RR)
    ├── encoder_driver.h/.ino       # Citire 4x encodere quadrature cu ISR + protectie atomica
    ├── diff_controller.h/.ino      # Controller PID cu anti-windup si factori de calibrare
    ├── README.md                   # Documentatie tehnica hardware si protocol
    └── rezumat.txt                 # Rezumat in romana: probleme hardware rezolvate, pinout complet
```

## Specificatii hardware

| Parametru | Valoare |
|---|---|
| Microcontroller | ESP32 Dev Module |
| Motoare | 4x DC cu encodere, gear ratio 40:1 |
| Drivere | 2x L298N dual H-bridge |
| Encodere | Quadrature AB Hall, 11 PPR → 1760 ticks/revolutie |
| Rezolutie odometrie | 0.116 mm/tick |
| Diametru roata | 65 mm |
| Wheelbase | 386.3 mm (Lx) / 372.3 mm (Ly) |

## Protocol serial (115200 baud)

| Comanda | Functie |
|---|---|
| `e` | Citire encodere (FL FR RL RR) |
| `m FL FR RL RR` | Setare viteze cu PID (ticks/frame) |
| `o FL FR RL RR` | PWM direct fara PID (−255 la 255) |
| `u Kp Kd Ki Ko` | Actualizare parametri PID |
| `r` | Reset encodere |
| `s` | Auto-stop de urgenta |

## Parametri PID impliciți

Kp=60, Kd=20, Ki=0, Ko=15, rata=30 Hz, auto-stop la 2s fara comanda.
