from typing import Set, Tuple, Dict
import sqlglot
from sqlglot import expressions as exp
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


def precision_recall_f1(gold: Set, pred: Set) -> Dict[str, float]:
    tp = len(gold & pred)
    fp = len(pred - gold)
    fn = len(gold - pred)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def parse_sql(query: str) -> exp.Expression:
    return sqlglot.parse_one(query)


# ------------ NORMALIZACIÓN DE COLUMNAS / IDENTIFICADORES ------------

def normalize_identifier(expr: exp.Expression) -> str:
    """
    Normaliza identificadores de columnas ignorando:
    - alias de tabla (t.account_id -> account_id)
    - comillas ("account_id" -> account_id)
    - mayúsculas/minúsculas
    """
    # Si es una columna reconocida por sqlglot
    if isinstance(expr, exp.Column):
        # Column tiene atributos .name y .table
        name = expr.name or ""
        return name.replace('"', "").lower().strip()

    # Fallback genérico: usar sql() y limpiarlo
    txt = expr.sql().lower()
    txt = txt.replace('"', "").strip()
    # Si viene algo como schema.table.col → nos quedamos con la última parte
    if "." in txt:
        txt = txt.split(".")[-1]
    return txt


# -------------------- SELECT --------------------

def extract_select_components(tree: exp.Expression) -> Set[Tuple]:
    """
    Extrae subcomponentes del SELECT:
    - Columnas simples: ("col", <col_normalizada>)
    - Agregaciones: ("agg", <funcion>, <col_normalizada>)
    """
    components = set()
    select_exprs = tree.args.get("expressions") or []

    AGG_FUNCS = {"sum", "count", "avg", "min", "max"}

    for expr in select_exprs:
        # Manejar alias: SUM(x) AS total, t.col AS alias, etc.
        target = expr.this if isinstance(expr, exp.Alias) else expr

        # ¿Es una función tipo SUM/COUNT/AVG...?
        func_name = str(getattr(target, "key", "")).lower()
        if func_name in AGG_FUNCS:
            # Tomamos el primer argumento de la función (ej: SUM(t.balance))
            arg_exprs = [
                a for a in target.args.values()
                if isinstance(a, exp.Expression)
            ]
            arg = arg_exprs[0] if arg_exprs else None
            col_name = normalize_identifier(arg) if arg is not None else ""
            components.add(("agg", func_name, col_name))
        else:
            # Columna o expresión directa → normalizamos columna
            col_name = normalize_identifier(target)
            components.add(("col", col_name))

    return components


# -------------------- WHERE --------------------

def _extract_boolean_conditions(expr: exp.Expression) -> Set[str]:
    """
    Extrae condiciones atómicas del WHERE, normalizando identificadores.
    Representamos cada comparación como:
        "<op>|<col_normalizada>|<valor_normalizado>"
    Ej:
        "eq|member_id|$1"
    """
    if expr is None:
        return set()

    result = set()

    # Si viene un wrapper WHERE, entrar a la condición interna
    if isinstance(expr, exp.Where):
        return _extract_boolean_conditions(expr.this)

    # AND / OR → descomponer recursivamente
    if isinstance(expr, (exp.And, exp.Or)):
        result |= _extract_boolean_conditions(expr.left)
        result |= _extract_boolean_conditions(expr.right)
        return result

    # BETWEEN col BETWEEN low AND high
    if isinstance(expr, exp.Between):
        col = expr.this
        low = expr.args.get("low")
        high = expr.args.get("high")
        col_name = normalize_identifier(col)
        low_txt = low.sql().lower() if low is not None else ""
        high_txt = high.sql().lower() if high is not None else ""
        result.add(f"between|{col_name}|{low_txt}|{high_txt}")
        return result

    # Comparaciones: =, >, >=, <, <=, <>, LIKE, etc.
    if isinstance(expr, (exp.EQ, exp.GT, exp.GTE, exp.LT, exp.LTE, exp.NEQ, exp.Like)):
        left = expr.left
        right = expr.right

        op = expr.key.lower()  # "eq", "gt", "gte", etc.

        # Normalizamos la izquierda si es columna
        if isinstance(left, exp.Column):
            left_norm = normalize_identifier(left)
        else:
            left_norm = left.sql().lower()

        right_norm = right.sql().lower() if isinstance(right, exp.Expression) else str(right).lower()

        result.add(f"{op}|{left_norm}|{right_norm}")
        return result

    # Fallback: cualquier otra expresión booleana, usamos sql() completo
    result.add(expr.sql().lower())
    return result


