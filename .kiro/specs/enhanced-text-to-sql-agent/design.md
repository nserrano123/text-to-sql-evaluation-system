# Design Document

## Overview

Este documento describe el diseño para mejorar el agente Text-to-SQL existente implementando las metodologías ACT-SQL, MCS-SQL y CHESS que están descritas en la arquitectura teórica pero no implementadas en el código actual.

## Architecture

### Current Architecture Analysis

El workflow actual (`Agente.json`) tiene la siguiente estructura:

- **Intension**: Analiza la intención del usuario
- **DIN-SQL**: Descompone la pregunta (sin chain-of-thought)
- **VectorTable/VectorQuestions**: Recuperación vectorial básica
- **DEA-SQL**: Planifica 4 queries SQL
- **Generate Sql1**: Genera UN solo SQL (sin múltiples candidatos)

### Enhanced Architecture

La arquitectura mejorada mantendrá la estructura existente pero agregará:

1. **ACT-SQL Chain-of-Thought** en el nodo DIN-SQL
2. **CHESS Schema Pruning** en la recuperación de contexto
3. **MCS-SQL Multi-Prompt Selection** en la generación SQL

## Components and Interfaces

### Component 1: Enhanced DIN-SQL with ACT-SQL

**Purpose**: Agregar chain-of-thought automático al proceso de descomposición

**Interface**:

- **Input**: Pregunta del usuario + contexto de intención
- **Output**: Descomposición + cadena de razonamiento estructurada

**Implementation**:

````json
{
  "name": "Enhanced-DIN-SQL",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "={{ $('Intension').item.json.output.replaceAll('@*SqlGenerator*@','') }}",
    "options": {
      "systemMessage": "=## 🧠 Agente de Descomposición con Chain-of-Thought Automático\n\n### FASE 1: GENERACIÓN AUTOMÁTICA DE CHAIN-OF-THOUGHT\nAntes de descomponer la pregunta, debes generar una cadena de razonamiento paso a paso:\n\n1. **Análisis de Intención**: ¿Qué busca realmente el usuario?\n2. **Identificación de Entidades**: ¿Qué conceptos del ERP están involucrados?\n3. **Relaciones Implícitas**: ¿Qué conexiones entre datos son necesarias?\n4. **Complejidad Estimada**: ¿Qué tan compleja será la consulta SQL?\n5. **Estrategia de Resolución**: ¿Cuál es el mejor enfoque para resolver esto?\n\n### FASE 2: DESCOMPOSICIÓN ESTRUCTURADA\nUsando el chain-of-thought generado, descompón la pregunta en:\n\n**Reformulación Clara**: El usuario desea obtener...\n**Pasos Lógicos**: Secuencia de operaciones necesarias\n**Complejidad**: Fácil/Media/Compleja con justificación\n\n### FORMATO DE SALIDA:\n```\n## Chain-of-Thought Automático:\n1. Análisis de Intención: [razonamiento]\n2. Identificación de Entidades: [razonamiento]\n3. Relaciones Implícitas: [razonamiento]\n4. Complejidad Estimada: [razonamiento]\n5. Estrategia de Resolución: [razonamiento]\n\n## Descomposición Estructurada:\n**Reformulación**: [reformulación clara]\n**Pasos Lógicos**: [pasos numerados]\n**Complejidad**: [nivel con justificación]\n```"
    }
  }
}
````

### Component 2: CHESS Schema Pruning Module

**Purpose**: Implementar pruning selectivo y recuperación jerárquica del esquema

**Interface**:

- **Input**: Pregunta descompuesta + esquema completo
- **Output**: Esquema podado + contexto jerárquico

**Implementation Strategy**:

1. **Nuevo nodo**: `CHESS-Schema-Pruning`
2. **Análisis semántico**: Identifica entidades relevantes en la pregunta
3. **Pruning selectivo**: Elimina tablas/columnas irrelevantes
4. **Recuperación jerárquica**: Expande contexto en niveles según necesidad

