from itertools import combinations

system_decyzyjny = open("./data/system_decyzyjny.txt").readlines()
system_decyzyjny = [wiersz.strip().split() for wiersz in system_decyzyjny]


def czy_niesprzeczna(
    kombinacja, wartosci_obiektu, oczekiwana_decyzja, system_decyzyjny
):
    """
    Funkcja sprawdzajaca niesprzecznosc reguly.
    Regula jest niesprzeczna, gdy ma wszystkie atrybuty i decyzje taka sama jak obiekt.
    """
    for wiersz in system_decyzyjny:
        if all(wiersz[k] == wartosci_obiektu[k] for k in kombinacja):
            if wiersz[-1] != oczekiwana_decyzja:
                return False
    return True


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


def wyswietl_reguly(reguly, pokaz_liste_support=False):
    for r in reguly:
        warunki = " AND ".join(
            f"(a{idx+1} = {r['wartosci'][idx]})" for idx in r["kombinacja"]
        )
        support = f"[{r['support']}]" if r["support"] > 1 else ""
        print(f"{warunki} => (d = {r['decyzja']}) {support}")
        if pokaz_liste_support and r["support"] > 1:
            print([x + 1 for x in r["lista_support"]])


def sequential_covering(system_decyzyjny):
    atrybuty = [wiersz[:-1] for wiersz in system_decyzyjny]
    decyzje = [wiersz[-1] for wiersz in system_decyzyjny]
    ile_atrybutow = len(atrybuty[0])

    # Zbior obiektow, ktore jeszcze nie posiadaja swojej reguly
    idx_niepokrytych = set(range(len(atrybuty)))
    reguly = []

    # Rzad oznacza dlugosc reguly
    for rzad in range(1, ile_atrybutow + 1):
        # Jesli wszystkie obiekty sa juz pokryte, konczymy algorytm
        if not idx_niepokrytych:
            break

        obiekty_pokryte = set()

        for idx_obiektu in idx_niepokrytych:
            # Pomijamy wiersze, ktore zostaly pokryte w biezacym rzedzie
            if idx_obiektu in obiekty_pokryte:
                continue

            # Generujemy wszystkie kombinacje atrybutow dlugosci rzedu
            for kombinacja in combinations(range(ile_atrybutow), rzad):
                # Sprawdzamy czy kombinacja jest niesprzeczna
                if czy_niesprzeczna(
                    kombinacja,
                    atrybuty[idx_obiektu],
                    decyzje[idx_obiektu],
                    system_decyzyjny,
                ):
                    obiekty_pokryte.add(idx_obiektu)

                    # Szukamy support reguly
                    lista_support = znajdz_support(
                        kombinacja,
                        atrybuty[idx_obiektu],
                        decyzje[idx_obiektu],
                        system_decyzyjny,
                    )

                    # Jesli kombinacja jest niesprzeczna i ma support > 0
                    if len(lista_support) > 0:
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
                        # Dodajemy obiekty pokryte przez regule do zbioru obslugiwanych obiektow
                        for idx_obiektu_w_support in lista_support:
                            obiekty_pokryte.add(idx_obiektu_w_support)
                        break

        # Usuwamy obiekty pokryte przez regule z zbioru niepokrytych obiektow
        idx_niepokrytych -= obiekty_pokryte
    return reguly


wynik = sequential_covering(system_decyzyjny)
wyswietl_reguly(wynik)
