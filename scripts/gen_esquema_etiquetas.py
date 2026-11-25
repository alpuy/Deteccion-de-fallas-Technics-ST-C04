#!/usr/bin/env python3
"""Genera ST-C04_display_teclado.kicad_sch (KiCad 7) a partir del netlist
reconstruido del manual de servicio Technics ST-C04."""
import uuid, sys

U = lambda: str(uuid.uuid4())
ROOT = U()
FONT = '(effects (font (size 1.27 1.27)))'
FONTH = '(effects (font (size 1.27 1.27)) hide)'

# ---------------------------------------------------------------- símbolos
def pin(num, name, x, y, ang, length=2.54, typ="passive"):
    return (f'(pin {typ} line (at {x} {y} {ang}) (length {length}) '
            f'(name "{name}" {FONT}) (number "{num}" {FONT}))')

def libsym(name, graphics, pins, pin_names_hide=True, ref="U", offset=None):
    pn = '(pin_names hide)' if pin_names_hide else '(pin_names (offset 0.762))'
    return (f'(symbol "STC04:{name}" {pn} (in_bom yes) (on_board yes)\n'
            f'  (property "Reference" "{ref}" (at 0 0 0) {FONT})\n'
            f'  (property "Value" "{name}" (at 0 0 0) {FONT})\n'
            f'  (property "Footprint" "" (at 0 0 0) {FONTH})\n'
            f'  (property "Datasheet" "" (at 0 0 0) {FONTH})\n'
            f'  (symbol "{name}_0_1" {" ".join(graphics)})\n'
            f'  (symbol "{name}_1_1" {" ".join(pins)}))')

ST = '(stroke (width 0.254) (type default))'
def poly(pts, fill="none", w=0.254):
    p = " ".join(f"(xy {a} {b})" for a, b in pts)
    return f'(polyline (pts {p}) (stroke (width {w}) (type default)) (fill (type {fill})))'
def rect(x1, y1, x2, y2, fill="background"):
    return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) {ST} (fill (type {fill})))'
def circ(x, y, r, fill="none"):
    return f'(circle (center {x} {y}) (radius {r}) {ST} (fill (type {fill})))'
def gtext(t, x, y):
    return f'(text "{t}" (at {x} {y} 0) {FONT})'

SYMS = {}   # name -> (libdef, {pinnum: (x, y, ang)})

def reg(name, graphics, pins_spec, **kw):
    pins = [pin(*p) for p in pins_spec]
    SYMS[name] = (libsym(name, graphics, pins, **kw),
                  {p[0]: (p[2], p[3], p[4]) for p in pins_spec})

# 2 pines verticales: 1 arriba, 2 abajo
reg("R", [rect(-1.016, -2.54, 1.016, 2.54, "none")],
    [("1", "~", 0, 5.08, 270), ("2", "~", 0, -5.08, 90)], ref="R")
reg("C", [poly([(-2.032, 0.508), (2.032, 0.508)], w=0.508),
          poly([(-2.032, -0.508), (2.032, -0.508)], w=0.508)],
    [("1", "~", 0, 5.08, 270, 4.572), ("2", "~", 0, -5.08, 90, 4.572)], ref="C")
reg("CP", [poly([(-2.032, 0.508), (2.032, 0.508)], w=0.508),
           poly([(-2.032, -0.508), (2.032, -0.508)], w=0.508),
           gtext("+", -1.6, 1.8)],
    [("1", "+", 0, 5.08, 270, 4.572), ("2", "-", 0, -5.08, 90, 4.572)], ref="C")
# diodo: A arriba, K abajo (conduce hacia abajo)
reg("D", [poly([(-1.27, 1.27), (1.27, 1.27), (0, -1.27), (-1.27, 1.27)], "outline"),
          poly([(-1.27, -1.27), (1.27, -1.27)])],
    [("1", "A", 0, 5.08, 270, 3.81), ("2", "K", 0, -5.08, 90, 3.81)], ref="D")
reg("XTAL", [rect(-1.27, -0.762, 1.27, 0.762, "none"),
             poly([(-1.778, 1.27), (1.778, 1.27)]), poly([(-1.778, -1.27), (1.778, -1.27)])],
    [("1", "1", 0, 5.08, 270, 3.81), ("2", "2", 0, -5.08, 90, 3.81)], ref="X")
# pulsador vertical
reg("SW_PUSH", [circ(0, 1.27, 0.508), circ(0, -1.27, 0.508),
                poly([(1.27, 2.032), (1.27, -2.032)]), poly([(1.27, 0), (2.54, 0)])],
    [("1", "1", 0, 5.08, 270, 3.302), ("2", "2", 0, -5.08, 90, 3.302)], ref="S")
