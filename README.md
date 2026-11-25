# Detección de fallas – Technics ST-C04

Herramientas para diagnosticar fallas en el display fluorescente (VFD) y el teclado del sintonizador **Technics ST-C04**. La sección del controlador PLL **µPD1703C-011 (IC901, SVID1703C011)** maneja a la vez el display y la matriz de teclas, así que una misma falla suele afectar las dos cosas.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `simulador/` | `index.html`: simulador interactivo del display y el teclado. Se abre directamente en el navegador, sin instalar nada. |
| `kicad/` | Esquemáticos KiCad 7+ de la sección PLL/display/teclado: versión con cables dibujados (`_cables`) y versión con etiquetas de red, más sus PDF y la lista de redes (`_redes.txt`). |
| `scripts/` | Scripts en Python que generan los dos esquemáticos a partir del netlist reconstruido. |

## Simulador

- Barrido real del µPD1703C: 5 ranuras de dígito (D1–D5) por Q905–Q909, y 7 líneas de segmento a–g con drenador abierto y pull-down a −21,4 V (Z902).
- Teclas operables: UP/DOWN (manteniendo más de 0,5 s recorre la banda), MEMO + CH1–CH6, banda FM/AM, búsqueda automática y encendido.
- Fallas combinables:
  - líneas de segmento: cortada, a masa, pegada en alto, Z902 abierta, corto entre líneas;
  - drivers de rejilla: transistor abierto o en corto, Z903 abierta;
  - teclas: trabada, con fuga, sin contacto; diodos de la matriz abiertos o en corto;
  - configuración: S16, D924, D919/D920;
  - alimentación: falta de −21,4 V, filamento abierto, IC sin 5 V, supercondensadores agotados.
- Diagnóstico en texto, tabla de niveles por ranura (lo que se vería con el osciloscopio), lectura de la matriz y modo de barrido lento.

## Líneas de segmento y teclado

Cada línea de segmento también es un estrobo de la matriz de teclas. Si una línea falla, falta ese segmento en el display y además dejan de funcionar las teclas o funciones de esa misma línea.

| Línea | Pin IC901 | Punto | En el display | Teclas y funciones en esa línea |
|---|---|---|---|---|
| a | 21 | P33 | segmento a | DOWN, UP, MEMO (D912) |
| b | 20 | P29 | segmento b, MEMORY | CH1–CH4 (D911) |
| c | 19 | P30 | segmento c, FM, MHz, punto decimal | CH5, CH6 (D910) |
| d | 18 | P27 | segmento d | ninguna |
| e | 17 | P31 | segmento e, AM, kHz | 108/104 (D924); AUTO y AM/FM (S3/S2 en placa F, vía D929/D928) |
| f | 16 | P28 | segmento f | B2: paso de AM (D925) |
| g | 15 | P32 | segmento g | B0/B1: región (S16, D916); IF0/IF1 (D920/D919) |

Los dígitos se reparten así:

| Salida | Driver | Rejilla | Qué enciende |
|---|---|---|---|
| D1 | Q905 | G7 + G1,2 | indicadores FM/AM/MHz/kHz/MEMORY y el último dígito (solo 0 o 5) |
| D2 | Q907 | G3 | dígito completo |
| D3 | Q906 | G4 | dígito completo |
| D4 | Q908 | G5 | dígito completo |
| D5 | Q909 | G6 | el "1" inicial |

## Rango del filtro cerámico (D919/D920)

| Color de CF101/CF102 | D919 (IF1) | D920 (IF0) | FI programada |
|---|---|---|---|
| Rojo | no | no | 10,700 MHz |
| Naranja | sí | sí | 10,675 MHz |
| Azul | no | sí | 10,725 MHz |

## Fuentes y supuestos

- Reconstruido del manual de servicio Technics ST-C04 (Order No. SD81061918C1) y del datasheet NEC µPD1703C-011. Esos documentos no se incluyen en el repositorio.
- En el dibujo original, la línea del segmento "a" aparece unida al común de Z902; es un error de dibujo y va a P33 / Z902-8.
- El orden de pines de Z901 es aproximado.
- D925 (B2) figura montado en el dibujo del manual. Según el datasheet, eso da AM de 522–1611 kHz con paso de 9 kHz en modo EE.UU., en contra del rótulo "AM 10 kHz" de S16. Hay que verificar en la placa si está montado.
- Supuestos del simulador:
  - Con dos teclas apretadas a la vez, el IC ignora ambas.
  - AUTO y AM/FM se leen por la línea e, según el datasheet; la placa F no está rastreada.
  - D925 arranca sin montar, para que el paso de AM en EE.UU. sea de 10 kHz; se puede montar desde el panel de fallas.
  - Las emisoras son de ejemplo.

## Regenerar los esquemáticos

```bash
python3 scripts/gen_esquema_cables.py kicad/ST-C04_display_teclado_cables.kicad_sch
python3 scripts/gen_esquema_etiquetas.py kicad/ST-C04_display_teclado.kicad_sch
```
