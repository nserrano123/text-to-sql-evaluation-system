# Requirements Document

## Introduction

Esta especificación define los requisitos para mejorar el agente Text-to-SQL existente implementando las metodologías ACT-SQL, MCS-SQL y CHESS que actualmente están descritas en la arquitectura pero no implementadas en el código.

## Glossary

- **ACT-SQL**: Metodología de In-Context Learning con Chain-of-Thought Automático
- **MCS-SQL**: Metodología de Multiple-Choice Selection con Multi-Prompts
- **CHESS**: Metodología de Contextual Harnessing for Efficient SQL Synthesis
- **Chain-of-Thought (CoT)**: Cadenas de razonamiento paso a paso generadas automáticamente
- **Multi-Prompt**: Generación de múltiples candidatos usando diferentes prompts
- **Schema_Pruning**: Selección selectiva de partes relevantes del esquema de base de datos
- **N8N_Workflow**: Flujo de trabajo implementado en la plataforma N8N
- **SQL_Generator**: Agente especializado en generar consultas SQL

## Requirements

### Requirement 1: Implementar ACT-SQL Chain-of-Thought Automático

**User Story:** Como desarrollador del sistema, quiero que el agente DIN-SQL genere cadenas de razonamiento automáticas, para que el proceso de descomposición sea más robusto y preciso en consultas complejas.

#### Acceptance Criteria

1. WHEN el agente DIN-SQL recibe una pregunta del usuario, THE System SHALL generar automáticamente una cadena de razonamiento paso a paso antes de la descomposición
2. WHEN se genera la cadena de razonamiento, THE System SHALL incluir pasos intermedios que expliquen el proceso de análisis de la pregunta
3. WHEN la cadena de razonamiento está completa, THE System SHALL usar esta información para mejorar la reformulación de la pregunta
4. THE Chain_of_Thought_Generator SHALL producir razonamiento estructurado sin requerir ejemplos anotados manualmente
5. WHEN se procesa una consulta multi-turn, THE System SHALL mantener contexto del razonamiento previo

### Requirement 2: Implementar MCS-SQL Multiple-Choice Selection

**User Story:** Como desarrollador del sistema, quiero que el generador SQL produzca múltiples candidatos de consulta y seleccione el mejor, para mejorar la robustez ante variaciones de prompt y reducir errores.

#### Acceptance Criteria

1. WHEN el agente Generate_Sql recibe un plan de consulta, THE System SHALL generar al menos 3 candidatos SQL diferentes usando prompts variados
2. WHEN se generan múltiples candidatos SQL, THE System SHALL aplicar criterios sintácticos para validar cada consulta
3. WHEN se validan los candidatos, THE System SHALL aplicar criterios semánticos para evaluar coherencia con la intención
4. WHEN todos los criterios son evaluados, THE System SHALL seleccionar el candidato más coherente y ajustado
5. IF ningún candidato pasa la validación, THEN THE System SHALL generar nuevos candidatos con prompts alternativos

### Requirement 3: Implementar CHESS Schema Pruning Selectivo

**User Story:** Como desarrollador del sistema, quiero que la recuperación de contexto implemente pruning selectivo del esquema, para reducir significativamente los tokens procesados manteniendo la calidad.

#### Acceptance Criteria

1. WHEN se inicia la recuperación de contexto, THE System SHALL identificar las partes más relevantes del esquema basado en la pregunta descompuesta
2. WHEN se identifican las partes relevantes, THE System SHALL aplicar pruning selectivo eliminando tablas y columnas irrelevantes
3. WHEN se aplica el pruning, THE System SHALL mantener las relaciones necesarias entre las entidades seleccionadas
4. THE Schema_Pruning_Module SHALL reducir el número de tokens procesados en al menos 60% comparado con el esquema completo
5. WHEN se construye el contexto reducido, THE System SHALL preservar suficiente información semántica para generar SQL correcto

### Requirement 4: Implementar Recuperación Jerárquica CHESS

**User Story:** Como desarrollador del sistema, quiero que la recuperación de contexto sea jerárquica, para optimizar la eficiencia sin degradar el rendimiento.

#### Acceptance Criteria

1. WHEN se requiere contexto del esquema, THE System SHALL implementar recuperación en múltiples niveles jerárquicos
2. WHEN se ejecuta el primer nivel, THE System SHALL recuperar entidades principales relacionadas con la pregunta
3. WHEN se ejecuta el segundo nivel, THE System SHALL expandir a entidades relacionadas solo si es necesario
4. THE Hierarchical_Retrieval SHALL balancear cobertura semántica con eficiencia computacional
5. WHEN se completa la recuperación jerárquica, THE System SHALL proporcionar contexto optimizado al planificador SQL

