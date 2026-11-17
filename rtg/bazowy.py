"""Bazowy detektor: różnica wzorzec–badany po wyrównaniu + próg.

1) wyrównanie przesunięcia korelacją fazową (FFT), 2) wyrównanie wzmocnienia
w dziedzinie pochłaniania (-log I), 3) różnica, wygładzenie, próg k·sigma (MAD),
4) otwarcie morfologiczne, spójne obszary >= min_pole -> ramki.

Wejście: manifest.json zbioru (pola wzorzec/badany). Wyjście: JSON
{"detektor": ..., "predykcje": {id: [[x0,y0,x1,y1,wynik], ...]}}.
Użycie: python -m rtg.bazowy --zbior dane/syntetyczne --wynik wyniki/bazowy.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def wczytaj(p: Path) -> np.ndarray:
    return np.asarray(Image.open(p).convert("L"), np.float32)


def przesuniecie(wz: np.ndarray, ba: np.ndarray) -> tuple[int, int]:
    """(dy, dx), o ile przesunięty jest badany względem wzorca."""
    F = np.fft.rfft2(ba - ba.mean()) * np.conj(np.fft.rfft2(wz - wz.mean()))
    r = np.fft.irfft2(F / (np.abs(F) + 1e-6), s=wz.shape)
    dy, dx = np.unravel_index(int(np.argmax(r)), r.shape)
    h, w = wz.shape
    return (dy - h if dy > h // 2 else dy), (dx - w if dx > w // 2 else dx)


def wykryj(wz: np.ndarray, ba: np.ndarray, k: float = 5.0, min_pole: int = 60, sigma: float = 2.0) -> list:
    dy, dx = przesuniecie(wz, ba)
    wz = np.roll(wz, (dy, dx), axis=(0, 1))
    A_wz, A_ba = -np.log((wz + 1) / 256), -np.log((ba + 1) / 256)
    # wzmocnienie: przesunięcie poziomu w -log (mnożnik w I) — mediana różnic
    d = A_ba - A_wz
    d -= np.median(d)
    d = ndimage.gaussian_filter(d, sigma)
    # brzegi po np.roll są śmieciem — wycinamy pas szerokości przesunięcia
    m = max(abs(dy), abs(dx)) + 3
    d[:m], d[-m:], d[:, :m], d[:, -m:] = 0, 0, 0, 0
    mad = np.median(np.abs(d)) * 1.4826 + 1e-6
    bin_ = d > k * mad  # dodatki tylko zwiększają pochłanianie
    bin_ = ndimage.binary_opening(bin_, iterations=2)
    lab, n = ndimage.label(bin_)
    ramki = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        pole = int((lab[sl] == i).sum())
        if pole < min_pole:
            continue
        ys, xs = sl
        ramki.append([xs.start, ys.start, xs.stop, ys.stop, float(d[sl].max() / mad)])
    return ramki


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--zbior", default="dane/syntetyczne")
    p.add_argument("--wynik", default="wyniki/bazowy.json")
    p.add_argument("--k", type=float, default=5.0, help="próg w wielokrotnościach sigma (MAD)")
    p.add_argument("--min-pole", type=int, default=60)
    a = p.parse_args(argv)
    z = Path(a.zbior)
    man = json.loads((z / "manifest.json").read_text())
    pred, t0, wzorce = {}, time.time(), {}
    for pr in man["probki"]:
        if pr["wzorzec"] not in wzorce:
            wzorce[pr["wzorzec"]] = wczytaj(z / pr["wzorzec"])
        pred[pr["id"]] = wykryj(wzorce[pr["wzorzec"]], wczytaj(z / pr["badany"]), a.k, a.min_pole)
    t = (time.time() - t0) / max(1, len(man["probki"]))
    Path(a.wynik).parent.mkdir(parents=True, exist_ok=True)
    Path(a.wynik).write_text(json.dumps({"detektor": f"bazowy roznica+prog k={a.k} min_pole={a.min_pole}",
                                         "s_na_obraz": round(t, 3), "predykcje": pred}, indent=1))
    print(f"bazowy: {len(pred)} obrazów, {t:.3f} s/obraz -> {a.wynik}")


if __name__ == "__main__":
    main()
