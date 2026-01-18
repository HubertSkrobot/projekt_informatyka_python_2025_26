import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QLabel, QStackedWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Rura:
    def __init__(self, punkty, grubosc=10, kolor=Qt.darkGray):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.czy_plynie = False
    def draw(self, painter): # Funkcja rysująca rure
        if len(self.punkty) < 2: return # Jeśli rura nie ma przynajmniej dwóch punktów, nie rysujee nic
        path = QPainterPath()
        path.moveTo(self.punkty[0]) # Ustawia ołówek na pierwszym punkcie rury
        for p in self.punkty[1:]: path.lineTo(p) # Rysuje linie od punktu do punktu zgodnie z trasą rury
        painter.setPen(QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)
        if self.czy_plynie:
            painter.setPen(QPen(QColor(0, 180, 255), self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)

class Zbiornik:
    def __init__(self, x, y, nazwa="", pojemnosc=100.0, w=80, h=110):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.nazwa, self.pojemnosc = nazwa, pojemnosc
        self.aktualna_ilosc, self.temperatura = 0.0, 20.0
    def draw(self, painter):
        poziom = self.aktualna_ilosc / self.pojemnosc # Oblicza wypełnienie zbiornika
        if poziom > 0: # Jeśli w zbiorniku jest jakakolwiek woda
            h_cieczy = (self.h - 4) * min(poziom, 1.0) # Oblicza wysokość słupa wody w pikselach
            painter.setBrush(QColor(0, 120, 255, 200)) # Wybiera niebieski kolor wypełnienia wody
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x + 2), int(self.y + self.h - h_cieczy - 2), int(self.w - 4), int(h_cieczy))
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.w), int(self.h))
        painter.drawText(int(self.x), int(self.y - 10), f"{self.nazwa}: {int(round(self.aktualna_ilosc))}L")
        if "Zbiornik 3" in self.nazwa:
            painter.drawText(int(self.x), int(self.y + self.h + 20), f"Temp: {int(round(self.temperatura))}°C")

class WidokGraficzny(QWidget):
    def __init__(self, system, id_inst):
        super().__init__()
        self.system, self.id_inst = system, id_inst
    def paint_pompa(self, painter, x, y, nazwa, wlaczona):
        painter.setBrush(QColor(0, 255, 0) if wlaczona else QColor(180, 0, 0))
        painter.setPen(QPen(Qt.white, 1))
        painter.drawEllipse(x, y, 30, 30)
        painter.setPen(Qt.white)
        painter.drawText(x + 5, y + 19, nazwa)
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(25, 25, 25))
        p.drawRect(self.rect()) # Koloruje całe tło widoku
        if self.id_inst == 'A': # Jeśli oglądamy instalację A
            rury, zbiorniki = self.system.ruryA, self.system.zbiornikiA # Pobiera dane rur i zbiorników z zestawu A
            p1, p2, p3 = self.system.pompaA1_on, self.system.pompaA2_on, self.system.pompaA3_on # Pobiera stany pomp A
            g_on, temp = self.system.grzalkaA_on, self.system.z3A.temperatura # Pobiera stan grzałki i temperaturę A
        else: # Jeśli oglądamy instalację B
            rury, zbiorniki = self.system.ruryB, self.system.zbiornikiB # Pobiera dane rur i zbiorników z zestawu B
            p1, p2, p3 = self.system.pompaB1_on, self.system.pompaB2_on, self.system.pompaB3_on # Pobiera stany pomp B
            g_on, temp = self.system.grzalkaB_on, self.system.z3B.temperatura # Pobiera stan grzałki i temperaturę B
        for r in rury: r.draw(p) # Rysuje każdą rurę z listy
        for z in zbiorniki: z.draw(p) # Rysuje każdy zbiornik z listy
        self.paint_pompa(p, 185, 145, "P1", p1)
        self.paint_pompa(p, 480, 90, "P2", p2)
        self.paint_pompa(p, 480, 340, "P3", p3)
        kolor_g = Qt.gray
        if g_on:
            kolor_g = QColor(255, 165, 0) if temp >= 60 else QColor(255, 0, 0)
        p.setPen(QPen(kolor_g, 3)) # Wybiera kolor pędzla dla grzałki
        for i in range(3): p.drawLine(380 + i*5, 350, 380 + i*5, 370) # Rysuje trzy pionowe kreski jako symbol grzałki

