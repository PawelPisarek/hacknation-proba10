# 03 — /write-prd

## Product Requirements Document: Wyszukiwarka anomalii na obrazach RTG pojazdów (KAS), wersja 1

**Autor**: Projektant · **Data**: 2026-11-17 · **Status**: Draft
**Podstawa**: `docs/pm/01-competitive-analysis.md`, `docs/pm/02-discover.md`, `docs/decyzje.md` (Artur w pokoju 17:17–17:36), `docs/zadanie.md`. „(zał.)” = założenie bez źródła.

## 1. Summary
Narzędzie porównuje obraz RTG badanego pojazdu z obrazem wzorcowym, samo wydaje werdykt „PODEJRZANY / CZYSTY”, zaznacza ramkami miejsca różnic i zapisuje raport. O kontroli fizycznej decyduje operator (Artur, 17:19). Jeden ekran, jedna ścieżka, demo poniżej 2 min.

## 2. Contacts
Artur (kształt produktu; w próbie gra go Paweł), Paweł (technika, wygląd, użyteczność), Programista (kod i makieta), Analityk (kryteria, ryzyka), Prezenter (README, teksty).

## 3. Background
Operatorzy RTG KAS oceniają obrazy pojazdów ręcznie; obecne narzędzie wykrywa papierosy, ale słabo małe ilości w konstrukcji (zadanie §1). Luka rynkowa: wykrywanie dowolnej zmiany względem wzorca, niezależnie od dostawcy skanera (01). Wynik bazowy Programisty (17:15, syntetyk 1200×400): sztywne wyrównanie daje FP 20/20 czystych i FN 0/34; bez rozciągnięcia FP 4/20 — wyrównanie to wąskie gardło (02, założenie b).

## 4. Objective
- **Cel**: operator od razu widzi, czy pojazd różni się od wzorca i gdzie, bez oglądania całego obrazu.
- **Metryki v1 (progi Szefa 17:33; zgodne ze spec §5)**: FP = 0 na czystych; FN ≤ 10% ogółem i ≤ 20% dla małych skrytek (ramka < 1% pola obrazu); wskazanie = pokrycie ≥ 50% ramki dodatku lub IoU ≥ 0,3; < 1 min na obraz ~50 MB (mediana i p95); zbiór strojeniowy 50+50 i kontrolny 50+50, rozjazd FP lub FN > 10 pkt proc. = porażka założenia (a); zbiór kontrolny (100 par) z wiersza poleceń bez awarii, bez sieci; czytelność: osoba bez wyjaśnień wskazuje, co jest podejrzane, w < 10 s; demo < 2 min.
- **Twarde kryteria dotyczą par pusty/„przed” z dodatkiem w pojeździe** (skrytka w ramie, w burcie, „paczka na podłodze” — też dodatek, liczy się do FN i do 50+50). Para z towarem zgodnym = eksperyment 5 z 02, mierzona i raportowana jako **ograniczenie** (wiersz na ekranie wyniku i w README), nie warunek gotowości.

## 5. Market Segments
- **Główny**: operator RTG przy skanerze KAS (Artur 17:17). Problem: małe skrytki łatwo przeoczyć, oglądanie każdego obrazu trwa. Obejście dziś: ręczna ocena + detektor papierosów.
- **Poza v1**: analityk w repozytorium obrazów, integratorzy IT KAS (zał.).

## 6. Value Proposition
- **Who**: operator RTG przy skanerze.
- **Why**: chce szybko i pewnie wiedzieć, czy pojazd ma coś spoza konstrukcji.
- **What before**: ogląda obraz w całości; małe skrytki umykają; detektor łapie tylko papierosy.
- **How**: wzorzec obok badanego, werdykt z ramkami, nakładka różnic do sprawdzenia, raport do zapisu.
- **What after**: od razu widzi zaznaczone miejsca, mało fałszywych alarmów, raport z miejscem i przedmiotem kontroli.
- **Alternatives**: ręczna ocena, detektory dostawców (Rapiscan InSight, Nuctech AI — wg 01), detektor papierosów KAS.

## 7. Solution
- Pomysły wybrane przez Artura (17:21): **1** alarm z ramkami, **2** wzorzec obok badanego z przełączaną nakładką różnic; raport (5) wchodzi do 1.
- Rola: automat sam orzeka (17:19). Wzorzec: ten sam typ pojazdu pusty lub „przed” (17:20); towar zgodny ze zgłoszeniem nie jest alarmem.
- Ekran, ścieżka i demo (Artur 17:36 „jest ok”): `docs/spec.md`.
- **Założenia i pytania otwarte**: (a) syntetyk ≈ prawdziwe skany — test zbiorem kontrolnym; (b) wyrównanie da FP = 0 — eksperyment 1 z 02; (c) operator zaufa werdyktowi — test czytelności (< 10 s); (d) towar zgodny — mierzone jako ograniczenie. Zał.: .bmp obu dostawców ma ten sam format — sprawdza Programista w kroku 0P.

## 8. Release
- **v1**: jeden ekran + raport (PNG z zaznaczeniami + JSON pełny z 01) + ekran wyniku na zbiorze testowym (wczytany z pliku policzonego wcześniej) + **partie z wiersza poleceń** (folder lub lista par → JSON + PNG na parę; bez listy partii na ekranie). Praca bez sieci. Kompresja = nakładka PNG lub zmniejszony podgląd; oryginał bez zmian.
- **Kolejność prac**: najpierw wyrównanie i ocena (FP), ekran na udawanych danych równolegle.
- **Poza v1** (Artur 17:21): suwak czułości, kolejka pojazdów, pewność ramki na ekranie (jest tylko w JSON), automatyczny wybór wzorca, dodawanie wzorców, „to nie anomalia”, wyjaśnienie alarmu; ukrycie w samym towarze.
- **Zostawione celowo**: logowanie, role, integracja z repozytorium KAS.

<!-- skill: przeplywy-pm -->
<!-- skill: create-prd -->
<!-- skill: przesluchanie-hackathon -->
<!-- skill: write-prd -->
