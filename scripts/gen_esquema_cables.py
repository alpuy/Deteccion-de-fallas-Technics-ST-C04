#!/usr/bin/env python3
"""ST-C04: PLL, display VFD y teclado. Esquemático KiCad 7 con cables dibujados.
Fila superior: IC901, Z903, Z904, FL, Z902, Z901 (pines hacia abajo).
Fila media: componentes discretos verticales. Canales horizontales arriba (U) y abajo (L)."""
import uuid, sys
U = lambda: str(uuid.uuid4())
ROOT = U()
F = '(effects (font (size 1.27 1.27)))'
FH = '(effects (font (size 1.27 1.27)) hide)'
ST = '(stroke (width 0.254) (type default))'
r3 = lambda v: round(v, 3)

# ------------------------------------------------------------------ símbolos
def pin(num, name, x, y, ang, length, typ="passive", hide=False):
    h = " hide" if hide else ""
    return (f'(pin {typ} line (at {x} {y} {ang}) (length {length}){h} '
            f'(name "{name}" {F}) (number "{num}" {F}))')
def poly(pts, fill="none", w=0.254):
    return (f'(polyline (pts {" ".join(f"(xy {a} {b})" for a, b in pts)}) '
            f'(stroke (width {w}) (type default)) (fill (type {fill})))')
def rect(x1, y1, x2, y2, fill="background"):
    return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) {ST} (fill (type {fill})))'
def circ(x, y, r, fill="none"):
    return f'(circle (center {x} {y}) (radius {r}) {ST} (fill (type {fill})))'
def gtext(t, x, y, s=1.27):
    return f'(text "{t}" (at {x} {y} 0) (effects (font (size {s} {s}))))'

SYMS = {}
def reg(name, g, pins, names=False, ref="U", power=False):
    pn = '(pin_names (offset 0.508))' if names else '(pin_names hide)'
    pw = '(power) ' if power else ''
    d = (f'(symbol "STC04:{name}" {pw}{pn} (in_bom {"no" if power else "yes"}) (on_board yes)\n'
         f' (property "Reference" "{ref}" (at 0 0 0) {F})\n (property "Value" "{name}" (at 0 0 0) {F})\n'
         f' (property "Footprint" "" (at 0 0 0) {FH})\n (property "Datasheet" "" (at 0 0 0) {FH})\n'
         f' (symbol "{name}_0_1" {" ".join(g)})\n'
         f' (symbol "{name}_1_1" {" ".join(pin(*p) for p in pins)}))')
    SYMS[name] = (d, {p[0]: (p[2], p[3]) for p in pins})

T, B = 270, 90  # ángulo de pin superior / inferior
reg("R", [rect(-1.016, -2.54, 1.016, 2.54, "none")], [("1", "~", 0, 5.08, T, 2.54), ("2", "~", 0, -5.08, B, 2.54)], ref="R")
capg = [poly([(-2.032, 0.508), (2.032, 0.508)], w=0.508), poly([(-2.032, -0.508), (2.032, -0.508)], w=0.508)]
reg("C", capg, [("1", "~", 0, 5.08, T, 4.572), ("2", "~", 0, -5.08, B, 4.572)], ref="C")
reg("CP", capg + [gtext("+", -1.4, 1.6)], [("1", "+", 0, 5.08, T, 4.572), ("2", "-", 0, -5.08, B, 4.572)], ref="C")
reg("D", [poly([(-1.27, 1.27), (1.27, 1.27), (0, -1.27), (-1.27, 1.27)], "outline"), poly([(-1.27, -1.27), (1.27, -1.27)])],
    [("1", "A", 0, 5.08, T, 3.81), ("2", "K", 0, -5.08, B, 3.81)], ref="D")
reg("XTAL", [rect(-1.27, -0.762, 1.27, 0.762, "none"), poly([(-1.778, 1.27), (1.778, 1.27)]), poly([(-1.778, -1.27), (1.778, -1.27)])],
    [("1", "1", 0, 5.08, T, 3.81), ("2", "2", 0, -5.08, B, 3.81)], ref="X")
