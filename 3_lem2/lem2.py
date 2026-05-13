system_decyzyjny = open("./data/system_decyzyjny_lem2.txt").readlines()
system_decyzyjny = [wiersz.strip().split() for wiersz in system_decyzyjny]
atrybuty = [wiersz[:-1] for wiersz in system_decyzyjny]
ile_obiektow = len(atrybuty)
ile_atrybutow = len(atrybuty[0])


def wyswietl_reguly(reguly, pokaz_liste_support=False):
    for r in reguly:
        warunki = " AND ".join(
            f"(a{idx+1} = {r['wartosci'][idx]})" for idx in r["kombinacja"]
        )
        decyzja = " OR ".join(f"(d = {d})" for d in r["decyzje"])
        support = f"[{r['support']}]" if r["support"] > 1 else ""
        print(f"r{r['idx_obiektu']+1} {warunki} => {decyzja} {support}")
        if pokaz_liste_support and r["support"] > 1:
            print([x + 1 for x in r["lista_support"]])


def lem2():
    # Obliczenie licznosci: dict[idx_atrybutu][wartosc_atrybutu] = set{idx_obiektow}
    licznosci_atrybutow = {}
    for idx_atrybutu in range(ile_atrybutow):
        licznosci_atrybutow[idx_atrybutu] = {}
        for idx_obiektu, wiersz in enumerate(system_decyzyjny):
            wartosc = wiersz[idx_atrybutu]
            if wartosc not in licznosci_atrybutow[idx_atrybutu]:
                licznosci_atrybutow[idx_atrybutu][wartosc] = set()
            licznosci_atrybutow[idx_atrybutu][wartosc].add(idx_obiektu)

    # Podzial na klasy decyzyjne
    klasy_decyzyjne = {}
    for idx, wiersz in enumerate(system_decyzyjny):
        decyzja = wiersz[-1]
        if decyzja not in klasy_decyzyjne:
            klasy_decyzyjne[decyzja] = []
        klasy_decyzyjne[decyzja].append(idx)

    reguly_systemu = []

    # Przechodzimy po wszystkich klasach decyzyjnych
    for klasa_decyzyjna in sorted(klasy_decyzyjne.keys()):
        obiekty_w_klasie = set(klasy_decyzyjne[klasa_decyzyjna])
        obiekty_niepokryte = obiekty_w_klasie.copy()

        # Tworzymy reguly poki wszystkie obiekty danej klasy nie zostana pokryte.
        while obiekty_niepokryte:
            obecna_regula = []
            # Poczatkowo kandydatami do pokrycia sa wszystkie obiekty
            obiekty_kandydujace = set(range(ile_obiektow))

            # Regula jest budowana dopoki zbior kandydatow nie jest podzbiorem klasy decyzyjnej
            while obiekty_kandydujace - obiekty_w_klasie:
                najlepszy_deskryptor = None
                max_pokrycie = -1

                # Sprawdzanie deskryptorow
                for idx_atrybutu in range(ile_atrybutow):
                    for wartosc_atrybutu, idx_obiektow in licznosci_atrybutow[
                        idx_atrybutu
                    ].items():
                        # Pomijamy deskryptory, które juz sa w obecnej regule
                        if (idx_atrybutu, wartosc_atrybutu) in obecna_regula:
                            continue

                        # Liczba pokrytych obiektow, ktore pozostaly niepokryte z klasy decyzyjnej i sa w zbiorze kandydatow
                        pokrycie = len(
                            idx_obiektow & obiekty_kandydujace & obiekty_niepokryte
                        )

                        # Omijamy deskryptory, ktore nie pokrywaja zadnego obiektu z klasy decyzyjnej
                        if pokrycie == 0:
                            continue

                        lepszy = False
                        if pokrycie > max_pokrycie:
                            lepszy = True
                        elif (
                            pokrycie == max_pokrycie
                            and najlepszy_deskryptor is not None
                        ):
                            # Rozwiazanie konfliktow
                            # Z lewej - mniejszy indeks atrybutu
                            if idx_atrybutu < najlepszy_deskryptor[0]:
                                lepszy = True
                            elif idx_atrybutu == najlepszy_deskryptor[0]:
                                # Od gory - mniejszy indeks obiektu
                                # Zbior kandydatow do pokrycia
                                zbior_kandydatow = (
                                    obiekty_kandydujace & obiekty_niepokryte
                                )

                                # Sprawdzamy indeks nowego deskryptora
                                idx_nowego_deskryptora = min(
                                    idx_obiektow & zbior_kandydatow
                                )

                                # Sprawdzamy indeks obecnego deskryptora
                                idx_obecnego_deskryptora = min(
                                    licznosci_atrybutow[najlepszy_deskryptor[0]][
                                        najlepszy_deskryptor[1]
                                    ]
                                    & zbior_kandydatow
                                )

                                # Jesli nowy deskryptor ma mniejszy indeks, to jest lepszy
                                if idx_nowego_deskryptora < idx_obecnego_deskryptora:
                                    lepszy = True

                        if lepszy:
                            max_pokrycie = pokrycie
                            najlepszy_deskryptor = (idx_atrybutu, wartosc_atrybutu)

                if najlepszy_deskryptor is None:
                    break

                # Dodajemy wybrany deskryptor do reguly i aktualizujemy zbior kandydatow.
                obecna_regula.append(najlepszy_deskryptor)
                obiekty_kandydujace = (
                    obiekty_kandydujace
                    & licznosci_atrybutow[najlepszy_deskryptor[0]][
                        najlepszy_deskryptor[1]
                    ]
                )

            # Gdy regula jest spojna to zapisujemy support i usuwamy pokryte obiekty z zbioru obiektow do pokrycia.
            pokryte_przez_regule = obiekty_kandydujace & obiekty_w_klasie
            obiekty_niepokryte -= pokryte_przez_regule

            # Znajdujemy wszystkie decyzje pokryte przez te regule
            decyzje_reguly = set()
            for idx in obiekty_kandydujace:
                decyzje_reguly.add(system_decyzyjny[idx][-1])

            reguly_systemu.append(
                {
                    "kombinacja": [deskryptor[0] for deskryptor in obecna_regula],
                    "wartosci": {
                        deskryptor[0]: deskryptor[1] for deskryptor in obecna_regula
                    },
                    "decyzje": decyzje_reguly,
                    "support": len(obiekty_kandydujace),
                    "lista_support": obiekty_kandydujace,
                }
            )

    # Grupowanie i usuwanie duplikatów przed zwróceniem wyniku
    zgrupowane_reguly = []
    klucze_regul = set()

    for reg in reguly_systemu:
        kombinacja = tuple(sorted(reg["kombinacja"]))
        wartosci_reguly = tuple(reg["wartosci"][idx] for idx in kombinacja)
        klucz_reguly = (kombinacja, wartosci_reguly, tuple(sorted(list(reg["decyzje"]))))

        if klucz_reguly not in klucze_regul:
            klucze_regul.add(klucz_reguly)
            zgrupowane_reguly.append(reg)

    return zgrupowane_reguly


wynik = lem2()
wyswietl_reguly(wynik, pokaz_liste_support=False)
