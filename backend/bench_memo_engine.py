"""
Bench Memo Engine for Arabic Legal Cases.

Generates a structured "Bench Memo" for judges, focusing on:
- Summary of Facts (Extracted timeline/events)
- Procedural Summary (Dates, jurisdiction)
- Core Legal Issues (Points of conflict)
- Statutory References (Relevant laws)
"""

from typing import Dict, List, Any, Optional
from models import AnalyzeResponse, BenchMemoResponse
import logging

logger = logging.getLogger(__name__)

class BenchMemoEngine:
    def __init__(self):
        pass

    def generate_memo(self, analysis: AnalyzeResponse, case_text: Optional[str] = None) -> BenchMemoResponse:
        """
        Generate a structured Bench Memo from existing analysis data.
        """
        classification = analysis.classification
        principles = analysis.legal_principles
        entities = analysis.entities or {}
        trends = analysis.trends
        recommendation = analysis.recommendation

        # 1. Summary of Facts
        facts_ar = entities.get("facts_block", "لم يتم استخراج الوقائع بشكل مفصل.")
        if facts_ar == "N/A" or not facts_ar:
            facts_ar = "يرجى مراجعة نص الدعوى لاستخراج الوقائع."
        
        # Simple English fallback for facts if not present in entities
        facts_en = entities.get("facts_block_en", "Summary of facts not available in English.")
        if facts_en == "Summary of facts not available in English." and facts_ar != "لم يتم استخراج الوقائع بشكل مفصل.":
            facts_en = "Fact summary available in Arabic. Please refer to the Arabic version for full details."

        # 2. Procedural Summary
        date = entities.get("date", "N/A")
        court = entities.get("court_name", "N/A")
        
        proc_ar = f"تاريخ الواقعة/الدعوى: {date}\nالمحكمة المختصة: {court}\nنوع القضية: {classification.name_ar}"
        proc_en = f"Date of Incident/Case: {date}\nCompetent Court: {court}\nCase Type: {classification.name_en}"

        # 3. Legal Issues (Conflict Points)
        issues_ar = []
        issues_en = []
        if classification.case_type == "labor_dispute":
            issues_ar = ["مشروعية إنهاء عقد العمل", "استحقاق مكافأة نهاية الخدمة"]
            issues_en = ["Legality of employment contract termination", "Entitlement to end-of-service benefits"]
        elif classification.case_type == "contract_dispute":
            issues_ar = ["الإخلال بالالتزامات التعاقدية", "تفسير بنود العقد"]
            issues_en = ["Breach of contractual obligations", "Interpretation of contract clauses"]
        else:
            issues_ar = [f"تكييف النزاع كـ {classification.name_ar}"]
            issues_en = [f"Characterization of the dispute as {classification.name_en}"]

        # 4. Statutory References
        refs = []
        for p in principles[:3]:
            refs.append({
                "article": p.name_ar,
                "context": p.description_ar,
                "article_en": p.name_en,
                "context_en": getattr(p, 'description_en', "") or ""
            })

        # 5. Recommended Actions
        actions_ar = [
            "التحقق من صحة التبليغ الإلكتروني للكيان.",
            "طلب تقديم أصل العقد/المستندات للمطابقة.",
            "حصر المبالغ المتنازع عليها بدقة."
        ]
        actions_en = [
            "Verify the validity of electronic notification.",
            "Request original documents for verification.",
            "Quantify disputed amounts precisely."
        ]

        # 6. Compose Final Memo (Arabic)
        issues_str_ar = "\n".join([f"- {issue}" for issue in issues_ar])
        refs_str_ar = "\n".join([f"- {ref['article']}: {ref['context']}" for ref in refs])
        actions_str_ar = "\n".join([f"- {action}" for action in actions_ar])

        memo_ar = f"""
### مذكرة تلخيص للقاضي (Bench Memo)

**أولاً: ملخص الوقائع**
{facts_ar}

**ثانياً: الجانب الإجرائي**
- النوع: {classification.name_ar}
- {proc_ar}

**ثالثاً: المسائل القانونية المحورية**
{issues_str_ar}

**رابعاً: الأسانيد النظامية المقترحة**
{refs_str_ar}

**خامساً: إجراءات مقترحة للدائرة**
{actions_str_ar}
"""

        # 7. Compose Final Memo (English)
        issues_str_en = "\n".join([f"- {issue}" for issue in issues_en])
        refs_str_en = "\n".join([f"- {ref['article_en']}" for ref in refs])
        
        memo_en = f"""
### Judge's Bench Memo

**I. Summary of Facts**
{facts_en}

**II. Procedural Summary**
- Type: {classification.name_en}
- Court: {court}
- Date: {date}

**III. Core Legal Issues**
{issues_str_en}

**IV. Statutory References**
{refs_str_en}

**V. Recommended Actions**
{chr(10).join([f"- {a}" for a in actions_en])}
"""

        return BenchMemoResponse(
            summary_of_facts_ar=facts_ar,
            summary_of_facts_en=facts_en,
            procedural_summary_ar=proc_ar,
            procedural_summary_en=proc_en,
            legal_issues_ar=issues_ar,
            legal_issues_en=issues_en,
            statutory_references=refs,
            recommended_actions_ar=actions_ar,
            recommended_actions_en=actions_en,
            bench_memo_ar=memo_ar.strip(),
            bench_memo_en=memo_en.strip()
        )

# Global instance
bench_memo_engine = BenchMemoEngine()