reg("SW_PUSH", [circ(0, 1.27, 0.508), circ(0, -1.27, 0.508), poly([(1.27, 2.032), (1.27, -2.032)]), poly([(1.27, 0), (2.286, 0)])],
    [("1", "1", 0, 5.08, T, 3.302), ("2", "2", 0, -5.08, B, 3.302)], ref="S")
reg("SW_SPDT", [circ(0, -1.27, 0.508), circ(-2.54, 1.778, 0.508), circ(2.54, 1.778, 0.508), poly([(0, -0.762), (-2.286, 1.524)])],
    [("2", "COM", 0, -5.08, B, 3.302), ("1", "A", -2.54, 5.08, T, 2.794), ("3", "B", 2.54, 5.08, T, 2.794)], ref="S")
# PNP con base arriba-izquierda, emisor arriba-derecha, colector abajo
reg("Q_PNP", [circ(1.27, 0, 2.794), poly([(0, 1.905), (0, -1.905)], w=0.508), poly([(-2.54, 2.54), (-2.54, 0), (0, 0)]),
              poly([(0, 0.635), (2.54, 2.54)]), poly([(0, -0.635), (2.54, -2.54)]),
              poly([(0.6, 1.6), (0.3, 0.9), (1.1, 1.0), (0.6, 1.6)], "outline")],
    [("B", "B", -2.54, 5.08, T, 2.54), ("E", "E", 2.54, 5.08, T, 2.54), ("C", "C", 2.54, -5.08, B, 2.54)], ref="Q")
reg("GND", [poly([(0, 0), (0, -1.27), (1.27, -1.27), (0, -2.54), (-1.27, -1.27), (0, -1.27)])],
    [("1", "GND", 0, 0, T, 0, "power_in", True)], ref="#PWR", power=True)

def bic(name, names, title, h=15.24, ref="U"):
    """IC con todos los pines en el borde inferior, x = 0, 2.54, 4.08..."""
    n = len(names)
    g = [rect(-1.27, -h / 2, r3((n - 1) * 2.54 + 1.27), h / 2), gtext(title, r3((n - 1) * 1.27), r3(h / 2 - 2.0))]
    pins = [(num, nm, r3(i * 2.54), r3(-h / 2 - 5.08), B, 5.08) for i, (num, nm) in enumerate(names)]
    reg(name, g, pins, names=True, ref=ref)
    return n

bic("SVID1703C011", [(str(i), n) for i, n in zip(range(1, 29),
    ["EO1", "EO2", "CE", "PSC", "X1", "X2", "SD", "MUT", "D1", "D2", "D3", "D4", "D5", "VDD",
     "g", "f", "e", "d", "c", "b", "a", "K3", "K2", "K1", "K0", "FM", "GND", "AM"])],
    "IC901 SVID1703C011  PLL / display / teclado")
FLP = ["F", "d", "FM/DP", "G7", "AM", "kHz", "G6", "MEM", "a", "G5", "b", "f", "G4", "G7b",
       "g", "G3", "c", "e", "f2", "G1,2", "g2", "a2", "MHz", "F"]
bic("SAD7BT05A", [(str(i + 1), FLP[i]) for i in range(24)], "Tubo VFD SAD7BT05A", ref="FL")
bic("RN8", [("1", "COM")] + [(str(i), str(i)) for i in range(2, 9)], "100k x7", ref="Z")
bic("RN6", [("1", "COM")] + [(str(i), str(i)) for i in range(2, 7)], "100k x5", ref="Z")
bic("CN8", [("1", "GND")] + [(str(i), str(i)) for i in range(2, 9)], "330p x7", ref="Z")
bic("CN6", [("1", "GND")] + [(str(i), str(i)) for i in range(2, 7)], "330p x5", ref="Z")

