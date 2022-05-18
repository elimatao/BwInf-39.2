import csv
from PIL import Image, ImageDraw, ImageFont, ImageShow  # Bibliothek zur Bildverarbeitung
import click  # Für die Eingabeverwaltung
import random  # Zum Testen
from sys import exit

angenommen = []
n_anfragen = 0
anfragen = []
free_rects = [{'s': 8, 'e': 18, 'l': 1000, 'pos': 0}]  # Menge mit allen maximalen freien Rechtecken. (Ist am Anfang der gesamte Marktplatz)


@click.command()
@click.argument("inputf", type=click.File(mode='r'))
@click.option("-o", '--outputf', type=str,
              help="Gibt die ausgewählten Anfragen in einer Datei aus, anstatt sie in der Kommandozeile zu drucken.")
@click.option('-i', "--imgf", "imgf", type=str,
              help="Datei, in der das generierte Bild gespeichert werden soll.")
@click.option('-d', '--debug', 'debug', is_flag=True,
              help="Wechselt in den Debugging-Modus.")
@click.option('-s', '--sorting', 'sorting', type=str, default=None,
              help="Die Reihenfolge, nach welcher die Anfragen sortiert werden sollen.\n"
                   "Möglichkeiten: s (Startzeit), e (Endzeit), l (Standlänge), a (Einkommen, das die Anfrage hervorbringen wird), "
                   "h (Zeit, die ein Stand im Markt verbringen wird.)\n"
                   "Ein '-' vor einer Möglichkeit sortiert sie absteigend.\n"
                   "Die Möglichkeiten werden einfach hintereinander geschrieben. Bsp: 'sl-a'")
@click.option('-a', '--algorithm', type=click.Choice(['maxrects', 'test']), default='maxrects',
              help="Der Algorithmus, der zur Anfragenwahl verwendet werden soll.")
@click.option('-h', '--heuristics', multiple=True, type=click.Choice(['bl', 'bssf', 'blsf']), default=['bssf'],
              help="Die Heuristik, die der Algorithmus verwenden soll (Bottom-left oder Best short side fit).")
@click.option('-g', '--global', 'glob', is_flag=True,
              help="Nimmt immer die global beste Anfrage im Sinne der verwendeten Heuristik.")
