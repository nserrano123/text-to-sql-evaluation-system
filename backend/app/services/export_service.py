"""Service for exporting evaluation data in various formats"""

import pandas as pd
from typing import Dict, Any, List
from io import StringIO
from ..database import get_supabase_client


class ExportService:
    """Service for exporting evaluation data to different formats"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def export_to_csv(self) -> str:
        """
        Export all evaluation data to CSV format with joins between all tables.
        
        Returns:
            str: CSV content as string
        """
        # Get all data with joins
        query = """
        SELECT 
            gq.id as gold_query_id,
            gq.chat_input,
            gq.session_id,
            gq.member_id,
            gq.clasificacion,
            gq.pregunta_descompuesta,
            gq.tablas_columnas_ddl,
            gq.sql_reference,
            gq.created_at as gold_query_created_at,
            
            e.id as evaluation_id,
            e.generated_sql,
            e.evaluation_date,
            e.created_at as evaluation_created_at,
            
            ea.id as execution_accuracy_id,
            ea.results_match,
            ea.is_correct,
            ea.evaluator_notes as execution_notes,
            ea.created_at as execution_accuracy_created_at,
            
            tta.id as time_to_answer_id,
            tta.start_time,
            tta.end_time,
            tta.duration_seconds,
            tta.created_at as time_to_answer_created_at,
            
            cm.id as component_matching_id,
            cm.select_correct,
            cm.where_correct,
            cm.group_by_correct,
            cm.order_by_correct,
            cm.keywords_correct,
            cm.f1_score,
            cm.evaluator_notes as component_notes,
            cm.created_at as component_matching_created_at
            
        FROM gold_queries gq
        LEFT JOIN evaluations e ON gq.id = e.gold_query_id
        LEFT JOIN execution_accuracy ea ON e.id = ea.evaluation_id
        LEFT JOIN time_to_answer tta ON e.id = tta.evaluation_id
        LEFT JOIN component_matching cm ON e.id = cm.evaluation_id
        ORDER BY gq.created_at, e.evaluation_date
        """
        
        try:
            # Execute the query
            result = self.client.rpc('execute_sql', {'query': query}).execute()
            
            if not result.data:
                # If RPC doesn't work, fall back to individual queries and manual joins
                return await self._export_csv_fallback()
            
            # Convert to DataFrame
            df = pd.DataFrame(result.data)
            
            # Convert to CSV
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue()
            
        except Exception:
            # Fallback to manual joins if RPC fails
            return await self._export_csv_fallback()
    
    async def _export_csv_fallback(self) -> str:
        """
        Fallback method to export CSV using individual table queries and pandas joins.
        
        Returns:
            str: CSV content as string
        """
        # Get data from each table
        gold_queries = self.client.table('gold_queries').select('*').execute().data
        evaluations = self.client.table('evaluations').select('*').execute().data
        execution_accuracy = self.client.table('execution_accuracy').select('*').execute().data
        time_to_answer = self.client.table('time_to_answer').select('*').execute().data
        component_matching = self.client.table('component_matching').select('*').execute().data
        
        # Convert to DataFrames
        df_gold = pd.DataFrame(gold_queries)
        df_eval = pd.DataFrame(evaluations)
        df_ea = pd.DataFrame(execution_accuracy)
        df_tta = pd.DataFrame(time_to_answer)
        df_cm = pd.DataFrame(component_matching)
        
        # Rename columns to avoid conflicts
        df_gold = df_gold.add_suffix('_gold')
        df_gold = df_gold.rename(columns={'id_gold': 'gold_query_id'})
        
        df_eval = df_eval.add_suffix('_eval')
        df_eval = df_eval.rename(columns={
            'id_eval': 'evaluation_id',
            'gold_query_id_eval': 'gold_query_id'
        })
        
        df_ea = df_ea.add_suffix('_ea')
        df_ea = df_ea.rename(columns={
            'id_ea': 'execution_accuracy_id',
            'evaluation_id_ea': 'evaluation_id'
        })
        
        df_tta = df_tta.add_suffix('_tta')
        df_tta = df_tta.rename(columns={
            'id_tta': 'time_to_answer_id',
            'evaluation_id_tta': 'evaluation_id'
        })
        
        df_cm = df_cm.add_suffix('_cm')
        df_cm = df_cm.rename(columns={
            'id_cm': 'component_matching_id',
            'evaluation_id_cm': 'evaluation_id'
        })
        
        # Perform joins
        # Start with gold_queries as base
        result_df = df_gold
        
        # Left join with evaluations
        if not df_eval.empty:
            result_df = result_df.merge(df_eval, on='gold_query_id', how='left')
        
        # Left join with execution_accuracy
        if not df_ea.empty and 'evaluation_id' in result_df.columns:
            result_df = result_df.merge(df_ea, on='evaluation_id', how='left')
        
        # Left join with time_to_answer
        if not df_tta.empty and 'evaluation_id' in result_df.columns:
            result_df = result_df.merge(df_tta, on='evaluation_id', how='left')
        
        # Left join with component_matching
        if not df_cm.empty and 'evaluation_id' in result_df.columns:
            result_df = result_df.merge(df_cm, on='evaluation_id', how='left')
        
        # Convert to CSV
        csv_buffer = StringIO()
        result_df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()  
  
    async def export_to_latex(self) -> str:
        """
        Export summary metrics to LaTeX table format compatible with IEEEtran.
        
        Returns:
            str: LaTeX table content as string
        """
        # Get summary metrics
        from .metrics_summary_service import MetricsSummaryService
        from .execution_accuracy_service import ExecutionAccuracyService
        from .time_to_answer_service import TimeToAnswerService
        from .component_matching_service import ComponentMatchingService
        from ..repositories.evaluation_repository import EvaluationRepository
        
        # Initialize services
        eval_repo = EvaluationRepository()
        ex_service = ExecutionAccuracyService()
        tta_service = TimeToAnswerService()
        cm_service = ComponentMatchingService()
        
        summary_service = MetricsSummaryService(
            eval_repo, ex_service, tta_service, cm_service
        )
        
        # Get metrics
        summary = await summary_service.get_metrics_summary()
        
        # Generate LaTeX table
        latex_content = self._generate_latex_table(summary)
        
        return latex_content
    
    def _generate_latex_table(self, summary) -> str:
        """
        Generate LaTeX table content from metrics summary.
        
        Args:
            summary: MetricsSummary object with all metrics
            
        Returns:
            str: LaTeX table content
        """
        # Format component scores
        component_scores = summary.component_scores
        select_f1 = component_scores.get('select', 0.0)
        where_f1 = component_scores.get('where', 0.0)
        group_by_f1 = component_scores.get('group_by', 0.0)
        order_by_f1 = component_scores.get('order_by', 0.0)
        keywords_f1 = component_scores.get('keywords', 0.0)
        
        # Calculate average F1 score
        avg_f1 = (select_f1 + where_f1 + group_by_f1 + order_by_f1 + keywords_f1) / 5
        
        latex_table = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Resultados de Evaluación del Modelo Text-to-SQL}}
\\label{{tab:evaluation_results}}
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Métrica}} & \\textbf{{Valor}} \\\\
\\hline
\\hline
Consultas Totales & {summary.total_evaluations} \\\\
\\hline
Consultas Evaluadas & {summary.completed_evaluations} \\\\
\\hline
Execution Accuracy (EX) & {summary.execution_accuracy:.2f}\\% \\\\
\\hline
Tiempo Promedio de Respuesta (TTA) & {summary.average_time_to_answer:.2f}s \\\\
\\hline
\\multicolumn{{2}}{{|c|}}{{\\textbf{{F1 Score por Componente}}}} \\\\
\\hline
SELECT & {select_f1:.4f} \\\\
\\hline
WHERE & {where_f1:.4f} \\\\
\\hline
GROUP BY & {group_by_f1:.4f} \\\\
\\hline
ORDER BY & {order_by_f1:.4f} \\\\
\\hline
KEYWORDS & {keywords_f1:.4f} \\\\
\\hline
F1 Score Promedio & {avg_f1:.4f} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}"""
        
        return latex_table