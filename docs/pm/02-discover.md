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
| 5 | Raport (miejsce, przedmiot kontroli) | wchodzi do 1 |
| 6 | Pewność przy każdej ramce | nie w v1 (pewność tylko w JSON) |
| 7 | Automatyczny wybór wzorca | nie w v1 |
| 8 | Dodawanie nowych wzorców | nie w v1 |
| 9 | „To nie anomalia” z pamięcią | nie w v1 |
| 10 | Wyjaśnienie alarmu | nie w v1 |

## 3. Najryzykowniejsze założenia (potwierdził Artur, 17:22: „ok”)
| Założenie | Ryzyko | Najtańszy test (w pokazie / ocenie) | Kryterium porażki |
|---|---|---|---|
| a) Dane syntetyczne ≈ prawdziwe skany | wynik na syntetyku nic nie mówi o KAS | ocena na zbiorze testowym zadania; jawnie opisać różnicę w README | wynik rozjeżdża się na obrazach spoza generatora |
| b) Wyrównanie da mało fałszywych alarmów | wynik bazowy: FP 20/20 (100%) z rozciągnięciem, 4/20 (20%) bez | wyrównanie nieliniowe + próg; liczyć FP/FN `./run.sh` | FP czystych > cel ustalony z Szefem (zał.: ≤ 10%) przy FN ≈ 0 |
| c) Operator zaufa werdyktowi | ślepa wiara lub ignorowanie | nakładka różnic widoczna obok wzorca (pomysł 2) — operator może sprawdzić | operator nie umie wskazać, skąd alarm |

## 4. Eksperymenty
1. **Wyrównanie nieliniowe** (zał.: rozciągnięcie ±1% poziomo to główne źródło FP): porównać FP/FN przed i po; odpowiedzialny: Programista.
2. **Demo 2 min** (pomysły 1+2): wybierz obraz → werdykt → nakładka → wzorzec obok; czas < 2 min.
3. **Czytelność dla operatora**: pokazać ekran jednej osobie bez wyjaśnień; pyta „co tu jest podejrzane?” — odpowiedź w < 10 s.

## 5. Wejście do `/write-prd`
- Zakres v1: pomysły 1 i 2 (+ raport z 5). Poza zakresem: 3, 4, 6–10, ukrycie w towarze.
- Kryteria akceptacji ze speca: FP/FN z `./run.sh`; demo < 2 min; nakładka włącz/wyłącz; JSON z ramkami i pewnością.
- Do ustalenia z Arturem przed speca: ekran główny, ścieżka, co w demo (krok c).

<!-- skill: przeplywy-pm -->
<!-- skill: brainstorm-ideas-new -->
<!-- skill: identify-assumptions-new -->
<!-- skill: prioritize-assumptions -->
<!-- skill: brainstorm-experiments-new -->