def cli(inputf, outputf, imgf, algorithm, heuristics, debug, sorting, glob):
    """Lösung des Flohmarktproblems. Nimmt die Information der Datei INPUTF und schreibt die Lösung in die Datei OUTPUTF."""
    global anfragen, free_rects, angenommen, n_anfragen
    # Liest die Anfragenzahl ein
    n_anfragen = int(inputf.readline())

    # Alle Anfragen einlesen
    anfragen = csv.DictReader(inputf, delimiter=' ', fieldnames=['s', 'e', 'l'])  # Startstunde, Endstunde, Standlänge

    #  Wandelt Inhalte in Zahlen um und fügt ID hinzu
    anfragen = list(anfragen)
    id = 1
    for anfrage in anfragen:
        for key in anfrage:
            anfrage[key] = int(anfrage[key])

        anfrage["id"] = id
        id += 1

    #  Sortiert aufsteigend nach Startzeit, absteigend nach Endzeit und absteigend nach Länge
    if sorting is not None:
        anfragen = sorted(anfragen, key=lambda k: order_sorting(k, sorting))  # Coool!!!

    # Führt den Algorithmus aus, den der Nutzer gewählt hat.
    # x = eval(algorithm)(free_rects[0]) # Nett, aber nicht so geeignet.
    max_l_free_rects = 0
    if algorithm == "maxrects":
        if glob:
            while maxrects(heuristics):
                if debug:
                    d = Drawer("debug.png")
                    d.bcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
                    d.fcolor = None
                    for f in free_rects:  # Malt die freien Rechtecke
                        d.bcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
                        d.draw_rect(f)
                    for ang in angenommen:  # Malt die platzierten Rechtecke
                        d.bcolor = "#99b"
                        d.fcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        d.draw_rect(ang)
                    d.show()
                continue
        else:
            anfragen_copy = anfragen.copy()
            for anfrage in anfragen_copy:
                maxrects(heuristics, anfrage)
                if max_l_free_rects < len(free_rects):
                    max_l_free_rects = len(free_rects)

                if debug:  # Zum Testen
                    d = Drawer("debug.png")
                    d.bcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
                    d.fcolor = None
                    for f in free_rects:  # Malt die freien Rechtecke
                        d.bcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
                        d.draw_rect(f)
                    for ang in angenommen:  # Malt die platzierten Rechtecke
                        d.bcolor = "#99b"
                        d.fcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        d.draw_rect(ang)
                    d.show()
                    # input("Press ENTER to continue")

        # Druckt alle eingesetzten Kästchen und die übriggebliebenen freien Rechtecke.
        if imgf is not None:
            d = Drawer(imgf)
            d.bcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
            d.fcolor = None
            for f in free_rects:  # Malt die freien Rechtecke
                d.bcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
                d.draw_rect(f)
            for ang in angenommen:  # Malt die platzierten Rechtecke
                d.bcolor = "#99b"
                d.fcolor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                d.draw_rect(ang)
            # d.show()
            d.store()

        measure_stats()
        print(f"Maximale Zahl freier Rechtecke: {max_l_free_rects}")  # Die maximale Anzahl an freien Rechtecken.

    elif algorithm == 'test':
        # Druckt alle Anfragen nebeneinander und sortiert.
        x = test()

        if imgf is not None:
            d = Drawer(imgf, w=x)
            for anfrage in anfragen:
                d.draw_rect(anfrage)
            d.store()

    print_struct(anfragen, outputf)  # Druckt Anfragen
    print_struct(angenommen, outputf)


# Gibt den Gewinnprozentsatz an, der erreicht wurde. (100% entspricht der vollständingen Abdeckung von Raum und Zeit.)
def measure_stats():
    global angenommen, anfragen, n_anfragen
    n_angenommen = 0
    tot_area = 1000 * 10  # Maximale Erträge (€) des Flohmarkts
    cov_area = 0
    for ang in angenommen:
        if 'pos' not in ang:
            continue
        else:
            cov_area += (ang['e']-ang['s']) * ang['l']
            n_angenommen += 1
    print(f"Erträge: {cov_area / tot_area * 100}%")
    print(f"Angenommene Anfragen: {n_angenommen} / {n_anfragen}")


def order_sorting(anfrage, order):
    i = 0
    o = []

    def area(x):
        return x['l'] * (x['e'] - x['s'])

    def height(x):
        return x['e'] - x['s']

    while i < len(order):
        if order[i] == '-':
            if order[i + 1] == 'a':
                o.append(-area(anfrage))
            elif order[i + 1] == 'h':
                o.append(-height(anfrage))
            else:
                o.append(-anfrage[order[i + 1]])
            i += 2
        else:
            if order[i] == 'a':
                o.append(area(anfrage))
            elif order[i] == 'h':
                o.append(height(anfrage))
            else:
                o.append(anfrage[order[i]])
            i += 1
    return tuple(o)


