#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figuras de ranking COMPLETO (19 configuraciones) para la tesis, calculadas
sobre el subconjunto comun de 53 consultas gold (IDs 2..54) para que todas las
configuraciones sean comparables (misma muestra).

Salidas (nombres listos para \\includegraphics):
  - "Figura 5.2 - Ranking EX 19 configuraciones.png"
  - "Figura 5.4 - Ranking SIN AUTO 19 configuraciones.png"
"""
import os, statistics as st
import openpyxl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.patches import Patch

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "dataset_sql_40_med_complex.xlsx")
FOCUS = "[Rag],[Memoria],[Intension],[Din],[Dea]"

C_BLUE, C_GREEN, C_ORANGE = "#2a78d6", "#008300", "#eb6834"
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF,
    "axes.edgecolor": "#c9c7c2", "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": "#e4e2dd", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 11, "figure.dpi": 150, "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

LBL = {"Rag": "RAG", "Memoria": "Memoria", "Intension": "Intensión",
       "Din": "DIN", "Dea": "DEA"}


def label(p):
    return "+".join(LBL[t.strip("[]")] for t in p.split(","))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def errs(v):
    s = str(v).strip() if v is not None else ""
    if not s:
        return 0.0
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return 0.0


def load():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb["Medianas_y_Complejas"]
    it = ws.iter_rows(values_only=True)
    hdr = list(next(it))
    H = {h: i for i, h in enumerate(hdr)}
    rows = [r for r in it
            if r[H["chatInput"]] and str(r[H["EVALUADO"]]) == "1"]
    wb.close()
    # subconjunto comun: las 53 preguntas gold que TODAS las configuraciones
    # respondieron (se toman de un bloque de referencia de n=53)
    ref = [r for r in rows if r[H["Parametros"]] == "[Rag],[Din],[Dea]"]
    gold53 = {str(r[H["chatInput"]]).strip() for r in ref}
    assert len(gold53) == 53, f"referencia inesperada: {len(gold53)}"
    agg = {}
    for r in rows:
        q = str(r[H["chatInput"]]).strip()
        if q not in gold53:
            continue
        p = r[H["Parametros"]]
        d = agg.setdefault(p, {"ex": [], "sa": [], "qs": set()})
        if q in d["qs"]:
            continue                      # una fila por pregunta y config
        d["qs"].add(q)
        e = num(r[H["VAL_EXECUTION"]])
        if e is not None:
            d["ex"].append(e)
        d["sa"].append(1 if errs(r[H["N8nErrorsSql"]]) < 1 else 0)
    out = []
    for p, d in agg.items():
        out.append({"p": p, "label": label(p), "n": len(d["sa"]),
                    "ex": st.mean(d["ex"]) * 100 if d["ex"] else None,
                    "sa": st.mean(d["sa"]) * 100})
    return out


def ranking(data, key, title, xlabel, fname, best_label_note):
    data = sorted(data, key=lambda d: d[key])
    labels = [d["label"] for d in data]
    vals = [d[key] for d in data]
    vmax = max(vals)
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    colors = []
    for d in data:
        if d["p"] == FOCUS:
            colors.append(C_ORANGE)
        elif d[key] == vmax:
            colors.append(C_GREEN)
        else:
            colors.append(C_BLUE)
    bars = ax.barh(labels, vals, color=colors, height=0.68, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(v + 0.9, b.get_y() + b.get_height() / 2, f"{v:.1f}%",
                va="center", fontsize=8.6, color=INK2)
    for tick, d in zip(ax.get_yticklabels(), data):
        if d["p"] == FOCUS:
            tick.set_color(C_ORANGE)
            tick.set_fontweight("bold")
    ax.set_xlim(0, 104)
    ax.xaxis.set_major_formatter(PercentFormatter())
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.legend(handles=[Patch(color=C_GREEN, label=best_label_note),
                       Patch(color=C_ORANGE, label="Configuración completa (conversacional)")],
              frameon=False, loc="lower right", fontsize=8.6)
    fig.savefig(os.path.join(BASE, fname))
    plt.close(fig)
    print("figura ->", fname)


def main():
    data = load()
    print(f"configuraciones: {len(data)} (subconjunto comun de 53 gold)")
    ranking(data, "ex",
            "Execution Accuracy por configuración (53 consultas gold)",
            "Execution Accuracy",
            "Figura 5.2 - Ranking EX 19 configuraciones.png",
            "Mejor EX")
    ranking(data, "sa",
            "Generación correcta al primer intento por configuración (53 consultas gold)",
            "SIN_AUTO_CORRECCION",
            "Figura 5.4 - Ranking SIN AUTO 19 configuraciones.png",
            "Mejor primer intento")


if __name__ == "__main__":
    main()
