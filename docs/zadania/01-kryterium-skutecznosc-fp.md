# 01 — kryterium: skuteczność (FP/FN) — waga 40%

- **Kryterium:** skuteczność mierzona liczbą alarmów false positive i false negative (40%).
- **Co jest (17:15, wynik bazowy):** FN 0/34, ale FP 20/20 czystych obrazów (100%) przy rozciągnięciu skanu ±1%; bez rozciągnięcia FP 4/20.
- **Czego brakuje:** odporności na zmienną prędkość przejazdu (rozciągnięcie/odkształcenie) — bez tego każdy czysty obraz alarmuje.
- **Poprawka (strojenie, rano):** próg alarmu dobrany na zbiorze czystych pod FP≈0 przy FN na tym samym poziomie; w materiałach (README, slajd) tabela FP/FN dla kilku progów. Wyrównanie nieliniowe Programista ma i tak w planie nocy — sprawdzić rano, czy weszło.
