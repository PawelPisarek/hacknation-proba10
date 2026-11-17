# Competitive Analysis: wykrywanie anomalii na obrazach RTG pojazdów (KAS)

**Data**: 2026-11-17 · **Przeanalizowano**: 5 konkurentów bezpośrednich + 3 pośrednich + 5 podejść do detekcji
**Podstawa**: `docs/zadanie.md`, `docs/decyzje.md` (w tym wynik bazowy Programisty, 17:15); badanie sieciowe (źródła na końcu). „(zał.)” = założenie bez źródła; liczby vendorów są marketingowe i jednoźródłowe.

## Kontekst (krok 1 skilla)
- **Produkt**: narzędzie porównujące obraz RTG badanego pojazdu z wzorcem, zaznaczające różnice i dające raport (nakładka PNG + JSON z ramkami i pewnością — decyzja Szefa 17:16). Wejście: .bmp ~50 MB, partie, docelowo bez chmury.
- **Użytkownik (Artur w pokoju, 17:17)**: operator RTG przy skanerze; problem: małe skrytki przeoczone i dużo oglądania; zysk: od razu zaznaczone miejsca różnic względem wzorca, mało fałszywych alarmów.
- **Rola narzędzia (pytanie 2, Artur w pokoju 17:19: „samo może orzec” — przyjęte)**: zadanie §3 każe działać „samodzielnie, bez interwencji człowieka”, a §1 mówi o wsparciu operatora. Rozstrzygnięcie: **automat sam analizuje pary/grupy obrazów i wydaje werdykt alarm / brak alarmu z ramkami; decyzję o kontroli fizycznej zawsze podejmuje operator** (narzędzie nie zleca kontroli). Powód: spełnia §3 i nie zastępuje decyzji funkcjonariusza.
- **Wzorzec (pytanie 3, Artur w pokoju 17:20: „tak” — przyjęte)**: §7 mówi o parach/grupach „przed i po” załadunku, a wstęp o ukryciu także w samym towarze. Rozstrzygnięcie (rekomendacja): **wzorzec = obraz tego samego typu pojazdu pustego albo tego samego pojazdu „przed” załadunkiem**; dla „po” różnice wynikające z towaru zgłoszonego (kształt/gęstość spodziewanego ładunku) **nie są alarmem**; alarm dla dodatku spoza konstrukcji i spoza typowego towaru (np. mała skrytka w ramie, burcie, podłodze). Ukrycie w samym towarze to zakres po v1 (wymaga wzorca towaru) — ryzyko, nie obietnica. Zbiór syntetyczny Programisty zawiera tylko pustą naczepę vs badany z dodatkami.
- **Metadane (zadanie §9)**: wyniki mają trafiać do repozytorium z przypisaniem do **miejsca i przedmiotu kontroli**, obrazy pochodzą z urządzeń Nuctech i Multicontrol. Raport (JSON) zawiera więc: identyfikator kontroli, miejsce kontroli, przedmiot kontroli (pojazd/typ), urządzenie (Nuctech/Multicontrol), identyfikatory obrazu wzorcowego i badanego, czas analizy, werdykt, ramki z pewnością. Na hackathonie wartości syntetyczne/podane ręcznie (zał.).
- **Ograniczenia z zadania**: ocena po FP na „czystych” i FN na obrazach z „dodatkami”, innowacyjność, skalowalność; < 1 min/obraz; ochrona danych KAS; własny zbiór syntetyczny.

## Przegląd rynku
Skanery wielkogabarytowe (Nuctech, Smiths Detection, Rapiscan/OSI; Leidos — zał., bez źródła) mają wbudowane narzędzia wspomagające operatora. Dominują detektory **konkretnych klas** (u KAS działa detektor papierosów, słaby przy małych ilościach w konstrukcji — zadanie §1) oraz narzędzia „high density / empty container” (Rapiscan, źródło niżej; u pozostałych zał.). Luka: **wykrywanie nieznanych zmian względem wzorca** (skrytki, przeróbki). Rozwiązania vendorów są zależne od sprzętu; KAS potrzebuje narzędzia działającego na obrazach obu dostawców.