````json
{
  "name": "CHESS-Schema-Pruning",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "=Pregunta Descompuesta: {{ $('Enhanced-DIN-SQL').item.json.output }}\n\nEsquema Completo: {{ $('UnirLista').item.json.pageContent }}",
    "options": {
      "systemMessage": "=## 🎯 CHESS Schema Pruning Agent\n\n### OBJETIVO\nImplementar pruning selectivo del esquema para reducir tokens procesados manteniendo calidad.\n\n### FASE 1: ANÁLISIS SEMÁNTICO\n1. Identifica entidades principales mencionadas en la pregunta\n2. Mapea entidades a tablas del esquema\n3. Identifica relaciones necesarias entre tablas\n\n### FASE 2: PRUNING SELECTIVO\n1. Selecciona SOLO tablas directamente relevantes\n2. Incluye tablas de relación necesarias para JOINs\n3. Elimina columnas irrelevantes de tablas seleccionadas\n4. Preserva claves primarias y foráneas necesarias\n\n### FASE 3: RECUPERACIÓN JERÁRQUICA\n**Nivel 1**: Entidades principales identificadas\n**Nivel 2**: Entidades relacionadas directamente\n**Nivel 3**: Entidades de soporte (solo si necesario)\n\n### CRITERIOS DE REDUCCIÓN\n- Objetivo: Reducir tokens en 60%+ manteniendo funcionalidad\n- Preservar: member_id, audit_status, claves de relación\n- Eliminar: Columnas de auditoría no críticas, campos descriptivos largos\n\n### FORMATO DE SALIDA\n```\n## Esquema Podado (Nivel 1):\n[tablas y columnas principales]\n\n## Esquema Expandido (Nivel 2):\n[relaciones necesarias]\n\n## Contexto Adicional (Nivel 3):\n[solo si requerido]\n\n## Métricas de Reducción:\nTokens originales: [número]\nTokens reducidos: [número]\nReducción: [porcentaje]%\n```"
    }
  }
}
````

### Component 3: MCS-SQL Multi-Prompt Generator

**Purpose**: Generar múltiples candidatos SQL y seleccionar el mejor

**Interface**:

- **Input**: Plan de consulta + esquema podado
- **Output**: Mejor consulta SQL seleccionada + métricas de selección

**Implementation Strategy**:

1. **Generador múltiple**: 3 nodos paralelos con prompts diferentes
2. **Selector**: Nodo que evalúa y selecciona el mejor candidato
3. **Validador**: Verificación sintáctica y semántica

```json
{
  "name": "MCS-SQL-Generator-1",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "=Plan SQL: {{ $('DEA-SQL').item.json.output }}\nEsquema: {{ $('CHESS-Schema-Pruning').item.json.output }}",
    "options": {
      "systemMessage": "=## 🎯 SQL Generator - Estilo Conservador\n\nGenera SQL siguiendo un enfoque conservador y explícito:\n- Usa JOINs explícitos siempre\n- Prefiere subconsultas a CTEs complejas\n- Incluye todos los filtros de seguridad\n- Usa alias descriptivos\n\n[resto del prompt de generación SQL]"
    }
  }
}
```

```json
{
  "name": "MCS-SQL-Generator-2",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "=Plan SQL: {{ $('DEA-SQL').item.json.output }}\nEsquema: {{ $('CHESS-Schema-Pruning').item.json.output }}",
    "options": {
      "systemMessage": "=## 🎯 SQL Generator - Estilo Optimizado\n\nGenera SQL siguiendo un enfoque optimizado:\n- Usa CTEs cuando mejore legibilidad\n- Optimiza JOINs para rendimiento\n- Minimiza subconsultas anidadas\n- Usa funciones de ventana cuando sea apropiado\n\n[resto del prompt de generación SQL]"
    }
  }
}
```

