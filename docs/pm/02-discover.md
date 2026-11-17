# 02 — /discover

**Podstawa**: `docs/pm/01-competitive-analysis.md`, `docs/decyzje.md` (Artur w pokoju 17:17–17:22), `docs/zadanie.md`. „(zał.)” = założenie bez źródła.

## 1. Ustalenia Artura (wejście)
- **Użytkownik**: operator RTG przy skanerze. Problem: małe skrytki łatwo przeoczyć, oglądanie każdego obrazu trwa. Zysk: od razu zaznaczone miejsca różnic względem wzorca, mało fałszywych alarmów.
- **Rola narzędzia**: samo wydaje werdykt „podejrzany / czysty” i zaznacza miejsca; o kontroli fizycznej decyduje operator.
- **Wzorzec**: ten sam typ pojazdu pusty lub ten sam pojazd „przed” załadunkiem; towar zgodny ze zgłoszeniem nie jest alarmem; alarm tylko na dodatek spoza konstrukcji i spoza typowego towaru. Ukrycie w samym towarze — poza v1.

## 2. Pomysły (10) i wybór
| # | Pomysł | Wybór Artura (17:21) |
|---|---|---|
| 1 | Alarm z ramkami: werdykt + ramki na obrazie badanym | **wybrany** |
| 2 | Wzorzec obok badanego z przełączaną nakładką różnic | **wybrany** |
| 3 | Suwak czułości | nie w v1 |
| 4 | Lista pojazdów z kolejką wg podejrzliwości | nie w v1 |
| 5 | Raport (miejsce, przedmiot kontroli, pełny JSON z 01) | wchodzi do 1 |
| 6 | Pewność przy każdej ramce | nie w v1 (pewność tylko w JSON, pełny zestaw pól) |
| 7 | Automatyczny wybór wzorca | nie w v1 |
| 8 | Dodawanie nowych wzorców | nie w v1 |
| 9 | „To nie anomalia” z pamięcią | nie w v1 |
| 10 | Wyjaśnienie alarmu | nie w v1 |

## 3. Najryzykowniejsze założenia (a–c potwierdził Artur 17:22 „ok”; d wynika z jego odp. 17:20 i zadania — Szef 17:31: bez nowych pytań)
| Założenie | Ryzyko | Najtańszy test (w pokazie / ocenie) | Kryterium porażki |
|---|---|---|---|
| a) Dane syntetyczne ≈ prawdziwe skany | wynik na syntetyku nic nie mówi o KAS (danych KAS nie mamy) | **zbiór kontrolny** (inne parametry generatora: inne modele naczep, inny szum i rozciągnięcie), nieużyty przy strojeniu; strojeniowy 50 czystych + 50 z dodatkami, kontrolny 50 + 50; w README jawnie opisać różnicę do prawdziwych skanów | **rozjazd = różnica FP lub FN między zbiorami > 10 pkt proc.** |
| b) Wyrównanie da brak fałszywych alarmów na czystych | wynik bazowy: FP 20/20 (100%) z rozciągnięciem, 4/20 (20%) bez | wyrównanie nieliniowe + próg; FP/FN z `./run.sh` | progi v1: **FP = 0 na czystych** (§6), **FN ≤ 10% ogółem i ≤ 20% dla małych skrytek** (mała skrytka = ramka < 1% pola obrazu); porażka = którykolwiek próg przekroczony |
| c) Operator zaufa werdyktowi | ślepa wiara lub ignorowanie | nakładka różnic widoczna obok wzorca (pomysł 2) — operator może sprawdzić | operator nie umie wskazać, skąd alarm |
| d) Towar zgodny ze zgłoszeniem nie wywoła alarmu (wzorzec „przed”/„po”, Artur 17:20); ukrycie w samym towarze poza v1 | towar daje FP albo maskuje małą skrytkę (zagrożenie z 01) | para przed/po z towarem zgodnym; wynik **mierzony i raportowany jako ograniczenie** (eksperyment 5), nie warunek gotowości | towar zgodny → ramka (FP) — zapis ograniczenia; bez wpływu na progi v1 |