def maxrects(heuristics, anfrage=None):
    """
    Implementierung des Maximal Rectangles-Algorithmus, nach
    Jukka Jylänki (http://pds25.egloos.com/pds/201504/21/98/RectangleBinPack.pdf)
    """
    global free_rects, anfragen, angenommen

    # Falls keine Anfrage übergeben wurde, führe die globale Option aus.
    if anfrage is None:

        min_score = 1000
        options = []

        for a in anfragen:
            min_score, f_r = assign_free_rect(heuristics, a)
            if f_r is None:
                continue
            options.append(f_r)  # erhält (anfrage, free_rect)

        i = 0  # Current heuristic iterator position
        while len(options) > 1 and i != len(heuristics):
            min_score, options = untier(options, heuristics[i])
            i += 1

        if min_score == 1000:
            return False  # Es konnte keine weiteres Rechteck eingesetzt werden.
        anfrage = options[0][0]
        fi = options[0][1]

    else:
        # wähle das nächste freie Rechteck, in das anfrage gesetzt werden soll.
        x, fi = assign_free_rect(heuristics, anfrage)
        if not fi:
            return  # Falls das Rechteck nicht passt, nächstes Rechteck
        fi = fi[1]

    # Setze die Anfrage in das freie Rechteck links ein
    anfrage['pos'] = fi['pos']

    anfragen.remove(anfrage)  # Entferne die angenommene (beste) Anfrage.
    angenommen.append(anfrage)

    # Erstelle die neuen maximalen Rechtecke
    temp_corrupted_rects = []
    temp_free_rects = []

    # Gucke, ob anfrage auch in einem der anderen free_rects (teilweise) enthalten ist und bilde ggf. neue maximale Rechtecke
    for f in free_rects:
        if anfrage['s'] >= f['e'] or anfrage['e'] <= f['s'] or (anfrage['pos'] + anfrage['l']) < f['pos'] or anfrage['pos'] > (f['pos'] + f['l']):
            continue
        else:
            temp_corrupted_rects.append(f)
            temp_free_rects += build_max_rects(anfrage, f)

    # Lösche alle alten maximalen Rechtecke
    for f in temp_corrupted_rects:
        free_rects.remove(f)
    free_rects += temp_free_rects  # Füge die neuen Rechtecke hinzu.

    # Prüft, ob alle Rechtecke tatsächlich maximale Rechtecke sind, indem für jedes Rechteck geguckt wird, ob dessen Fläche
    # eine Teilmenge der Fläche des anderen Rechtecks ist.
    temp = []
    for f1 in free_rects:
        for f2 in free_rects:
            if f1 == f2: continue
            if f1['s'] < f2['s'] or f1['e'] > f2['e'] or (f1['pos'] + f1['l']) > (f2['pos'] + f2['l']) or f1['pos'] < f2['pos']:
                continue
            else:
                temp.append(f1)
    for i in temp:  # TODO use sets for better performance.
        try:
            free_rects.remove(i)
        except:
            pass

    return True


# Tied: [(anfrage, f)]
def untier(tied, heuristic):
    """Findet die eindeutig beste Anfrage --> Rechteck Zuordnung"""
    min_val = 1000
    min_rects = []
    for paar in tied:
        tmp_val = eval(heuristic)(paar[0], paar[1])
        if tmp_val == min_val:
            min_rects.append(paar)
        elif tmp_val < min_val:
            min_rects = [paar]
            min_val = tmp_val

    return (min_val, min_rects)


def assign_free_rect(heuristics, anfrage):
    """
    Findet das beste freie Rechteck im Sinne der übergebenen Heuristik.
    i = current heuristic iterator position
    """
    global free_rects
    tmp_best = (1000, [])

    # Filtert die Rechtecke, in die die Anfrage passt.
    for f in free_rects:
        if anfrage['e'] <= f['e'] and anfrage['l'] <= f['l'] and anfrage['s'] >= f['s']:
            tmp_best[1].append((anfrage, f))

    # Solange es mehrere beste Paare gibt und es heuristische Regeln zum probieren gibt.
    i = 0  # Current heuristic iterator position
    while len(tmp_best[1]) > 1 and i != len(heuristics):
        tmp_best = untier(tmp_best[1], heuristics[i])
        i += 1

    if len(tmp_best[1]) > 0:
        return tmp_best[0], tmp_best[1][0]  # Erste Anfrage in tmp_best
    else:
        return tmp_best[0], None


def bssf(anfrage, f):
    """
    Gibt die Länge der kürzeren übriggeblieben Seite zurück.
    """
    f_hoehe = (f['e'] - f['s']) - (anfrage['e'] - anfrage['s'])
    f_breite = f['l'] - anfrage['l']
    return min(f_breite, f_hoehe)


