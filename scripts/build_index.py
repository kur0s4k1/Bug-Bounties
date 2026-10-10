#!/usr/bin/env python3
"""
build_index.py — Genera el README.md del repositorio Bug-Bounties
a partir de data/findings.csv.

Uso:
    python3 scripts/build_index.py

Recomendaciones de divulgación responsable:
    Por defecto, la columna "Activo" se sanea (se conserva solo el host y se
    enmascara cualquier ruta, query o fragmento) para evitar publicar
    endpoints explotables de programas que aún no han autorizado su
    divulgación. Si un programa ya autorizó la publicación del endpoint
    completo, se puede cambiar SANITIZE_ASSET = False.
"""

import csv
import os
import unicodedata
from collections import Counter, OrderedDict
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
SANITIZE_ASSET = True          # Enmascara rutas/query del activo mostrado.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "findings.csv")
OUT_PATH = os.path.join(ROOT, "README.md")

# Orden de severidad
PRIORITY_ORDER = ["P1", "P2", "P3", "P4", "P5", "-"]
ESTADO_ORDER = ["Aceptado", "En analisis", "Duplicado", "No Aplica"]
TIPO_ORDER = ["Web App", "Source Code", "Otro"]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def slug(text: str) -> str:
    """Convierte un texto en un ancla de Markdown ASCII."""
    norm = unicodedata.normalize("NFKD", text)
    norm = norm.encode("ascii", "ignore").decode("ascii").lower()
    out = []
    for ch in norm:
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_/":
            out.append("-")
    anchor = "".join(out)
    while "--" in anchor:
        anchor = anchor.replace("--", "-")
    return anchor.strip("-")


def sanitize_asset(asset: str) -> str:
    """Conserva el host y enmascara rutas, query y fragmentos."""
    a = (asset or "").strip()
    if not a:
        return "—"
    # Recursos de código (paquetes/orgs), no URLs
    if not a.startswith("http://") and not a.startswith("https://"):
        return a
    scheme_split = a.split("://", 1)
    rest = scheme_split[1] if len(scheme_split) == 2 else a
    host = rest.split("/", 1)[0]
    path = rest[len(host):]
    # Enmascarar cualquier parte de la ruta / query existente
    if path and path not in ("/", ""):
        return host + "/…"
    return host


def parse_money(dinero: str):
    """Devuelve (monto_usd, es_valorizado).

    - '1.000 USD' -> (1000.0, True)  (punto = separador de miles)
    - '100 USD'   -> (100.0, True)
    - 'Reconocimiento' / 'N/A' / 'No Definido' -> (0.0, False)
    """
    d = (dinero or "").strip()
    if not d or "USD" not in d.upper():
        return 0.0, False
    num = ""
    for ch in d:
        if ch.isdigit() or ch == ".":
            num += ch
    if not num:
        return 0.0, False
    # Heurística: si 'X.YYY' con 3 decimales -> separador de miles
    if "." in num:
        entero, frac = num.rsplit(".", 1)
        if len(frac) == 3 and entero.isdigit():
            num = entero + frac
        else:
            num = entero + "." + frac
    try:
        return float(num), True
    except ValueError:
        return 0.0, False


def fmt_money(value: float) -> str:
    # Formato internacional: $1,425 (coma como separador de miles)
    return f"${value:,.0f}"


def money_cell(dinero: str) -> str:
    amount, valued = parse_money(dinero)
    if valued and amount > 0:
        return f"💵 {fmt_money(amount)}"
    d = (dinero or "").strip()
    if d in ("Reconocimiento",):
        return "🏅 Reconocimiento"
    return "—"


def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh)]
    clean = []
    for r in rows:
        if not (r.get("Hallazgo") or "").strip():
            continue
        clean.append(r)
    return clean


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------
def build_stats(rows):
    total = len(rows)
    by_estado = Counter((r["Estado"] or "").strip() for r in rows)
    by_prio = Counter((r["Prioridad"] or "").strip() for r in rows)
    by_tipo = Counter((r["Tipo"] or "").strip() for r in rows)

    earned = 0.0
    for r in rows:
        amt, valued = parse_money(r["Dinero"])
        if valued:
            earned += amt

    accepted = by_estado.get("Aceptado", 0)
    dup = by_estado.get("Duplicado", 0)

    lines = []
    lines.append("| Métrica | Valor |")
    lines.append("|:--|:--|")
    lines.append(f"| Hallazgos totales | **{total}** |")
    lines.append(f"| Aceptados / validados | **{accepted}** |")
    lines.append(f"| Duplicados | {dup} |")
    lines.append(f"| Recompensas acumuladas | **{fmt_money(earned)} USD** |")
    lines.append(f"| Programas (empresas) | {len(set((r['Empresa'] or '').strip() for r in rows))} |")
    by_vuln = Counter((r["Vulnerabilidad"] or "").strip() for r in rows)
    lines.append(f"| Clases de vulnerabilidad | {len(by_vuln)} |")
    lines.append("")
    return "\n".join(lines), earned, by_estado, by_prio, by_tipo, by_vuln