## 4. Eksperymenty
1. **Wyrównanie nieliniowe** (zał.: rozciągnięcie ±1% poziomo to główne źródło FP): FP/FN przed i po, na zbiorze strojeniowym; odpowiedzialny: Programista.
2. **Zbiór kontrolny (test założenia a)**: strojeniowy 50 czystych + 50 z dodatkami; kontrolny (inne parametry generatora: inne modele naczep, szum, rozciągnięcie) 50 + 50, nieużyty przy strojeniu. Porażka = różnica FP lub FN > 10 pkt proc.
3. **Czas i pamięć na pełnym rozmiarze**: wynik bazowy był na 1200×400; zmierzyć czas na obraz ~50 MB (`--szer 7200 --wys 7200`), mediana i p95, szczytową pamięć oraz przetwarzanie partii (wiele par naraz). Kryterium: < 1 min na obraz (zadanie §7), partia bez awarii.
4. **Małe skrytki**: mała skrytka = ramka < 1% pola obrazu; FN osobno dla małych (cel ≤ 20%) i ogółem (cel ≤ 10%); krzywa FP/FN dla kilku progów.
5. **Para przed/po z towarem (test założenia d; ograniczenie, nie warunek gotowości)**: towar zgodny ze zgłoszeniem, bez dodatku → oczekiwany brak alarmu; zmierzyć i zapisać FP. Opcjonalnie (jeśli generator towaru gotowy — zał.): ten sam towar z dodatkiem ukrytym — zmierzyć FN, bez wymogu wskazania (poza v1). Ryzyko: towar maskuje małą skrytkę albo sam wywołuje FP — raportować w README/prezentacji jako ograniczenie.
6. **Demo 2 min** (pomysły 1+2): wybierz obraz → werdykt → nakładka → wzorzec obok; czas < 2 min.
7. **Czytelność dla operatora**: ekran pokazany jednej osobie bez wyjaśnień; pytanie „co tu jest podejrzane?” — odpowiedź w < 10 s.

## 5. Wejście do `/write-prd`
- Zakres v1: pomysły 1 i 2 (+ raport z 5); twarde kryteria dla par pusty/„przed” z dodatkami w konstrukcji. Poza zakresem: 3, 4, 6–10 oraz ukrycie w samym towarze (para z towarem — tylko raportowane ograniczenie, eksperyment 5).
- Kryteria akceptacji ze speca: **FP = 0 na czystych**; **FN ≤ 10% ogółem i ≤ 20% dla małych skrytek** (mała skrytka = ramka < 1% pola obrazu); zbiory: strojeniowy 50+50, kontrolny 50+50 (inne parametry generatora), rozjazd FP/FN ≤ 10 pkt proc.; **< 1 min na obraz ~50 MB**; przetwarzanie partii (wiele par naraz); demo < 2 min; nakładka włącz/wyłącz. Test z towarem (d) — raportowany, bez wpływu na gotowość.
- **Raport JSON w v1 — pełny zestaw z 01**: identyfikator kontroli, miejsce kontroli, przedmiot kontroli, urządzenie (Nuctech/Multicontrol), identyfikatory obrazu wzorcowego i badanego, czas analizy, werdykt, ramki z pewnością (wartości metadanych syntetyczne/ręczne — zał.). Wybór „1 i 2” dotyczył ekranu, nie skracania raportu.
- Do ustalenia z Arturem przed speca: ekran główny, ścieżka, co w demo (krok c).

<!-- skill: przeplywy-pm -->
<!-- skill: brainstorm-ideas-new -->
<!-- skill: identify-assumptions-new -->
<!-- skill: prioritize-assumptions -->
<!-- skill: brainstorm-experiments-new -->
