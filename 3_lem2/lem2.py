import pprint

system_decyzyjny = open("./data/system_decyzyjny_lem2.txt").readlines()
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


def lem2(system_decyzyjny):
    atrybuty = [wiersz[:-1] for wiersz in system_decyzyjny]
    ile_obiektow = len(atrybuty)
    ile_atrybutow = len(atrybuty[0])

    # Budowa slownika z indeksami atrybutow, ktory zawiera slownik z wartosciami atrybutu i zbiorem indeksow obiektow zawierajacych dana wartosc danego atrybutu
    licznosci_atrybutow = {}
    for idx_atrybutu in range(ile_atrybutow):
        licznosci_atrybutow[idx_atrybutu] = {}
        for idx_obiektu, wiersz in enumerate(system_decyzyjny):
            wartosc = wiersz[idx_atrybutu]
            if wartosc not in licznosci_atrybutow[idx_atrybutu]:
                licznosci_atrybutow[idx_atrybutu][wartosc] = set()
            licznosci_atrybutow[idx_atrybutu][wartosc].add(idx_obiektu)
    # pprint.pprint(licznosci_atrybutow)

    # Podzial na klasy decyzyjne
    klasy_decyzyjne = {}
    for idx, wiersz in enumerate(system_decyzyjny):
        decyzja = wiersz[-1]
        if decyzja not in klasy_decyzyjne:
            klasy_decyzyjne[decyzja] = []
        klasy_decyzyjne[decyzja].append(idx)

    reguly_systemu = []
    for klasa_decyzyjna in sorted(klasy_decyzyjne.keys()):
        obiekty_w_klasie = set(klasy_decyzyjne[klasa_decyzyjna])
        obiekty_niepokryte = obiekty_w_klasie.copy()

        while obiekty_niepokryte:
            obecna_regula = []
            obiekty_kandydujace = set(range(ile_obiektow))

            while obiekty_kandydujace - obiekty_w_klasie:
                najlepszy_deskryptor = None
                max_pokrycie = -1

                for idx_atrybutu in range(ile_atrybutow):
                    for wartosc_atrybutu, idx_obiektow in licznosci_atrybutow[
                        idx_atrybutu
                    ].items():
                        if (idx_atrybutu, wartosc_atrybutu) in obecna_regula:
                            continue

                        pokrycie = len(
                            idx_obiektow.intersection(
                                obiekty_kandydujace.intersection(obiekty_niepokryte)
                            )
                        )

                        lepszy = False
                        if pokrycie > max_pokrycie:
                            lepszy = True
                        elif (
                            pokrycie == max_pokrycie
                            and najlepszy_deskryptor is not None
                        ):
                            if idx_atrybutu < najlepszy_deskryptor[0]:
                                lepszy = True
                            elif (
                                idx_atrybutu == najlepszy_deskryptor[0]
                                and wartosc_atrybutu < najlepszy_deskryptor[1]
                            ):
                                lepszy = True

                        if lepszy:
                            max_pokrycie = pokrycie
                            najlepszy_deskryptor = (idx_atrybutu, wartosc_atrybutu)

                if najlepszy_deskryptor is None or max_pokrycie == 0:
                    break

                obecna_regula.append(najlepszy_deskryptor)
                obiekty_kandydujace = obiekty_kandydujace.intersection(
                    licznosci_atrybutow[najlepszy_deskryptor[0]][
                        najlepszy_deskryptor[1]
                    ]
                )
            pokryte_przez_regule = obiekty_kandydujace.intersection(obiekty_w_klasie)
            obiekty_niepokryte -= pokryte_przez_regule

            reguly_systemu.append(
                {
                    "kombinacja": [deskryptor[0] for deskryptor in obecna_regula],
                    "wartosci": {
                        deskryptor[0]: deskryptor[1] for deskryptor in obecna_regula
                    },
                    "decyzja": klasa_decyzyjna,
                    "support": len(pokryte_przez_regule),
                    "lista_support": sorted(list(pokryte_przez_regule)),
                }
            )

    return reguly_systemu


wynik = lem2(system_decyzyjny)
wyswietl_reguly(wynik, pokaz_liste_support=False)
