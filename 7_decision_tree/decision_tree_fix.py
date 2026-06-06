import numpy as np


system_decyzyjny = np.loadtxt(
    "./data/drzewa_decyzyjne.txt", encoding="utf-8", dtype=str, delimiter=" "
)
liczba_atrybutow = len(system_decyzyjny[0]) - 1
nazwy_atrybutow = ["Pogoda", "Temperatura", "Wilgotność", "Wiatr", "Gram w tenisa"]


def entropy(s):
    decyzje = s[:, -1]
    wartosci_decyzji, liczebnosci = np.unique(decyzje, return_counts=True)
    p = liczebnosci / len(s)
    return -np.sum(p * np.log2(p))


def gain(s, idx_atrybutu):
    entropy_s = entropy(s)
    wartosci_atrybutu, liczebnosci = np.unique(s[:, idx_atrybutu], return_counts=True)
    suma_entropii = 0
    for wartosc, liczba in zip(wartosci_atrybutu, liczebnosci):
        podzbior = s[s[:, idx_atrybutu] == wartosc]
        suma_entropii += (liczba / len(s)) * entropy(podzbior)
    return entropy_s - suma_entropii


def najczestsza_decyzja(decyzje):
    wartosci, liczebnosci = np.unique(decyzje, return_counts=True)
    return wartosci[np.argmax(liczebnosci)]


def id3(system, wykorzystane_atrybuty):
    decyzje = system[:, -1]

    # Jesli wszystkie obiekty maja ta sama decyzje, tworzymy lisc
    if len(np.unique(decyzje)) == 1:
        return decyzje[0], wykorzystane_atrybuty

    # Wybieramy atrybuty, ktore nie byly jeszcze wykorzystane w innych galeziach
    atrybuty = [a for a in range(liczba_atrybutow) if a not in wykorzystane_atrybuty]

    # Jesli nie ma juz wiecej atrybutow do podzialu, zwracamy decyzje, ktora wystepuje wiecej razy
    if not atrybuty:
        return najczestsza_decyzja(decyzje), wykorzystane_atrybuty

    # Wybor najlepszego atrybutu
    gains = [gain(system, a) for a in atrybuty]
    najlepszy_id = np.argmax(gains)
    najlepszy_atrybut = atrybuty[najlepszy_id]

    # Gain <= 0 - zwracamy decyzje, ktora wystepuje wiecej razy
    if gains[najlepszy_id] <= 0:
        return najczestsza_decyzja(decyzje), wykorzystane_atrybuty

    # Tworzymy nowy wezel drzewa
    drzewo = {"atrybut": najlepszy_atrybut, "dzieci": {}}

    wartosci_atrybutu = np.unique(system[:, najlepszy_atrybut])

    # Dodajemy atrybut do wykorzystanych
    wykorzystane_w_galezi = wykorzystane_atrybuty.union({najlepszy_atrybut})

    for wartosc in wartosci_atrybutu:
        podzbior = system[system[:, najlepszy_atrybut] == wartosc]

        if len(podzbior) == 0:
            # jesli podzbior jest pusty bierzemy wiekszosc z rodzica
            drzewo["dzieci"][wartosc] = najczestsza_decyzja(decyzje)
        else:
            # budowanie galezi
            galaz, wykorzystane_w_galezi = id3(podzbior, wykorzystane_w_galezi)
            drzewo["dzieci"][wartosc] = galaz

    return drzewo, wykorzystane_w_galezi


def wyswietl_drzewo(drzewo, sciezka=""):
    # jesli lisc to wypisz decyzje
    if not isinstance(drzewo, dict):
        print(f"{sciezka} => {drzewo}")
        return

    atrybut_idx = drzewo["atrybut"]
    nazwa_atrybutu = nazwy_atrybutow[atrybut_idx]

    for wartosc, galez in drzewo["dzieci"].items():
        warunek = f"{nazwa_atrybutu}({wartosc})"
        nowa_sciezka = f"{sciezka} AND {warunek}" if sciezka else warunek
        wyswietl_drzewo(galez, nowa_sciezka)


wynik, _ = id3(system_decyzyjny, set())
wyswietl_drzewo(wynik)
