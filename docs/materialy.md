# Materiały zadania (krok 0)

Źródło: `docs/zadanie.md` (cytaty dosłowne w cudzysłowie), ustalenia: `docs/decyzje.md`. Liczby bez źródła nie występują; szacunki oznaczone „szac.".

## 1. Wymagania z zadania

### Wejście
| Wymaganie | Źródło (pkt zadania) | Uwaga |
|---|---|---|
| Format `*.bmp` | §3, §5, §7 | tylko BMP; głębia bitowa i rozdzielczość nieznane (zob. pytania) |
| Pliki „~50 MB każdy", ~200 obrazów, ~10 GB | §3, §7 | szac.: 50 MB ≈ 16,7 mln px przy 24 bit (np. ~4096×4096) lub ~50 mln px przy 8 bit — rozdzielczość do ustalenia |
| „Pary/grupy" do porównań (np. „przed" i „po" załadunku) | §7 | obraz wzorcowy (pusty środek) vs badany z dodatkami |
| Uczenie na obrazach wzorcowych bez anomalii | §5 | model uczony tylko na „prawidłowych" → podejście one-class / anomaly detection, nie nadzorowana klasyfikacja |
| Dane anonimizowane, symulacyjne | §7 | |
| Dane z pendrive'a na stoisku KAS | §7 | nie mamy ich teraz → zbiór syntetyczny (decyzje 17:11) |

### Wyjście
- Porównanie par/grup obrazów: podobieństwa i różnice (anomalie, segmentacja lub różnice pikselowe) — §3.
- Identyfikacja odstępstwa od „reguły" (wzorzec pusty vs z dodatkowymi elementami) — §3.
- **Raport z wykrytymi anomaliami, np. zaznaczone obszary na obrazie** — §3. Na czystym obrazie: brak jakichkolwiek zaznaczeń — §6.
- Działanie samodzielne, bez interwencji człowieka — §3.
- Pliki duże: „kompresja, przetwarzanie partiami"; skalowalność na większe zbiory — §3.
- Czas jednego obrazu < 1 min — §7 (wpisane przy zasobach; traktujemy jako limit).
- Docelowo bez chmury/internetu (§9); w hackathonie narzędzia AI/płatne dozwolone do tworzenia kodu.
- Do oceny: opis i tytuł, repozytorium, PDF ≤ 10 slajdów (§4); opcjonalnie zrzuty, linki do dema.

## 2. Sposób testowania → co mierzyć

Zadanie (§6) wyróżnia dwa zestawy testowe i ocenę: skuteczność (FP i FN), innowacyjność, skalowalność.

| Zestaw (§6) | Oczekiwanie | Miara dla naszego zbioru syntetycznego |
|---|---|---|
| Obrazy „czyste" | zero zaznaczeń | **FP**: odsetek czystych obrazów z ≥1 alarmem (poziom obrazu) oraz liczba fałszywych regionów na obraz / łączna powierzchnia fałszywych regionów (poziom regionu). Zadanie mówi o „poziomie alarmów FP" bez definicji — liczymy oba. |
| Obrazy z „dodatkami" | zaznaczenie miejsca dodatku graficznie | **FN**: odsetek dodatków bez trafionego zaznaczenia. Trafienie = IoU zaznaczenia z maską prawdy ≥ próg (próg do ustalenia; rekomendacja: raportować dla kilku progów) lub środek zaznaczenia wewnątrz maski. Dodatkowo odsetek obrazów z dodatkiem bez żadnego trafienia (poziom obrazu). |
| Skalowalność (§6, §3) | większe zbiory w przyszłości | czas/obraz (mediana, p95; limit < 60 s), szczytowa pamięć RAM, przepustowość obrazów/min przy przetwarzaniu partiami, zależność od liczby obrazów |
| Innowacyjność (§6) | — | kryterium opisowe, niemierzalne; zob. otwarte pytania (kryteria §8 zna Szef) |

