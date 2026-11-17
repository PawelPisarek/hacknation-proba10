# Competitive Analysis: wykrywanie anomalii na obrazach RTG pojazdów (KAS)

**Data**: 2026-11-17 · **Przeanalizowano**: 5 konkurentów bezpośrednich + 3 pośrednich + 4 rodziny metod
**Podstawa**: `docs/zadanie.md`, `docs/decyzje.md`; badanie sieciowe (źródła na końcu). Liczby vendorów są marketingowe/jednoźródłowe — oznaczone „(zał.)” tam, gdzie nie zweryfikowane.

## Kontekst (krok 1 skilla)
- **Produkt**: narzędzie, które porównuje obraz RTG badanego pojazdu z wzorcem (pusty/czysty środek przewozowy), zaznacza różnice i generuje raport z zaznaczonymi obszarami. Wejście: pliki .bmp (~50 MB), partie, bez chmury docelowo.
- **Kategoria**: AI wspierające operatora RTG w kontroli nieinwazyjnej (cargo/pojazdy).
- **Soczewka**: funkcje i podejście do detekcji; zastosowanie: wybór kształtu produktu i metody na hackathon.
- **Ustalone zadaniem**: ocena po FP na obrazach „czystych” i FN na obrazach z „dodatkami”, innowacyjność, skalowalność; działanie lokalne.
- **Ograniczenie**: danych KAS nie mamy — własny syntetyczny zbiór (`docs/decyzje.md`).

## Przegląd rynku
Skanery wielkogabarytowe (Nuctech, Smiths Detection, Rapiscan/OSI, Leidos) mają wbudowane narzędzia wspomagające operatora. Dominują detektory **konkretnych klas** (papierosy, broń, narkotyki — u KAS już działa detektor papierosów, słaby przy małych ilościach w konstrukcji) oraz narzędzia „high density / empty container”. Luka, którą wskazuje zadanie: **wykrywanie nieznanych zmian względem wzorca** (skrytki, przeróbki), bez listy klas. Producenci sprzętu sprzedają to wraz ze skanerem (zamknięte, zależne od dostawcy); KAS potrzebuje rozwiązania działającego na obrazach obu dostawców (Nuctech i Multicontrol).

## Krajobraz konkurencji
| Konkurent | Kategoria | Odbiorca | Pozycjonowanie | Mocna strona | Słaba strona |
|---|---|---|---|---|---|
| Rapiscan (OSI) – InSight (Empty Container, High Density, Non-Homogeneous Cargo) | bezpośredni | służby graniczne/celne | analityka obrazu w ekosystemie skanera | funkcje porównania pustego kontenera, algorytmy intensywność/tekstura/kształt; wynik 96% wykrycia / 3% fałszywych alarmów na realnym cargo (jedno źródło, slajd konferencyjny CBP 2023) | związane z własnym sprzętem; cena i szczegóły nieujawnione |
| Nuctech – platforma inspekcji z warstwą AI | bezpośredni | celne, granice (dostawca KAS) | „inteligentna platforma inspekcji” z głębokim uczeniem | integracja ze skanerem, skala wdrożeń | brak publicznych metryk dla anomalii/pustego pojazdu; zamknięta; zastrzeżenia regulacyjne wobec dostawcy (zał.) |
| Smiths Detection | bezpośredni | lotniska, granice | algorytmy detekcji wykrywające zagrożenia | marka, doświadczenie | brak publicznych danych o AI dla cargo; nacisk na bagaż |
| Multicontrol | bezpośredni | celne (dostawca KAS) | skanery wielkogabarytowe | obecny u KAS | brak publicznych informacji o module anomalii (zał.) |
| Obecne narzędzie KAS (detektor papierosów) | bezpośredni (wewnętrzny) | operatorzy KAS | detekcja jednej klasy | już wdrożone | słabe przy małych ilościach w konstrukcji (zadanie, §1) |
| Pośredni: ręczna ocena operatora | pośredni | wszyscy | jedyny pewny standard | elastyczny | zmęczenie, czas, brak powtarzalności |
| Pośredni: kontrola fizyczna / rewizja | pośredni | celnicy | skuteczna | pewna | wolna, kosztowna, inwazyjna |
| Pośredni: badania akademickie (np. Tufts: ~98% skuteczności, trening na syntetycznych anomaliach — wynik autorów, nie niezależny benchmark) | pośredni | — | pokazują, że syntetyczne anomalie działają | uzasadnia nasz syntetyczny zbiór | brak produktu |