## Krajobraz konkurencji
| Konkurent | Kategoria | Odbiorca | Pozycjonowanie | Mocna strona | Słaba strona |
|---|---|---|---|---|---|
| Rapiscan (OSI) – InSight (Empty Container, High Density, Non-Homogeneous Cargo) | bezpośredni | służby graniczne/celne | analityka obrazu w ekosystemie skanera | porównanie z pustym kontenerem, algorytmy intensywność/tekstura/kształt; 96% wykrycia / 3% fałszywych alarmów na realnym cargo (jedno źródło: slajd konferencyjny CBP 2023) | związane z własnym sprzętem; cena i szczegóły nieujawnione |
| Nuctech – platforma inspekcji z warstwą AI | bezpośredni | celne, granice (dostawca KAS) | „inteligentna platforma inspekcji” z głębokim uczeniem (artykuł prasowy) | integracja ze skanerem | brak publicznych metryk dla anomalii/pustego pojazdu; zamknięta (zał.) |
| Smiths Detection | bezpośredni | lotniska, granice | algorytmy detekcji zagrożeń (zał. — brak źródła dla cargo) | marka (zał.) | brak publicznych danych o AI dla cargo (zał.) |
| Multicontrol | bezpośredni | celne (dostawca KAS) | skanery wielkogabarytowe (zadanie §1) | obecny u KAS | brak publicznych informacji o module anomalii (zał.) |
| Obecne narzędzie KAS (detektor papierosów) | bezpośredni (wewnętrzny) | operatorzy KAS | detekcja jednej klasy (zadanie §1) | już wdrożone | słabe przy małych ilościach w konstrukcji (zadanie §1) |
| Pośredni: ręczna ocena operatora | pośredni | wszyscy | obecny standard (zadanie §1) | elastyczny | zmęczenie, czas (zał.) |
| Pośredni: kontrola fizyczna | pośredni | celnicy | pewna | skuteczna | wolna, kosztowna (zał.) |
| Pośredni: badania akademickie (Tufts: ~98%, trening na syntetycznych anomaliach — deklaracja autorów) | pośredni | — | dowód, że syntetyk działa | uzasadnia nasz zbiór | brak produktu; nie niezależny benchmark |

## Przegląd metod detekcji anomalii na obrazach
| Podejście | Jak działa | Plus | Minus | Dopasowanie |
|---|---|---|---|---|
| **A. Różnica po wyrównaniu** | dopasowanie pary, mapa różnic | wprost wzorzec–badany; bez treningu; wyjaśnialne | wrażliwe na przesunięcie, skalę, rozciągnięcie, szum → FP | rdzeń; **zmierzone: sztywne wyrównanie (korelacja fazowa + próg 5σ) daje FP 20/20, FN 0/34 (379 fałszywych ramek); bez rozciągnięcia FP 4/20** (Programista, 17:15, 1200×400, zbiór syntetyczny) |
| **B. Pamięć łatek (PatchCore, PaDiM)** | cechy łatek z „czystych”; anomalia = łatka daleka od normy | lokalizacja, bez etykiet, odporne na szum (badanie przemysłowe RTG) | pamięć/czas przy 50 MB → kafelki; brak benchmarku na pojazdach | pasuje do §5 |
| **C. Autoenkoder** | słabo odtwarza to, czego nie było w „czystych” | prosty | rozmyte rekonstrukcje → FP na detalach | uzupełnienie |
| **D. Nadzorowana segmentacja dodatków** | uczenie na oznaczonych dodatkach | dokładna dla znanych klas | wymaga etykiet; nie uogólnia; ryzyko rozjazdu syntetyk–rzeczywistość | pomocniczo |
| **E. Hybryda** | wyrównanie **odporne na rozciągnięcie/odkształcenie w poziomie** (pierwszy krok) → różnica → ocena łatek; próg z „czystych” | wynik bazowy pokazuje, że wyrównanie jest wąskim gardłem | więcej elementów | rekomendacja do `/discover` |

**Kryterium wyboru metody (liczy oba błędy):** na tym samym zbiorze syntetycznym (czyste + z dodatkami, w tym **najmniejsze skrytki**) mierzymy: FP% na czystych obrazach (docelowo 0 — §6), FN% na dodatkach ogółem **i osobno dla małych skrytek**, liczbę fałszywych ramek na obraz oraz czas na obraz (< 1 min). Metoda wygrywa, gdy minimalizuje FP + FN przy FN małych skrytek nie gorszym niż reszta; metoda z FN 0 kosztem FP 100% (jak bazowa) odpada. Ranking dla pojazdów RTG nie jest zweryfikowany publicznie — decyduje własny pomiar.

## Macierz funkcji (konkurenci; „?” = brak publicznych danych)
| Zdolność | Rapiscan InSight | Nuctech AI | Smiths / Multicontrol | Detektor papierosów KAS | Operator ręcznie |
|---|---|---|---|---|---|
| Porównanie pary wzorzec–badany | tak, „Empty Container” | ? | ? | nie | tak (wzrokowo) |
| Nieznane anomalie bez klasy | ograniczone | ? | ? | nie | tak |
| Raport z zaznaczonymi obszarami | tak, w oprogramowaniu skanera | ? | ? | tak (zał.) | nie |
| Niezależność od producenta skanera | nie | nie | nie | zał. | tak |
| Działanie lokalne | zwykle tak (zał.) | zwykle tak (zał.) | ? | tak | tak |
| Publiczne FP/FN | jedno źródło (3% FP) | brak | brak | brak | brak |

