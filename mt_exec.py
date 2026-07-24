#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper de ejecucion para la corrida multiturno del flujo agentico.

Subcomandos:
  run       --sql-file F --session S      Ejecuta SELECT(s) contra la BD de prueba
  schema    --tables s.t1,s.t2            Columnas reales de las tablas
  tables    --like kw                     Busca tablas por nombre
  entities                                Lista de entidades del sistema (cacheada)
  mem-get   --session S                   Ultimos 10 mensajes de la memoria
  mem-add   --session S --file F          Inserta {"human":..., "ai":...} en memoria
  ex        --gold-file F --pred-file F   Execution Accuracy normalizada (port del JS n8n)

Seguridad: conexion READ ONLY + statement_timeout. Solo SELECT/WITH.
La memoria se guarda en public.n8n_chat_histories (formato LangChain n8n).
mem-get / mem-add registran timestamps por sesion para medir el tiempo real
de procesamiento de cada turno (timing_log.jsonl).
"""

import sys, os, re, json, time, argparse, datetime, decimal, uuid

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import psycopg2
import psycopg2.extras

DB = dict(host="172.17.240.1", dbname="main_20260721",
          user="postgres", password="Msmpostgres", connect_timeout=10)
MEMBER_ID = "915c6f4b-e8de-467f-95ea-7b379f19fc11"
BASE = os.path.dirname(os.path.abspath(__file__))
RUNDIR = os.path.join(BASE, "analisis_pruebas", "multiturn_run")
TIMING = os.path.join(RUNDIR, "timing_log.jsonl")
ENT_CACHE = os.path.join(RUNDIR, "entities.json")
os.makedirs(RUNDIR, exist_ok=True)


def connect(readonly=True):
    opts = "-c statement_timeout=20000"
    if readonly:
        opts += " -c default_transaction_read_only=on"
    return psycopg2.connect(options=opts, **DB)


def jsonable(v):
    if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, memoryview):
        return v.hex()
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, dict):
        return {k: jsonable(x) for k, x in v.items()}
    return v


def clean_sql(sql):
    sql = sql.replace("```sql", "").replace("```", "").strip()
    sql = sql.replace("$1", f"'{MEMBER_ID}'")
    return sql


def split_statements(sql):
    # split por ';' fuera de comillas
    parts, cur, q = [], [], None
    for ch in sql:
        if q:
            cur.append(ch)
            if ch == q:
                q = None
        elif ch in ("'", '"'):
            q = ch
            cur.append(ch)
        elif ch == ";":
            s = "".join(cur).strip()
            if s:
                parts.append(s)
            cur = []
        else:
            cur.append(ch)
    s = "".join(cur).strip()
    if s:
        parts.append(s)
    return parts


def cmd_run(args):
    sql = open(args.sql_file, encoding="utf-8").read()
    sql = clean_sql(sql)
    stmts = split_statements(sql)
    for s in stmts:
        head = re.sub(r"^\s*(--[^\n]*\n|/\*.*?\*/)*", "", s, flags=re.S).lstrip()
        if not re.match(r"(?is)^(SELECT|WITH)\b", head):
            print(json.dumps({"ok": False, "error":
                              "Solo se permiten sentencias SELECT/WITH."}))
            return
    t0 = time.time()
    out = {"ok": True, "statements": []}
    try:
        conn = connect(readonly=True)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        for s in stmts:
            cur.execute(s)
            rows = [dict(r) for r in cur.fetchmany(100)]
            out["statements"].append({"rowcount": len(rows),
                                      "rows": jsonable(rows)})
        conn.close()
    except Exception as e:
        out = {"ok": False, "error": str(e).strip()[:600]}
    out["ms"] = int((time.time() - t0) * 1000)
    print(json.dumps(out, ensure_ascii=False, default=str))


def cmd_schema(args):
    tabs = [t.strip() for t in args.tables.split(",") if t.strip()]
    conn = connect()
    cur = conn.cursor()
    out = {}
    for t in tabs:
        if "." in t:
            sch, tab = t.split(".", 1)
        else:
            sch, tab = "public", t
        cur.execute("""SELECT column_name, data_type FROM information_schema.columns
                       WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position""",
                    (sch, tab))
        cols = cur.fetchall()
        out[t] = [f"{c} ({d})" for c, d in cols] if cols else "NO EXISTE"
    conn.close()
    print(json.dumps(out, ensure_ascii=False))


def cmd_tables(args):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""SELECT table_schema||'.'||table_name FROM information_schema.tables
                   WHERE table_schema NOT IN ('pg_catalog','information_schema')
                   AND (table_name ILIKE %s OR table_schema ILIKE %s)
                   ORDER BY 1 LIMIT 40""",
                (f"%{args.like}%", f"%{args.like}%"))
    print(json.dumps([r[0] for r in cur.fetchall()], ensure_ascii=False))
    conn.close()


