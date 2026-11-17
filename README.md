# hacknation-proba10
Próba 17.11: faza 1, konkurs zna tylko Szef, etap produktu z ludźmi.

## Uruchomienie

Wymaga Pythona 3.10+ (z `uv` albo `venv`). Jedna komenda — środowisko, zbiór syntetyczny, bazowy detektor, ocena FP/FN:

```sh
./run.sh                       # 20 czystych + 20 z dodatkami, 1200x400 px, ~10 s
./run.sh --czyste 100 --dodatki 100 --szer 7200 --wys 7200   # obrazy ~50 MB jak w zadaniu (ciężkie)
```

Kroki osobno: `python -m rtg.generuj` (zbiór `.bmp` + `manifest.json` z ramkami prawdy + maski),
`python -m rtg.bazowy` (predykcje JSON `{id: [[x0,y0,x1,y1,wynik]]}`), `python -m rtg.ocena` (FP/FN dla dowolnych predykcji w tym formacie).
