import random
import numpy as np

dane = np.loadtxt("./data/australian.csv", delimiter=" ")

liczba_systemow = 6
liczba_obiektow = dane.shape[0]
ile_atrybutow = dane.shape[1] - 1


def przygotuj_system_treningowy(systemy, idx_systemu_testowego):
    """
    Funkcja tworzaca system treningowy z podanych systemow bez systemu testowego.
    """
    system_treningowy = []
    for id_systemu, obiekty in systemy.items():
        if id_systemu != idx_systemu_testowego:
            system_treningowy.extend(obiekty)
    return system_treningowy


def aktualizuj_macierz_pomylek(decyzja_prawdziwa, decyzja_predykcyjna, macierz_pomylek):
    """
    Funkcja aktualizujaca macierz pomylek.
    """
    if decyzja_prawdziwa == 0 and decyzja_predykcyjna == 0:
        macierz_pomylek["TN"] += 1
    elif decyzja_prawdziwa == 0 and decyzja_predykcyjna == 1:
        macierz_pomylek["FP"] += 1
    elif decyzja_prawdziwa == 1 and decyzja_predykcyjna == 0:
        macierz_pomylek["FN"] += 1
    elif decyzja_prawdziwa == 1 and decyzja_predykcyjna == 1:
        macierz_pomylek["TP"] += 1


def normalizuj(wiersz, srednie, odchylenia):
    return (wiersz[:-1] - srednie) / odchylenia


def sigma(z):
    return 1 / (1 + np.exp(-z))


def oblicz_z(x, wagi, bias):
    return np.sum(x * wagi) + bias


def klasyfikuj(x, wagi, bias):
    z = oblicz_z(x, wagi, bias)
    return 1 if sigma(z) >= 0.5 else 0


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
global_none = 0

globalna_macierz_pomylek = {
    "TN": 0,
    "FP": 0,
    "FN": 0,
    "TP": 0,
}


# Petla kroswalidacji - kazdy system musi byc raz systemem testowym, reszta to systemy treningowe
for idx_systemu_testowego in range(liczba_systemow):
    # Tworzymy systemy treningowe - wszystkie oprocz testowego
    system_treningowy = przygotuj_system_treningowy(systemy, idx_systemu_testowego)
    system_testowy = systemy[idx_systemu_testowego]

    # Obliczamy srednia i odchylenie standardowe dla kazdego atrybutu w systemie treningowym
    dane_treningowe = dane[system_treningowy, :-1]
    srednie = np.mean(dane_treningowe, axis=0)
    odchylenia = np.std(dane_treningowe, axis=0)

    # Ustawienie wartosci poczatkowych
    wagi = np.zeros(ile_atrybutow)
    bias = 0
    alfa = 0.01
    iteracje = 100

    # Petla uczenia
    for i in range(iteracje):
        gradient_wag = np.zeros(ile_atrybutow)
        gradient_bias = 0
        ile_trenowanych = len(system_treningowy)

        # Obliczanie gradientow dla obiektow z systemu treningowego
        for idx in system_treningowy:
            x = normalizuj(dane[idx], srednie, odchylenia)
            y = dane[idx, -1]
            z = oblicz_z(x, wagi, bias)
            y_prim = sigma(z)
            error = y_prim - y
            gradient_wag += error * x
            gradient_bias += error

        # Usrednienie gradientow
        sredni_gradient_wag = gradient_wag / ile_trenowanych
        sredni_gradient_bias = gradient_bias / ile_trenowanych

        # Aktualizacja wag i biasu
        wagi -= alfa * sredni_gradient_wag
        bias -= alfa * sredni_gradient_bias

    poprawne_decyzje = 0
    lacznie_testowanych = len(system_testowy)

    macierz_pomylek = {
        "TN": 0,
        "FP": 0,
        "FN": 0,
        "TP": 0,
    }

    # Przechodzimy po kazdym obiekcie z systemu testowego
    for idx_obiektu_test in system_testowy:
        x_test_norm = normalizuj(dane[idx_obiektu_test], srednie, odchylenia)

        # Klasyfikacja
        decyzja_predykcyjna = klasyfikuj(x_test_norm, wagi, bias)

        decyzja_prawdziwa = int(dane[idx_obiektu_test, -1])

        # Liczenie poprawnych decyzji
        if decyzja_prawdziwa == decyzja_predykcyjna:
            poprawne_decyzje += 1

        # Zapisujemy decyzje do macierzy pomylek
        aktualizuj_macierz_pomylek(
            decyzja_prawdziwa, decyzja_predykcyjna, macierz_pomylek
        )

        # Zapisujemy decyzje
        decyzje_prawdziwe.append(decyzja_prawdziwa)
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