def extract_where_components(tree: exp.Expression) -> Set[str]:
    where_expr = tree.args.get("where")
    if where_expr is None:
        return set()
    # Aseguramos que si es exp.Where, entramos a su interior
    return _extract_boolean_conditions(where_expr)


# -------------------- GROUP BY --------------------

def extract_group_by_components(tree: exp.Expression) -> Set[str]:
    group = tree.args.get("group")
    if group is None:
        return set()
    cols = getattr(group, "expressions", [])
    return {normalize_identifier(c) for c in cols}


# -------------------- ORDER BY --------------------

def extract_order_by_components(tree: exp.Expression) -> Set[Tuple[str, str]]:
    order = tree.args.get("order")
    if order is None:
        return set()

    components = set()
    for item in order.expressions:
        direction = "desc" if item.args.get("desc") else "asc"
        expr_sql = item.this.sql().lower()
        components.add((direction, expr_sql))
    return components


# -------------------- KEYWORDS --------------------

def extract_keyword_components(tree: exp.Expression) -> Set[str]:
    keywords = set()

    if tree.args.get("distinct"):
        keywords.add("distinct")
    if tree.args.get("limit"):
        keywords.add("limit")
    if tree.args.get("group"):
        keywords.add("group by")
    if tree.args.get("order"):
        keywords.add("order by")
    if tree.args.get("having"):
        keywords.add("having")

    from_expr = tree.args.get("from")
    if from_expr:
        for join in from_expr.find_all(exp.Join):
            kind = join.args.get("kind")
            if kind:
                keywords.add(f"{kind.lower()} join")
            else:
                keywords.add("join")

    if tree.args.get("where"):
        keywords.add("where")

    keywords.add("select")
    return keywords


# -------------------- EVALUACIÓN GLOBAL --------------------

def evaluate_component_matching(gold_sql: str, pred_sql: str) -> Dict[str, Dict[str, float]]:
    gold_tree = parse_sql(gold_sql)
    pred_tree = parse_sql(pred_sql)

    gold_select = extract_select_components(gold_tree)
    pred_select = extract_select_components(pred_tree)

    gold_where = extract_where_components(gold_tree)
    pred_where = extract_where_components(pred_tree)

    gold_group = extract_group_by_components(gold_tree)
    pred_group = extract_group_by_components(pred_tree)

    gold_order = extract_order_by_components(gold_tree)
    pred_order = extract_order_by_components(pred_tree)

    gold_kw = extract_keyword_components(gold_tree)
    pred_kw = extract_keyword_components(pred_tree)

    return {
        "select": precision_recall_f1(gold_select, pred_select),
        "where": precision_recall_f1(gold_where, pred_where),
        "group_by": precision_recall_f1(gold_group, pred_group),
        "order_by": precision_recall_f1(gold_order, pred_order),
        "keywords": precision_recall_f1(gold_kw, pred_kw),
    }


app = FastAPI(title="Text-to-SQL Component Matching API")

class ComponentMatchingRequest(BaseModel):
    gold_sql: str
    pred_sql: str

@app.post("/component-matching")
def component_matching(request: ComponentMatchingRequest):
    result = evaluate_component_matching(request.gold_sql, request.pred_sql)
    return {"ok": True, "metrics": result}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