## Przegląd metod detekcji anomalii na obrazach (porównanie)
| Podejście | Jak działa | Plus | Minus | Dopasowanie do zadania |
|---|---|---|---|---|
| **A. Porównanie z wzorcem (rejestracja + różnica pikselowa/strukturalna)** | dopasowanie pary obrazów, mapa różnic | wprost „wzorzec vs badany”, szybkie, wyjaśnialne, nie wymaga treningu | wrażliwe na przesunięcia/skalę/szum RTG i naturalną zmienność pojazdu → FP | rdzeń (zadanie §3 mówi o porównaniach pikselowych) |
| **B. Uczenie na samych „czystych” – pamięć łatek (PatchCore, PaDiM)** | cechy łatek z obrazów czystych; anomalia = łatka daleka od norm | dobra lokalizacja, bez etykiet anomalii, odporne na szum (badanie przemysłowe RTG) | pamięć i czas przy 50 MB/obraz → kafelkowanie; brak bezpośredniego benchmarku na pojazdach | pasuje do §5 (nauka na obrazach wzorcowych) |
| **C. Rekonstrukcja (autoenkoder)** | zły odtwarza się to, czego nie widział w „czystych” | prosty, bez etykiet | rozmyte rekonstrukcje → FP na detalach konstrukcji | opcja uzupełniająca |
| **D. Nadzorowana segmentacja/detekcja „dodatków”** | uczenie na obrazach z oznaczonymi dodatkami | najlepsza dokładność dla znanych klas | potrzebuje etykiet; nie uogólnia na nowe skrytki; u nas dane syntetyczne = ryzyko rozjazdu z rzeczywistymi | pomocniczo, na syntetyku do kalibracji progu |
| **E. Hybryda: rejestracja + różnica + ocena łatek, próg dobrany na „czystych”** | A + B | kontrola FP, mapa/ramki do raportu | więcej elementów | rekomendowane do rozważenia w `/discover` |

Wniosek: metody B i E są zgodne z warunkiem „uczenie na prawidłowych”; ranking dla pojazdów RTG niezweryfikowany publicznie — trzeba zmierzyć na własnym zbiorze.

## Macierz funkcji (wymagania zadania × podejścia)
| Zdolność | My (cel) | Vendorzy (Rapiscan/Nuctech/Smiths) | Detektor klasy (papierosy) | Operator ręcznie |
|---|---|---|---|---|
| Porównanie pary wzorzec–badany | tak | częściowo (Rapiscan) | nie | tak (wzrokowo) |
| Nieznane anomalie bez klasy | tak | ograniczone | nie | tak |
| Raport z zaznaczonymi obszarami | tak | zależy od sprzętu | tak | nie |
| Niezależność od producenta skanera | tak | nie | zależy | tak |
| Działanie lokalne, bez chmury | tak | zwykle tak | tak | tak |
| Pliki ~50 MB, partie, skalowanie | tak (cel) | w sprzęcie | tak | nie |
| Mierzalne FP/FN | tak | jednoźródłowe | tak | brak |

