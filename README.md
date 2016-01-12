KrakRobot 2016
==============

Przedszkole robotów – instrukcja obsługi symulatora
-------------------


Niniejszy dokument stanowi instrukcję obsługi symulatora używanego w etapie online zawodów KrakRobot 2016. Aby zapoznać się z formalnymi regułami zadania, należy odnieść się do regulaminu zamieszczonego na stronie www.krakrobot.pl

Zadaniem drużyn jest samodzielne stworzenie programu, który będzie sterować robotem znajdującym kolorowe pola na planszy.

Nacisk w zadaniu położony jest na problemy związane z niedokładnością w poruszaniu się robotów. Programy zawodników muszą wykorzystywać strukturę planszy, aby upewniać się co do dokładnego położenia robota.

W razie jakichkolwiek pytań lub wątpliwości, prosimy o kontakt: http://krakrobot.pl/kontakt


Zasady używania symulatora
------------------------

1. Niniejsza wersja symulatora przeznaczona jest do wykorzystania przez zawodników do lokalnego testowania rozwiązań na własnych komputerach. Dla zarejestrowanych drużyn zostanie udostępniona w internecie automatyczna testerka służąca do nadsyłania rozwiązań i testowania ich online.
. Organizatorzy zastrzegają sobie prawo do zmiany sposobu działania symulatora, z zastrzeżeniem że zmiany te nie mogą wpływać na poprawność rozwiązań


Podsumowanie zadania
--------------------

Uwaga: to podsumowanie jest niepełne. Prosimy o odniesienie się do formalnego regulaminu na stronie.

1. Robot znajduje się na kwadratowej planszy o białej powierzchni z czarnymi liniami formującymi kratę 5 x 5 pól, z których niektóre są kolorowe (czerwone, zielone lub niebieskie), a niektóre – białe
2. Robot może się poruszać po planszy, odczytywać kolor planszy czujnikiem koloru oraz wydawać z siebie pojedyncze piknięcia ("beeps")
3. Zadaniem robota jest wydanie pojedynczych piknięć kolejno na polach: czerwonym, zielonym i niebieskim, a następnie zakończenie przejazdu


Instalacja
----------------

### Windows

W systemie Windows należy zainstalować Python 2.7 : http://www.python.org/getit/ . Należy upewnić się, że python.exe zostało dodane do zmiennej środowiskowej PATH.
Następnie należy zainstalować pakiety numpy oraz PyQt. Instalacja tych pakietów dla Windows może być wykonana przy użyciu kodów binarnych ze strony http://www.lfd.uci.edu/~gohlke/pythonlibs/ . Można także użyć systemu zarządzania pakietami do Pythona, na przykład pip.

### Linux

W systemie Linux należy zainstalować Python 2.7 oraz pakiety PyQt i numpy. Można zainstalować numpy używając pip. Dla dystrybucji Ubuntu, pakiet Qt jest dostępny pod nazwą python-qt4, więc można po prostu wykonać w terminalu polecenie ``sudo apt-get install python-qt4``


Plansza do gry
---------------
Obecnie w symulatorze dostępna jest pojedyncza przykładowa mapa do gry:

![Example map](simulator/maps/1.png)

Symulator
------------

### Podstawowe informacje

. Symulator komunikuje się z botem przy pomocy standardowego wejścia i wyjścia
. Do pisania programu można wykorzystać języki programowania: Python 2.7, Python 3, C++ oraz Java (te języki będą dopuszczone na automatycznej testerce)
.
. Symulacja jest aktualizowana krokowo. W każdym kroku symulacji robot jest proszony o wybór swojej kolejnej akcji.

### Uruchamianie

Są dwa sposoby uruchomienia symulatora: w trybie graficznym lub w trybie konsolowym.
Tryb graficzny umożliwia zobaczenie przejazdu robota na wizualizacji, jak również odtwarzanie przejazdu lub jego fragmentów w ramach powtórki. Aby uruchomić symulator w trybie graficznym, należy wykonać polecenie

``python simulator/main.py``

Uruchamianie symulatora w trybie konsolowym:

``python simulator/main.py -c``

wiąże się z podaniem programowi opcji konfiguracyjnych (patrz niżej).

W obu trybach można kontrolować parametry symulacji.

### Implementacja symulatora

Parametry, które mogą się zmieniać między przejazdami, są podawane botowi na starcie symulacji.

Symulator wykonuje symulację dopóki któryś z następujących warunków nie zostanie spełniony:

* Osiągnięty został limit czasu symulacji
* Robot przekroczył limit czasu obliczeń
* Robot przekroczył limit pamięci RAM (odnosi się tylko do testerki online)
* Robot zakończył przejazd, wysyłając odpowiednią komendę
* W kodzie robota rzucony został wyjątek
* Robot uległ zniszczeniu na skutek kolizji ze ściankami otaczającymi planszę

Przed każdym krokiem symulacji, symulator podaje botowi dwie informacje:
* aktualny odczyt koloru w formacie RGB
* aktualny czas symulacji

W każdym kroku symulacji, wykonywane jest jedno polecenie (z odpowiednim zaaplikowanym do niego szumem, np. niedokładnością w poruszaniu się). W pojedynczym kroku, robot może

* Jechać do przodu lub do tyłu (odległość o którą przemieszcza się robot w jednym kroku jest zdefiniowana na liście stałych poniżej)
* Skręcać (odległość kątowa zdefiniowana poniżej)
* Zakomunikować zakończenie zadania
* Odczytać kolor podłoża pod czujnikiem koloru (obecnie funkcja ta nie jest potrzebna ponieważ kolor jest przesyłany automatycznie - patrz powyżej)

Mimo, że krata na planszy składa się z dyskretnych pól, pozycja robota jest zakodowana jako 64-bitowa liczba rzeczywista - nie jako liczba całkowita.

Jeżeli podczas ruchu robot miałby wyjechać poza granice planszy, ruch nie odbywa się (chociaż czas potrzebny na jego wykonanie jest zużywany).

Bot
---------

Aby umożliwić tworzenie rozwiązań w różnych językach programowania, w tegorocznej edycji bot do gry jest tworzony przez zawodników jako niezależny program i komunikuje się z symulatorem przez standardowe wejście i wyjście programu - a nie jest, jak to było w poprzednich edycjach, klasą napisaną w języku Python używaną bezpośrednio w symulatorze.

Struktura programu jest dowolna, dopóki bot poprawnie komunikuje się z symulatorem. Jednak aby ułatwić rozpoczęcie pracy nad rozwiązaniem, organizatorzy zapewniają szablony rozwiązań zawierające już obsługę komunikacji z symulatorem. UWAGA: organizatorzy nie gwarantują pełnej poprawności działania szablonów. Zawodnicy mogą oprzeć swoje rozwiązania na tych programach na własną odpowiedzialność.


Na przykład:

```
color
255 255 255
time
1.23
```

przekazuje botowi informację, że w tym kroku czujnik wykrywa kolor biały (255, 255, 255) oraz że od rozpoczęcia zadania upłynęło 1.23 sekundy.

If, by moving, the robot collides with a wall, it doesn't move (but the time for movement is consumed).
The robot can issue commands with multiple ticks, for instance [MOVE, 10], but such a move will be
discretized into 10 separate 1-tick moves.
