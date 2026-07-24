# Dataset de evaluación multiturno — especificación

Archivo: **`preguntas_multiturno.csv`** (UTF-8 con BOM). Generado por
[`generar_multiturno.py`](../generar_multiturno.py) a partir de las preguntas de
la configuración foco `RAG+Memoria+Intención+DIN+DEA`.

## Propósito

Medir dos capacidades conversacionales que la *Execution Accuracy* de un solo
turno **no** captura:

1. **Gating de intención** — ¿el sistema decide correctamente *cuándo* ejecutar
   SQL y cuándo no?
2. **Uso de memoria** — cuando sí corresponde ejecutar SQL en un turno de
   seguimiento, ¿construye la consulta a partir del contexto acumulado
   (la entidad / resultado de turnos anteriores)?

El **orden de los turnos importa**: cada fila con `depends_on_turn` solo tiene
sentido después del turno indicado.

## Estructura

- 100 conversaciones (`conversation_id` 1–100 / `session_id` `MT001`…`MT100`).
- 5 a 10 turnos por conversación; una fila por turno.
- Cada conversación mezcla, como mínimo, turnos que **deben** ejecutar SQL,
  turnos que **no** deben hacerlo y (en la mayoría) turnos ambiguos.

## Columnas

| Columna | Descripción |
|---|---|
| `conversation_id` | Identificador numérico de la conversación. |
| `session_id` | Id de sesión (`MTxxx`); **ejecutar los turnos en orden** dentro de la misma sesión. |
| `turn_index` | Orden del turno dentro de la conversación (1…N). |
| `expected_action` | **Etiqueta de oro del gating**: `EXECUTE_SQL`, `NO_SQL` o `CLARIFY`. |
| `requires_context` | `Si` si el turno depende de contexto previo (memoria). |
| `depends_on_turn` | `turn_index` del que depende este turno (vacío si es independiente). |
| `subject_entity` | Entidad de dominio activa en ese punto (p. ej. *producto*, *cuenta bancaria*). |
| `user_message` | Mensaje del usuario para ese turno (lo que se envía al sistema). |
| `gold_sql` | SQL de referencia real (solo en turnos semilla / cambio de tema). Vacío en seguimientos contextuales. |
| `expected_behavior` | Qué se espera que haga el sistema; para SQL contextual, la transformación esperada respecto al turno del que depende. |
| `turn_type` | Rol del turno (ver abajo). |
| `seed_id` | Traza a la pregunta semilla del dataset original. |

## Valores de `expected_action`

- **`EXECUTE_SQL`** — debe generar y ejecutar SQL.
  - `seed_sql`: pregunta inicial autónoma (trae `gold_sql`).
  - `switch_sql`: cambio de tema con una nueva entidad (trae `gold_sql`); a partir
    de aquí la memoria debe apuntar a la **nueva** entidad.
  - `ctx_*`: seguimiento que **depende del contexto** (`requires_context = Si`).
    El SQL correcto depende de la entidad/resultado del turno `depends_on_turn`,
    por eso `gold_sql` va vacío y la transformación esperada está en
    `expected_behavior`.
- **`NO_SQL`** — mensaje conversacional (saludo, cortesía, pregunta meta,
  fuera de dominio, o explicación conceptual respondible con documentación del
  esquema). El sistema **no debe** ejecutar SQL.
- **`CLARIFY`** — petición ambigua sin entidad/métrica resoluble. El sistema
  **debe pedir aclaración**, no ejecutar SQL.

## Métricas sugeridas

Sea, por turno, `pred_action` la decisión real del sistema y `pred_sql` el SQL que
haya generado.

1. **Gating Accuracy** (decisión de intención)
   `#(pred_action == expected_action) / #turnos`.
   Reportar además la matriz de confusión 3×3 y, en particular:
   - **False-execute rate**: turnos `NO_SQL`/`CLARIFY` en los que el sistema
     ejecutó SQL (el error más costoso: consulta innecesaria a la BD).
   - **False-abstain rate**: turnos `EXECUTE_SQL` en los que no ejecutó.

2. **Context Resolution Accuracy** (memoria) — solo sobre turnos con
   `requires_context = Si` y `expected_action = EXECUTE_SQL`:
   proporción en los que el SQL generado referencia la entidad correcta
   (la del turno `depends_on_turn`) y aplica la transformación de
   `expected_behavior`. Puede evaluarse por *execution match* contra el resultado
   esperado o con un juez LLM que compare contra `expected_behavior`.

3. **Conversational Success Rate (turno)** — turno correcto si acierta el gating
   **y** (cuando es SQL) produce el resultado correcto.

4. **Dialogue Success Rate (conversación)** — proporción de conversaciones en las
   que **todos** los turnos son correctos (métrica estricta, sensible al orden).

## Reproducibilidad

`generar_multiturno.py` usa `SEED = 42`; volver a ejecutarlo produce exactamente
el mismo CSV. Para variar el conjunto, cambiar `SEED`, `N_CONVERSACIONES` o los
rangos `TURNOS_MIN`/`TURNOS_MAX`.