## Mapa pozycjonowania (2×2)
Oś X: wymaga znanej klasy ↔ wykrywa dowolną zmianę względem wzorca; oś Y: zamknięty/związany ze sprzętem ↔ niezależny od dostawcy.
- Dół-lewo: detektor papierosów, moduły vendorów.
- Dół-prawo: Rapiscan Empty Container (częściowo).
- Góra-prawo: **nasze rozwiązanie** (dowolna zmiana, niezależne od skanera).
- Góra-lewo: pusta (niszczone przez brak nadzorowanych danych).

## Szanse różnicowania
1. **Dowolna zmiana względem wzorca, bez listy klas** — odpowiada na lukę (małe skrytki w konstrukcji); bronialne, bo vendorzy są nastawieni na klasy.
2. **Niezależność od dostawcy skanera (obrazy .bmp z Nuctech i Multicontrol)** — KAS integruje oba urządzenia.
3. **Raport zrozumiały dla operatora** (zaznaczone obszary, miara pewności) — zmniejsza zaufanie „czarnej skrzynki”.
4. **Kontrola FP jako cecha** — kryterium oceny to FP/FN; próg i miara wyjaśnione operatorowi.
5. **Lokalne i skalowalne przetwarzanie dużych plików** (kafelki, partie) — wymóg zadania i warunek wdrożenia bez chmury.

## Zagrożenia
1. **Rozjazd syntetyk–rzeczywistość** — wyniki na własnym zbiorze nie przeniosą się 1:1; mówimy to otwarcie.
2. **Vendorzy rozszerzają moduły o porównanie z wzorcem** — reakcja: nacisk na niezależność i raport.
3. **Zmienność wzorców (typy naczep, ustawienie, szum)** — źródło FP; potrzeba rejestracji obrazów.
4. **Ochrona danych KAS** — dane chronione; nie kopiować poza cel hackathonu.

## Rekomendacje
- **Postaw na**: porównanie z wzorcem + kontrola FP + raport z zaznaczonymi obszarami.
- **Dociągnij (table stakes)**: obsługa .bmp ~50 MB, partie, czas < 1 min/obraz.
- **Zignoruj**: wyścig na klasy przedmiotów (papierosy, broń) — tego nie wygramy.

## Hipotezy do potwierdzenia z Arturem (nie rozstrzygnięte zadaniem)
1. Kto jest głównym użytkownikiem (operator przy skanerze / analityk centralny / kierownik zmiany)?
2. Jaki problem boli najbardziej (czas, pominięte małe skrytki, zmęczenie)?
3. Co zyska (mniej przeoczeń, mniej fałszywych alarmów, szybszy przegląd)?
Odpowiedzi trafią do `docs/decyzje.md` i do `/discover`.

## Źródła (sprawdzone 2026-11-17, wyniki wyszukiwania)
- [Rapiscan InSight Operator Assist Tools](https://www.rapiscan-ase.com/products/software/insight-operator-assist-tools)
- [Rapiscan – technologia](https://rapiscan-ase.com/resource-center/technology)
- [Tufts – AI do kontrabandy (98%)](https://now.tufts.edu/2025/01/09/new-ai-enabled-technology-98-accurate-spotting-illegal-contraband)
- [Illicit object detection in X-ray imaging – porównanie metod](https://arxiv.org/html/2507.17508v1)
- [Anomalib – praktyczny przewodnik](https://www.ml6.eu/blogpost/a-practical-guide-to-image-based-anomaly-detection-using-anomalib)
- [Unsupervised anomaly instance segmentation for baggage threat recognition](https://khazna.ku.ac.ae/en/publications/unsupervised-anomaly-instance-segmentation-for-baggage-threat-rec/)
- [X-ray anomaly detection in industrial pipelines](https://icarus.csd.auth.gr/wp-content/uploads/2024/10/X-ray_Anomaly_Detection_in_Industrial_Pipelines.pdf)
- [Orange – Contraband AI](https://hellofuture.orange.com/en/contraband-ai-efficiently-detects-anomalies-in-shipping-containers/)

<!-- skill: przeplywy-pm -->
<!-- skill: competitor-analysis -->