class SystemSCADA(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System SCADA")
        self.setFixedSize(950, 800)
        self.setStyleSheet("background-color: #1e1e1e; color: #eee; font-family: Arial;")
        self.runningA = self.runningB = False
        self.pompaA1_on = self.pompaA2_on = self.pompaA3_on = False
        self.pompaB1_on = self.pompaB2_on = self.pompaB3_on = False
        self.grzalkaA_on = self.grzalkaB_on = False
        self.init_procesy() # rozpoczyna tworzenie zbiornikow i rur
        self.init_ui() # rozpoczyna tworzenie tabeli i przyciskow
        self.odswiez_tabele('A') #wpisuje poczatkowe dane do tabeli A
        self.odswiez_tabele('B') # wpisuje poczatkowe dane do tabeli B
        self.timerA = QTimer() #zegar A
        self.timerA.timeout.connect(self.logika_A)
        self.timerB = QTimer() #zegar B
        self.timerB.timeout.connect(self.logika_B)
    def init_procesy(self):
        pts = [[(130, 160), (250, 160)], [(250, 160), (250, 105), (350, 105)],
               [(250, 160), (250, 355), (350, 355)], [(430, 105), (750, 105), (750, 175)],
               [(430, 355), (830, 355), (830, 285), (780, 285)]] #lista punktow rur
        self.z1A = Zbiornik(50, 100, "Zbiornik 1", 100.0)
        self.z1A.aktualna_ilosc = 100.0
        self.z2A = Zbiornik(350, 50, "Zbiornik 2")
        self.z3A = Zbiornik(350, 300, "Zbiornik 3")
        self.z4A = Zbiornik(700, 175, "Zbiornik 4")
        self.zbiornikiA = [self.z1A, self.z2A, self.z3A, self.z4A] # Grupuje zbiorniki A w listę
        self.ruryA = [Rura(p) for p in pts] # Tworzy rury dla instalacji A na podstawie punktów
        self.z1B = Zbiornik(30, 60, "Zbiornik 1", 200.0, 120, 150)
        self.z1B.aktualna_ilosc = 200.0
        self.z2B = Zbiornik(350, 50, "Zbiornik 2")
        self.z3B = Zbiornik(350, 300, "Zbiornik 3")
        self.z4B = Zbiornik(700, 175, "Zbiornik 4")
        self.zbiornikiB = [self.z1B, self.z2B, self.z3B, self.z4B] # Grupuje zbiorniki B w listę
        self.ruryB = [Rura(p) for p in pts] # Tworzy rury dla instalacji B
    def init_ui(self): # Funkcja budująca wygląd okna
        lay = QVBoxLayout(self)
        nav = QHBoxLayout()
        st = "QPushButton { background: #333; border: 1px solid #555; padding: 12px; font-weight: bold; }"
        self.bV = QPushButton("WIZUALIZACJA")
        self.bR = QPushButton("RAPORTY")
        for b in [self.bV, self.bR]:
            b.setStyleSheet(st)
            nav.addWidget(b)
        self.bV.clicked.connect(lambda: self.stack.setCurrentIndex(0)) # Po kliknięciu "Wizualizacja" pokaż pierwszą stronę
        self.bR.clicked.connect(lambda: self.stack.setCurrentIndex(1)) # Po kliknięciu "Raporty" pokaż drugą stronę
        lay.addLayout(nav) # Dodaje pasek nawigacji na górę okna
        self.stack = QStackedWidget()
        lay.addWidget(self.stack)
        v_cont = QWidget()
        v_lay = QVBoxLayout(v_cont)
        sw = QHBoxLayout()
        bA = QPushButton("INSTALACJA A")
        bB = QPushButton("INSTALACJA B")
        for b in [bA, bB]: sw.addWidget(b)
        bA.clicked.connect(lambda: self.inst_stack.setCurrentIndex(0))
        bB.clicked.connect(lambda: self.inst_stack.setCurrentIndex(1))
        v_lay.addLayout(sw)
        self.inst_stack = QStackedWidget()
        for t in ['A', 'B']:
            p = QWidget()
            l = QVBoxLayout(p)
            l.addWidget(WidokGraficzny(self, t))
            b = QPushButton("START / STOP")
            b.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 15px;")
            if t == 'A':
                b.clicked.connect(self.toggleA)
                self.btn_startA = b
            else:
                b.clicked.connect(self.toggleB)
                self.btn_startB = b
            l.addWidget(b)
            self.inst_stack.addWidget(p)
        v_lay.addWidget(self.inst_stack)
        self.stack.addWidget(v_cont)
        r_cont = QWidget()
        r_lay = QVBoxLayout(r_cont)
        for t in ['A', 'B']:
            r_lay.addWidget(QLabel(f"<b>RAPORT OPERACYJNY - INSTALACJA {t}</b>"))
            tab = QTableWidget(6, 3)
            tab.setHorizontalHeaderLabels(["ELEMENT", "STATUS", "WARTOŚĆ"])
            tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tab.setStyleSheet("QTableWidget { background-color: #252525; color: white; } QHeaderView::section { background-color: #333; color: white; }")
            if t == 'A': self.tabA = tab
            else: self.tabB = tab
            r_lay.addWidget(tab)
        self.stack.addWidget(r_cont)
    def toggleA(self):
        self.runningA = not self.runningA
        if self.runningA: self.timerA.start(50) #jesli instalacja A ma dzialac odpala zegar co 50 ms
        else: self.timerA.stop() # jesli nie, wylacza zegar
        self.btn_startA.setText("STOP" if self.runningA else "START") #zamienia napis po kliknieciu przycisku
    def toggleB(self):
        self.runningB = not self.runningB
        if self.runningB: self.timerB.start(50)
        else: self.timerB.stop()
        self.btn_startB.setText("STOP" if self.runningB else "START")
    def logika_A(self):
        v = 0.2 # Prędkość wypływu wody z 1 zbiornika
        if self.z1A.aktualna_ilosc > 5.0: #jesli w zzbiorniku jest więcej niż rezerwowe 5 litrów włącza pompę P1
            self.pompaA1_on = True
            self.z1A.aktualna_ilosc -= v
            self.z2A.aktualna_ilosc += v/2
            self.z3A.aktualna_ilosc += v/2
            for i in range(3): self.ruryA[i].czy_plynie = True
        else: # Jeśli mniej niż 5 litrów wyłącza pompę
            self.pompaA1_on = False
            for i in range(3): self.ruryA[i].czy_plynie = False
        if self.z2A.aktualna_ilosc > 20.0: # Jeśli zbiornik 2 ma więcej niż 20 litrów
            self.pompaA2_on = True # Włącz pompę P2
            self.z2A.aktualna_ilosc -= 0.1
            self.z4A.aktualna_ilosc += 0.1
            self.ruryA[3].czy_plynie = True
        else: # Jeśli w zbiorniku 2 jest mało wody
            self.pompaA2_on = False # Wyłącz pompę P2
            self.ruryA[3].czy_plynie = False
        if self.z3A.aktualna_ilosc > 4.0: # Jeśli w zbiorniku 3 jest więcej niż 4 litry
            if self.z3A.temperatura < 60.0: # Jeśli woda nie osiągnęła jeszcze 60 stopni
                self.grzalkaA_on = True # Wlacz grzałkę na pełną moc
                self.z3A.temperatura += 0.2 # Zwiększ temperaturę wody
                self.pompaA3_on = False
                self.ruryA[4].czy_plynie = False
            else: # Jeśli woda ma już 60 stopni
                self.z3A.temperatura = 60.0 # Trzymaj sztywne 60 stopni
                self.grzalkaA_on = True # Grzałka podtrzymuje temperaturę
                self.pompaA3_on = True # Włącz pompę P3
                self.z3A.aktualna_ilosc -= 0.1
                self.z4A.aktualna_ilosc += 0.1
                self.ruryA[4].czy_plynie = True
        else: # Jeśli zbiornik 3 jest prawie pusty (<4 litry)
            self.grzalkaA_on = self.pompaA3_on = False # Wyłącz grzałkę i pompę P3
            self.ruryA[4].czy_plynie = False
            self.z3A.temperatura = max(20.0, self.z3A.temperatura - 0.2)
        self.odswiez_tabele('A')
        self.update()
    def logika_B(self):
        v = 0.2
        if self.z4B.aktualna_ilosc >= 99.0: #jesli ostatni zbiornik sie prawie przelewa
            self.pompaB1_on = self.pompaB2_on = self.pompaB3_on = self.grzalkaB_on = False #Wyłącza wszystkie pompy
            self.z3B.temperatura = max(20.0, self.z3B.temperatura - 0.5)
            if self.runningB: self.toggleB()  # Samo wciska przycisk STOP
        else:
            if self.z1B.aktualna_ilosc > 5.0:
                self.pompaB1_on = True
                self.z1B.aktualna_ilosc -= v
                self.z2B.aktualna_ilosc += v/2
                self.z3B.aktualna_ilosc += v/2
                for i in range(3): self.ruryB[i].czy_plynie = True
            else:
                self.pompaB1_on = False
                for i in range(3): self.ruryB[i].czy_plynie = False
            if self.z2B.aktualna_ilosc > 20.0:
                self.pompaB2_on = True
                self.z2B.aktualna_ilosc -= 0.1
                self.z4B.aktualna_ilosc += 0.1
                self.ruryB[3].czy_plynie = True
            else:
                self.pompaB2_on = False
                self.ruryB[3].czy_plynie = False
            if self.z3B.aktualna_ilosc > 4.0:
                if self.z3B.temperatura < 60.0:
                    self.grzalkaB_on = True
                    self.z3B.temperatura += 0.2
                    self.pompaB3_on = False
                    self.ruryB[4].czy_plynie = False
                else:
                    self.z3B.temperatura = 60.0
                    self.grzalkaB_on = True
                    self.pompaB3_on = True
                    self.z3B.aktualna_ilosc -= 0.1
                    self.z4B.aktualna_ilosc += 0.1
                    self.ruryB[4].czy_plynie = True
            else:
                self.grzalkaB_on = self.pompaB3_on = False
                self.ruryB[4].czy_plynie = False
                self.z3B.temperatura = max(20.0, self.z3B.temperatura - 0.2)
        self.odswiez_tabele('B')
        self.update()
    def odswiez_tabele(self, tag): # Funkcja wpisująca dane do tabeli raportów
        t = self.tabA if tag == 'A' else self.tabB # Wybiera tabelę A lub B
        z1, z2, z3, z4 = (self.z1A, self.z2A, self.z3A, self.z4A) if tag == 'A' else (self.z1B, self.z2B, self.z3B, self.z4B)
        p1, p2, p3 = (self.pompaA1_on, self.pompaA2_on, self.pompaA3_on) if tag == 'A' else (self.pompaB1_on, self.pompaB2_on, self.pompaB3_on)
        grz, run = (self.grzalkaA_on, self.runningA) if tag == 'A' else (self.grzalkaB_on, self.runningB)
        d = [("POMPA P1 (Z1)", "PRACA" if p1 else "STOP", f"{int(round(z1.aktualna_ilosc))} L"),
             ("POMPA P2 (Z2)", "PRACA" if p2 else "STOP", f"{int(round(z2.aktualna_ilosc))} L"),
             ("POMPA P3 (Z3)", "PRACA" if p3 else "STOP", f"{int(round(z3.aktualna_ilosc))} L"),
             ("GRZAŁKA G1", "PODTRZYMANIE" if (z3.temperatura >= 60 and grz) else ("ON" if grz else "OFF"), f"{int(round(z3.temperatura))} °C"),
             ("ZBIORNIK 4", "ALARM" if z4.aktualna_ilosc > 99 else "OK", f"{int(round(z4.aktualna_ilosc))} L"),
             ("SYSTEM", "AKTYWNY" if run else "STOP", "-")]
        for i, (e, s, v) in enumerate(d): # Dla każdego wiersza danych z listy powyżej
            t.setItem(i, 0, QTableWidgetItem(e)) # Wpisz nazwę elementu do pierwszej kolumny
            t.setItem(i, 1, QTableWidgetItem(s)) # Wpisz status do drugiej kolumny
            t.setItem(i, 2, QTableWidgetItem(v)) # Wpisz wartość (litry/temperatura) do trzeciej kolumny

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SystemSCADA()
    ex.show()
    sys.exit(app.exec_())