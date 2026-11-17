# 03 — kryterium: skalowalność (na rano, faza 2)

- **Kryterium:** skalowalność, waga 30%.
- **Co jest (spec v1):** analiza partii z wiersza poleceń (`python -m rtg.partia`), 100 par bez awarii, kafelki dla obrazu ~50 MB, czas mediana/p95 na 10 parach pełnego rozmiaru, praca bez sieci.
- **Czego brakuje:** brak liczby przepustowości (par/godz. na jednej maszynie) i opisu, jak rośnie z liczbą maszyn / rdzeni; brak zużycia pamięci na obraz 50 MB.
- **Poprawka (strojenie + materiał):** z pomiaru czasu policzyć przepustowość i pamięć, dopisać tabelę do README i slajdu (1 maszyna → N równoległych procesów); ewentualnie równoległe przetwarzanie par w `rtg.partia` (proste, bez nowej funkcji dla użytkownika).