# conmutador SPDT: COM abajo, A arriba-izq, B arriba-der
reg("SW_SPDT", [circ(0, -1.27, 0.508), circ(-2.54, 1.778, 0.508), circ(2.54, 1.778, 0.508),
                poly([(0, -0.762), (-2.286, 1.524)])],
    [("2", "COM", 0, -5.08, 90, 3.302), ("1", "A", -2.54, 5.08, 270, 2.794),
     ("3", "B", 2.54, 5.08, 270, 2.794)], ref="S")
# PNP: B izq, E arriba, C abajo
reg("Q_PNP", [circ(1.27, 0, 2.794), poly([(0, 1.905), (0, -1.905)], w=0.508),
              poly([(0, 0.635), (2.54, 2.54)]), poly([(0, -0.635), (2.54, -2.54)]),
              poly([(0.6, 1.6), (0.3, 0.9), (1.1, 1.0), (0.6, 1.6)], "outline")],
    [("B", "B", -5.08, 0, 0, 5.08), ("E", "E", 2.54, 5.08, 270, 2.54),
     ("C", "C", 2.54, -5.08, 90, 2.54)], ref="Q")

def ic(name, left, right, w=20.32, ref="U", title=None):
    """left/right: listas de (num, nombre) de arriba hacia abajo."""
    n = max(len(left), len(right))
    h = n * 2.54 + 2.54
    top = h / 2
    pins = []
    for i, (num, nm) in enumerate(left):
        pins.append((num, nm, -w / 2 - 5.08, round(top - 2.54 - i * 2.54, 3), 0, 5.08))
    for i, (num, nm) in enumerate(right):
        pins.append((num, nm, w / 2 + 5.08, round(top - 2.54 - i * 2.54, 3), 180, 5.08))
    g = [rect(-w / 2, -top, w / 2, top)]
    if title:
        g.append(gtext(title, 0, top + 1.5))
    reg(name, g, pins, pin_names_hide=False, ref=ref)

ic("SVID1703C011",
   [("1", "EO1"), ("2", "EO2"), ("3", "CE"), ("4", "PSC"), ("5", "X1"), ("6", "X2"),
    ("7", "SD"), ("8", "MUT"), ("9", "D1"), ("10", "D2"), ("11", "D3"), ("12", "D4"),
    ("13", "D5"), ("14", "VDD")],
   [("28", "AM"), ("27", "GND"), ("26", "FM"), ("25", "K0"), ("24", "K1"), ("23", "K2"),
    ("22", "K3"), ("21", "a"), ("20", "b"), ("19", "c"), ("18", "d"), ("17", "e"),
    ("16", "f"), ("15", "g")], w=22.86, title="PLL controller")
FLP = ["F", "d", "FM/DP", "G7", "AM", "kHz", "G6", "MEM", "a", "G5", "b", "f", "G4", "G7b",
       "g", "G3", "c", "e", "f2", "G1,2", "g2", "a2", "MHz", "F"]
ic("SAD7BT05A", [(str(i + 1), FLP[i]) for i in range(24)], [], w=17.78, ref="FL",
   title="Tubo VFD")
def net(name, n, common_label, title):
    ic(name, [("1", common_label)] + [(str(i), f"{i}") for i in range(2, n + 1)], [],
       w=12.7, ref="Z", title=title)
net("RN8_100k", 8, "COM", "100k x7")
net("RN6_100k", 6, "COM", "100k x5")
net("CN8_330p", 8, "GND", "330p x7")
net("CN6_330p", 6, "GND", "330p x5")

# ---------------------------------------------------------------- dibujo
items = []

def label(name, x, y, ang, glob=False):
    just = {0: "left bottom", 90: "left bottom", 180: "right bottom", 270: "right bottom"}[ang]
    if glob:
        gj = "left" if ang in (0, 90) else "right"
        items.append(f'(global_label "{name}" (shape passive) (at {x} {y} {ang}) (fields_autoplaced) '
                     f'(effects (font (size 1.27 1.27)) (justify {gj})) (uuid {U()}) '
                     f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) {FONTH}))')
    else:
        items.append(f'(label "{name}" (at {x} {y} {ang}) (fields_autoplaced) '
                     f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid {U()}))')

def wire(x1, y1, x2, y2):
    items.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid {U()}))')

def text(t, x, y, size=1.5, bold=False):
    b = " bold" if bold else ""
    t = t.replace('"', "'")
    items.append(f'(text "{t}" (at {x} {y} 0) (effects (font (size {size} {size}){b}) (justify left top)) (uuid {U()}))')