ENTITIES_SQL = """
select e.name from core.page c inner join system.entity_catal e on c.entity_catal_id = e.id
where c.id in (select distinct record from core.menu where member_id = %s) group by e.name
union
select e.name from core.page c inner join core.member_entity_catal e on c.entity_catal_id = e.id
where c.id in (select distinct record from core.menu where member_id = %s) group by e.name;
"""


def cmd_entities(args):
    if os.path.exists(ENT_CACHE):
        print(open(ENT_CACHE, encoding="utf-8").read())
        return
    conn = connect()
    cur = conn.cursor()
    cur.execute(ENTITIES_SQL, (MEMBER_ID, MEMBER_ID))
    names = sorted({r[0] for r in cur.fetchall()})
    conn.close()
    data = json.dumps(names, ensure_ascii=False)
    open(ENT_CACHE, "w", encoding="utf-8").write(data)
    print(data)


def log_t(session, event):
    with open(TIMING, "a", encoding="utf-8") as f:
        f.write(json.dumps({"session": session, "event": event,
                            "t": time.time()}) + "\n")


def mem_key(session):
    return f"{session}_{MEMBER_ID}_global"


def cmd_mem_get(args):
    log_t(args.session, "turn_start")
    conn = connect(readonly=True)
    cur = conn.cursor()
    cur.execute("""select message->>'type' t, message->>'content' c from (
                     select * from public.n8n_chat_histories
                     where session_id=%s order by id desc limit 10
                   ) a order by id asc""", (mem_key(args.session),))
    msgs = [f"{t}: {c}" for t, c in cur.fetchall()]
    conn.close()
    print(json.dumps({"history": msgs}, ensure_ascii=False))


def cmd_mem_add(args):
    d = json.load(open(args.file, encoding="utf-8"))
    conn = connect(readonly=False)
    cur = conn.cursor()
    for typ, key in (("human", "human"), ("ai", "ai")):
        msg = {"type": typ, "content": d[key],
               "additional_kwargs": {}, "response_metadata": {}}
        cur.execute("insert into public.n8n_chat_histories (session_id, message) "
                    "values (%s, %s)", (mem_key(args.session), json.dumps(msg)))
    conn.commit()
    conn.close()
    log_t(args.session, "turn_end")
    print(json.dumps({"ok": True}))


# ------------------- Execution Accuracy (port del Code node n8n) ----------- #
def _stable(o):
    if o is None:
        return "null"
    if isinstance(o, bool):
        return "true" if o else "false"
    if isinstance(o, (int, float)):
        if isinstance(o, float) and o.is_integer():
            o = int(o)
        return json.dumps(o)
    if isinstance(o, str):
        return json.dumps(o, ensure_ascii=False)
    if isinstance(o, list):
        return "[" + ",".join(_stable(x) for x in o) + "]"
    if isinstance(o, dict):
        keys = sorted(o.keys())
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + _stable(o[k])
                              for k in keys) + "}"
    return json.dumps(str(o), ensure_ascii=False)


