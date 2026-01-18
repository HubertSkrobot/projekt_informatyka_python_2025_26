# projekt_informatyka_python_2025_26
Projekt Informatyka II Etap 2
System przypominający SCADA

Cel i Proces programu:
System symuluje linię, w której ciecz jest transportowana z jednego zbiornika zasilającego do dwóch zbiorników procesowych, a stamtąd do zbiornika końcowego.
Całość działa automatycznie po uruchomieniu programu. System sam decyduje o włączaniu i wyłączaniu pomp i grzałki na podstawie poziomów wody i jej temperatury

Działanie:
Pompa P1 rozdziela ciecz na dwa tory. Proces trwa do momentu, gdy w pierwszym zbiorniku zostanie bezpieczna rezerwa 5 litrów wody.
Pompa P2 zaczyna pompować wodę do zbiornika 4 dopiero wtedy, gdy w zbiorniku 2 jest więcej niż 20 litrów wody.
Ze zbiornika odpompowywana jest woda dopiero wtedy, gdy woda zostanie podgrzana do 60°C. Po uzyskaniu temperatury grzałka zmienia kolor na pomarańczowy, co oznacza, że nie grzeje już wody, tylko podtrzymuje temperaturę. Pompa przestaje działać, gdy w zbiorniku zostaną 4 litry wody.

Bezpieczeństwo:
W instalacji B użytkownik może zasymulować sytuację, gdy nadmiar płynu wyzwala alarm.
Po osiągnięciu w czwartym zbiorniku 99 litrów wody, system automatycznie się wyłącza razem ze wszystkimi pompami i grzałką.

Obsługa:
Użytkownik nawiguje między widokiem graficznym a tabelami raportów.
Każda instalacja posiada własny panel sterowania Start/Stop, co pozwala na ręczną interwencję w dowolnym momencie.
