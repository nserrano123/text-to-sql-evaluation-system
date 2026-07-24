#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolida la corrida multiturno REAL en el Excel y calcula las metricas.

Fases:
 1. Lee analisis_pruebas/multiturn_run/results_*.jsonl (salidas del flujo
    agentico) + timing_log.jsonl (tiempos reales por turno).
 2. Calcula Execution Accuracy normalizada (mismo algoritmo del workflow n8n,
    portado en mt_exec.py) ejecutando gold y prediccion contra la BD de prueba.
 3. Calcula Component Matching con workflowAgente/componentMaching.py (sqlglot).
 4. Escribe en dataset_sql_40_med_complex.xlsx via COM (preserva graficos):
    M  N8nSqlGenerated      N  N8nDINSql        O  N8nLLmResponse
    P  N8nTimeToResponse    Q  N8nErrorsSql
    V  ComponentMatching    W..AA CM_*          AB ExecutionAccuracy
    AC ExecutionAccuracyTotal
    Las columnas TSR (L) y VAL_* son formulas ya insertadas y se recalculan solas.
 5. Exporta un resumen JSON con las metricas multiturno para las graficas.
"""

import os, re, io, json, glob, sys

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
RUNDIR = os.path.join(BASE, "analisis_pruebas", "multiturn_run")
XLSX = os.path.join(BASE, "dataset_sql_40_med_complex.xlsx")

sys.path.insert(0, BASE)
from mt_exec import run_rows, _norm_rows, _stable  # noqa: E402

# --- cargar componentMaching sin fastapi/uvicorn ---
src = io.open(os.path.join(BASE, "workflowAgente", "componentMaching.py"),
              encoding="utf-8").read()
src = src.split("app = FastAPI")[0]
src = src.replace("from fastapi import FastAPI", "")
src = src.replace("from pydantic import BaseModel", "")
src = src.replace("import uvicorn", "")
cm_ns = {}
exec(src, cm_ns)
evaluate_cm = cm_ns["evaluate_component_matching"]


def load_results():
    rows = {}
    for fn in sorted(glob.glob(os.path.join(RUNDIR, "results_*.jsonl"))):
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                print("  ! linea invalida en", os.path.basename(fn))
                continue
            rows[int(d["excel_id"])] = d
    return rows


def load_timing():
    """Empareja turn_start/turn_end por sesion en orden -> lista de ms."""
    ev = {}
    fn = os.path.join(RUNDIR, "timing_log.jsonl")
    if not os.path.exists(fn):
        return {}
    for line in open(fn, encoding="utf-8"):
        d = json.loads(line)
        ev.setdefault(d["session"], []).append((d["t"], d["event"]))
    per_turn = {}
    for s, events in ev.items():
        events.sort()
        times, start = [], None
        for t, e in events:
            if e == "turn_start":
                start = t          # el mas reciente antes del end
            elif e == "turn_end" and start is not None:
                times.append(int((t - start) * 1000))
                start = None
        per_turn[s] = times
    return per_turn


def ex_eval(gold_sql, pred_sql):
    try:
        gold = run_rows(gold_sql)
    except Exception as e:
        return None, {"gold_error": str(e)[:300]}
    if not pred_sql.strip():
        return 0, {"normalized_ex_match": False, "normalized_ex": 0,
                   "mismatch_reason": {"pred": "no se genero SQL"}}
    try:
        pred = run_rows(pred_sql)
    except Exception as e:
        return 0, {"normalized_ex_match": False, "normalized_ex": 0,
                   "mismatch_reason": {"pred_error": str(e)[:300]}}
    gn, pn = _norm_rows(gold), _norm_rows(pred)
    gf, pf = _stable(gn), _stable(pn)
    match = gf == pf
    tot = {"normalized_ex_match": match, "normalized_ex": 1 if match else 0,
           "gold_fingerprint": gf[:800], "pred_fingerprint": pf[:800]}
    if not match:
        tot["mismatch_reason"] = {"gold_row_count": len(gold),
                                  "pred_row_count": len(pred)}
    return (1 if match else 0), tot


def cm_eval(gold_sql, pred_sql):
    try:
        m = evaluate_cm(gold_sql, pred_sql)
        f1 = {k: round(v["f1"], 6) for k, v in m.items()}
        return json.dumps(m, ensure_ascii=False)[:2500], f1
    except Exception as e:
        return json.dumps({"error": str(e)[:200]}), None


def main():
    import openpyxl
    results = load_results()
    timing = load_timing()
    print("Turnos con resultado:", len(results))

    # gold SQL por excel_id desde el Excel (columna J) sin tocar formato
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb["Medianas_y_Complejas"]
    gold = {}
    session_of = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        try:
            rid = int(r[0]) if r[0] is not None else None
        except (TypeError, ValueError):
            continue
        if rid and rid in results:
            gold[rid] = str(r[9] or "").strip()
            session_of[rid] = str(r[4] or "")
    wb.close()

    # ordenar por sesion/turno para asignar tiempos
    per_sess_counter = {}
    updates = {}   # excel_id -> dict de columnas
    summary = []
    for rid in sorted(results):
        d = results[rid]
        s = d["session"]
        idx = per_sess_counter.get(s, 0)
        per_sess_counter[s] = idx + 1
        tms = None
        if s in timing and idx < len(timing[s]):
            tms = timing[s][idx]
        g = gold.get(rid, "")
        pred = (d.get("sql") or "").strip()
        row = {"M": pred, "N": d.get("din") or "", "O": d.get("llm_response") or "",
               "P": tms if tms is not None else "", "Q": d.get("errors_sql", 0)}
        exv = cmj = None
        f1 = None
        if g:  # turno con gold SQL -> EX y CM aplican
            exv, tot = ex_eval(g, pred)
            if exv is not None:
                row["AB"] = float(exv)
                row["AC"] = json.dumps(tot, ensure_ascii=False)[:2500]
            if pred:
                cmj, f1 = cm_eval(g, pred)
                row["V"] = cmj
                if f1:
                    row["W"] = f1.get("select", 0.0)
                    row["X"] = f1.get("where", 0.0)
                    row["Y"] = f1.get("group_by", 0.0)
                    row["Z"] = f1.get("order_by", 0.0)
                    row["AA"] = f1.get("keywords", 0.0)
        updates[rid] = row
        summary.append({"excel_id": rid, "session": s, "turn": d["turn"],
                        "action": d["action"], "has_gold": bool(g),
                        "ex": exv, "cm_f1": f1, "errors": d.get("errors_sql", 0),
                        "time_ms": tms})

    json.dump(summary, open(os.path.join(RUNDIR, "resumen_metricas.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print("EX evaluado en", sum(1 for s in summary if s["ex"] is not None), "turnos")

    # ---- escribir via COM ----
    import win32com.client as win32
    excel = win32.gencache.EnsureDispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wbx = excel.Workbooks.Open(XLSX)
        wsx = wbx.Worksheets("Medianas_y_Complejas")
        last = wsx.Cells(wsx.Rows.Count, 1).End(-4162).Row
        # mapa id->fila (las filas nuevas: ID == fila, pero verificamos)
        id2row = {}
        vals = wsx.Range(wsx.Cells(2, 1), wsx.Cells(last, 1)).Value
        for i, (v,) in enumerate(vals, start=2):
            try:
                id2row[int(v)] = i
            except (TypeError, ValueError):
                pass
        n = 0
        for rid, row in updates.items():
            xr = id2row.get(rid)
            if not xr:
                continue
            for col, val in row.items():
                wsx.Range(f"{col}{xr}").Value = val
            n += 1
        wbx.Save()
        print(f"Excel actualizado: {n} filas.")
    finally:
        excel.Quit()


if __name__ == "__main__":
    main()