# ------------------------------------------------------------------ redes
S = {"Sa": "d_P27", "Sb": "c_P30", "Sc": "e_P31", "Sd": "f_P28", "Se": "g_P32", "Sf": "b_P29", "Sg": "a_P33"}
K = {0: "K0_P37", 1: "K1_P36", 2: "K2_P35", 3: "K3_P34"}
G = {g: f"REJ_{g}_P{p}" for g, p in [("G7", 18), ("G3", 19), ("G4", 20), ("G5", 21), ("G6", 22)]}
NEG = "@-21V4"

TOP = [  # (sym, ref, value, conns)
    ("SVID1703C011", "IC901", "SVID1703C011", {
        "1": "@EO1_FILTRO_LAZO", "2": "@EO2_FILTRO_LAZO", "3": "@CE", "4": "@PSC_IC902", "5": "XTAL_X1",
        "6": "XTAL_X2", "7": "@SD_ESTEREO", "8": "@MUTE", "9": "DIG_D1", "10": "DIG_D2", "11": "DIG_D3",
        "12": "DIG_D4", "13": "DIG_D5", "14": "VDD_5V", "15": "g_P32", "16": "f_P28", "17": "e_P31",
        "18": "d_P27", "19": "c_P30", "20": "b_P29", "21": "a_P33", "22": K[3], "23": K[2], "24": K[1],
        "25": K[0], "26": "@FM_IN_C915", "27": "GND", "28": "@AM_OSC_IN"}),
    ("RN6", "Z903", "100k x5", {"1": NEG, "2": G["G6"], "3": G["G5"], "4": G["G4"], "5": G["G3"], "6": G["G7"]}),
    ("CN6", "Z904", "330p x5", {"1": "GND", "2": G["G6"], "3": G["G5"], "4": G["G4"], "5": G["G3"], "6": G["G7"]}),
    ("SAD7BT05A", "FL1", "SAD7BT05A", {str(k): v for k, v in {
        1: "@FIL_B_P23", 2: S["Sa"], 3: S["Sb"], 4: G["G7"], 5: S["Sc"], 6: S["Sc"], 7: G["G6"], 8: S["Sf"],
        9: S["Sg"], 10: G["G5"], 11: S["Sf"], 12: S["Sd"], 13: G["G4"], 14: G["G7"], 15: S["Se"], 16: G["G3"],
        17: S["Sb"], 18: S["Sc"], 19: S["Sd"], 20: G["G7"], 21: S["Se"], 22: S["Sg"], 23: S["Sb"],
        24: "@FIL_A_P17"}.items()}),
    ("RN8", "Z902", "100k x7", {"1": NEG, "2": S["Sa"], "3": S["Sd"], "4": S["Sf"], "5": S["Sb"], "6": S["Sc"], "7": S["Se"], "8": S["Sg"]}),
    ("CN8", "Z901", "330p x7", {"1": "GND", "2": S["Sa"], "3": S["Sd"], "4": S["Sf"], "5": S["Sb"], "6": S["Sc"], "7": S["Se"], "8": S["Sg"]}),
]
def t2(sym, ref, val, a, b): return (sym, ref, val, {"1": a, "2": b})
MID = [
    t2("XTAL", "X901", "4.5MHz", "XTAL_X1", "XTAL_X2"),
    t2("C", "C913", "15p", "XTAL_X1", "GND"),
    t2("C", "C914", "15p", "XTAL_X2", "GND"),
    t2("D", "D901", "MA150", "@+B_5V6", "VDD_5V"),
    t2("C", "C903", "0.01u", "VDD_5V", "GND"),
    t2("CP", "C902", "1000u", "VDD_5V", "GND"),
    t2("R", "R901", "680", "VDD_5V", "VBACKUP"),
    t2("CP", "C905", "3.3F", "VBACKUP", "VB1"),
    t2("CP", "C906", "3.3F", "VB1", "VB2"),
    t2("CP", "C907", "3.3F", "VB2", "GND"),
    "gap",
    t2("D", "D921", "MA150", "@+B_5V6", "VFL_DRV"),
    t2("CP", "C904", "330u", "VFL_DRV", "GND"),
]
for q, r, d, g in [("Q905", "R913", "DIG_D1", "G7"), ("Q907", "R915", "DIG_D2", "G3"), ("Q906", "R914", "DIG_D3", "G4"),
                   ("Q908", "R916", "DIG_D4", "G5"), ("Q909", "R917", "DIG_D5", "G6")]:
    MID.append(t2("R", r, "10k", d, f"BASE_{q}"))
    MID.append(("Q_PNP", q, "2SA733", {"B": f"BASE_{q}", "E": "VFL_DRV", "C": G[g]}))
