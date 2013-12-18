# Testerka 
=========

# Plan:
---
# Serwer
---
(może być w python'ie)

((TCP) nasłuchuje wyniki zadań -> 
-> wynik przesyła do bazy danych MSQL strony -> 
-> strona za pomocą skryptu wyświetla wyniki (Albo ogarnia to Bruno albo ja)

---
# Testerka
---

Zadania
1. Wywołuje kod (bebehy) programu testującego kod).
2. Wysyła wynik ze sprawdzonego zadania do serwera.
3. Ewentualna odpowiedź od serwa czy przekazała wyniki w odpowiednie miejsce.

Wygląd ( UZUPEŁNIĆ ! ) 
1. Ma mieć możliwość rejestracji użytkowników ( ? )
2. Ma przypominać z wyglądu BaCę ( ? )

---
Skrypt na stronie
---

To niestety wordpress nie wygląda to tak prosto bez pluginów.

Zadaniami głównym będzie :
1. Budowa tekstowa strony.
2. Wyznaczenie stylu strony.
3. Umieszczenie odpowiednich stałych. 
4. Konstrukcja filtrów odpowiedzialnych za zapytania do MySQL (odpowiednie stałe tekstowe do przefiltrowania)(nic na to nie poradzić -- bezpieczeństwo).




---
Sulphux