"""Skrypt oceny wg rozdziału 6 zadania (FP / FN).

- FP (obrazy): obraz „czysty”, na którym detektor zaznaczył cokolwiek (>= 1 ramka).
- FN (dodatki): dodatek z prawdy, którego nie wskazano. Dodatek jest wskazany, gdy
  suma ramek detektora pokrywa >= POKRYCIE (domyślnie 50%) jego ramki ALBO któraś
  ramka ma z nim IoU >= IOU (domyślnie 0.3).
- Dodatkowo: FN-obrazy (obraz z dodatkami bez żadnej trafionej ramki) i fałszywe
  ramki na obrazach z dodatkami (ramka niepokrywająca żadnego dodatku w >= 10% swojej
  powierzchni) — dla informacji, zadanie ich wprost nie nazywa.

Format predykcji (dowolny detektor): {"predykcje": {id: [[x0,y0,x1,y1(,wynik)], ...]}}.
Użycie: python -m rtg.ocena --zbior dane/syntetyczne --predykcje wyniki/bazowy.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def iou(a, b) -> float:
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def pokrycie(gt, pred) -> float:
    """Ułamek pola ramki gt pokryty sumą ramek pred (bez podwójnego liczenia)."""
    x0, y0, x1, y1 = (int(v) for v in gt[:4])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for p in pred:
        a0, b0 = max(int(p[0]), x0) - x0, max(int(p[1]), y0) - y0
        a1, b1 = min(int(p[2]), x1) - x0, min(int(p[3]), y1) - y0
        if a1 > a0 and b1 > b0:
            m[b0:b1, a0:a1] = True
    return float(m.mean())


def ocen(man: dict, pred: dict, prog_pokrycia=0.5, prog_iou=0.3) -> dict:
    w = {"czyste": 0, "FP_obrazy": 0, "FP_ramki_na_czystych": 0, "dodatki": 0, "FN_dodatki": 0,
         "obrazy_z_dodatkami": 0, "FN_obrazy": 0, "falszywe_ramki_na_dodatkach": 0, "brak_predykcji": 0}
    for pr in man["probki"]:
        if pr["id"] not in pred:
            w["brak_predykcji"] += 1
        p = [r[:4] for r in pred.get(pr["id"], [])]
        if pr["rodzaj"] == "czysty":
            w["czyste"] += 1
            w["FP_obrazy"] += bool(p)
            w["FP_ramki_na_czystych"] += len(p)
            continue
        w["obrazy_z_dodatkami"] += 1
        trafione = 0
        for gt in pr["ramki"]:
            w["dodatki"] += 1
            ok = pokrycie(gt, p) >= prog_pokrycia or any(iou(gt, r) >= prog_iou for r in p)
            trafione += ok
            w["FN_dodatki"] += not ok
        w["FN_obrazy"] += trafione == 0
        for r in p:
            if all(pokrycie(r, [gt]) < 0.1 for gt in pr["ramki"]):
                w["falszywe_ramki_na_dodatkach"] += 1
    w["FP_proc"] = round(100 * w["FP_obrazy"] / max(1, w["czyste"]), 1)
    w["FN_proc"] = round(100 * w["FN_dodatki"] / max(1, w["dodatki"]), 1)
    return w


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--zbior", default="dane/syntetyczne")
    p.add_argument("--predykcje", default="wyniki/bazowy.json")
    p.add_argument("--pokrycie", type=float, default=0.5)
    p.add_argument("--iou", type=float, default=0.3)
    p.add_argument("--json", help="zapisz wynik oceny do pliku")
    a = p.parse_args(argv)
    man = json.loads((Path(a.zbior) / "manifest.json").read_text())
    pr = json.loads(Path(a.predykcje).read_text())
    w = ocen(man, pr["predykcje"], a.pokrycie, a.iou)
    w["detektor"] = pr.get("detektor", "?")
    print(f"{w['detektor']}: FP {w['FP_obrazy']}/{w['czyste']} czystych obrazów ({w['FP_proc']}%), "
          f"FN {w['FN_dodatki']}/{w['dodatki']} dodatków ({w['FN_proc']}%); "
          f"FN-obrazy {w['FN_obrazy']}/{w['obrazy_z_dodatkami']}, "
          f"fałszywe ramki na obrazach z dodatkami {w['falszywe_ramki_na_dodatkach']}")
    if a.json:
        Path(a.json).write_text(json.dumps(w, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