```json
{
  "name": "MCS-SQL-Generator-3",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "=Plan SQL: {{ $('DEA-SQL').item.json.output }}\nEsquema: {{ $('CHESS-Schema-Pruning').item.json.output }}",
    "options": {
      "systemMessage": "=## 🎯 SQL Generator - Estilo Directo\n\nGenera SQL siguiendo un enfoque directo y simple:\n- Minimiza complejidad sintáctica\n- Usa la menor cantidad de JOINs posible\n- Prefiere filtros WHERE simples\n- Evita funciones complejas\n\n[resto del prompt de generación SQL]"
    }
  }
}
```

````json
{
  "name": "MCS-SQL-Selector",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "=Candidato 1: {{ $('MCS-SQL-Generator-1').item.json.output }}\nCandidato 2: {{ $('MCS-SQL-Generator-2').item.json.output }}\nCandidato 3: {{ $('MCS-SQL-Generator-3').item.json.output }}\n\nPlan Original: {{ $('DEA-SQL').item.json.output }}",
    "options": {
      "systemMessage": "=## 🎯 MCS-SQL Selector Agent\n\n### OBJETIVO\nSeleccionar el mejor candidato SQL basado en criterios objetivos.\n\n### CRITERIOS DE EVALUACIÓN\n\n**1. Validez Sintáctica (40%)**\n- SQL válido y ejecutable\n- Sintaxis PostgreSQL correcta\n- Nombres de tablas/columnas existentes\n\n**2. Coherencia Semántica (35%)**\n- Responde la pregunta original\n- Lógica de JOINs correcta\n- Filtros apropiados\n\n**3. Seguridad Multi-tenant (15%)**\n- Incluye member_id = $1\n- Incluye audit_status <> 'D'\n- Incluye LIMIT apropiado\n\n**4. Eficiencia (10%)**\n- Minimiza JOINs innecesarios\n- Usa índices disponibles\n- Evita subconsultas complejas\n\n### PROCESO DE SELECCIÓN\n1. Evalúa cada candidato con los criterios\n2. Asigna puntuación 0-100 a cada criterio\n3. Calcula puntuación ponderada total\n4. Selecciona el candidato con mayor puntuación\n5. Si empate, prefiere el más simple\n\n### FORMATO DE SALIDA\n```\n## Evaluación de Candidatos:\n**Candidato 1**: [puntuación] - [justificación]\n**Candidato 2**: [puntuación] - [justificación] \n**Candidato 3**: [puntuación] - [justificación]\n\n## Candidato Seleccionado: [número]\n**Justificación**: [razones de selección]\n**SQL Final**: [consulta seleccionada]\n```"
    }
  }
}
````

## Data Models

### Chain-of-Thought Output Model

```typescript
interface ChainOfThoughtOutput {
  intentionAnalysis: string;
  entityIdentification: string[];
  implicitRelations: string[];
  complexityEstimate: "Easy" | "Medium" | "Complex";
  resolutionStrategy: string;
  structuredDecomposition: {
    reformulation: string;
    logicalSteps: string[];
    complexity: string;
  };
}
```

### Schema Pruning Output Model

```typescript
interface SchemaPruningOutput {
  level1Schema: SchemaEntity[];
  level2Schema: SchemaEntity[];
  level3Schema: SchemaEntity[];
  reductionMetrics: {
    originalTokens: number;
    reducedTokens: number;
    reductionPercentage: number;
  };
}
```

### MCS-SQL Output Model