Protokół na syntetyce: podział na zbiór uczący (tylko „czyste"), walidacyjny (dobór progu) i testowy (czyste + z dodatkami) bez wspólnych scen; dodatki różnej wielkości/gęstości/położenia (też „w konstrukcji" i „w towarze", §1 zadania), żeby FN nie był zawyżony łatwymi przypadkami; podać pary FP/FN dla kilku progów (krzywa), nie jeden punkt. Ograniczenie: wynik na syntetyku nie przenosi się wprost na obrazy KAS — komunikować tak w README/prezentacji.

Ciężkie liczenie (trening, ocena na zbiorze, pomiar czasu/RAM) — tylko przez orkiestrator na OMENa.

## 3. Publiczne zbiory i metody (przydatne przy syntetyce i porównaniu)

Linki podane z pamięci wiedzy, **nie zweryfikowane w tej próbie** (brak pobierania); sprawdzić licencję i dostępność przed użyciem.

### Zbiory RTG (inspiracja, ewentualny pretrening/walidacja domenowa)
- SIXray — RTG bagażu, ~1 mln obrazów, 6 klas zakazanych: https://github.com/MeioJane/SIXray
- OPIXray — przedmioty ostre w bagażu (syntetyczne wklejanie): https://github.com/OPIXray-author/OPIXray
- PIDray — zakazane przedmioty, ukrycia: https://github.com/bywang2018/security-dataset
- GDXray (Domingo Mery) — RTG do kontroli/odlewy/bagaż: https://domingomery.ing.puc.cl/material/gdxray/
- Zbiór pojazdów/kontenerów w skanerach cargo — brak znanego pewnego publicznego odpowiednika; do dopytania/wyszukania.

### Metody wykrywania anomalii (uczenie tylko na „czystych")
- Biblioteka anomalib (Intel/OpenVINO; PatchCore, PaDiM, STFPM, FastFlow, EfficientAD): https://github.com/openvinotoolkit/anomalib
- PatchCore (Roth i in., 2022): https://arxiv.org/abs/2106.08265 — dobry punkt wyjścia, lokalizacja anomalii z mapy cech, działa offline.
- PaDiM: https://arxiv.org/abs/2011.08785
- MVTec AD (benchmark metod, metryki): https://www.mvtec.com/company/research/datasets/mvtec-ad

### Porównanie wzorzec–badany (klasyka, bez uczenia)
- Rejestracja obrazów (dopasowanie wzorca do badanego przed różnicą): OpenCV — ECC `findTransformECC`, ORB+RANSAC: https://docs.opencv.org/4.x/
- SSIM / różnica strukturalna: scikit-image `structural_similarity`: https://scikit-image.org/docs/stable/api/skimage.metrics.html
- Segmentacja/regiony z różnicy: progowanie + operacje morfologiczne (OpenCV), komponenty spójne.
- Wczytanie dużych BMP i praca na kafelkach/mipmapach: Pillow (`Image.open`, `crop`), OpenCV `IMREAD_REDUCED_*`, `numpy.memmap` — przetwarzanie partiami i kafelkami.

### Generowanie syntetyki
- Syntetyczna „naczepa": tło (rama, ściany, oś — kształty geometryczne) + tekstura szumu RTG (Poisson/Gauss) + wklejanie „dodatków" o innej gęstości/pochłanianiu (modyfikacja intensywności wg prawa Beera–Lamberta: I = I0·exp(−μ·d)), z zapisem maski prawdy. Technika wklejania dodatków do obrazów RTG jak w OPIXray (zob. wyżej).
- Wariacje między „parami": przesunięcie, skala, jasność, szum — żeby model nie uczył się dopasowania dokładnego co do piksela (realne wzorce i badane nie są idealnie zgodne — założenie do potwierdzenia).

## 4. Ograniczenia

- **Rozmiar:** ~50 MB/obraz, ~10 GB całość; synt. zbiór dla OMENa trzymać raz w `~/dane`, nie wysyłać za każdym razem. BMP bez kompresji → duże repo: obrazów nie commitować (`.gitattributes` istnieje; dane syntetyczne generować skryptem, w repo tylko generator i małe próbki).
- **Czas:** < 1 min/obraz (§7) — dotyczy docelowego sprzętu, który nie jest podany (CPU/GPU?).
- **Offline:** docelowo bez chmury/internetu (§9) → żadnych wywołań API LLM/chmury w czasie działania; wagi modeli lokalne.
- **Ochrona danych:** zbiory KAS są chronione — zakaz udostępniania, kopiowania, przekazywania i użycia poza hackathonem (§7). Wynika: nie wrzucać ich do repo (publiczne), do chmury ani narzędzi zewnętrznych; syntetyk jest wolny od tego ograniczenia, ale nie wolno go „uzupełniać" fragmentami prawdziwych obrazów KAS.
- **Repo publiczne** — bez sekretów i bez danych KAS.
- **Zasoby sprzętowe:** ThinkPad 7,6 GB RAM — nie pomieści pełnego obrazu przy ciężkich modelach; ciężkie przez OMENa (instrukcja zespołu).
- **Pary zbiorów:** liczba i struktura par/grup (ile wzorców na pojazd) nieznane do odbioru danych na stoisku.

## 5. Brakuje w materiałach (nie ma w zadaniu)

- Dane KAS (odbiór dopiero na stoisku z pendrive'a); do tego czasu — syntetyk.
- Rozdzielczość, głębia bitowa, kanały (RTG zwykle 1-kanałowe — nie z zadania), kalibracja urządzeń Nuctech vs Multicontrol.
- Definicja „dodatku" (rozmiar minimalny; „małe ilości papierosów" w konstrukcji, §1), definicja trafienia w FN, format raportu.
- Dokładne kryteria oceny (§8 — w zadaniu wskazane tylko „zna Szef").

## 6. Otwarte pytania (zadanie ich nie rozstrzyga)

1. **Format raportu:** obraz z ramkami/maską, plik JSON z współrzędnymi, PDF/HTML? Zadanie: „np. zaznaczone obszary na obrazie". Rekomendacja: oba — nakładka PNG + JSON (współrzędne, wynik, id pary) — bo wyniki mają trafiać do repozytorium z przypisaniem do miejsca i przedmiotu kontroli (§9).
2. **Próg trafienia dla FN i definicja FP** (poziom obrazu vs regionu) — rekomendacja z sekcji 2; potwierdzić u Szefa/Artura, jeśli zmienia kryteria.
3. **Czy wzorzec jest zawsze ten sam pojazd** (para „przed/po") **czy ogólny wzorzec typu pojazdu** (grupa)? Wpływa na wybór: różnica po rejestracji vs model uczony na rozkładzie „czystych".
4. **Typ docelowego sprzętu** do limitu < 1 min (CPU bez GPU?) — wpływa na wybór metody (PatchCore na pełnej rozdzielczości bywa wolny; szac., do pomiaru na OMENie).
5. **Waga „innowacyjności"** (§8 nieznane) — czy lepiej metoda hybrydowa (rejestracja + anomalia) niż sam model.
6. **Wersja demo:** UI do przeglądania wyników (poza wymaganym „raportem")? Zadanie wymaga repozytorium i PDF, nie aplikacji z UI.
7. **Zakres syntetyki:** ile typów pojazdów (tylko naczepy — decyzja 17:11) i jak trudne dodatki (ukryte w konstrukcji vs w towarze)? Rekomendacja: 3 poziomy trudności.

<!-- skill: brak (krok 0, bez skilla) -->
