#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volcado robusto (con reintentos COM) de la corrida multiturno al Excel.
Reutiliza analisis_pruebas/multiturn_run/resumen_metricas.json (EX/tiempo ya
calculados contra la BD) + results_*.jsonl (N8nSql/DIN/respuesta/errores) y
recalcula Component Matching con componentMaching.py (sqlglot, sin BD).
"""
import os, io, re, json, glob, sys, time
sys.stdout.reconfigure(encoding="utf-8")
BASE=os.path.dirname(os.path.abspath(__file__))
RUN=os.path.join(BASE,"analisis_pruebas","multiturn_run")
XLSX=os.path.join(BASE,"dataset_sql_40_med_complex.xlsx")

# cargar componentMaching sin fastapi
src=io.open(os.path.join(BASE,"workflowAgente","componentMaching.py"),encoding="utf-8").read()
src=src.split("app = FastAPI")[0].replace("from fastapi import FastAPI","").replace("from pydantic import BaseModel","").replace("import uvicorn","")
ns={}; exec(src,ns); evaluate_cm=ns["evaluate_component_matching"]

import openpyxl, pythoncom
import win32com.client as win32

def retry(fn,tries=60,delay=2):
    last=None
    for _ in range(tries):
        try: return fn()
        except pythoncom.com_error as e:
            # RPC_E_CALL_REJECTED / RPC_E_SERVERCALL_RETRYLATER / "excepcion" por ocupado
            if e.hresult in (-2147418111,-2147417846,-2147352567): last=e; time.sleep(delay); continue
            raise
    raise last

# 1) resultados del modelo por excel_id
res={}
for fn in glob.glob(os.path.join(RUN,"results_*.jsonl")):
    for line in open(fn,encoding="utf-8"):
        s=line.strip()
        if not s: continue
        d=json.loads(s); res[int(d["excel_id"])]=d
# 2) metricas ya calculadas (EX, tiempo)
metr={r["excel_id"]:r for r in json.load(open(os.path.join(RUN,"resumen_metricas.json"),encoding="utf-8"))}
# 3) gold SQL desde el Excel
wb=openpyxl.load_workbook(XLSX,data_only=True,read_only=True)
ws=wb["Medianas_y_Complejas"]
gold={}
for r in ws.iter_rows(min_row=2,values_only=True):
    try: rid=int(r[0])
    except (TypeError,ValueError): continue
    if rid in res: gold[rid]=str(r[9] or "").strip()
wb.close()

# 4) construir updates
updates={}
for rid,d in res.items():
    m=metr.get(rid,{})
    pred=(d.get("sql") or "").strip()
    row={"M":pred,"N":d.get("din") or "","O":d.get("llm_response") or "",
         "P":m.get("time_ms") if m.get("time_ms") is not None else "",
         "Q":d.get("errors_sql",0)}
    if m.get("ex") is not None:
        row["AB"]=float(m["ex"])
        row["AC"]=json.dumps({"normalized_ex":m["ex"]},ensure_ascii=False)
    g=gold.get(rid,"")
    if g and pred:
        try:
            cm=evaluate_cm(g,pred)
            row["V"]=json.dumps(cm,ensure_ascii=False)[:2500]
            row["W"]=round(cm["select"]["f1"],6); row["X"]=round(cm["where"]["f1"],6)
            row["Y"]=round(cm["group_by"]["f1"],6); row["Z"]=round(cm["order_by"]["f1"],6)
            row["AA"]=round(cm["keywords"]["f1"],6)
        except Exception as e:
            row["V"]=json.dumps({"error":str(e)[:150]})
    updates[rid]=row
print("Filas a escribir:",len(updates))

# 5) escribir via COM con reintentos (registra un message filter y calc manual)
excel=win32.gencache.EnsureDispatch("Excel.Application")
retry(lambda: setattr(excel,"Visible",False))
retry(lambda: setattr(excel,"DisplayAlerts",False))
try:
    wbx=retry(lambda: excel.Workbooks.Open(XLSX, UpdateLinks=0, ReadOnly=False))
    time.sleep(25)  # dejar terminar el recalculo de ~23k formulas
    retry(lambda: setattr(excel,"Calculation",-4135))  # xlCalculationManual
    retry(lambda: setattr(excel,"ScreenUpdating",False))
    wsx=retry(lambda: wbx.Worksheets("Medianas_y_Complejas"))
    last=retry(lambda: wsx.Cells(wsx.Rows.Count,1).End(-4162).Row)
    id2row={}
    vals=retry(lambda: wsx.Range(wsx.Cells(2,1),wsx.Cells(last,1)).Value)
    for i,(v,) in enumerate(vals,start=2):
        try: id2row[int(v)]=i
        except (TypeError,ValueError): pass
    n=0
    for rid,row in updates.items():
        xr=id2row.get(rid)
        if not xr: continue
        # escribir el bloque de columnas de una vez por fila (menos llamadas COM)
        for col,val in row.items():
            retry(lambda c=col,r=xr,v=val: setattr(wsx.Cells(r, openpyxl.utils.column_index_from_string(c)),"Value",v))
        n+=1
        if n%100==0: print(f"  {n} filas...")
    retry(lambda: wbx.Save())
    print(f"Excel actualizado: {n} filas.")
finally:
    try: retry(lambda: setattr(excel,"Calculation",-4105), tries=3)  # xlCalculationAutomatic
    except Exception: pass
    try: excel.Quit()
    except Exception: pass