```typescript
interface MCSQLOutput {
  candidates: SQLCandidate[];
  selectedCandidate: {
    candidateNumber: number;
    sql: string;
    score: number;
    justification: string;
  };
  evaluationMetrics: {
    syntacticScore: number;
    semanticScore: number;
    securityScore: number;
    efficiencyScore: number;
  };
}
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: Chain-of-Thought Completeness

_For any_ user question processed by Enhanced-DIN-SQL, the output should contain all five chain-of-thought components (intention analysis, entity identification, implicit relations, complexity estimate, resolution strategy) before the structured decomposition.
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Schema Pruning Effectiveness

_For any_ schema pruning operation, the reduced schema should contain at least 60% fewer tokens than the original while preserving all entities and relationships necessary to answer the user's question.
**Validates: Requirements 3.4, 4.4**

### Property 3: Multi-Candidate Generation

_For any_ SQL generation request, MCS-SQL should produce exactly 3 distinct SQL candidates using different prompting strategies, and each candidate should be syntactically valid PostgreSQL.
**Validates: Requirements 2.1, 2.2**

### Property 4: Best Candidate Selection

_For any_ set of SQL candidates generated by MCS-SQL, the selector should choose the candidate with the highest weighted score based on the defined criteria (syntactic 40%, semantic 35%, security 15%, efficiency 10%).
**Validates: Requirements 2.3, 2.4**

### Property 5: Security Preservation

_For any_ SQL query generated by the enhanced system, it should include the multi-tenant security filters (member_id = $1, audit_status <> 'D') and appropriate LIMIT clauses.
**Validates: Requirements 7.1, 7.2, 7.4**

### Property 6: Performance Optimization

_For any_ query processed through CHESS schema pruning, the total token count sent to the LLM should be reduced by at least 60% compared to sending the complete schema.
**Validates: Requirements 8.3, 3.4**

### Property 7: Backward Compatibility

_For any_ input that worked in the original system, the enhanced system should produce equivalent or better results while maintaining the same input/output interface.
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 8: Chain-of-Thought Reasoning Quality

_For any_ complex query (classified as Medium or Complex), the chain-of-thought should identify at least 2 implicit relationships and provide a multi-step resolution strategy.
**Validates: Requirements 1.4, 1.5**

### Property 9: Hierarchical Context Efficiency

_For any_ schema pruning operation, Level 1 should contain primary entities, Level 2 should contain direct relationships, and Level 3 should only be populated when necessary for query completeness.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 10: Candidate Diversity

_For any_ MCS-SQL generation, the three candidates should use measurably different SQL construction approaches (conservative, optimized, direct) as evidenced by different JOIN strategies or query structures.
**Validates: Requirements 2.1, 2.5**

## Error Handling

### Chain-of-Thought Failures

- **Fallback**: If ACT-SQL fails, revert to original DIN-SQL behavior
- **Logging**: Record failure reason and context for debugging
- **Recovery**: Attempt simplified chain-of-thought with fewer steps

### Schema Pruning Failures

- **Fallback**: If CHESS pruning fails, use original vector retrieval
- **Validation**: Ensure pruned schema contains minimum required entities
- **Recovery**: Gradually expand schema levels if initial pruning is too aggressive

### Multi-Candidate Generation Failures

- **Fallback**: If MCS-SQL fails, use single best-effort SQL generation
- **Validation**: Ensure at least one syntactically valid candidate is produced
- **Recovery**: Regenerate failed candidates with alternative prompts

### Selection Failures

- **Fallback**: If selector fails, use first syntactically valid candidate
- **Validation**: Ensure selected candidate meets security requirements
- **Recovery**: Apply rule-based selection if AI-based selection fails

## Testing Strategy

### Unit Testing

- Test each new component independently
- Validate chain-of-thought generation with sample questions
- Test schema pruning with various schema sizes
- Verify multi-candidate generation produces distinct results

### Property-Based Testing

- Generate random user questions and verify all properties hold
- Test with various schema configurations and complexity levels
- Validate security properties across all generated SQL
- Test performance properties with large schemas

### Integration Testing

- Test complete enhanced workflow end-to-end
- Verify compatibility with existing N8N infrastructure
- Test fallback mechanisms under failure conditions
- Validate metrics collection and logging functionality

### Performance Testing

- Measure token reduction achieved by CHESS pruning
- Compare response times with and without enhancements
- Test resource usage under concurrent load
- Validate 60% token reduction target is consistently met