GLOBALS = set()
NETS = {}  # para informe

def place(sym, ref, value, x, y, conns, wl=2.54):
    """conns: {pin: netname}. Coloca símbolo, cable corto y etiqueta en cada pin."""
    libdef, pins = SYMS[sym]
    props = (f'(property "Reference" "{ref}" (at {x + 3.5} {y - 1} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
             f'(property "Value" "{value}" (at {x + 3.5} {y + 1.5} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
             f'(property "Footprint" "" (at {x} {y} 0) {FONTH})\n(property "Datasheet" "" (at {x} {y} 0) {FONTH})')
    if sym in ("SVID1703C011", "SAD7BT05A") or sym.startswith(("RN", "CN")):
        nrows = max(sum(1 for p in pins.values() if p[2] == 0), sum(1 for p in pins.values() if p[2] == 180))
        top = (nrows * 2.54 + 2.54) / 2
        props = (f'(property "Reference" "{ref}" (at {x} {y - top - 4} 0) {FONT})\n'
                 f'(property "Value" "{value}" (at {x} {y + top + 2} 0) {FONT})\n'
                 f'(property "Footprint" "" (at {x} {y} 0) {FONTH})\n(property "Datasheet" "" (at {x} {y} 0) {FONTH})')
    pinuuids = " ".join(f'(pin "{p}" (uuid {U()}))' for p in pins)
    items.append(f'(symbol (lib_id "STC04:{sym}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) '
                 f'(uuid {U()})\n{props}\n{pinuuids}\n'
                 f'(instances (project "ST-C04_display_teclado" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
    for p, (px, py, ang) in pins.items():
        n = conns.get(p)
        if n is None:
            continue
        cx, cy = round(x + px, 3), round(y - py, 3)
        # dirección hacia afuera (opuesta a la del pin) en coords de esquema
        dx, dy, la = {0: (-1, 0, 180), 180: (1, 0, 0), 90: (0, 1, 270), 270: (0, -1, 90)}[ang]
        ex, ey = round(cx + dx * wl, 3), round(cy + dy * wl, 3)
        wire(cx, cy, ex, ey)
        g = n.startswith("@")
        nm = n.lstrip("@")
        label(nm, ex, ey, la, glob=False)
        NETS.setdefault(nm, []).append(f"{ref}.{p}")

def two(sym, ref, val, x, y, n1, n2):
    place(sym, ref, val, x, y, {"1": n1, "2": n2})

# ---- nombres de red
S = {"Sa": "d_P27", "Sb": "c_P30", "Sc": "e_P31", "Sd": "f_P28", "Se": "g_P32", "Sf": "b_P29", "Sg": "a_P33"}
K = {0: "K0_P37", 1: "K1_P36", 2: "K2_P35", 3: "K3_P34"}
G = {"G7": "GRID_G7_P18", "G3": "GRID_G3_P19", "G4": "GRID_G4_P20",
     "G5": "GRID_G5_P21", "G6": "GRID_G6_P22"}
NEG = "-21V4"

# ---------------- IC901 + reloj + alimentación lógica
place("SVID1703C011", "IC901", "SVID1703C011", 80, 120, {
    "1": "@EO1_FILTRO_LAZO", "2": "@EO2_FILTRO_LAZO", "3": "@CE", "4": "@PSC_IC902-6",
    "5": "XTAL_X1", "6": "XTAL_X2", "7": "@SD_ESTEREO_IC301", "8": "@MUTE",
    "9": "DIG_D1", "10": "DIG_D2", "11": "DIG_D3", "12": "DIG_D4", "13": "DIG_D5",
    "14": "VDD_5V0",
    "28": "@AM_OSC_IN", "27": "GND", "26": "@FM_PRESCALER_IN_C915",
    "25": K[0], "24": K[1], "23": K[2], "22": K[3],
    "21": "a_P33", "20": "b_P29", "19": "c_P30", "18": "d_P27", "17": "e_P31",
    "16": "f_P28", "15": "g_P32"}, wl=5.08)

y0 = 175
place("XTAL", "X901", "4.5MHz", 30, y0, {"1": "XTAL_X1", "2": "XTAL_X2"})
two("C", "C913", "15p", 45, y0, "XTAL_X1", "GND")
two("C", "C914", "15p", 58, y0, "XTAL_X2", "GND")
two("D", "D901", "MA150", 80, y0, "@+B_PLL_5V6", "VDD_5V0")
two("C", "C903", "0.01u", 93, y0, "VDD_5V0", "GND")
two("CP", "C902", "1000u 6.3V", 106, y0, "VDD_5V0", "GND")
two("R", "R901", "680", 125, y0, "VDD_5V0", "VBACKUP")
two("CP", "C905", "3.3F 1.8V", 140, y0, "VBACKUP", "VB_1")
two("CP", "C906", "3.3F 1.8V", 153, y0, "VB_1", "VB_2")
two("CP", "C907", "3.3F 1.8V", 166, y0, "VB_2", "GND")
text("Memoria: C905-C907 (supercap 3.3F x3 en serie) mantienen VDD con el equipo apagado.", 20, y0 + 14, 1.27)

# ---------------- drivers de rejilla
drv = [("Q905", "R913", "DIG_D1", G["G7"]), ("Q907", "R915", "DIG_D2", G["G3"]),
       ("Q906", "R914", "DIG_D3", G["G4"]), ("Q908", "R916", "DIG_D4", G["G5"]),
       ("Q909", "R917", "DIG_D5", G["G6"])]
for i, (q, r, d, g) in enumerate(drv):
    x = 200 + i * 28
    two("R", r, "10k", x - 12, 70, d, f"B_{q}")
    place("Q_PNP", q, "2SA733", x, 90, {"B": f"B_{q}", "E": "VFL_DRV", "C": g})
two("D", "D921", "MA150", 180, 110, "@+B_PLL_5V6", "VFL_DRV")
two("CP", "C904", "330u 6.3V", 195, 110, "VFL_DRV", "GND")
grids = [G["G6"], G["G5"], G["G4"], G["G3"], G["G7"]]  # pines 2..6 de Z903/Z904
place("RN6_100k", "Z903", "100k x5", 240, 125,
      {"1": NEG, **{str(i + 2): grids[i] for i in range(5)}}, wl=5.08)
place("CN6_330p", "Z904", "330p x5", 300, 125,
      {"1": "GND", **{str(i + 2): grids[i] for i in range(5)}}, wl=5.08)

# ---------------- tubo fluorescente
FLNET = {1: "@FIL_B_P23", 2: S["Sa"], 3: S["Sb"], 4: G["G7"], 5: S["Sc"], 6: S["Sc"],
         7: G["G6"], 8: S["Sf"], 9: S["Sg"], 10: G["G5"], 11: S["Sf"], 12: S["Sd"],
         13: G["G4"], 14: G["G7"], 15: S["Se"], 16: G["G3"], 17: S["Sb"], 18: S["Sc"],
         19: S["Sd"], 20: G["G7"], 21: S["Se"], 22: S["Sg"], 23: S["Sb"], 24: "@FIL_A_P17"}
place("SAD7BT05A", "FL1", "SAD7BT05A", 400, 110, {str(k): v for k, v in FLNET.items()}, wl=7.62)
two("C", "C918", "0.01u", 430, 160, "@FIL_B_P23", "GND")

# ---------------- pull-down de segmentos y filtro
seg_order = [S["Sa"], S["Sd"], S["Sf"], S["Sb"], S["Sc"], S["Se"], S["Sg"]]  # pines 2..8
place("RN8_100k", "Z902", "100k x7", 480, 110,
      {"1": NEG, **{str(i + 2): seg_order[i] for i in range(7)}}, wl=5.08)
place("CN8_330p", "Z901", "330p x7", 540, 110,
      {"1": "GND", **{str(i + 2): seg_order[i] for i in range(7)}}, wl=5.08)
text("Fuente -21,4 V (D702/D922) - viene de la fuente", 455, 140, 1.27)
items.append(f'(global_label "-21V4" (shape input) (at 470 150 180) (fields_autoplaced) '
             f'(effects (font (size 1.27 1.27)) (justify right)) (uuid {U()}) '
             f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at 470 150 0) {FONTH}))')
