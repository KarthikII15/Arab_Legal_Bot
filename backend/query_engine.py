"""
Deterministic Query Engine for Interactive Legal Panel.

Routes structured user queries to specific analysis outputs without
using generative AI, ensuring safety and explainability.
"""

import logging
from typing import Dict, Any, List
from models import AnalyzeResponse, QueryResponse

logger = logging.getLogger(__name__)

def process_query(query_type: str, analysis_data: AnalyzeResponse) -> QueryResponse:
    """
    Process a structured query based on existing analysis data.
    
    Args:
        query_type: One of 'outcome', 'principles', 'similar_cases', 'compensation', 'confidence'
        analysis_data: The full analysis result object
        
    Returns:
        QueryResponse object with the answer and source
    """
    logger.info(f"Processing query: {query_type}")
    
    if query_type == "outcome":
        rec = analysis_data.recommendation
        if not rec:
            return QueryResponse(answer="لا تتوفر توصية كافية لهذه القضية.", type="text", source="recommendation_engine")
        
        direction_map = {
            "plaintiff_likely": "نرجح نجاح المدعي في هذه الدعوى.",
            "defendant_likely": "نرجح رفض الدعوى لصالح المدعى عليه.",
            "uncertain": "النتيجة غير مؤكدة وتحتاج لمزيد من الأدلة.",
            "insufficient_data": "البيانات غير كافية للتنبؤ."
        }
        answer = direction_map.get(rec.direction, "اتجاه غير محدد")
        confidence_pct = int(rec.confidence * 100)
        full_answer = f"{answer} (نسبة الثقة: {confidence_pct}%)"
        
        return QueryResponse(
            answer=full_answer,
            type="text", 
            source="recommendation_engine",
            data={"direction": rec.direction, "confidence": rec.confidence}
        )

    elif query_type == "principles":
        principles = analysis_data.legal_principles
        if not principles:
            return QueryResponse(answer="لم يتم استخراج مبادئ قانونية محددة.", type="text", source="legal_principles_engine")
            
        principle_names = [f"- {p.name_ar} ({p.source_section})" for p in principles[:5]]
        answer = "المبادئ القانونية المطبقة هي:\n" + "\n".join(principle_names)
        
        return QueryResponse(
            answer=answer,
            type="list",
            source="legal_principles_engine",
            data={"principles": [p.dict() for p in principles]}
        )

    elif query_type == "similar_cases":
        # We don't have the similar cases list in AnalyzeResponse directly usually, 
        # but in our system the frontend has it separately usually. 
        # However, AnalyzeResponse MIGHT have trends data which comes from similar cases.
        # But wait, AnalyzeResponse structure in models.py:
        # classification, legal_principles, trends, recommendation.
        # It does NOT have 'similar_cases' list details (ids, texts) usually, those come from /similar endpoint.
        # BUT, 'trend_stats' has 'sample_size'.
        # If the user wants specific similar cases, the backend /analyze usually returns trends based on them.
        # For this engine, we might only be able to give stats unless we pass similar cases list too.
        # Ref checking models.py... AnalyzeResponse has classification, legal_principles, trends, recommendation.
        # It does NOT contain the list of actual similar case objects.
        # So we can only summarize trends here.
        
        trends = analysis_data.trends
        if not trends:
             return QueryResponse(answer="لا توجد سوابق قضائية كافية.", type="text", source="trend_analyzer")

        answer = f"تم العثور على {trends.sample_size} سابقة قضائية مشابهة. " \
                 f"نسبة منها انتهت لصالح المدعي: {trends.plaintiff_win_rate}%."
                 
        return QueryResponse(
            answer=answer,
            type="stats",
            source="trend_analyzer",
            data=trends.dict()
        )

    elif query_type == "compensation":
        trends = analysis_data.trends
        if not trends or trends.average_compensation == 0:
            return QueryResponse(answer="لا توجد بيانات كافية عن التعويضات أو القضية لا تتضمن تعويضاً مالياً.", type="text", source="trend_analyzer")
            
        avg = "{:,}".format(int(trends.average_compensation))
        max_comp = "{:,}".format(int(max(trends.compensation_range.values()) if trends.compensation_range else 0))
        
        answer = f"متوسط التعويض في قضايا مشابهة: {avg} ريال سعودي.\n" \
                 f"أعلى تعويض مسجل: {max_comp} ريال."
                 
        return QueryResponse(
            answer=answer,
            type="stats",
            source="trend_analyzer",
            data={"average": trends.average_compensation}
        )

    elif query_type == "confidence":
        rec = analysis_data.recommendation
        if not rec:
             return QueryResponse(answer="غير متاح.", type="text", source="system")
             
        answer = f"مستوى الموثوقية: {rec.reliabilityAr if hasattr(rec, 'reliabilityAr') else rec.reliability}.\n" \
                 f"هذا التحليل يستند إلى {rec.based_on_sample_size} سابقة قضائية."
                 
        return QueryResponse(
            answer=answer,
            type="text",
            source="recommendation_engine",
            data={"reliability": rec.reliability}
        )

    else:
        return QueryResponse(answer="نوع استفسار غير معروف.", type="error", source="system")
