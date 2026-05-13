from itertools import combinations

system_decyzyjny = open("./data/system_decyzyjny.txt").readlines()
system_decyzyjny = [wiersz.strip().split() for wiersz in system_decyzyjny]
atrybuty = [wiersz[:-1] for wiersz in system_decyzyjny]
decyzje = [wiersz[-1] for wiersz in system_decyzyjny]
ile_atrybutow = len(atrybuty[0])


def czy_niesprzeczna(kombinacja, wartosci_obiektu, oczekiwana_decyzja):
    """
    Funkcja sprawdzajaca niesprzecznosc reguly.
    Regula jest niesprzeczna, gdy ma wszystkie atrybuty i decyzje taka sama jak obiekt.
    Jezeli wyczerpalismy wszystkie atrybuty, dopuszczamy regule sprzeczna.
    """
    for wiersz in system_decyzyjny:
        if all(wiersz[k] == wartosci_obiektu[k] for k in kombinacja):
            if wiersz[-1] != oczekiwana_decyzja:
                return False
    return True


def znajdz_support(kombinacja, wartosci_obiektu, decyzja_reguly):
    """
    Funckja obliczajaca support reguly.
    Szuka wszystkich obiektow, ktore pasuja do warunkow reguly i maja jedna z dopuszczalnych decyzji.
    """
    lista_support = []
    for idx, wiersz in enumerate(system_decyzyjny):
        if all(wiersz[k] == wartosci_obiektu[k] for k in kombinacja):
            # Jeśli decyzja jest None, to bierzemy wszystkie obiekty o tych samych atrybutach
            if decyzja_reguly is None or wiersz[-1] == decyzja_reguly:
                lista_support.append(idx)
    return lista_support


def wyswietl_reguly(reguly, pokaz_liste_support=False):
    for r in reguly:
        warunki = " AND ".join(
            f"(a{idx+1} = {r['wartosci'][idx]})" for idx in r["kombinacja"]
        )
        decyzja = f"(d = {r['decyzja']})" if r["decyzja"] is not None else None
        support = f"[{r['support']}]" if r["support"] > 1 else ""
        print(f"o{r["idx_obiektu"]+1} {warunki} => {decyzja} {support}")
        if pokaz_liste_support and r["support"] > 1:
            print([x + 1 for x in r["lista_support"]])


def sequential_covering():
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
                decyzja = decyzje[idx_obiektu]

                # Jesli kombinacja nie jest niesprzeczna, szukamy kombinacji
                if not czy_niesprzeczna(kombinacja, atrybuty[idx_obiektu], decyzja):
                    # Jesli to nie jest ostatni rzad, szukamy kombinacji
                    if rzad < ile_atrybutow:
                        continue
                    # Jesli to ostatni rzad, to dopuszczamy regule sprzeczna
                    decyzja = None

                # Szukamy support reguly - obiektow, ktore pasuja do reguly
                lista_support = znajdz_support(
                    kombinacja,
                    atrybuty[idx_obiektu],
                    decyzja,
                )

                # Jesli kombinacja ma support > 0, dodajemy regule
                reguly.append(
                    {
                        "idx_obiektu": idx_obiektu,
                        "kombinacja": kombinacja,
                        "wartosci": atrybuty[idx_obiektu],
                        "decyzja": decyzja,
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


wynik = sequential_covering()
wyswietl_reguly(wynik, pokaz_liste_support=False)