wire(470, 150, 480, 150)
label(NEG, 480, 150, 0)

# ---------------- matriz de teclado
yk = 245
# diodos de fila (estrobos)
two("D", "D910", "MA150", 200, yk, S["Sb"], "FILA_D910")
two("D", "D911", "MA150", 225, yk, S["Sf"], "FILA_D911")
two("D", "D912", "MA150", 250, yk, "a_P33", "FILA_D912")
# pulsadores
keys = [("S7", "MEMO", "FILA_D912", "COL_D908"), ("S8", "DOWN", "FILA_D912", "COL_D906"),
        ("S9", "UP", "FILA_D912", "COL_D907"), ("S10", "CH1", "FILA_D911", "COL_D909"),
        ("S11", "CH2", "FILA_D911", "COL_D908"), ("S12", "CH3", "FILA_D911", "COL_D907"),
        ("S13", "CH4", "FILA_D911", "COL_D906"), ("S14", "CH5", "FILA_D910", "COL_D909"),
        ("S15", "CH6", "FILA_D910", "COL_D908")]
for i, (s, nm, a, b) in enumerate(keys):
    two("SW_PUSH", s, nm, 290 + i * 22, yk, a, b)
# diodos de columna hacia K
yc = 285
for i, (d, col, k) in enumerate([("D906", "COL_D906", 0), ("D907", "COL_D907", 1),
                                 ("D908", "COL_D908", 2), ("D909", "COL_D909", 3)]):
    two("D", d, "MA150", 300 + i * 25, yc, col, K[k])
