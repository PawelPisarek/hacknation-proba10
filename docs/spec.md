# Spec v1 — wyszukiwarka anomalii na obrazach RTG (KAS)

**Źródła**: `docs/pm/03-write-prd.md`, `02-discover.md`, `01-competitive-analysis.md`, `docs/decyzje.md` (Artur w pokoju 17:17–17:36), `docs/zadanie.md`. „(zał.)” = założenie. Dane na ekranach są **udawane** (syntetyczne, z generatora Programisty).

## 1. Co zobaczy i zrobi użytkownik (według Artura)
Operator RTG otwiera jeden ekran, wybiera parę (wzorzec + badany), klika „Analizuj”, czyta werdykt, patrzy na ramki, włącza/wyłącza nakładkę różnic i zapisuje raport. Narzędzie samo orzeka; o kontroli fizycznej decyduje operator (17:19). Wzorzec = ten sam typ pojazdu pusty lub „przed” (17:20). Zakres = pomysły 1 i 2 (17:21).

## 2. Ekrany (makieta)
Jeden ekran „Analiza pary”. Układ od góry:

| Blok | Zawartość | Dane udawane |
|---|---|---|
| **Pasek wyboru** | lista „Obraz wzorcowy”, lista „Obraz badany”, przycisk **Analizuj**; pole „Miejsce kontroli”, „Przedmiot kontroli”, „Urządzenie” (Nuctech/Multicontrol) | wzorce: `wzorzec_model1…5.bmp`; badane: `badany_c01…c05.bmp` (czyste), `badany_d01…d05.bmp` (z dodatkami); miejsce: „Terespol, pas 2”; przedmiot: „naczepa model 3”; urządzenie: „Nuctech” |
| **Werdykt** (duży pasek) | „PODEJRZANY — 3 zaznaczone miejsca” na czerwono albo „CZYSTY — brak zaznaczeń” na zielono; obok czas analizy („4,2 s”) | z wyniku analizy |
| **Dwa obrazy obok siebie** | lewo: wzorzec; prawo: badany z czerwonymi ramkami (numerowane 1…n); nad prawym obrazem przełącznik **„pokaż różnice”** (włącza/wyłącza półprzezroczystą nakładkę różnic i ramki) | obrazy RTG syntetyczne naczepy (np. 1200×400 na ekranie; pełny plik ~50 MB przeskalowany) |
| **Lista ramek** (pod obrazami) | wiersz na ramkę: nr, pozycja (x, y), rozmiar; kliknięcie wiersza podświetla ramkę (pewność tylko w JSON) | np. „1 · (412, 88) · 40×22” |
| **Zapisz raport** | przycisk zapisuje nakładkę PNG i plik JSON; komunikat „Zapisano: raport_<id>.png / .json” | patrz §4 |
| **Wynik na zbiorze testowym** (zakładka lub sekcja na dole) | przycisk „Wczytaj wynik” (plik policzony wcześniej, nie liczony na żywo); tabela osobno dla zbioru **strojeniowego** i **kontrolnego**: FP (czyste z alarmem, x/50), FN ogółem (y/50), FN małych skrytek, **rozjazd** zbiorów w pkt proc. (FP i FN), czas na obraz: mediana i p95; przy każdym progu znacznik spełnia/nie; osobny wiersz **„ograniczenie: para z towarem zgodnym”** (FP/FN, nie warunek gotowości) | wynik z `./run.sh` / `rtg/ocena.py` zapisany do pliku JSON; wartości z ostatniego przebiegu |

Stany: przed analizą — werdykt „Wybierz parę i kliknij Analizuj”; w trakcie — „Analiza…” z blokadą przycisku; błąd pliku (nie .bmp / uszkodzony) — czerwony komunikat „Nie można wczytać obrazu”, bez zawieszenia.

## 3. Główna ścieżka (demo < 2 min)
1. (0:00) Wybierz wzorzec model 3 i badany `d03` (z dodatkiem) → **Analizuj**.
2. (0:15) Werdykt „PODEJRZANY — 2 miejsca”, ramki na prawym obrazie; przełącz „pokaż różnice” (nakładka znika i wraca).
3. (0:40) Kliknij wiersz ramki 1 — podświetla się; **Zapisz raport** — komunikat z nazwami plików.
4. (1:00) Wybierz badany `c03` (czysty) → Analizuj → „CZYSTY — brak zaznaczeń”.
5. (1:20) „Wczytaj wynik”: tabela z wynikiem na zbiorze testowym wczytana z pliku policzonego wcześniej (strojeniowy i kontrolny: FP, FN ogółem i małych, rozjazd, mediana i p95 czasu, wiersz „ograniczenie”) — nie liczymy na żywo.
Wszystko musi działać na wcześniej przygotowanych parach, bez ręcznego wpisywania.

