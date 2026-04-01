from itertools import combinations
import numpy as np

system_decyzyjny = open("./data/system_decyzyjny.txt").readlines()
system_decyzyjny = [wiersz.strip().split() for wiersz in system_decyzyjny]


def wyswietl_reguly(reguly, pokaz_liste_support=False):
    for r in reguly:
        warunki = " AND ".join(
            f"(a{idx+1} = {r['wartosci'][idx]})" for idx in r["kombinacja"]
        )
        support = f"[{r['support']}]" if r["support"] > 1 else ""
        print(f"{warunki} => (d = {r['decyzja']}) {support}")
        if pokaz_liste_support and r["support"] > 1:
            print([x + 1 for x in r["lista_support"]])


def znajdz_support(kombinacja, wartosci_obiektu, oczekiwana_decyzja, system_decyzyjny):
    """
    Funckja obliczajaca support reguly.
    Szuka wszystkich obiektow, ktore pasuja do warunkow reguly i maja taka sama decyzje.
    """
    lista_support = []
    for idx, wiersz in enumerate(system_decyzyjny):
        if all(wiersz[k] == wartosci_obiektu[k] for k in kombinacja):
            if wiersz[-1] == oczekiwana_decyzja:
                lista_support.append(idx)
    return lista_support


def exhaustive(system_decyzyjny):
    atrybuty = [wiersz[:-1] for wiersz in system_decyzyjny]
    decyzje = [wiersz[-1] for wiersz in system_decyzyjny]
    ile_obiektow = len(atrybuty)
    ile_atrybutow = len(atrybuty[0])
    macierz_nieodroznialnosci = np.full((ile_obiektow, ile_obiektow), set())

    # Budowa macierzy nieodroznialnosci
    # Porownujemy kazdy obiekt z kazdym, do zbioru dodajemy tylko te atrybuty, ktore sa takie same w obu obiektach, ale maja rozne decyzje.
    for i in range(ile_obiektow):
        for j in range(ile_obiektow):
            if decyzje[i] != decyzje[j]:
                macierz_nieodroznialnosci[i][j] = {
                    k for k in range(ile_atrybutow) if atrybuty[i][k] == atrybuty[j][k]
                }
    print("Macierz nieodroznialnosci")
    print(macierz_nieodroznialnosci)

    reguly_dla_rzedu = {}
    ostateczne_reguly = {i: [] for i in range(ile_obiektow)}

    # Rzad to dlugosc reguly
    for rzad in range(1, ile_atrybutow + 1):
        reguly = []
        for idx_obiektu in range(ile_obiektow):
            for kombinacja in combinations(range(ile_atrybutow), rzad):
                kombinacja_set = set(kombinacja)

                # Jesli kombinacja jest podzbiorem innej krotszej kombinacji, to ja pomijamy.
                if any(
                    set(krotsza_kombinacja).issubset(kombinacja_set)
                    for krotsza_kombinacja in ostateczne_reguly[idx_obiektu]
                ):
                    continue

                # Jesli kombinacja jest podzbiorem komorki macierzy nieodroznialnosci, to ja pomijamy.
                if any(
                    kombinacja_set.issubset(komorka)
                    for komorka in macierz_nieodroznialnosci[:, idx_obiektu]
                ):
                    continue

                # Szukamy support reguly
                lista_support = znajdz_support(
                    kombinacja,
                    atrybuty[idx_obiektu],
                    decyzje[idx_obiektu],
                    system_decyzyjny,
                )

                # Jesli kombinacja jest niesprzeczna i ma support > 0
                if lista_support:
                    ostateczne_reguly[idx_obiektu].append(kombinacja)
                    reguly.append(
                        {
                            "idx_obiektu": idx_obiektu,
                            "kombinacja": kombinacja,
                            "wartosci": atrybuty[idx_obiektu],
                            "decyzja": decyzje[idx_obiektu],
                            "support": len(lista_support),
                            "lista_support": lista_support,
                        }
                    )

        # Usuwamy duplikaty reguly
        zgrupowane_reguly = []
        klucze_regul = set()
        for reg in reguly:
            # Tworzymy klucz reguly
            wartosci_reguly = tuple(reg["wartosci"][idx] for idx in reg["kombinacja"])
            klucz_reguly = (reg["kombinacja"], wartosci_reguly, reg["decyzja"])
            # Jesli klucz reguly nie jest w zbiorze kluczy, dodajemy go do zbioru i reguly do listy
            if klucz_reguly not in klucze_regul:
                klucze_regul.add(klucz_reguly)
                zgrupowane_reguly.append(reg)

        reguly_dla_rzedu[rzad] = zgrupowane_reguly

        if not zgrupowane_reguly:
            break

    return reguly_dla_rzedu


wynik = exhaustive(system_decyzyjny)

for rzad in wynik:
    print(f"Reguly dla rzedu {rzad}")
    if len(wynik[rzad]) == 0:
        print("Brak reguł")
    else:
        wyswietl_reguly(wynik[rzad], pokaz_liste_support=False)