Nasz cel względem tej macierzy: sekcja „Szanse różnicowania”.

## Mapa pozycjonowania (2×2)
Oś X: wymaga znanej klasy ↔ wykrywa dowolną zmianę względem wzorca; oś Y: związany ze sprzętem ↔ niezależny od dostawcy.
- Dół-lewo: detektor papierosów, moduły vendorów.
- Dół-prawo: Rapiscan Empty Container (częściowo).
- Góra-prawo: **nasz cel** (dowolna zmiana, niezależne od skanera).
- Góra-lewo: pusta.

## Szanse różnicowania
1. **Dowolna zmiana względem wzorca, bez listy klas** — luka z zadania (małe skrytki w konstrukcji).
2. **Niezależność od dostawcy skanera (.bmp z Nuctech i Multicontrol)** — KAS integruje oba.
3. **Raport zrozumiały dla operatora** — nakładka z ramkami, pewność, metadane kontroli (miejsce, przedmiot) gotowe do repozytorium (§9).
4. **Kontrola FP jako cecha** — kryterium oceny to FP/FN; wynik bazowy pokazuje, że to główne ryzyko.
5. **Lokalne, skalowalne przetwarzanie dużych plików** (kafelki, partie) — wymóg zadania i wdrożenia bez chmury.

## Zagrożenia
1. **Rozjazd syntetyk–rzeczywistość** — wyniki na własnym zbiorze nie przeniosą się 1:1; mówimy to otwarcie.
2. **Rozciągnięcie/odkształcenie przy przejeździe** — zmierzone źródło FP (bazowy: FP 100%); wymaga wyrównania nieliniowego.
3. **Vendorzy rozszerzają moduły o porównanie z wzorcem** — odpowiedź: niezależność od sprzętu i raport.
4. **Towar a wzorzec** — różnice od towaru mogą dawać FP lub maskować skrytkę w towarze (poza v1).
5. **Ochrona danych KAS** — nie kopiować poza cel hackathonu.

## Rekomendacje
- **Postaw na**: porównanie z wzorcem + odporne wyrównanie + kontrola FP + raport z metadanymi kontroli.
- **Dociągnij (table stakes)**: .bmp ~50 MB, partie, < 1 min/obraz.
- **Zignoruj**: wyścig na klasy przedmiotów (papierosy, broń).

## Hipotezy / ustalenia z Arturem
- ✔ Użytkownik, problem, zysk (17:17, „ok”): operator RTG przy skanerze; małe skrytki przeoczone i dużo oglądania; zysk — zaznaczone miejsca różnic i mało fałszywych alarmów.
- ✔ Rola narzędzia (alarm + ramki, decyduje operator) — pytanie 2, Artur w pokoju 17:19.
- ✔ Wzorzec (pusty lub „przed”; towar zgodny ze zgłoszeniem nie jest alarmem) — pytanie 3, Artur w pokoju 17:20.
- Do `/discover`: wybór metody według kryterium powyżej; ukrycie w towarze jako ryzyko.

## Źródła (wyniki wyszukiwania z 2026-11-17; strony nie otwierane w całości)
- [Rapiscan InSight Operator Assist Tools](https://www.rapiscan-ase.com/products/software/insight-operator-assist-tools)
- [Rapiscan – technologia](https://rapiscan-ase.com/resource-center/technology)
- [Tufts – AI do kontrabandy](https://now.tufts.edu/2025/01/09/new-ai-enabled-technology-98-accurate-spotting-illegal-contraband)
- [Illicit object detection in X-ray imaging](https://arxiv.org/html/2507.17508v1)
- [Anomalib – przewodnik](https://www.ml6.eu/blogpost/a-practical-guide-to-image-based-anomaly-detection-using-anomalib)
- [Unsupervised anomaly instance segmentation for baggage](https://khazna.ku.ac.ae/en/publications/unsupervised-anomaly-instance-segmentation-for-baggage-threat-rec/)
- [X-ray anomaly detection in industrial pipelines](https://icarus.csd.auth.gr/wp-content/uploads/2024/10/X-ray_Anomaly_Detection_in_Industrial_Pipelines.pdf)
- [Orange – Contraband AI](https://hellofuture.orange.com/en/contraband-ai-efficiently-detects-anomalies-in-shipping-containers/)
- Wynik bazowy: `docs/decyzje.md`, wpis 17:15.

<!-- skill: przeplywy-pm -->
<!-- skill: competitor-analysis -->