# diodos de configuración / rango
cfg = [("D924", S["Sc"], K[0]), ("D925", S["Sd"], K[3]),
       ("D919", S["Se"], K[2]), ("D920", S["Se"], K[3])]
for i, (d, a, k) in enumerate(cfg):
    two("D", d, "MA150", 420 + i * 25, yc, a, k)
# S16 asignación FM/AM
two("D", "D916", "MA150", 200, yc, "g_P32", "S16_COM_P73")
place("SW_SPDT", "S16", "FM/AM ALLOCATION", 225, yc + 5,
      {"2": "S16_COM_P73", "1": K[1], "3": K[0]})

# ---------------- textos
text("Technics ST-C04 - Controlador PLL, display VFD y teclado", 15, 12, 3, True)
text("Reconstruido del manual de servicio (Order No. SD81061918C1), páginas 11-15. "
     "Redes nombradas por función; el sufijo _Pnn es el número del puente/conexión entre placas del esquema original.", 15, 19, 1.5)
text("DRIVERS DE REJILLA (Q905-Q909 2SA733)", 175, 52, 2, True)
text("TUBO FLUORESCENTE + PULL-DOWN DE SEGMENTOS", 360, 52, 2, True)
text("MATRIZ DE TECLADO (estrobos = líneas de segmento a..g; retornos = K0..K3)", 180, 218, 2, True)
text("IC901 + RELOJ 4,5 MHz + ALIMENTACIÓN/MEMORIA", 20, 52, 2, True)
notes = [
    "NOTAS (verificado con el datasheet NEC uPD1703C-011)",
    "1) Las salidas de segmento a..g de IC901 (pines 21..15, P-ch drenador abierto, activas en alto) manejan el VFD y a la vez son los",
    "   estrobos de la matriz de teclas (entradas K0..K3). Un problema en una línea de segmento afecta al display Y a las teclas de esa línea.",
    "2) Matriz (datasheet Fig. 2): a = DOWN/UP/MEMO (D912) | b = CH1..CH4 (D911) | c = CH5/CH6 (D910) | d = sin teclas |",
    "   e = 108/104 (D924) + DIM/AUTO-MAN/AM-FM (S2/S3 en placa F, no dibujados) | f = B2 paso AM (D925) | g = B0/B1 región (S16) + IF0/IF1 (D920/D919).",
    "3) En el dibujo original la línea del segmento 'a' aparece unida al común de Z902: es un error de dibujo; va a P33 / Z902-8.",
    "4) D919/D920 = diodos de 'rango' del FI (IF0/IF1); pueden no estar montados según el filtro cerámico. Orden de pines de Z901 aproximado.",
    "5) +B_5V6 viene de la fuente (ánodos de D901 y D921). -21V4 de D702/D922. Filamento FIL_A/FIL_B: 3,2 Vca. Rejillas: D1 = G7+G1,2 (indicadores",
    "   y último dígito), D2 = G3, D3 = G4, D4 = G5, D5 = G6 (el '1'). S16: A = EE.UU. (B1, K1); B = Europa (B0, K0).",
]
for i, n in enumerate(notes):
    text(n, 15, 330 + i * 5, 1.5, i == 0)

# ---------------------------------------------------------------- salida
lib = "\n".join(v[0] for v in SYMS.values())
out = (f'(kicad_sch (version 20230121) (generator eeschema)\n(uuid {ROOT})\n(paper "A2")\n'
       f'(title_block (title "ST-C04 - PLL, display y teclado") (company "Reconstrucción desde manual Technics") (rev "1"))\n'
       f'(lib_symbols\n{lib}\n)\n' + "\n".join(items) +
       f'\n(sheet_instances (path "/" (page "1")))\n)\n')
open(sys.argv[1], "w").write(out)
with open(sys.argv[1].replace(".kicad_sch", "_redes.txt"), "w") as f:
    for n in sorted(NETS):
        f.write(f"{n}: {', '.join(NETS[n])}\n")
print("ok", len(items))
