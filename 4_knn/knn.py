import random

import numpy as np

dane = np.loadtxt("./data/australian.csv", delimiter=" ")

liczba_systemow = 6
liczba_obiektow = dane.shape[0]

k = 5


def odleglosc_euklidesowa(p, q):
    """
    Funkcja obliczajaca dystans euklidesowy pomiedzy dwoma obiektami.
    """
    return np.sqrt(np.sum((p[:-1] - q[:-1]) ** 2))


def przygotuj_obiekty_treningowe(systemy, idx_systemu_testowego):
    """
    Funkcja tworzaca systemy treningowe z podanych systemow.
    """
    systemy_treningowe = []
    for id_systemu, obiekty in systemy.items():
        if id_systemu != idx_systemu_testowego:
            systemy_treningowe.extend(obiekty)
    return systemy_treningowe


def sklasyfikuj_obiekt(wiersz_test, systemy_treningowe, dane, k):
    """
    Funkcja klasyfikujaca obiekt na podstawie k najblizszych sasiadow.
    """
    dystanse = []
    for idx_obiektu_trening in systemy_treningowe:
        wiersz_trening = dane[idx_obiektu_trening]

        # Obliczanie dystansu euklidesowego
        dystans = odleglosc_euklidesowa(wiersz_test, wiersz_trening)
        decyzja_sasiada = wiersz_trening[-1]

        dystanse.append((dystans, decyzja_sasiada))

    # Sortowanie listy dystansow
    dystanse.sort()

    # Wybieramy k najblizszych sasiadow
    k_najblizszych = dystanse[:k]

    # Liczymy dominujaca klase decyzyjna
    decyzje = [decyzja for dystans, decyzja in k_najblizszych]
    return int(max(set(decyzje), key=decyzje.count))


def aktualizuj_macierz_pomylek(prawdziwa_decyzja, decyzja_predykcyjna, macierz_pomylek):
    """
    Funkcja aktualizujaca macierz pomylek.
    """
    if prawdziwa_decyzja == 0 and decyzja_predykcyjna == 0:
        macierz_pomylek["TN"] += 1
    elif prawdziwa_decyzja == 0 and decyzja_predykcyjna == 1:
        macierz_pomylek["FP"] += 1
    elif prawdziwa_decyzja == 1 and decyzja_predykcyjna == 0:
        macierz_pomylek["FN"] += 1
    elif prawdziwa_decyzja == 1 and decyzja_predykcyjna == 1:
        macierz_pomylek["TP"] += 1


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

decyzje_predykcyjne = []
decyzje_prawdziwe = []
globalna_accuracy = 0

globalna_macierz_pomylek = {
    "TN": 0,
    "FP": 0,
    "FN": 0,
    "TP": 0,
}

# Petla kroswalidacji - kazdy system musi byc raz systemem testowym, reszta to systemy treningowe
for idx_systemu_testowego in range(liczba_systemow):
    # Tworzymy systemy treningowe - wszystkie oprocz testowego
    systemy_treningowe = przygotuj_obiekty_treningowe(systemy, idx_systemu_testowego)

    obiekty_testowe = systemy[idx_systemu_testowego]

    poprawne_decyzje = 0
    lacznie_testowanych = len(obiekty_testowe)

    macierz_pomylek = {
        "TN": 0,
        "FP": 0,
        "FN": 0,
        "TP": 0,
    }

    # Przechodzimy po kazdym obiekcie z systemu testowego
    for idx_obiektu_test in obiekty_testowe:
        wiersz_test = dane[idx_obiektu_test]

        decyzja_predykcyjna = sklasyfikuj_obiekt(
            wiersz_test, systemy_treningowe, dane, k
        )
        prawdziwa_decyzja = int(wiersz_test[-1])

        # Liczenie poprawnych decyzji
        if prawdziwa_decyzja == decyzja_predykcyjna:
            poprawne_decyzje += 1

        # Zapisujemy decyzje do macierzy pomylek
        aktualizuj_macierz_pomylek(
            prawdziwa_decyzja, decyzja_predykcyjna, macierz_pomylek
        )

        # Zapisujemy decyzje
        decyzje_prawdziwe.append(prawdziwa_decyzja)
        decyzje_predykcyjne.append(decyzja_predykcyjna)

    # Obliczanie accuracy dla obecnego systemu testowego
    accuracy = (poprawne_decyzje / lacznie_testowanych) * 100
    globalna_accuracy += accuracy

    print(f"\n===== SYSTEM TESTOWY NR {idx_systemu_testowego + 1} =====")
    print(f"Accuracy = {accuracy:.2f}%")
    print("Macierz pomylek:")
    macierz_pomylek_2x2 = np.array(
        [
            [macierz_pomylek["TN"], macierz_pomylek["FP"]],
            [macierz_pomylek["FN"], macierz_pomylek["TP"]],
        ]
    )
    print(macierz_pomylek_2x2)

    for obserwacja, ilosc in macierz_pomylek.items():
        globalna_macierz_pomylek[obserwacja] += ilosc

print("\n===== PODSUMOWANIE GLOBALNE =====")
print(f"Srednia accuracy: {globalna_accuracy / liczba_systemow:.2f}%")

print("Macierz pomylek dla wszystkich systemow:")
globalna_macierz_pomylek_2x2 = np.array(
    [
        [globalna_macierz_pomylek["TN"], globalna_macierz_pomylek["FP"]],
        [globalna_macierz_pomylek["FN"], globalna_macierz_pomylek["TP"]],
    ]
)
print(globalna_macierz_pomylek_2x2)
