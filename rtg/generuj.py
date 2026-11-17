"""Generator syntetycznych obrazów RTG naczep (.bmp, 8 bit, skala szarości).

Konwencja RTG: jasne = powietrze (małe pochłanianie), ciemne = materiał gęsty.
Każda próbka to para: wzorzec (pusta naczepa danego modelu) i obraz badany
(ta sama naczepa ponownie prześwietlona: przesunięcie, inne wzmocnienie, szum).
Obraz badany jest „czysty” albo ma 1–3 „dodatki” (skrytki w konstrukcji albo
paczki na podłodze). Prawda: ramki w manifest.json i maska *_maska.png.

Użycie: python -m rtg.generuj --wyjscie dane/syntetyczne --czyste 20 --dodatki 20
Duże obrazy (~50 MB jak w zadaniu): --szer 7200 --wys 7200 (8 bit => ~50 MB).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def model_naczepy(rng: np.random.Generator) -> dict:
    """Losowe parametry konstrukcji jednego modelu naczepy."""
    return {
        "zebra": int(rng.integers(8, 20)),          # liczba żeber burty
        "osie": int(rng.integers(2, 4)),
        "rama": float(rng.uniform(0.9, 1.6)),       # grubość podłużnic (względna)
        "gestosc": float(rng.uniform(0.25, 0.45)),  # pochłanianie blach
        "zbiorniki": int(rng.integers(0, 3)),       # zbiorniki/skrzynki pod podłogą
        "ziarno": int(rng.integers(0, 2**31)),
    }


def rysuj_wzorzec(m: dict, w: int, h: int) -> np.ndarray:
    """Mapa pochłaniania (0 = powietrze, większe = gęściej) pustej naczepy."""
    rng = np.random.default_rng(m["ziarno"])
    a = np.zeros((h, w), np.float32)
    s = h / 400.0  # skala względem obrazu bazowego 400 px wysokości
    x0, x1 = int(0.04 * w), int(0.96 * w)
    gora, podloga = int(0.12 * h), int(0.70 * h)
    g = m["gestosc"]
    # skrzynia: dach, podłoga, ściany czołowe
    a[gora:gora + max(2, int(4 * s)), x0:x1] += g
    a[podloga:podloga + max(3, int(8 * s)), x0:x1] += 1.4 * g
    a[gora:podloga, x0:x0 + max(3, int(6 * s))] += g
    a[gora:podloga, x1 - max(3, int(6 * s)):x1] += g
    # blacha burty (lekkie tło całej skrzyni) + tekstura
    a[gora:podloga, x0:x1] += 0.06 + 0.02 * rng.standard_normal((podloga - gora, x1 - x0)).astype(np.float32)
    # żebra burty
    for x in np.linspace(x0, x1, m["zebra"] + 2)[1:-1].astype(int):
        a[gora:podloga, x:x + max(2, int(3 * s))] += 0.5 * g
    # rama (podłużnice) pod podłogą
    r0 = podloga + int(10 * s)
    grub = max(3, int(9 * s * m["rama"]))
    a[r0:r0 + grub, x0:x1] += 1.2 * g
    a[r0 + grub + int(6 * s):r0 + 2 * grub + int(6 * s), x0:x1] += 0.9 * g
    # poprzeczki ramy
    for x in np.linspace(x0, x1, 14)[1:-1].astype(int):
        a[podloga:r0 + 2 * grub + int(6 * s), x:x + max(2, int(4 * s))] += 0.6 * g
    # zbiorniki / skrzynki narzędziowe
    for i in range(m["zbiorniki"]):
        cx = int(w * (0.2 + 0.25 * i))
        a[r0 + 2 * grub + int(8 * s):r0 + 2 * grub + int(40 * s), cx:cx + int(70 * s)] += 0.5 * g
    # osie i koła
    kol = int(0.75 * w)
    yy, xx = np.ogrid[:h, :w]
    rad = int(32 * s)
    cy = min(h - rad - 2, int(0.86 * h))
    for i in range(m["osie"]):
        cx = kol + i * int(2.3 * rad)
        d = (yy - cy) ** 2 + (xx - cx) ** 2
        a[d < rad ** 2] += 0.9 * g
        a[d < (0.45 * rad) ** 2] += 0.8 * g
    # sworzeń / nogi podporowe z przodu
    a[podloga:int(0.9 * h), int(0.2 * w):int(0.2 * w) + max(3, int(6 * s))] += 0.8 * g
    return a


def dodaj_dodatki(a: np.ndarray, rng: np.random.Generator, n: int) -> tuple[np.ndarray, list, np.ndarray]:
    """Dokłada n „dodatków”. Zwraca nową mapę, ramki [x0,y0,x1,y1,typ] i maskę."""
    h, w = a.shape
    s = h / 400.0
    a = a.copy()
    maska = np.zeros((h, w), bool)
    ramki = []
    for _ in range(n):
        typ = rng.choice(["skrytka_rama", "skrytka_burta", "paczka"])
        if typ == "skrytka_rama":  # w podłużnicy / pod podłogą — mała, słaba
            bw, bh = int(rng.uniform(25, 90) * s), int(rng.uniform(6, 14) * s)
            y = int(0.71 * h + rng.uniform(0, 30) * s)
        elif typ == "skrytka_burta":  # w ścianie/dachu
            bw, bh = int(rng.uniform(15, 40) * s), int(rng.uniform(20, 80) * s)
            y = int(0.13 * h + rng.uniform(0, 0.4) * h)
        else:  # paczka na podłodze
            bw, bh = int(rng.uniform(30, 120) * s), int(rng.uniform(20, 70) * s)
            y = int(0.70 * h) - bh
        bw, bh = max(bw, 4), max(bh, 4)
        x = int(rng.uniform(0.06 * w, 0.94 * w - bw))
        sila = float(rng.uniform(0.08, 0.35))  # papierosy: niska/średnia gęstość
        kawalek = np.full((bh, bw), sila, np.float32)
        kawalek *= 1 + 0.15 * rng.standard_normal((bh, bw)).astype(np.float32)  # tekstura
        a[y:y + bh, x:x + bw] += kawalek
        maska[y:y + bh, x:x + bw] = True
        ramki.append([x, y, x + bw, y + bh, str(typ)])
    return a, ramki, maska


def skanuj(a: np.ndarray, rng: np.random.Generator, przes: int, f: float = 1.0) -> np.ndarray:
    """Mapa pochłaniania -> obraz RTG uint8 (Beer-Lambert, rozciągnięcie f w poziomie
    — zmienna prędkość przejazdu przez skaner liniowy, przesunięcie, szum, wzmocnienie)."""
    dx, dy = (int(v) for v in rng.integers(-przes, przes + 1, 2))
    if f != 1.0:
        a = ndimage.affine_transform(a, [1.0, 1.0 / f], order=1)
    a = np.roll(a, (dy, dx), axis=(0, 1))
    a = ndimage.gaussian_filter(a, 0.8)
    wzm = float(rng.uniform(0.92, 1.08))
    i = 235 * wzm * np.exp(-2.2 * a)
    i += rng.normal(0, 3.0, a.shape)
    # pasy detektora (typowe dla skanerów liniowych)
    i += rng.normal(0, 1.5, (a.shape[0], 1))
    return np.clip(i, 0, 255).astype(np.uint8)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wyjscie", default="dane/syntetyczne")
    p.add_argument("--czyste", type=int, default=20)
    p.add_argument("--dodatki", type=int, default=20)
    p.add_argument("--modele", type=int, default=5, help="liczba modeli naczep (wzorców)")
    p.add_argument("--szer", type=int, default=1200)
    p.add_argument("--wys", type=int, default=400)
    p.add_argument("--przes", type=int, default=6, help="maks. przesunięcie badany vs wzorzec [px]")
    p.add_argument("--rozciag", type=float, default=0.01, help="maks. względne rozciągnięcie w poziomie")
    p.add_argument("--ziarno", type=int, default=17)
    a = p.parse_args(argv)

    rng = np.random.default_rng(a.ziarno)
    out = Path(a.wyjscie)
    (out / "wzorce").mkdir(parents=True, exist_ok=True)
    (out / "badane").mkdir(parents=True, exist_ok=True)
    (out / "maski").mkdir(parents=True, exist_ok=True)
    modele = [model_naczepy(rng) for _ in range(a.modele)]
    mapy = [rysuj_wzorzec(m, a.szer, a.wys) for m in modele]
    for k, mp in enumerate(mapy):
        Image.fromarray(skanuj(mp, rng, 0)).save(out / "wzorce" / f"model{k:02d}.bmp")

    manifest = {"opis": "syntetyczny zbiór RTG naczep; ramki [x0,y0,x1,y1] w pikselach obrazu badanego",
                "parametry": vars(a), "probki": []}
    zadania = ["czysty"] * a.czyste + ["dodatki"] * a.dodatki
    for nr, rodzaj in enumerate(zadania):
        k = int(rng.integers(0, a.modele))
        mp, ramki = mapy[k], []
        maska = np.zeros(mp.shape, bool)
        if rodzaj == "dodatki":
            mp, ramki, maska = dodaj_dodatki(mp, rng, int(rng.integers(1, 4)))
        ident = f"{rodzaj}_{nr:04d}"
        # przesunięcie skanu dotyczy też prawdy — liczymy je tu, żeby ramki pasowały
        f = float(rng.uniform(1 - a.rozciag, 1 + a.rozciag))
        st = rng.bit_generator.state
        dx, dy = (int(v) for v in rng.integers(-a.przes, a.przes + 1, 2))
        rng.bit_generator.state = st
        img = skanuj(mp, rng, a.przes, f)
        ramki = [[round(x0 * f) + dx, y0 + dy, round(x1 * f) + dx, y1 + dy, t] for x0, y0, x1, y1, t in ramki]
        if f != 1.0:
            maska = ndimage.affine_transform(maska.astype(np.float32), [1.0, 1.0 / f], order=0) > 0.5
        Image.fromarray(img).save(out / "badane" / f"{ident}.bmp")
        Image.fromarray((np.roll(maska, (dy, dx), axis=(0, 1)) * 255).astype(np.uint8)).save(
            out / "maski" / f"{ident}_maska.png")
        manifest["probki"].append({"id": ident, "rodzaj": rodzaj, "wzorzec": f"wzorce/model{k:02d}.bmp",
                                   "badany": f"badane/{ident}.bmp", "rozciag": round(f, 4), "maska": f"maski/{ident}_maska.png",
                                   "ramki": [r[:4] for r in ramki], "typy": [r[4] for r in ramki]})
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    print(f"zbiór: {out} — {a.czyste} czystych, {a.dodatki} z dodatkami, {a.modele} wzorców, {a.szer}x{a.wys}")


if __name__ == "__main__":
    main()
