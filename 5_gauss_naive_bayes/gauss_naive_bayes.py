import random
import numpy as np

dane = np.loadtxt("./data/iris.data", delimiter=",", dtype=str)

liczba_systemow = 5
liczba_obiektow = dane.shape[0]
liczba_atrybutow = dane.shape[1] - 1
klasy = np.unique(dane[:, -1])
liczba_klas = len(klasy)

# Losowanie indeksow obiektow
rozlosowane_indeksy = []
while len(rozlosowane_indeksy) < liczba_obiektow:
    j = random.randint(0, liczba_obiektow - 1)
    if j not in rozlosowane_indeksy:
        rozlosowane_indeksy.append(j)

# Podzial na systemy
systemy = {i: [] for i in range(liczba_systemow)}
for i, idx_obiektu in enumerate(rozlosowane_indeksy):
    id_systemu = i % liczba_systemow
    systemy[id_systemu].append(idx_obiektu)


def przygotuj_system_treningowy(systemy, idx_systemu_testowego):
    """
    Funkcja tworzaca system treningowy z podanych systemow bez systemu testowego.
    """
    system_treningowy = []
    for id_systemu, obiekty in systemy.items():
        if id_systemu != idx_systemu_testowego:
            system_treningowy.extend(obiekty)
    return system_treningowy


def gauss(a, srednia, wariancja):
    wariancja = max(wariancja, 1e-9)
    return np.log(
        1
        / np.sqrt(2 * np.pi * wariancja)
        * np.e ** (-((a - srednia) ** 2) / (2 * wariancja))
    )


def sklasyfikuj_obiekt(wiersz_test, statystyki_klas):
    """
    Funkcja klasyfikujaca obiekt na podstawie obliczenia prawdopodobienstwa przynaleznosci do kazdej z klas i wybrania klasy o najwiekszym prawdopodobienstwie.
    """
    atrybuty = wiersz_test[:-1]
    najlepsza_klasa = None
    najlepszy_wynik = -np.inf
    for klasa, statystyki in statystyki_klas.items():
        wynik = statystyki["log_p_c"]
        for i, atrybut in enumerate(atrybuty):
            wynik += gauss(float(atrybut), statystyki["srednie"][i], statystyki["wariancje"][i])
        if wynik > najlepszy_wynik:
            najlepszy_wynik = wynik
            najlepsza_klasa = klasa
    return najlepsza_klasa


globalne_poprawne = 0
globalna_accuracy = 0
globalna_macierz_pomylek = {
    klasa_prawdziwa: {klasa_predykcyjna: 0 for klasa_predykcyjna in klasy}
    for klasa_prawdziwa in klasy
}

# Petla kroswalidacji - kazdy system musi byc raz systemem testowym, reszta to systemy treningowe
for idx_systemu_testowego in range(liczba_systemow):

    system_treningowy = przygotuj_system_treningowy(systemy, idx_systemu_testowego)

    statystyki_klas = {}
    for klasa in klasy:
        obiekty_klasy = [
            idx_obiektu
            for idx_obiektu in system_treningowy
            if dane[idx_obiektu][-1] == klasa
        ]
        ilosc_obiektow_klasy = len(obiekty_klasy)

        # Obliczanie apriori klasy
        p_c = ilosc_obiektow_klasy / len(system_treningowy)

        # Obliczanie statystyk dla kazdego atrybutu
        atrybuty_klasy = dane[obiekty_klasy, :liczba_atrybutow].astype(float)
        statystyki_klas[klasa] = {
            "srednie": [np.mean(atrybuty_klasy[:, i]) for i in range(liczba_atrybutow)],
            "wariancje": [
                np.var(atrybuty_klasy[:, i]) for i in range(liczba_atrybutow)
            ],
            "log_p_c": np.log(p_c),
        }

    poprawne_decyzje = 0
    system_testowy = systemy[idx_systemu_testowego]
    macierz_pomylek = {
        klasa_prawdziwa: {klasa_predykcyjna: 0 for klasa_predykcyjna in klasy}
        for klasa_prawdziwa in klasy
    }

    for idx_obiektu_test in system_testowy:
        wiersz_test = dane[idx_obiektu_test]
        decyzja_predykcyjna = sklasyfikuj_obiekt(wiersz_test, statystyki_klas)
        prawdziwa_decyzja = wiersz_test[-1]
        globalna_macierz_pomylek[prawdziwa_decyzja][decyzja_predykcyjna] += 1
        macierz_pomylek[prawdziwa_decyzja][decyzja_predykcyjna] += 1
        if prawdziwa_decyzja == decyzja_predykcyjna:
            poprawne_decyzje += 1
            globalne_poprawne += 1

    accuracy = (poprawne_decyzje / len(system_testowy)) * 100
    globalna_accuracy += accuracy

    print(f"\n===== SYSTEM TESTOWY NR {idx_systemu_testowego + 1} =====")
    print(f"Accuracy = {accuracy:.2f}%")

    print("\nMacierz pomylek (wiersze: realne, kolumny: predykcyjne):")
    print(f"{'Klasa':<15} {'\t'.join(klasy)}")
    for klasa_prawdziwa in klasy:
        row = f"{klasa_prawdziwa:<15}"
        for klasa_predykcyjna in klasy:
            row += f"{macierz_pomylek[klasa_prawdziwa][klasa_predykcyjna]:>12}"
        print(row)

print("\n===== PODSUMOWANIE GLOBALNE =====")
print(f"Srednia accuracy: {globalna_accuracy / liczba_systemow:.2f}%")

print("\nMacierz pomylek (wiersze: realne, kolumny: predykcyjne):")
print(f"{'Klasa':<15} {'\t'.join(klasy)}")
for klasa_prawdziwa in klasy:
    row = f"{klasa_prawdziwa:<15}"
    for klasa_predykcyjna in klasy:
        row += f"{globalna_macierz_pomylek[klasa_prawdziwa][klasa_predykcyjna]:>12}"
    print(row)