def _norm_col(name):
    s = str(name or "").strip().lower().replace('"', "")
    return s.split(".")[-1] if "." in s else s


RX_NUM = re.compile(r"^-?\d+(\.\d+)?$")
RX_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$")


def _norm_val(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        r = round(float(v), 6)
        return int(r) if float(r).is_integer() else r
    if isinstance(v, str):
        t = v.strip()
        if (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]")):
            try:
                return _norm_val(json.loads(t))
            except Exception:
                pass
        if not re.search(r"[a-zA-Z]", t) and RX_NUM.match(t):
            r = round(float(t), 6)
            return int(r) if float(r).is_integer() else r
        return t
    if isinstance(v, list):
        arr = [_norm_val(x) for x in v]
        arr.sort(key=_stable)
        return arr
    if isinstance(v, dict):
        vals = [_norm_val(x) for x in v.values()]
        vals.sort(key=_stable)
        return {"__values__": vals}
    return str(v)


def _norm_rows(rows):
    if not rows:
        return []
    colset = set()
    for r in rows:
        colset.update(_norm_col(k) for k in r.keys())
    order = sorted(colset)
    tuples = []
    for r in rows:
        nm = {_norm_col(k): _norm_val(v) for k, v in r.items()}
        tuples.append([nm.get(c) for c in order])
    tuples.sort(key=_stable)
    return tuples


def run_rows(sql):
    sql = clean_sql(sql)
    stmts = split_statements(sql)
    conn = connect(readonly=True)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    rows = []
    try:
        for s in stmts:
            cur.execute(s)
            rows.extend(dict(r) for r in cur.fetchmany(100))
    finally:
        conn.close()
    return jsonable(rows)


def cmd_ex(args):
    try:
        gold = run_rows(open(args.gold_file, encoding="utf-8").read())
    except Exception as e:
        print(json.dumps({"ok": False, "side": "gold", "error": str(e)[:300]}))
        return
    try:
        pred = run_rows(open(args.pred_file, encoding="utf-8").read())
    except Exception as e:
        print(json.dumps({"ok": True, "normalized_ex_match": False, "normalized_ex": 0,
                          "gold_fingerprint": _stable(_norm_rows(gold)),
                          "pred_fingerprint": None,
                          "mismatch_reason": {"pred_error": str(e)[:300]}},
                         ensure_ascii=False))
        return
    gn, pn = _norm_rows(gold), _norm_rows(pred)
    gf, pf = _stable(gn), _stable(pn)
    match = gf == pf
    out = {"ok": True, "normalized_ex_match": match,
           "normalized_ex": 1 if match else 0,
           "gold_fingerprint": gf, "pred_fingerprint": pf}
    if not match:
        out["mismatch_reason"] = {"gold_row_count": len(gold),
                                  "pred_row_count": len(pred),
                                  "gold_norm_preview": gn[:5],
                                  "pred_norm_preview": pn[:5]}
    print(json.dumps(out, ensure_ascii=False, default=str))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run"); p.add_argument("--sql-file", required=True); p.add_argument("--session", default="")
    p = sub.add_parser("schema"); p.add_argument("--tables", required=True)
    p = sub.add_parser("tables"); p.add_argument("--like", required=True)
    sub.add_parser("entities")
    p = sub.add_parser("mem-get"); p.add_argument("--session", required=True)
    p = sub.add_parser("mem-add"); p.add_argument("--session", required=True); p.add_argument("--file", required=True)
    p = sub.add_parser("ex"); p.add_argument("--gold-file", required=True); p.add_argument("--pred-file", required=True)
    args = ap.parse_args()
    {"run": cmd_run, "schema": cmd_schema, "tables": cmd_tables,
     "entities": cmd_entities, "mem-get": cmd_mem_get,
     "mem-add": cmd_mem_add, "ex": cmd_ex}[args.cmd](args)


if __name__ == "__main__":
    main()
