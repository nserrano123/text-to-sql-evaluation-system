#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisis de la evaluacion MULTITURNO (config [Rag],[Memoria],[Intension],[Din],[Dea]).

Entradas:
  - analisis_pruebas/multiturn_run/resumen_metricas.json (corrida real consolidada)
  - analisis_pruebas/preguntas_multiturno.csv (diseño: accion esperada, tipo de turno)

Salidas:
  - analisis_pruebas/figs/fig7_gating.png
  - analisis_pruebas/figs/fig8_tsr_tipo.png
  - analisis_pruebas/figs/fig9_contexto.png
  - analisis_pruebas/analisis_multiturno.md
"""

import os, csv, json
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
AP = os.path.join(BASE, "analisis_pruebas")
FIGS = os.path.join(AP, "figs")
os.makedirs(FIGS, exist_ok=True)

# paleta (validada con el validador dataviz; WARN de contraste cubierto con
# etiquetas directas sobre/junto a cada marca)
C_BLUE, C_YELLOW, C_MAGENTA = "#2a78d6", "#eda100", "#e87ba4"
C_AQUA, C_ORANGE = "#1baf7a", "#eb6834"
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

ACTIONS = ["EXECUTE_SQL", "NO_SQL", "CLARIFY"]
ACT_COLOR = {"EXECUTE_SQL": C_BLUE, "NO_SQL": C_YELLOW, "CLARIFY": C_MAGENTA}
ACT_LABEL = {"EXECUTE_SQL": "Ejecutó SQL", "NO_SQL": "Conversacional",
             "CLARIFY": "Pidió aclaración"}

TYPE_GROUP = {"seed_sql": "Inicial (semilla)", "switch_sql": "Cambio de tema"}


def type_group(t):
    if t in TYPE_GROUP:
        return TYPE_GROUP[t]
    if t.startswith("ctx_"):
        return "Seguimiento contextual"
    if t.startswith("ns_"):
        return "Conversacional (no SQL)"
    return "Ambiguo (aclaración)"


def load():
    run = {r["excel_id"]: r for r in json.load(
        open(os.path.join(AP, "multiturn_run", "resumen_metricas.json"),
             encoding="utf-8"))}
    design = list(csv.DictReader(
        open(os.path.join(AP, "preguntas_multiturno.csv"), encoding="utf-8-sig")))
    # turnos diseñados por sesion -> para saber que conversaciones estan completas
    designed = defaultdict(set)
    for d in design:
        designed[d["session_id"]].add(int(d["turn_index"]))
    have = defaultdict(set)
    for d in design:
        if int(d["excel_id"]) in run:
            have[d["session_id"]].add(int(d["turn_index"]))
    complete_sessions = {s for s in designed if have[s] >= designed[s]}
    rows = []
    for d in design:
        rid = int(d["excel_id"])
        r = run.get(rid)
        if not r:
            continue
        rows.append({
            "id": rid, "session": d["session_id"], "turn": int(d["turn_index"]),
            "expected": d["expected_action"], "ttype": d["turn_type"],
            "group": type_group(d["turn_type"]),
            "actual": r["action"], "ex": r.get("ex"),
            "cm": r.get("cm_f1"), "errors": r.get("errors", 0),
            "session_complete": d["session_id"] in complete_sessions,
        })
    return rows, complete_sessions


def pct(x):
    return f"{x*100:.1f} %".replace(".", ",")


def fig_gating(rows):
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    ys = list(reversed(ACTIONS))
    for yi, exp in enumerate(ys):
        sub = [r for r in rows if r["expected"] == exp]
        n = len(sub)
        left = 0.0
        for act in ACTIONS:
            p = sum(1 for r in sub if r["actual"] == act) / n * 100 if n else 0
            if p == 0:
                continue
            ax.barh(yi, p, left=left, color=ACT_COLOR[act], height=0.62,
                    edgecolor=SURF, linewidth=2, zorder=3)
            if p >= 6:
                ax.text(left + p / 2, yi, f"{p:.0f}%", ha="center", va="center",
                        color="white" if act == "EXECUTE_SQL" else INK,
                        fontsize=10, fontweight="bold")
            left += p
        ax.text(101, yi, f"n={n}", va="center", fontsize=9, color=INK2)
    ax.set_yticks(range(len(ys)))
    ax.set_yticklabels([f"Esperado:\n{ACT_LABEL[a]}" for a in ys], fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Decisión del sistema (% de turnos)")
    ax.set_title("Gating de intención: decisión real vs. esperada por tipo de turno",
                 loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=ACT_COLOR[a], label=ACT_LABEL[a])
                       for a in ACTIONS],
              loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3,
              frameon=False, fontsize=9.5)
    fig.savefig(os.path.join(FIGS, "fig7_gating.png"))
    plt.close(fig)


def tsr_hit(r):
    """TSR segun la formula del dataset: SQL esperado y SQL ejecutado coinciden
    en presencia/ausencia."""
    expected_sql = r["expected"] == "EXECUTE_SQL"
    did_sql = r["actual"] == "EXECUTE_SQL"
    return expected_sql == did_sql


def fig_tsr(rows):
    groups = ["Inicial (semilla)", "Cambio de tema", "Seguimiento contextual",
              "Conversacional (no SQL)", "Ambiguo (aclaración)"]
    vals, ns = [], []
    for g in groups:
        sub = [r for r in rows if r["group"] == g]
        ns.append(len(sub))
        vals.append(sum(tsr_hit(r) for r in sub) / len(sub) * 100 if sub else 0)
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    bars = ax.barh(range(len(groups))[::-1], vals, color=C_BLUE, height=0.6,
                   zorder=3)
    for yi, (v, n) in zip(range(len(groups))[::-1], zip(vals, ns)):
        ax.text(v + 1.2, yi, f"{v:.1f}%  (n={n})", va="center", fontsize=9.5,
                color=INK2)
    ax.set_yticks(range(len(groups))[::-1])
    ax.set_yticklabels(groups, fontsize=10)
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Task Success Rate (%)")
    ax.set_title("TSR por tipo de turno (decisión correcta de ejecutar o no ejecutar SQL)",
                 loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="y", visible=False)
    fig.savefig(os.path.join(FIGS, "fig8_tsr_tipo.png"))
    plt.close(fig)


def cm_avg(r):
    if not r["cm"]:
        return None
    ks = ["select", "where", "group_by", "keywords"]
    return sum(r["cm"].get(k, 0) for k in ks) / len(ks)


def fig_contexto(rows):
    cats = [("Inicial (semilla)", ["Inicial (semilla)", "Cambio de tema"]),
            ("Seguimiento contextual", ["Seguimiento contextual"])]
    ex_vals, cm_vals, ns = [], [], []
    for _, gs in cats:
        sub = [r for r in rows if r["group"] in gs and r["ex"] is not None]
        ns.append(len(sub))
        ex_vals.append(sum(r["ex"] for r in sub) / len(sub) * 100 if sub else 0)
        cms = [cm_avg(r) for r in sub if cm_avg(r) is not None]
        cm_vals.append(sum(cms) / len(cms) * 100 if cms else 0)
    x = range(len(cats))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    b1 = ax.bar([i - w / 2 for i in x], cm_vals, w, color=C_AQUA,
                edgecolor=SURF, linewidth=2, zorder=3, label="Component Matching (F1)")
    b2 = ax.bar([i + w / 2 for i in x], ex_vals, w, color=C_BLUE,
                edgecolor=SURF, linewidth=2, zorder=3, label="Execution Accuracy")
    for bars, vals in ((b1, cm_vals), (b2, ex_vals)):
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}%",
                    ha="center", fontsize=10, color=INK)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{c[0]}\n(n={n})" for c, n in zip(cats, ns)])
    ax.set_ylim(0, 110)
    ax.set_ylabel("%")
    ax.set_title("Calidad del SQL en turnos iniciales vs. seguimientos con memoria",
                 loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="lower right", fontsize=9.5)
    fig.savefig(os.path.join(FIGS, "fig9_contexto.png"))
    plt.close(fig)


def main():
    rows, complete_sessions = load()
    n = len(rows)
    print("Turnos analizados:", n)

    gate_ok = sum(1 for r in rows if r["actual"] == r["expected"])
    tsr = sum(tsr_hit(r) for r in rows)
    false_exec = sum(1 for r in rows
                     if r["expected"] != "EXECUTE_SQL" and r["actual"] == "EXECUTE_SQL")
    false_abst = sum(1 for r in rows
                     if r["expected"] == "EXECUTE_SQL" and r["actual"] != "EXECUTE_SQL")
    no_exec_n = sum(1 for r in rows if r["expected"] != "EXECUTE_SQL")
    exec_n = n - no_exec_n

    sql_rows = [r for r in rows if r["ex"] is not None]
    ex_rate = sum(r["ex"] for r in sql_rows) / len(sql_rows) if sql_rows else 0
    ctx = [r for r in sql_rows if r["group"] == "Seguimiento contextual"]
    ini = [r for r in sql_rows if r["group"] in ("Inicial (semilla)", "Cambio de tema")]
    ex_ctx = sum(r["ex"] for r in ctx) / len(ctx) if ctx else 0
    ex_ini = sum(r["ex"] for r in ini) / len(ini) if ini else 0
    first_try = sum(1 for r in sql_rows if r["errors"] == 0) / len(sql_rows) if sql_rows else 0

    # exito por conversacion (turno correcto = gating ok y, si aplica EX, ex=1)
    # SOLO sobre conversaciones completas
    conv = defaultdict(list)
    for r in rows:
        if not r["session_complete"]:
            continue
        ok = (r["actual"] == r["expected"]) and (r["ex"] != 0 if r["ex"] is not None else True)
        conv[r["session"]].append(ok)
    dsr = sum(1 for v in conv.values() if all(v)) / len(conv) if conv else 0

    fig_gating(rows)
    fig_tsr(rows)
    fig_contexto(rows)
    print("figuras -> figs/fig7_gating.png, fig8_tsr_tipo.png, fig9_contexto.png")

    L = []
    A = L.append
    A("# Evaluación multiturno — RAG+Memoria+Intención+DIN+DEA\n")
    A(f"Corrida real sobre **{len(complete_sessions)} conversaciones completas** "
      f"({n} turnos evaluados) contra la BD de prueba, con memoria conversacional "
      "persistente. Métricas por conversación (DSR) calculadas solo sobre "
      "conversaciones completas; métricas por turno sobre todos los turnos con "
      "resultado.\n")
    A("## Métricas globales\n")
    A(f"- **Gating accuracy** (decisión exacta EXECUTE_SQL/NO_SQL/CLARIFY): **{pct(gate_ok/n)}**")
    A(f"- **Task Success Rate** (ejecutar SQL exactamente cuando corresponde): **{pct(tsr/n)}**")
    A(f"- **False-execute** (ejecutó SQL cuando no debía): {pct(false_exec/no_exec_n)} "
      f"({false_exec}/{no_exec_n})")
    A(f"- **False-abstain** (no ejecutó cuando debía): {pct(false_abst/exec_n)} "
      f"({false_abst}/{exec_n})")
    A(f"- **Execution Accuracy global** (turnos con SQL de oro): {pct(ex_rate)}")
    A(f"  - En turnos iniciales: {pct(ex_ini)} (n={len(ini)})")
    A(f"  - En seguimientos contextuales (requieren memoria): {pct(ex_ctx)} (n={len(ctx)})")
    A(f"- **Correcto al primer intento** (sin autocorrección): {pct(first_try)}")
    A(f"- **Dialogue Success Rate** (conversaciones con TODOS los turnos correctos): {pct(dsr)}\n")
    A("![Gating](figs/fig7_gating.png)\n")
    A("![TSR por tipo](figs/fig8_tsr_tipo.png)\n")
    A("![Contexto](figs/fig9_contexto.png)\n")
    open(os.path.join(AP, "analisis_multiturno.md"), "w",
         encoding="utf-8").write("\n".join(L))
    print("markdown -> analisis_pruebas/analisis_multiturno.md")
    print(json.dumps({"gating": gate_ok/n, "tsr": tsr/n, "ex": ex_rate,
                      "ex_ctx": ex_ctx, "ex_ini": ex_ini, "dsr": dsr,
                      "first_try": first_try}, indent=1))


if __name__ == "__main__":
    main()
