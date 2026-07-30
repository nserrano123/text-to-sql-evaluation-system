#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenera "Tabla Estado del Arte.png" (Tabla I de la tesis) con:
  - los años corregidos segun la bibliografia (DAIL-SQL 2024, GraphRAG 2025);
  - el numero de referencia [n] de cada trabajo (trazabilidad IEEE);
  - el mismo estilo matplotlib del resto de tablas del pipeline.

Los numeros [n] corresponden al orden de \\bibitem en tesis_text_to_sql.tex.
"""
import os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
INK, SURF = "#0b0b0b", "#fcfcfb"

ROWS = [
    ("2023", "DIN-SQL (Pourreza & Rafiei) [3]",
     "Descomposición + autocorrección (ICL)",
     "Descompone la tarea en subproblemas e integra autocorrección para mejorar desempeño sin fine-tuning.",
     "Reporta mejoras competitivas en Spider y BIRD (según ejecución).",
     "Alta: útil para prototipos rápidos y queries multi-paso."),
    ("2023", "ACT-SQL (Zhang et al.) [25]",
     "Auto-CoT (ICL)",
     "Genera automáticamente razonamientos tipo chain-of-thought para mejorar prompts y trazabilidad.",
     "Reporta SOTA en Spider dev entre métodos ICL.",
     "Alta: facilita depuración y auditoría de consultas."),
    ("2024", "DEA-SQL (Xie et al.) [14]",
     "Workflow modular + descomposición",
     "Enfoque tipo workflow para mejorar atención y resolución por etapas.",
     "Evidencia experimental en Findings ACL 2024 (mejoras sobre baselines).",
     "Alta: modularidad favorece escalabilidad en esquemas grandes."),
    ("2024", "CodeS (Li et al.) [17]",
     "Pre-entrenamiento SQL + adaptación",
     "Modelos open-source entrenados con corpus SQL y estrategias para schema linking/robustez.",
     "Reporta SOTA en múltiples benchmarks y diagnósticos.",
     "Media–alta: base sólida para dominios contables/financieros."),
    ("2024", "DAIL-SQL (Gao et al.) [22]",
     "Few-shot dinámico (ICL)",
     "Selección automática de demostraciones y estudio sistemático ICL+representación.",
     "Reporta actualización del leaderboard Spider (exec. acc.).",
     "Alta: útil en consultas recurrentes y catálogos estables ERP."),
    ("2024", "CHESS (Talaei et al.) [24]",
     "Recuperación + selección de esquema + generación",
     "Pipeline para eficiencia en BD complejas (recuperación contextual y selección).",
     "Reporta eficiencia y desempeño en escenarios complejos.",
     "Muy alta: diseñado para catálogos grandes (cientos de tablas)."),
    ("2024", "Knowledge-to-SQL / DELLM (Hong et al.) [21]",
     "Conocimiento experto + feedback DB",
     "Introduce un “Data Expert LLM” y aprendizaje por retroalimentación de BD para aportar conocimiento faltante (reglas, fórmulas).",
     "Evidencia en Findings ACL 2024 (Spider/BIRD).",
     "Muy alta: ERP depende de reglas de negocio y métricas derivadas."),
    ("2025", "MAC-SQL (Wang et al.) [16]",
     "Multi-agente (Selector– Decomposer–Refiner)",
     "Cooperación de agentes + herramientas de ejecución para refinar SQL iterativamente.",
     "Reporta SOTA en BIRD holdout test (exec. acc.).",
     "Muy alta: arquitectura afín a agentes en ERP (control y robustez)."),
    ("2025", "GraphRAG (Han et al.) [18]",
     "RAG con grafos",
     "Recuperación estructurada combinando contexto global-local con relaciones explícitas.",
     "Survey/estudio sistemático de GraphRAG.",
     "Alta: útil para grounding semántico de entidades y relaciones ERP."),
]

COLS = ["Año", "Trabajo / Modelo [ref.]", "Enfoque", "Aporte central",
        "Evidencia de SOTA reportada", "Aplicabilidad a ERP"]
WRAP = [4, 26, 28, 48, 38, 36]      # ancho de envoltura por columna (caracteres)
CW   = [0.045, 0.16, 0.16, 0.26, 0.20, 0.185]


def wrap_cell(text, width):
    return "\n".join(textwrap.wrap(text, width)) or text


def main():
    cells = [[wrap_cell(c, w) for c, w in zip(r, WRAP)] for r in ROWS]
    nlines = [max(c.count("\n") + 1 for c in row) for row in cells]
    total = sum(nlines)

    fig = plt.figure(figsize=(13.6, 0.21 * total + 0.9), facecolor=SURF)
    ax = fig.add_axes([0.004, 0.01, 0.992, 0.98])
    ax.axis("off")
    tbl = ax.table(cellText=cells, colLabels=COLS, cellLoc="left",
                   loc="center", colWidths=CW)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.6)
    HDR = 0.055
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#d7d5cf")
        cell.set_linewidth(0.6)
        cell.PAD = 0.015
        if r == 0:
            cell.set_facecolor("#eef2f6")
            cell.set_text_props(weight="bold", color=INK, ha="left")
            cell.set_height(HDR)
        else:
            cell.set_facecolor(SURF if r % 2 else "#f7f6f3")
            cell.set_text_props(color=INK, ha="left", va="center")
            cell.set_height((1 - HDR) * nlines[r - 1] / total)
        if c == 0:
            cell.set_text_props(ha="center")
    out = os.path.join(BASE, "Tabla Estado del Arte.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("tabla ->", os.path.basename(out))


if __name__ == "__main__":
    main()