## 4. Raport
- **PNG**: obraz badany z zaznaczonymi ramkami (numery jak na ekranie).
- **JSON (pełny zestaw z 01)**: identyfikator kontroli, miejsce kontroli, przedmiot kontroli, urządzenie, identyfikatory obrazu wzorcowego i badanego, czas analizy, werdykt, ramki (x, y, szer., wys., **pewność — tylko tu, nie na ekranie**).
- **Partie (wiersz poleceń, bez ekranu)**: `python -m rtg.partia <folder_par | lista.txt> --wyj <folder>`; wejście: folder z parami (`wzorzec_*.bmp` + `badany_*.bmp`) albo lista par w pliku tekstowym (wzorzec;badany); wynik: JSON + PNG na parę (nazwa komendy do potwierdzenia przez Programistę, zał.). Kompresja = nakładka PNG lub zmniejszony podgląd; plik oryginalny bez zmian. Wartości metadanych syntetyczne lub z pól ekranu (zał.).

## 5. Kryteria akceptacji (z `02-discover.md`, progi Szefa 17:33; PRD §4 zgodne)
**Zakres twardych kryteriów**: pary pusty/„przed” z dodatkiem w pojeździe; „paczka na podłodze” to też dodatek (liczy się do FN i do 50 + 50).
1. **FP = 0** na czystych obrazach (zbiór strojeniowy 50 + kontrolny 50).
2. **FN ≤ 10%** ogółem i **≤ 20% dla małych skrytek** (ramka < 1% pola obrazu); wskazanie = pokrycie ≥ 50% ramki dodatku lub IoU ≥ 0,3 (Programista 17:15).
3. Zbiory: strojeniowy 50 + 50, kontrolny 50 + 50 (inne parametry generatora); **rozjazd** FP lub FN > 10 pkt proc. = porażka założenia (a).
4. **< 1 min na obraz ~50 MB** (mediana i p95), zbiór kontrolny (100 par) przetworzony z wiersza poleceń **bez awarii**; narzędzie działa **bez sieci**.
5. Ekran: werdykt widoczny bez przewijania; przełącznik nakładki działa; ramki zgodne z JSON (pewność tylko w JSON); raport zapisuje się (PNG + JSON).
6. Demo z §3 mieści się w < 2 min.
7. Czytelność (założenie c): osoba bez wyjaśnień odpowiada „co tu jest podejrzane?” w < 10 s.
9. Wynik na zbiorze testowym na ekranie zawiera wszystkie wartości z §2 (strojeniowy, kontrolny, FP, FN, FN małych, rozjazd, mediana, p95).
8. Para z towarem zgodnym ze zgłoszeniem (eksperyment 5 z 02): **mierzona i raportowana jako ograniczenie** — osobny wiersz na ekranie wyniku i w README; nie warunek gotowości. Ukrycie w samym towarze poza v1.

## 6. Ryzyka (najryzykowniejsze założenia z `/discover`)
- **(b) Wyrównanie**: bazowo FP 100% (z rozciągnięciem), 20% bez — najsłabsze miejsce; kolejność prac: najpierw wyrównanie i ocena (FP), ekran na udawanych danych równolegle.
- **(a) Syntetyk ≠ prawdziwe skany**: jawnie opisane w README; test zbiorem kontrolnym.
- **(c) Zaufanie operatora**: nakładka i wzorzec obok pozwalają sprawdzić werdykt.
- **(d) Towar**: może dać FP lub maskować małą skrytkę — ograniczenie w README/prezentacji.
- **Format .bmp obu dostawców**: zał. ten sam format; sprawdza Programista (0P).
- **Skala**: 50 MB na ekranie — przeskalowany podgląd, analiza na pełnym pliku (kafelki).

## 7. Poza v1
Suwak czułości, kolejka pojazdów, pewność ramki na ekranie (jest tylko w JSON), automatyczny wybór wzorca, dodawanie wzorców, „to nie anomalia”, wyjaśnienie alarmu, ukrycie w samym towarze, logowanie, integracja z repozytorium KAS.

<!-- skill: przeplywy-pm -->
<!-- skill: create-prd -->
<!-- skill: write-prd -->