MID += ["gap", t2("C", "C918", "0.01u", "@FIL_B_P23", "GND"), "gap",
        t2("D", "D910", "MA150", S["Sb"], "FILA_1"),
        t2("D", "D911", "MA150", S["Sf"], "FILA_2"),
        t2("D", "D912", "MA150", "a_P33", "FILA_3")]
for s, nm, a, b in [("S7", "MEMO", "FILA_3", "COL_D908"), ("S8", "DOWN", "FILA_3", "COL_D906"),
                    ("S9", "UP", "FILA_3", "COL_D907"), ("S10", "CH1", "FILA_2", "COL_D909"),
                    ("S11", "CH2", "FILA_2", "COL_D908"), ("S12", "CH3", "FILA_2", "COL_D907"),
                    ("S13", "CH4", "FILA_2", "COL_D906"), ("S14", "CH5", "FILA_1", "COL_D909"),
                    ("S15", "CH6", "FILA_1", "COL_D908")]:
    MID.append(t2("SW_PUSH", s, nm, a, b))
for d, k in [("D906", 0), ("D907", 1), ("D908", 2), ("D909", 3)]:
    MID.append(t2("D", d, "MA150", f"COL_{d}", K[k]))
MID += [t2("D", "D924", "MA150", S["Sc"], K[0]), t2("D", "D925", "MA150", S["Sd"], K[3]),
        t2("D", "D919", "MA150", S["Se"], K[2]), t2("D", "D920", "MA150", S["Se"], K[3]),
        t2("D", "D916", "MA150", "g_P32", "S16_COM_P73"),
        ("SW_SPDT", "S16", "FM/AM ALLOC", {"2": "S16_COM_P73", "1": K[1], "3": K[0]})]

