from itertools import combinations

system_decyzyjny = open("./data/system_decyzyjny.txt").readlines()
system_decyzyjny = [wiersz.strip().split() for wiersz in system_decyzyjny]


def czy_niesprzeczna(
    kombinacja, wartosci_obiektu, oczekiwana_decyzja, system_decyzyjny
):
    """Funkcja sprawdzajaca niesprzecznosc reguly"""
    for wiersz in system_decyzyjny:
        if all(wiersz[k] == wartosci_obiektu[k] for k in kombinacja):
            if wiersz[-1] != oczekiwana_decyzja:
                return False
    return True


def znajdz_support(kombinacja, wartosci_obiektu, oczekiwana_decyzja, system_decyzyjny):
    """Znajduje support reguly - obiekty ktore sa pokryte przez regule i maja ta sama decyzje"""
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
    idx_niepokrytych = set(range(len(atrybuty)))
    reguly = []

    for rzad in range(1, ile_atrybutow + 1):
        if not idx_niepokrytych:
            break
        obiekty_pokryte = set()
        for idx_obiektu in idx_niepokrytych:
            # pomin obiekty ktore zostaly juz pokryte
            if idx_obiektu in obiekty_pokryte:
                continue
            for kombinacja in combinations(range(ile_atrybutow), rzad):
                if czy_niesprzeczna(
                    kombinacja,
                    atrybuty[idx_obiektu],
                    decyzje[idx_obiektu],
                    system_decyzyjny,
                ):
                    obiekty_pokryte.add(idx_obiektu)

                    # znajdz obiekty ktore sa pokryte przez regule i maja ta sama decyzje - support
                    lista_support = znajdz_support(
                        kombinacja,
                        atrybuty[idx_obiektu],
                        decyzje[idx_obiektu],
                        system_decyzyjny,
                    )

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
                        for idx_obiektu_w_support in lista_support:
                            obiekty_pokryte.add(idx_obiektu_w_support)
                        break
        idx_niepokrytych -= obiekty_pokryte
    return reguly


wynik = sequential_covering(system_decyzyjny)
wyswietl_reguly(wynik)
