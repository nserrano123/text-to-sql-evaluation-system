#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agrega el dataset MULTITURNO a `dataset_sql_40_med_complex.xlsx`
(hoja "Medianas_y_Complejas") respetando el estandar de columnas de las filas
existentes (referencia: sessionId = TestMultiturn1) y repara las formulas
danadas del export de Google Sheets en la hoja "Tabla Anexo".

- Las filas nuevas quedan con relleno AZUL CLARO para diferenciarlas.
- Parametros: [Rag],[Memoria],[Intension],[Din],[Dea]
- Se llenan SOLO las columnas del dataset (ID..SQL) + las formulas estandar
  (Sql para ejecutar, TSR, VAL_*). Las columnas del modelo (N8n*) y de la
  evaluacion (Metric*, CM_*, ExecutionAccuracy*) se llenan con la EJECUCION
  REAL del flujo agentico, no aqui.
- Usa Excel via COM para no danar los graficos nativos del libro.

Genera ademas `analisis_pruebas/preguntas_multiturno.csv` sincronizado con las
filas insertadas (incluye expected_action y el ID de fila en Excel, necesario
para calcular las metricas multiturno tras la ejecucion real).
"""

import os
import re
import csv
import json
import random

import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "dataset_sql_40_med_complex.xlsx")
SHEET = "Medianas_y_Complejas"
OUTCSV = os.path.join(BASE, "analisis_pruebas", "preguntas_multiturno.csv")

FOCUS = "[Rag],[Memoria],[Intension],[Din],[Dea]"
MEMBER_ID = "915c6f4b-e8de-467f-95ea-7b379f19fc11"

N_CONVERSACIONES = 100
TURNOS_MIN, TURNOS_MAX = 5, 10
SEED = 42
FILL_BGR = 0xF7EBDD  # RGB(221,235,247) azul claro en BGR para COM

# --------------------------------------------------------------------------- #
# Transformaciones SQL derivables (gold SQL de los turnos contextuales)
# --------------------------------------------------------------------------- #
RX_LIMIT = re.compile(r"\s+limit\s+\d+\s*;?\s*$", re.I)
RX_AGG = re.compile(r"(SUM|COUNT|AVG)\s*\(([^)]*)\)\s+AS\s+(\w+)", re.I)


def strip_tail(sql):
    s = sql.strip().rstrip(";").strip()
    s = RX_LIMIT.sub("", s + " ").strip()
    return s


def agg_alias(sql):
    m = RX_AGG.search(sql)
    return m.group(3) if m else None


def t_top5(sql):
    return strip_tail(sql) + " LIMIT 5;"


def t_orden(sql):
    a = agg_alias(sql)
    return strip_tail(sql) + f" ORDER BY {a} DESC LIMIT 100;" if a else None


def t_max(sql):
    a = agg_alias(sql)
    return strip_tail(sql) + f" ORDER BY {a} DESC LIMIT 1;" if a else None


def t_promedio(sql):
    if not re.search(r"SUM\s*\(", sql, re.I):
        return None
    return re.sub(r"SUM\s*\(", "AVG(", sql, count=1, flags=re.I)


def t_total(sql):
    return ("SELECT COUNT(*) AS total_registros FROM ( "
            + strip_tail(sql) + " ) AS sub;")


CTX = [
    ("ctx_top5", "De ese resultado, muéstrame solo los primeros 5.",
     "Aplicar LIMIT 5 sobre la consulta del turno anterior.", t_top5),
    ("ctx_orden", "Ordena ese resultado de mayor a menor.",
     "Aplicar ORDER BY descendente sobre el agregado del turno anterior.", t_orden),
    ("ctx_max", "De ese resultado, ¿cuál tiene el valor más alto?",
     "Devolver el registro con el máximo del agregado del turno anterior.", t_max),
    ("ctx_promedio", "Y en vez de la suma, dame el promedio.",
     "Sustituir SUM por AVG en la consulta del turno anterior.", t_promedio),
    ("ctx_total", "¿Cuántos registros dio ese resultado en total?",
     "Contar los registros del resultado del turno anterior (COUNT sobre subconsulta).", t_total),
]

NO_SQL = [
    ("ns_gracias", "Listo, muchas gracias, justo lo que necesitaba."),
    ("ns_ok", "Perfecto, entendido."),
    ("ns_saludo", "Hola, buenas, ¿cómo vas?"),
    ("ns_capacidad", "¿Qué otras cosas puedes consultar de mi empresa?"),
    ("ns_identidad", "¿Y tú quién eres exactamente?"),
    ("ns_offtopic", "Oye, ¿y me recomiendas algo para almorzar hoy?"),
    ("ns_explica", "¿Me puedes explicar qué significa ese dato?"),
    ("ns_opinion", "¿Ese número te parece normal para un negocio como el mío?"),
]

CLARIFY = [
    ("cl_vago", "Dame los datos."),
    ("cl_otro", "Y lo otro también, porfa."),
    ("cl_siempre", "Muéstrame lo de siempre."),
    ("cl_comparar", "Compáralo."),
    ("cl_eso", "¿Y eso cómo va?"),
]


# --------------------------------------------------------------------------- #
def load_seeds():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb[SHEET]
    it = ws.iter_rows(values_only=True)
    hdr = list(next(it))
    seen = {}
    for r in it:
        d = dict(zip(hdr, r))
        if (d.get("chatInput") and d.get("Parametros") == FOCUS
                and str(d.get("EVALUADO")) == "1" and d.get("SQL")
                and d.get("Tablas y columnas (DDL)")):
            q = str(d["chatInput"]).strip()
            if q in seen:
                continue
            sql = re.sub(r"\s+", " ", str(d["SQL"])).strip()
            if not re.search(r'FROM\s+"?\w+"?\."?\w+"?', sql, re.I):
                continue
            seen[q] = {
                "q": q, "sql": sql,
                "ddl": str(d["Tablas y columnas (DDL)"]).strip(),
                "clasif": d.get("Clasificacion") or "Mediana",
                "descomp": str(d.get("Pregunta Descompuesta") or "").strip(),
            }
    wb.close()
    return list(seen.values())


def build_conversations(seeds, rnd):
    """Devuelve lista de turnos (dicts) en orden estricto de ejecucion."""
    turns = []
    for cid in range(1, N_CONVERSACIONES + 1):
        session = f"TestMultiturn{cid + 1}"        # TestMultiturn1 ya existe
        total = rnd.randint(TURNOS_MIN, TURNOS_MAX)
        greeting = rnd.random() < 0.30
        used_ctx, used_ns, used_cl = set(), set(), set()
        tno = 0

        def add(action, msg, sql, ddl, clasif, descomp, ttype, dep=None):
            nonlocal tno
            tno += 1
            turns.append({
                "session": session, "turn": tno, "action": action,
                "msg": msg, "sql": sql or "", "ddl": ddl or "",
                "clasif": clasif, "descomp": descomp or "",
                "ttype": ttype, "dep": dep or "",
            })
            return tno

        if greeting:
            add("NO_SQL", "Hola, buenos días.", "", "", "Facil", "", "ns_saludo")

        seed = rnd.choice(seeds)
        anchor = add("EXECUTE_SQL", seed["q"], seed["sql"], seed["ddl"],
                     seed["clasif"], seed["descomp"], "seed_sql")
        anchor_seed = seed

        n_follow = max(3, total - tno)
        plan = ["ctx", "ctx", "nosql"]
        if rnd.random() < 0.55:
            plan.append("clarify")
        if rnd.random() < 0.35:
            plan.append("switch")
        while len(plan) < n_follow:
            plan.append(rnd.choice(["ctx", "ctx", "nosql", "clarify"]))
        plan = plan[:n_follow]
        rnd.shuffle(plan)
        if plan and plan[0] == "switch":
            plan[0], plan[-1] = plan[-1], plan[0]
        if len(plan) > 1 and plan[-1] == "switch":
            mid = len(plan) // 2
            plan[mid], plan[-1] = plan[-1], plan[mid]

        ns_pool = [t for t in NO_SQL if not (greeting and t[0] == "ns_saludo")]

        def pick(pool, used):
            opts = [t for t in pool if t[0] not in used] or list(pool)
            t = rnd.choice(opts)
            used.add(t[0])
            return t

        for role in plan:
            if role == "switch":
                s2 = rnd.choice(seeds)
                msg = ("Ahora, cambiando de tema: "
                       + s2["q"][0].lower() + s2["q"][1:])
                anchor = add("EXECUTE_SQL", msg, s2["sql"], s2["ddl"],
                             s2["clasif"], s2["descomp"], "switch_sql")
                anchor_seed = s2
            elif role == "ctx":
                opts = [t for t in CTX if t[0] not in used_ctx
                        and t[3](anchor_seed["sql"])]
                if not opts:
                    used_ctx.clear()
                    opts = [t for t in CTX if t[3](anchor_seed["sql"])]
                if not opts:
                    continue
                code, msg, desc, fn = rnd.choice(opts)
                used_ctx.add(code)
                gold = fn(anchor_seed["sql"])
                descomp = ("1) Recuperar de la memoria la consulta del turno "
                           f"{anchor} de esta sesión. 2) {desc}")
                add("EXECUTE_SQL", msg, gold, anchor_seed["ddl"],
                    anchor_seed["clasif"], descomp, code, dep=anchor)
            elif role == "nosql":
                code, msg = pick(ns_pool, used_ns)
                add("NO_SQL", msg, "", "", "Facil", "", code,
                    dep=anchor if code == "ns_explica" else None)
            else:
                code, msg = pick(CLARIFY, used_cl)
                add("CLARIFY", msg, "", "", "Facil", "", code)
    return turns


# --------------------------------------------------------------------------- #
def insert_com(turns):
    import win32com.client as win32
    excel = win32.gencache.EnsureDispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(XLSX)
        ws = wb.Worksheets(SHEET)
        last = ws.Cells(ws.Rows.Count, 1).End(-4162).Row  # xlUp
        max_id = int(ws.Cells(last, 1).Value or last)
        r0 = last + 1
        n = len(turns)

        # ---- bloque de valores A..J (dataset) ----
        data = []
        for i, t in enumerate(turns):
            data.append((
                max_id + 1 + i,            # A ID
                "E",                       # B Status
                FOCUS,                     # C Parametros
                t["msg"],                  # D chatInput
                t["session"],              # E sessionId
                MEMBER_ID,                 # F member_id
                t["clasif"],               # G Clasificacion
                t["descomp"],              # H Pregunta Descompuesta
                t["ddl"],                  # I DDL
                t["sql"],                  # J SQL (gold)
            ))
        ws.Range(ws.Cells(r0, 1), ws.Cells(r0 + n - 1, 10)).Value = data

        # ---- formulas estandar (rango completo; Excel ajusta refs) ----
        rng = lambda c1, c2=None: ws.Range(f"{c1}{r0}:{c2 or c1}{r0 + n - 1}")
        rng("K").Formula = (
            f'= TRIM(IF(IFERROR(FIND("$1",J{r0},1),0)>=1,'
            f'REPLACE(J{r0},FIND("$1",J{r0},1),2,'
            f'CONCATENATE("\'",F{r0},"\'")),J{r0}))')
        rng("L").Formula = (
            f'=IF(OR(AND(ISBLANK(TRIM(J{r0})),ISBLANK(TRIM(M{r0}))),'
            f'AND(NOT( ISBLANK(TRIM(J{r0}))),NOT(ISBLANK(TRIM(M{r0}))))),1,0)')
        rng("AD").Formula = f"=P{r0}*1/1000"
        for col, src in (("AE", "W"), ("AF", "X"), ("AG", "Y"),
                         ("AH", "Z"), ("AI", "AA"), ("AJ", "AB")):
            rng(col).Formula = f'=SUBSTITUTE({src}{r0},".",",")*1'
        rng("AK").Formula = f'=1-IF((SUBSTITUTE(Q{r0},".",",")*1)>=3,1,0)'
        rng("AL").Formula = f'=1-IF((SUBSTITUTE(Q{r0},".",",")*1)>=1,1,0)'
        # AM..AO (OrdenP / Orden_Y_Parametros / EVALUADO) se dejan vacios:
        # igual que TestMultiturn1, estas filas no entran al analisis de
        # ablacion de un solo turno.

        # en turnos sin SQL (NO_SQL / CLARIFY) las metricas VAL_* no aplican
        for i, t in enumerate(turns):
            if t["action"] != "EXECUTE_SQL":
                ws.Range(f"AD{r0 + i}:AL{r0 + i}").ClearContents()

        # ---- relleno azul claro en todo el bloque nuevo ----
        block = ws.Range(ws.Cells(r0, 1), ws.Cells(r0 + n - 1, 41))
        block.Interior.Color = FILL_BGR

        # ---- reparar formulas danadas de "Tabla Anexo" ----
        wa = wb.Worksheets("Tabla Anexo")
        la = wa.Cells(wa.Rows.Count, 2).End(-4162).Row
        fix = lambda c: wa.Range(f"{c}2:{c}{la}")
        fix("G").Formula = (
            '=TRIM(IF(IFERROR(FIND("$1",F2,1),0)>=1,'
            'REPLACE(F2,FIND("$1",F2,1),2,'
            f'"\'{MEMBER_ID}\'"),F2))')
        fix("AF").Formula = "=MINIFS(A:A,C:C,C2)"
        fix("AG").Formula = "=CONCAT(AF2,C2)"
        fix("AH").Formula = '=IF(ISBLANK(B2),0,1)'

        wb.Save()
        print(f"Insertadas {n} filas en '{SHEET}' (filas {r0}..{r0 + n - 1}, "
              f"IDs {max_id + 1}..{max_id + n}).")
        print(f"Formulas de 'Tabla Anexo' reparadas (filas 2..{la}).")
        return r0, max_id
    except Exception:
        import traceback
        traceback.print_exc()
        raise
    finally:
        try:
            excel.Quit()
        except Exception:
            pass


def write_csv(turns, r0, max_id):
    os.makedirs(os.path.dirname(OUTCSV), exist_ok=True)
    cols = ["excel_id", "session_id", "turn_index", "expected_action",
            "depends_on_turn", "turn_type", "user_message", "gold_sql"]
    with open(OUTCSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, t in enumerate(turns):
            w.writerow([max_id + 1 + i, t["session"], t["turn"], t["action"],
                        t["dep"], t["ttype"], t["msg"], t["sql"]])
    print("CSV sincronizado ->", os.path.relpath(OUTCSV, BASE))


def main():
    rnd = random.Random(SEED)
    seeds = load_seeds()
    print("Semillas utilizables (config foco, con DDL y SQL):", len(seeds))
    turns = build_conversations(seeds, rnd)
    from collections import Counter
    acc = Counter(t["action"] for t in turns)
    print(f"Conversaciones: {N_CONVERSACIONES} | Turnos: {len(turns)} | {dict(acc)}")
    r0, max_id = insert_com(turns)
    write_csv(turns, r0, max_id)


if __name__ == "__main__":
    main()