### Requirement 5: Integrar Metodologías en Pipeline Existente

**User Story:** Como desarrollador del sistema, quiero que las nuevas metodologías se integren sin romper el flujo existente, para mantener la compatibilidad con el sistema actual.

#### Acceptance Criteria

1. WHEN se implementan las nuevas metodologías, THE System SHALL mantener la compatibilidad con los nodos N8N existentes
2. WHEN se ejecuta el workflow mejorado, THE System SHALL preservar todas las funcionalidades actuales
3. WHEN ocurre un error en las nuevas metodologías, THE System SHALL hacer fallback al comportamiento original
4. THE Enhanced_Workflow SHALL mantener los mismos puntos de entrada y salida que el workflow actual
5. WHEN se completa una consulta, THE System SHALL registrar métricas de rendimiento de las nuevas metodologías

### Requirement 6: Validar Mejoras de Rendimiento

**User Story:** Como investigador, quiero medir el impacto de las nuevas metodologías, para validar que efectivamente mejoran la precisión y robustez del sistema.

#### Acceptance Criteria

1. WHEN se ejecuta una consulta con las nuevas metodologías, THE System SHALL registrar métricas de Execution Accuracy
2. WHEN se completa el procesamiento, THE System SHALL medir el Time-to-Answer comparado con el sistema original
3. WHEN se aplica CHESS, THE System SHALL registrar la reducción de tokens procesados
4. THE Metrics_Collector SHALL almacenar datos para análisis comparativo con el sistema base
5. WHEN se evalúa MCS-SQL, THE System SHALL registrar la tasa de éxito en la selección del mejor candidato

### Requirement 7: Mantener Seguridad Multi-tenant

**User Story:** Como administrador del sistema, quiero que las mejoras mantengan todas las restricciones de seguridad multi-tenant, para garantizar el aislamiento de datos entre empresas.

#### Acceptance Criteria

1. WHEN se generan múltiples candidatos SQL, THE System SHALL aplicar filtros member_id en todos los candidatos
2. WHEN se aplica schema pruning, THE System SHALL respetar las restricciones de acceso por empresa
3. WHEN se ejecuta chain-of-thought, THE System SHALL evitar exponer información de otras empresas
4. THE Security_Validator SHALL verificar que todas las consultas generadas cumplan las políticas multi-tenant
5. WHEN se selecciona el mejor candidato, THE System SHALL validar que no contenga vulnerabilidades de seguridad

### Requirement 8: Optimizar Recursos Computacionales

**User Story:** Como operador del sistema, quiero que las mejoras optimicen el uso de recursos, para mantener tiempos de respuesta aceptables a pesar de la mayor complejidad.

#### Acceptance Criteria

1. WHEN se ejecuta el chain-of-thought automático, THE System SHALL completar el proceso en menos de 2 segundos adicionales
2. WHEN se generan múltiples candidatos SQL, THE System SHALL paralelizar la generación cuando sea posible
3. WHEN se aplica schema pruning, THE System SHALL reducir el tiempo de procesamiento del LLM
4. THE Resource_Monitor SHALL alertar si el consumo de recursos excede los límites establecidos
5. WHEN se completa una consulta compleja, THE System SHALL mantener el tiempo total de respuesta bajo 30 segundos

### Requirement 9: Implementar Logging y Debugging

**User Story:** Como desarrollador, quiero tener visibilidad completa del proceso de las nuevas metodologías, para poder debuggear y optimizar el sistema.

#### Acceptance Criteria

1. WHEN se ejecuta ACT-SQL, THE System SHALL registrar cada paso del chain-of-thought generado
2. WHEN se generan múltiples candidatos, THE System SHALL loggear todos los candidatos y los criterios de selección
3. WHEN se aplica CHESS pruning, THE System SHALL registrar qué partes del esquema fueron incluidas/excluidas
4. THE Debug_Logger SHALL proporcionar trazabilidad completa de cada decisión del sistema
5. WHEN ocurre un error, THE System SHALL registrar el contexto completo para facilitar el debugging

### Requirement 10: Configurabilidad de Metodologías

**User Story:** Como administrador del sistema, quiero poder habilitar/deshabilitar cada metodología independientemente, para poder hacer pruebas A/B y rollbacks seguros.

#### Acceptance Criteria

1. THE System SHALL permitir habilitar/deshabilitar ACT-SQL mediante configuración
2. THE System SHALL permitir habilitar/deshabilitar MCS-SQL mediante configuración
3. THE System SHALL permitir habilitar/deshabilitar CHESS mediante configuración
4. WHEN una metodología está deshabilitada, THE System SHALL usar el comportamiento original para esa función
5. THE Configuration_Manager SHALL validar que las combinaciones de metodologías sean compatibles