# ------------------------------------------------------------------ colocación
items, pins_at = [], []   # pins_at: (net, x, y, canal)
pwr = [0]
def sym_inst(sym, ref, val, x, y, rx, ry, vx, vy, hide_ref=False):
    _, pins = SYMS[sym]
    pu = " ".join(f'(pin "{p}" (uuid {U()}))' for p in pins)
    rh = FH if hide_ref else '(effects (font (size 1.27 1.27)) (justify left))'
    items.append(f'(symbol (lib_id "STC04:{sym}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {U()})\n'
                 f' (property "Reference" "{ref}" (at {rx} {ry} 0) {rh})\n'
                 f' (property "Value" "{val}" (at {vx} {vy} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
                 f' (property "Footprint" "" (at {x} {y} 0) {FH}) (property "Datasheet" "" (at {x} {y} 0) {FH})\n {pu}\n'
                 f' (instances (project "ST-C04_display_teclado" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
def gnd(x, y):
    pwr[0] += 1
    sym_inst("GND", f"#PWR{pwr[0]:03d}", "GND", x, y, x, y + 4, x - 2, y + 4.2, hide_ref=True)

def place(sym, ref, val, x, y, conns, top_row):
    _, pins = SYMS[sym]
    if top_row:
        h = 15.24
        sym_inst(sym, ref, val, x, y, r3(x - 1.27), r3(y - h / 2 - 1.5), r3(x - 1.27), r3(y + h / 2 + 7.0))
    else:
        sym_inst(sym, ref, val, x, y, r3(x + 3.3), r3(y - 0.5), r3(x + 3.3), r3(y + 1.6))
    for p, (px, py) in pins.items():
        n = conns.get(p)
        cx, cy = r3(x + px), r3(y - py)
        if n is None:
            continue
        if n == "GND":
            gnd(cx, cy)
            continue
        ch = "U" if (top_row or py > 0) else "L"
        pins_at.append((n, cx, cy, ch))

YT = 90.17                      # fin de pines de la fila superior
x = 50.8
for sym, ref, val, conns in TOP:
    n = len(SYMS[sym][1])
    place(sym, ref, val, x, r3(YT - 7.62 - 5.08), conns, True)
    x = r3(x + n * 2.54 + 25.4)
TOP_END = x

# canal U: se calcula después; fila media a una altura provisional
mid_x = []
xm = 52.07
for it in MID:
    if it == "gap":
        xm = r3(xm + 5.08)
        continue
    mid_x.append((it, xm))
    xm = r3(xm + 12.7)
MID_END = xm

# ------------------------------------------------------------------ enrutado
def nets_of(ch):
    d = {}
    for n, px, py, c in pins_at:
        if c == ch:
            d.setdefault(n, []).append(px)
    return d

# colocar la fila media una vez conocida la altura del canal U: primero contar redes
top_nets = {}
for n, px, py, c in pins_at:
    top_nets.setdefault(n, []).append(px)
# pines de la fila media (posiciones relativas: arriba = y-5.08, abajo = y+5.08)
mid_pins = []
for (sym, ref, val, conns), cx in mid_x:
    for p, (px, py) in SYMS[sym][1].items():
        n = conns.get(p)
        if n is None or n == "GND":
            continue
        mid_pins.append((n, r3(cx + px), "U" if py > 0 else "L"))

U_nets, L_nets = {}, {}
for n, xs in top_nets.items():
    U_nets.setdefault(n, []).extend(xs)
for n, px, ch in mid_pins:
    (U_nets if ch == "U" else L_nets).setdefault(n, []).append(px)

# columnas libres para "risers" entre la fila media (x = centro + 5.08)
free_cols = []
for (it, cx) in mid_x:
    free_cols.append(r3(cx + 7.62))
used_x = {r3(px) for n, px, ch in mid_pins} | {r3(v) for xs in top_nets.values() for v in xs}
free_cols = [c for c in free_cols if c not in used_x]
risers = {}
for n in sorted(set(U_nets) & set(L_nets)):
    allx = U_nets[n] + L_nets[n]
    cen = sum(allx) / len(allx)
    c = min(free_cols, key=lambda v: abs(v - cen))
    free_cols.remove(c)
    risers[n] = c
    U_nets[n].append(c)
    L_nets[n].append(c)

XLEFT = 30.48
def levels(nets):
    """Asigna un nivel (fila) por red en el canal; redes sin solape comparten nivel."""
    spans = []
    for n, xs in nets.items():
        ext = n.startswith("@")
        lo = XLEFT if ext else min(xs)
        hi = max(xs)
        if len(xs) < 2 and not ext:
            continue
        spans.append((lo, hi, n))
    spans.sort()
    lv_end, assign = [], {}
    for lo, hi, n in spans:
        lab = len(n.lstrip("@")) * 1.27 + 3
        for i, e in enumerate(lv_end):
            if lo > e + 2.54 and not n.startswith("@"):
                lv_end[i] = max(hi, lo + lab); assign[n] = i; break
        else:
            lv_end.append(max(hi, lo + lab)); assign[n] = len(lv_end) - 1
    return assign, len(lv_end)

Ua, Un = levels(U_nets)
La, Ln = levels(L_nets)
YU0 = r3(YT + 7.62)
yU = lambda i: r3(YU0 + i * 3.81)
YM = r3(yU(Un) + 7.62 + 5.08)          # centro de la fila media
YMB = r3(YM + 5.08)                       # fin de pines inferiores
YL0 = r3(YMB + 10.16)
yL = lambda i: r3(YL0 + i * 3.81)

for (sym, ref, val, conns), cx in mid_x:
    place(sym, ref, val, cx, YM, conns, False)

def wire(x1, y1, x2, y2):
    if (x1, y1) != (x2, y2):
        items.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid {U()}))')
