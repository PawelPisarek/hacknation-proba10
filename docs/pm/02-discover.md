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
| a) Dane syntetyczne ≈ prawdziwe skany | wynik na syntetyku nic nie mówi o KAS (danych KAS nie mamy) | **zbiór kontrolny** z innymi parametrami generatora (inne modele naczep, inny szum i rozciągnięcie), którego nie użyto przy strojeniu; progi i metodę stroimy tylko na zbiorze strojeniowym; w README jawnie opisać różnicę do prawdziwych skanów | wyraźny rozjazd FP lub FN między zbiorem strojeniowym a kontrolnym (np. FP czystych > 0 na kontrolnym przy 0 na strojeniowym albo FN dodatków wyraźnie wyższy) |
| b) Wyrównanie da brak fałszywych alarmów na czystych | wynik bazowy: FP 20/20 (100%) z rozciągnięciem, 4/20 (20%) bez | wyrównanie nieliniowe + próg; liczyć FP/FN `./run.sh` | **cel wg zadania §6: FP = 0 na czystych obrazach** (czysty obraz bez żadnego zaznaczenia); porażka = jakikolwiek czysty obraz z ramką przy FN ogółem i dla małych skrytek nie gorszym niż reszta |
| c) Operator zaufa werdyktowi | ślepa wiara lub ignorowanie | nakładka różnic widoczna obok wzorca (pomysł 2) — operator może sprawdzić | operator nie umie wskazać, skąd alarm |
| d) Towar zgodny ze zgłoszeniem nie wywoła alarmu, a dodatek ukryty w ładunku zostanie wskazany (wzorzec „przed” i „po”, Artur 17:20) | towar daje FP albo maskuje małą skrytkę (zagrożenie z 01) | para przed/po z towarem zgodnym ze zgłoszeniem; para przed/po z dodatkiem ukrytym wśród towaru (eksperyment 5) | towar zgodny → ramka (FP) albo dodatek ukryty → brak ramki (FN) |

## 4. Eksperymenty
1. **Wyrównanie nieliniowe** (zał.: rozciągnięcie ±1% poziomo to główne źródło FP): FP/FN przed i po, na zbiorze strojeniowym; odpowiedzialny: Programista.
2. **Zbiór kontrolny (test założenia a)**: osobny zbiór z innymi parametrami generatora (inne modele naczep, szum, rozciągnięcie), nieużyty przy strojeniu; porównać FP/FN ze zbiorem strojeniowym. Porażka = wyraźny rozjazd.
3. **Czas i pamięć na pełnym rozmiarze**: wynik bazowy był na 1200×400; zmierzyć czas na obraz ~50 MB (`--szer 7200 --wys 7200`), mediana i p95, szczytową pamięć oraz przetwarzanie partii (wiele par naraz). Kryterium: < 1 min na obraz (zadanie §7), partia bez awarii.
4. **Małe skrytki**: FN osobno dla najmniejszych dodatków i dla całości; krzywa FP/FN dla kilku progów.
5. **Para przed/po z towarem (test założenia d)**: (i) towar zgodny ze zgłoszeniem, bez dodatku → brak alarmu; (ii) ten sam towar z dodatkiem ukrytym → alarm i ramka. Ryzyko: towar maskuje małą skrytkę (FN) albo sam wywołuje FP; wynik zapisać jako ograniczenie v1, jeśli generator towaru nie jest gotowy (zał.).
6. **Demo 2 min** (pomysły 1+2): wybierz obraz → werdykt → nakładka → wzorzec obok; czas < 2 min.
7. **Czytelność dla operatora**: ekran pokazany jednej osobie bez wyjaśnień; pytanie „co tu jest podejrzane?” — odpowiedź w < 10 s.

## 5. Wejście do `/write-prd`
- Zakres v1: pomysły 1 i 2 (+ raport z 5). Poza zakresem: 3, 4, 6–10; ukrycie w samym towarze nie jest obietnicą v1 — eksperyment 5 mierzy to jako ograniczenie/ryzyko.
- Kryteria akceptacji ze speca: **FP = 0 na czystych obrazach** (zadanie §6) i FN ogółem oraz osobno dla małych skrytek (`./run.sh`, zbiór strojeniowy i kontrolny bez wyraźnego rozjazdu); **< 1 min na obraz ~50 MB** i przetwarzanie partii (wiele par naraz); demo < 2 min; nakładka włącz/wyłącz; towar zgodny ze zgłoszeniem bez alarmu (test d).
- **Raport JSON w v1 — pełny zestaw z 01**: identyfikator kontroli, miejsce kontroli, przedmiot kontroli, urządzenie (Nuctech/Multicontrol), identyfikatory obrazu wzorcowego i badanego, czas analizy, werdykt, ramki z pewnością (wartości metadanych syntetyczne/ręczne — zał.). Wybór „1 i 2” dotyczył ekranu, nie skracania raportu.
- Do ustalenia z Arturem przed speca: ekran główny, ścieżka, co w demo (krok c).

<!-- skill: przeplywy-pm -->
<!-- skill: brainstorm-ideas-new -->
<!-- skill: identify-assumptions-new -->
<!-- skill: prioritize-assumptions -->
<!-- skill: brainstorm-experiments-new -->