def build_breakdown(title, counter, order=None):
    items = list(counter.items())
    if order:
        items.sort(key=lambda kv: (order.index(kv[0]) if kv[0] in order else len(order),
                                   -kv[1]))
    else:
        items.sort(key=lambda kv: (-kv[1], kv[0]))
    total = sum(c for _, c in items) or 1
    lines = [f"**{title}**", "", "| Categoría | Nº | % |", "|:--|--:|--:|"]
    for name, count in items:
        pct = count / total * 100
        lines.append(f"| {name or '—'} | {count} | {pct:.0f}% |")
    lines.append("")
    return "\n".join(lines)


def build_table(rows):
    # Orden: severidad y luego fecha descendente
    def sort_key(r):
        p = (r["Prioridad"] or "-").strip()
        pi = PRIORITY_ORDER.index(p) if p in PRIORITY_ORDER else len(PRIORITY_ORDER)
        return (pi, r["Fecha"] or "")

    rows_sorted = sorted(rows, key=sort_key, reverse=False)

    lines = []
    lines.append("| # | Hallazgo | Empresa | Programa | Tipo | Vulnerabilidad | Prioridad | Estado | Fecha | Recompensa |")
    lines.append("|--:|:--|:--|:--|:--|:--|:--:|:--:|:--:|:--|")
    for i, r in enumerate(rows_sorted, 1):
        hallazgo = (r["Hallazgo"] or "").strip().replace("|", "\\|")
        empresa = (r["Empresa"] or "").strip()
        programa = (r["Programa"] or "").strip()
        tipo = (r["Tipo"] or "").strip()
        vuln = (r["Vulnerabilidad"] or "").strip()
        prio = (r["Prioridad"] or "—").strip()
        estado = (r["Estado"] or "").strip()
        fecha = (r["Fecha"] or "").strip()
        asset = sanitize_asset(r["Activo"]) if SANITIZE_ASSET else (r["Activo"] or "").strip()
        if asset and asset != "—":
            hallazgo = f"{hallazgo} <br>`{asset}`"
        cell = money_cell(r["Dinero"])
        lines.append(
            f"| {i} | {hallazgo} | {empresa} | {programa} | {tipo} | "
            f"{vuln} | {prio} | {estado} | {fecha} | {cell} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_by_company(rows):
    groups = {}
    for r in rows:
        key = (r["Empresa"] or "").strip()
        groups.setdefault(key, []).append(r)
    lines = []
    for empresa in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        items = groups[empresa]
        acc = sum(1 for x in items if (x["Estado"] or "").strip() == "Aceptado")
        earned = 0.0
        for x in items:
            amt, valued = parse_money(x["Dinero"])
            if valued:
                earned += amt
        badge = f"{len(items)} hallazgo(s)"
        if acc:
            badge += f" · {acc} aceptado(s)"
        money = f" · {fmt_money(earned)} USD" if earned > 0 else ""
        lines.append(f"<details><summary><b>{empresa}</b> — {badge}{money}</summary>")
        lines.append("")
        lines.append("| Hallazgo | Vulnerabilidad | Prioridad | Estado |")
        lines.append("|:--|:--|:--:|:--:|")
        for x in sorted(items, key=lambda r: r["Fecha"] or ""):
            h = (x["Hallazgo"] or "").strip().replace("|", "\\|")
            lines.append(
                f"| {h} | {x['Vulnerabilidad']} | {x['Prioridad']} | {x['Estado']} |"
            )
        lines.append("")
        lines.append("</details>")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------
HEADER = """<div align="center">

<img src="assets/banner.svg" width="100%" alt="Bug Bounty Research — kur0s4k1"/>

# 🎯 Bug Bounties — Vulnerability Research Portfolio

**Hallazgos reales de seguridad reportados a programas de Bugcrowd, HackerOne y VDP directos.**
Reporte responsable · CVEs · Hall of Fame · Recompensas.

[![Programs](https://img.shields.io/badge/Programas-Bugcrowd%20%7C%20HackerOne%20%7C%20VDP-2ea44f?style=for-the-badge)](https://github.com/kur0s4k1)
[![Hall of Fame](https://img.shields.io/badge/Hall%20of%20Fame-NASA%20%7C%20WHO%20%7C%20DHS%20%7C%20Harvard-1f6feb?style=for-the-badge)](https://github.com/kur0s4k1)
[![Writeups](https://img.shields.io/badge/Writeups-HackTheBox-9cf?style=for-the-badge&logo=hackthebox&logoColor=white)](https://github.com/kur0s4k1/HackTheBox-Writeups)

</div>

---

## 👤 Sobre este repositorio

Este repositorio documenta mi trabajo como **security researcher** en programas de
divulgación de vulnerabilidades. Cada entrada corresponde a un hallazgo reportado
a través de una plataforma (Bugcrowd, HackerOne) o un programa de divulgación
directa (VDP), con su empresa objetivo, programa, tipo, clase de vulnerabilidad,
prioridad, estado y —cuando aplica— la recompensa obtenida.

> ⚠️ **Divulgación responsable.** Los endpoints y detalles sensibles están
> deliberadamente **saneados** (se conserva el host y se enmascaran rutas,
> parámetros y payloads). Solo se publican detalles completos cuando el programa
> autoriza la divulgación o tras la resolución del reporte. Consulta
> [`DISCLOSURE.md`](DISCLOSURE.md).

---

## 📊 Resumen ejecutivo

<<STATS>>

<<TOPVULN>>

---

## 📈 Desglose

<<ESTADO>>

<<PRIO>>

<<TIPO>>

---

## 📁 Hallazgos

> Tabla resumida. La leyenda `host` indica el activo saneado. El detalle
> técnico cuando está autorizado vive en [`Findings/`](Findings/).

<<TABLE>>

---

## 🏢 Por programa / empresa

<<COMPANY>>

---

## 🗂️ Estructura del repositorio

```
Bug-Bounties/
├── data/
│   └── findings.csv          # Dataset canónico (una fila por hallazgo)
├── Findings/
│   └── TEMPLATE/             # Plantilla de writeup
├── scripts/
│   └── build_index.py        # Regenera este README desde el CSV
├── DISCLOSURE.md             # Política de divulgación responsable
└── README.md
```

Regenerar el índice tras editar el dataset:

```bash
python3 scripts/build_index.py
```

---

## 🔐 Timeline de CVEs y Hall of Fame

| Reconocimiento | Detalle |
|:--|:--|
| CVE-2026-48770 | Asignado |
| CVE-2026-46710 | Asignado |
| CVE-2026-71858 | Asignado |
| NASA · WHO · DHS · Harvard · Drexel · HPE | Hall of Fame |

---

<div align="center">

**Contacto / Portafolio**

[GitHub](https://github.com/kur0s4k1) · [HackTheBox Writeups](https://github.com/kur0s4k1/HackTheBox-Writeups) · [Perfil](https://github.com/kur0s4k1/kur0s4k1)

<sub>Generado automáticamente por <code>scripts/build_index.py</code> · Última actualización: <<DATE>></sub>

</div>
"""


def main():
    rows = load_rows()
    stats_md, earned, by_estado, by_prio, by_tipo, by_vuln = build_stats(rows)
    estado_md = build_breakdown("Por estado", by_estado, ESTADO_ORDER)
    prio_order = [p for p in PRIORITY_ORDER if p != "-"]
    prio_md = build_breakdown("Por prioridad (severidad)", by_prio, prio_order)
    tipo_md = build_breakdown("Por tipo de target", by_tipo, TIPO_ORDER)
    table_md = build_table(rows)
    company_md = build_by_company(rows)
    today = datetime.now().strftime("%d/%m/%Y")

    out = HEADER
    replacements = {
        "<<STATS>>": stats_md,
        "<<TOPVULN>>": build_top_vulns(by_vuln),
        "<<ESTADO>>": estado_md,
        "<<PRIO>>": prio_md,
        "<<TIPO>>": tipo_md,
        "<<TABLE>>": table_md,
        "<<COMPANY>>": company_md,
        "<<DATE>>": today,
    }
    for token, value in replacements.items():
        out = out.replace(token, value)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"[+] README generado: {OUT_PATH}")
    print(f"[+] Hallazgos: {len(rows)} | Recompensas: {fmt_money(earned)} USD")


def build_top_vulns(by_vuln):
    lines = ["**Top clases de vulnerabilidad**", "",
             "| Vulnerabilidad | Nº |", "|:--|--:|"]
    for name, count in by_vuln.most_common(10):
        lines.append(f"| {name or '—'} | {count} |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
