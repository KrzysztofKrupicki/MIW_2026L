from itertools import combinations

system_decyzyjny = open("system_decyzyjny.txt").readlines()
system_decyzyjny = [wiersz.strip().split() for wiersz in system_decyzyjny]


# Funkcja sprawdzajaca niesprzecznosc reguly
def czy_niesprzeczna(kombinacja_atrybutow, obiekt, system_decyzyjny, idx_obiektu):
    for i, wiersz in enumerate(system_decyzyjny):
        if all(wiersz[j] == obiekt[j] for j in kombinacja_atrybutow):
            if wiersz[-1] != system_decyzyjny[idx_obiektu][-1]:
                return False
    return True


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
                    system_decyzyjny,
                    idx_obiektu,
                ):
                    obiekty_pokryte.add(idx_obiektu)
                    lista_support = []
                    # znajdz obiekty ktore sa pokryte przez regule i maja ta sama decyzje - support
                    for idx_obiektu_do_sprawdzenia in range(len(system_decyzyjny)):
                        czy_pokryty_przez_regule = False
                        for atrybut in kombinacja:
                            if (
                                system_decyzyjny[idx_obiektu_do_sprawdzenia][atrybut]
                                != atrybuty[idx_obiektu][atrybut]
                            ):
                                czy_pokryty_przez_regule = False
                                break
                            else:
                                czy_pokryty_przez_regule = True
                        czy_decyzja_ta_sama = (
                            system_decyzyjny[idx_obiektu_do_sprawdzenia][-1]
                            == decyzje[idx_obiektu]
                        )
                        if czy_pokryty_przez_regule and czy_decyzja_ta_sama:
                            lista_support.append(idx_obiektu_do_sprawdzenia + 1)

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
                        obiekty_pokryte.add(idx_obiektu_w_support - 1)
                    break
        idx_niepokrytych -= obiekty_pokryte
    return reguly


def wyswietl_reguly(reguly):
    for r in reguly:
        warunki = " AND ".join(
            [f"(a{idx+1} = {r['wartosci'][idx]})" for idx in r["kombinacja"]]
        )
        support = f"[{r['support']}]" if r["support"] > 1 else ""
        print(f"o{r['idx_obiektu']+1} -> {warunki} => d = {r['decyzja']} {support}")
        # print(r["lista_support"] if r["support"] > 1 else "")


wynik = sequential_covering(system_decyzyjny)
wyswietl_reguly(wynik)