def blsf(anfrage, f):
    """
    Gibt die Länge der kürzeren übriggeblieben Seite zurück.
    """
    f_hoehe = (f['e'] - f['s']) - (anfrage['e'] - anfrage['s'])
    f_breite = f['l'] - anfrage['l']
    return max(f_breite, f_hoehe)


def bl(anfrage, f):
    """
    Gibt die Differenz zwischen Start von Anfrage und Start von f zurück (0, falls sich Anfrage in bl von f platzieren lässt)
    """
    return anfrage['s'] - f['s']


def build_max_rects(anfrage, fi):
    """
    Baut die maximalen Rechtecke um die Anfrage herum und speichert sie in free_rects.
    Es wird angenommen, dass sich das neue Rechteck am linken Rand on fi befindet.
    """
    global free_rects
    temp_free_rects = []
    if anfrage['s'] > fi['s']:  # freies Rechteck unter anfrage
        temp_free_rects.append({'s': fi['s'], 'e': anfrage['s'], 'l': fi['l'], 'pos': fi['pos']})

    if anfrage['pos'] > fi['pos']:  # freies Rechteck links von Anfrage
        temp_free_rects.append({'s': fi['s'], 'e': fi['e'], 'l': anfrage['pos'] - fi['pos'], 'pos': fi['pos']})

    if (anfrage['pos'] + anfrage['l']) < (fi['pos'] + fi['l']):  # freies Rechteck rechts von anfrage
        temp_free_rects.append({'s': fi['s'], 'e': fi['e'], 'l': (fi['pos'] + fi['l']) - (anfrage['pos'] + anfrage['l']), 'pos': anfrage['pos'] + anfrage['l']})

    if anfrage['e'] < fi['e']:  # freies Rechteck über anfrage
        temp_free_rects.append({'s': anfrage['e'], 'e': fi['e'], 'l': fi['l'], 'pos': fi['pos']})

    return temp_free_rects


def test():
    """Zum Testen: Ordnet alle Anfragen nebeneinander an."""
    global anfragen
    x = 0
    for anfrage in anfragen:
        anfrage['pos'] = x
        x += anfrage['l']
    return x


def print_struct(blocks, outputf):
    if outputf is None:
        for block in blocks:
            print(block)
    else:
        with open(outputf, 'w') as f:
            for block in blocks:
                f.write(block.__repr__())
                f.write('\n')


class Drawer:
    def __init__(self, outputf, mult=5, w=1000, h=10, fcolor="#ddd", bcolor="#99b"):
        self.outputf = outputf
        self.mult = mult
        self.w = w * mult
        self.h = h * mult
        self.fcolor = fcolor
        self.bcolor = bcolor

        self.img = Image.new("RGBA", (self.w, self.h), color="#888")
        ImageShow.register(ImageShow.EogViewer, order=0)  # Setzt das Programm für die Ausgabe
        self.draw = ImageDraw.Draw(self.img)  # Objekt zum Zeichnen

        self.fnt = ImageFont.truetype("./pzim3x5.ttf", 10)  # Schriftart (so klein wie möglich)

    def draw_rect(self, anfrage):
        if 'pos' not in anfrage: return
        x0 = self.mult * anfrage['pos']
        y0 = self.h - (anfrage['s'] - 8) * self.mult - 1
        x1 = self.mult * (anfrage['l'] + anfrage['pos']) - 1
        y1 = self.h - (anfrage['e'] - 8) * self.mult
        self.draw.rectangle([x0, y0, x1, y1], outline=self.bcolor, fill=self.fcolor, width=1)  # Malt Anfrage als Rechteck

        try:
            self.draw.text((x0, y1), text=f"{anfrage['id']}", font=self.fnt, fill="red", spacing=1)  # Schreibt ID in das Rechteck
        except KeyError:
            pass

    def store(self):
        self.img.save(fp=self.outputf, format="PNG")

    def show(self):
        self.img.show()


if __name__ == '__main__':
    cli()