def junction(x, y):
    items.append(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
def label(n, x, y, glob=False, ang=0):
    if glob:
        items.append(f'(global_label "{n}" (shape passive) (at {x} {y} 180) (fields_autoplaced) '
                     f'(effects (font (size 1.27 1.27)) (justify right)) (uuid {U()}) '
                     f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) {FH}))')
    else:
        items.append(f'(label "{n}" (at {x} {y} {ang}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {U()}))')

def route(nets, assign, yfun, ch):
    for n, xs in nets.items():
        drops = []  # (x, y_from)
        for nn, px, py, c in pins_at:
            if nn == n and c == ch:
                drops.append((px, py))
        ext = n.startswith("@")
        name = n.lstrip("@")
        if n not in assign:            # red de un solo pin sin track
            px, py = drops[0]
            label(name, px, py, ang=270 if ch == "L" else 90)
            continue
        yt = yfun(assign[n])
        pts = sorted({r3(px) for px, _ in drops} | ({risers[n]} if n in risers else set()) | ({XLEFT} if ext else set()))
        for a, b in zip(pts, pts[1:]):
            wire(a, yt, b, yt)
        for px, py in drops:
            wire(px, py, px, yt)
        deg = {}
        for p in pts:
            deg[p] = (p != pts[0]) + (p != pts[-1]) + (0 if (ext and p == XLEFT) else 1)
        if n in risers:
            deg[risers[n]] = (risers[n] != pts[0]) + (risers[n] != pts[-1]) + 1
        for p, d in deg.items():
            if d >= 3:
                junction(p, yt)
        if ext:
            label(name, XLEFT, yt, glob=True)
        else:
            label(name, r3(pts[0] + 0.635), yt)
    if ch == "L":
        for n, c in risers.items():
            wire(c, yU(Ua[n]), c, yL(La[n]))

route(U_nets, Ua, yU, "U")
route(L_nets, La, yL, "L")

# ------------------------------------------------------------------ textos
def text(t, x, y, size=1.5, bold=False):
    b = " bold" if bold else ""
    items.append(f'(text "{t}" (at {x} {y} 0) (effects (font (size {size} {size}){b}) (justify left top)) (uuid {U()}))')
text("Technics ST-C04 - Controlador PLL (IC901), display VFD y teclado", 20.32, 14, 3, True)
text("Reconstruido del manual de servicio SD81061918C1 (págs. 11-15). Sufijo _Pnn = número de conexión entre placas del original. "
     "Los cruces sin punto NO están conectados.", 20.32, 21, 1.5)
yn = r3(yL(Ln) + 12)
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
    text(n, 20.32, r3(yn + i * 5), 1.5, i == 0)

W = max(TOP_END, MID_END) + 20
H = yn + len(notes) * 5 + 15
W, H = int(W) + 10, int(H) + 10
paper = f'"User" {W} {H}'
lib = "\n".join(v[0] for v in SYMS.values())
out = (f'(kicad_sch (version 20230121) (generator eeschema)\n(uuid {ROOT})\n(paper {paper})\n'
       f'(title_block (title "ST-C04 - PLL, display y teclado (cables dibujados)") (company "Reconstrucción desde manual Technics") (rev "2"))\n'
       f'(lib_symbols\n{lib}\n)\n' + "\n".join(items) + '\n(sheet_instances (path "/" (page "1")))\n)\n')
open(sys.argv[1], "w").write(out)
print("papel", paper, "W", W, "H", H, "niveles U", Un, "L", Ln, "risers", len(risers))
