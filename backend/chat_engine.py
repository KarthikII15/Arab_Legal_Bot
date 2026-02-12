# -*- coding: utf-8 -*-
"""
Chat Engine: Manages conversational interactions with the legal analysis system.
Maintains context and routes user messages to appropriate analysis engines.
"""

import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# Try to import deep-translator for user message translation
try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
    logger.warning("deep-translator not found. Install it for translation features: pip install deep-translator")

# Try to import LocalLLM
try:
    from llm_local import LocalLLM
    HAS_LLM = True
except ImportError:
    HAS_LLM = False
    logger.warning("LocalLLM module not found or failed to import.")

try:
    from research_engine import LegalResearchEngine
    HAS_RESEARCH = True
except ImportError:
    HAS_RESEARCH = False
    logger.warning("LegalResearchEngine module not found.")




class ConversationContext:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 20):
        self.messages: List[Dict[str, Any]] = []
        self.analysis_data: Optional[Dict] = None  # Stores current case analysis
        self.case_text: Optional[str] = None  # Stores current case text
        self.max_history = max_history
        
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history."""
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,  # "user" or "assistant"
            "content": content,
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def set_analysis(self, analysis_data: Dict, case_text: str):
        """Store the current case analysis data."""
        self.analysis_data = analysis_data
        self.case_text = case_text
    
    def get_last_n_messages(self, n: int) -> List[Dict]:
        """Get last n messages for context."""
        return self.messages[-n:] if self.messages else []
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []
        self.analysis_data = None
        self.case_text = None


class ChatEngine:
    """
    Handles conversational interactions with the legal analysis system.
    Routes user queries to appropriate analysis engines based on intent detection.
    """
    
    def __init__(self):
        self.context = ConversationContext()
        self.intent_keywords = self._initialize_intents()
        # Initialize Local LLM (lazy loading inside the class)
        self.llm = LocalLLM() if HAS_LLM else None
        # Initialize Legal Research Engine
        self.research_engine = LegalResearchEngine() if HAS_RESEARCH else None
        # Shared analyzer logic
        self.analyzer = None
        
    def set_analyzer(self, analyzer_func):
        """Inject the full analysis pipeline function."""
        self.analyzer = analyzer_func
        
    def _initialize_intents(self) -> Dict[str, List[str]]:
        """Define intent detection keywords in Arabic and English."""
        return {
            "case_summary": ["ملخص", "summary", "ملخص القضية", "summarize", "اختصار", "case_summary", "show_details"],
            "case_type": ["النوع", "type", "classification", "التصنيف", "نوع القضية"],
            "similar_cases": ["حالات مشابهة", "similar", "precedent", "similar cases", "قضايا شبيهة", "قضايا مشابهة", "مشابهة", "search_similar"],
            "legal_principles": ["المبادئ", "principles", "قواعد قانونية", "legal_principles"],
            "trends": ["الاتجاهات", "trends", "statistics", "إحصائيات", "معدلات"],
            "recommendation": ["توصية", "advice", "رأي", "اقتراح", "recommendations"],
            "full_analysis": ["تحليل", "analyze", "analysis", "تحليل شامل", "اشرح", "full_analysis"],
            "draft": ["مسودة", "draft", "نماذج"],
            "draft_claim": ["لائحة دعوى", "plaintiff claim", "صحيفة دعوى", "claim draft", "تقديم دعوى", "plaintiff_claim"],
            "draft_defense": ["مذكرة دفاع", "defense memo", "defense draft", "مذكرة جوابية", "رد على دعوى", "defense_memo"],
            "outcome": ["النتيجة", "outcome", "result", "probability", "احتمالية"],
            "compensation": ["تعويض", "compensation", "damages", "amount", "مبلغ"],
            "entities": ["الأطراف", "parties", "entities", "من", "شخصيات"]
        }

    def _get_legal_context(self, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Retrieve relevant legal articles for the query."""
        if not self.research_engine:
            return "", []
        
        results = self.research_engine.search(query, top_k=2)
        if not results:
            return "", []
            
        context_parts = []
        citations = []

        for res in results:
            article = res['article']
            score = res['score']
            if score > 50: # Only include relevant articles
                context_parts.append(f"Article {article['article_number']} ({article['source']}):\n{article['text_ar']}")
                citations.append({
                    "source": article['source'],
                    "article_number": article['article_number'],
                    "text": article['text_ar'],
                    "confidence": score
                })
        
        context_str = ""
        if context_parts:
            context_str = "المواد النظامية ذات الصلة:\n" + "\n---\n".join(context_parts)
            
        return context_str, citations
    
    def _is_likely_case(self, text: str) -> bool:
        """Detect if text is likely a legal case description."""
        if len(text) < 100:
            return False
            
        case_markers = [
            "الوقائع", "الأسباب", "منطوق الحكم", "حكمت المحكمة", 
            "المدعي", "المدعى عليه", "قضية رقم", "بناءً على"
        ]
        
        # Count how many markers are present
        matches = sum(1 for marker in case_markers if marker in text)
        
        # If it's long and has legal terms, it's likely a case description
        return matches >= 2 or (len(text) > 500 and matches >= 1)

    def detect_intent(self, query: str) -> str:
        """Detect user's intent from their message with priority for specific actions."""
        query_lower = query.lower().strip()
        
        # 1. Check for EXACT action matches first (highest priority)
        # This prevents "draft" from matching "draft_claim"
        for intent in self.intent_keywords.keys():
            if query_lower == intent:
                return intent
        
        # 2. Score each intent based on keyword presence
        intent_scores = {}
        import re
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for kw in keywords:
                # Use word boundaries for English keywords to avoid partial matches
                if any(char.isalpha() for char in kw):
                    if re.search(rf"\b{re.escape(kw)}\b", query_lower):
                        score += 5 # Higher weight for word-bounded matches
                else:
                    # For Arabic, standard substring matching is usually fine
                    if kw in query_lower:
                        score += 1
            
            if score > 0:
                intent_scores[intent] = score
        
        # 3. Custom logic: If text is long and looks like a case, default to case_summary
        if self._is_likely_case(query):
            return "case_summary"

        # Return highest scoring intent, or "general_inquiry" if none match
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return "general_inquiry"
    
    def _detect_language(self, text: str) -> str:
        """Detect if the input text is primarily Arabic or English."""
        if not text:
            return "ar"
        # Simple heuristic: concentration of Arabic characters
        arabic_chars = len([c for c in text if '\u0600' <= c <= '\u06FF'])
        english_chars = len([c for c in text if 'a' <= c.lower() <= 'z'])
        return "ar" if arabic_chars >= english_chars else "en"

    async def process_message(
        self,
        user_message: str,
        analysis_data: Optional[Dict] = None,
        case_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate an appropriate response.
        
        Args:
            user_message: The user's input
            analysis_data: Optional current case analysis data
            case_text: Optional current case text
            
        Returns:
            Dict with response, suggested_actions, and metadata
        """
        try:
            # Update context if new analysis data provided
            if analysis_data:
                self.context.set_analysis(analysis_data, case_text)
            
            # Add user message to history
            self.context.add_message("user", user_message)
            
            # Translate User Message if Arabic and translator is available
            user_translation = None
            if HAS_TRANSLATOR and any('\u0600' <= char <= '\u06FF' for char in user_message):
                try:
                    # Limit to avoid huge payload issues (2000 chars max)
                    text_to_translate = user_message[:2000] 
                    user_translation = GoogleTranslator(source='auto', target='en').translate(text_to_translate)
                    logger.info(f"User translation success: {user_translation[:50]}...")
                except Exception as e:
                    logger.warning(f"User message translation failed: {e}")
            
            # Detect intent
            intent = self.detect_intent(user_message)
            
            # Decisive Action: If likely a case but no analysis, run analyzer immediately
            if intent == "case_summary" and not self.context.analysis_data and self.analyzer:
                logger.info("Decisive action: Running full analysis on pasted text...")
                try:
                    analysis_result = await self.analyzer(user_message)
                    # Update context with new analysis
                    analysis_dict = analysis_result.dict()
                    self.context.set_analysis(analysis_dict, user_message)
                except Exception as e:
                    logger.error(f"Decisive analysis failed: {e}")

            # Generate response based on intent and current analysis
            response = await self._generate_response(user_message, intent)
            
            # Automatic Assistant Translation (Full Bilingual Support)
            assistant_text = response.get("text", "")
            if HAS_TRANSLATOR and assistant_text and any('\u0600' <= char <= '\u06FF' for char in assistant_text):
                try:
                    # Skip translation if it already seems to have a significant English section
                    # or if it's already bilingual (contains the separator)
                    is_bilingual = "---" in assistant_text
                    
                    if not is_bilingual:
                        # Translate assistant response
                        translated_text = GoogleTranslator(source='auto', target='en').translate(assistant_text[:4500])
                        if translated_text and translated_text.lower() != assistant_text.lower():
                            response["text"] = f"{assistant_text}\n\n---\n\n{translated_text}"
                            response["assistant_translation"] = translated_text
                except Exception as e:
                    logger.warning(f"Assistant translation failed: {e}")

            # Add assistant response to history
            self.context.add_message("assistant", response["text"], 
                                    metadata={"intent": intent})
            
            # Add user translation to response
            if user_translation:
                response["user_translation"] = user_translation

            return response
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}", exc_info=True)
            return {
                "text": "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مجدداً.\nSorry, an error occurred. Please try again.",
                "intent": "error",
                "suggested_actions": [],
                "error": str(e)
            }
    
    async def _generate_response(self, user_message: str, intent: str) -> Dict[str, Any]:
        """Generate response based on detected intent."""
        
        # Check if we have analysis data
        analysis = self.context.analysis_data
        
        # Define handlers that work with AND without analysis
        has_analysis_handlers = {
            "case_summary": self._handle_case_summary,
            "case_type": self._handle_case_type,
            "similar_cases": self._handle_similar_cases,
            "legal_principles": self._handle_legal_principles,
            "trends": self._handle_trends,
            "recommendation": self._handle_recommendation,
            "full_analysis": self._handle_full_analysis,
            "draft": self._handle_draft_request,
            "draft_claim": self._handle_draft_claim,
            "draft_defense": self._handle_draft_defense,
            "outcome": self._handle_outcome,
            "compensation": self._handle_compensation,
            "entities": self._handle_entities,
        }
        
        # If intent requires analysis but we don't have it, ask for case file
        if intent in has_analysis_handlers and not analysis:
            return await self._handle_no_analysis(user_message)
        
        # If we have analysis, use appropriate handler
        if analysis:
            handler = has_analysis_handlers.get(intent, self._handle_general_inquiry)
            return await handler(user_message, analysis)
        
        # If no analysis but general inquiry, provide helpful responses
        return await self._handle_general_inquiry(user_message, {})
    
    async def _handle_no_analysis(self, user_message: str) -> Dict[str, Any]:
        """Handle case when no analysis has been performed yet."""
        return {
            "text": """مرحباً! أنا مساعدك القانوني الذكي المتخصص في تحليل القضايا السعودية.

لتحليل قضيتك، يمكنك:
1. **رفع مستند** - PDF, DOCX, أو ملف نصي
2. **لصق نص القضية** - مباشرة في مربع المدخل

كيف أستطيع مساعدتك اليوم؟

---

Hello! I'm your AI Legal Assistant specializing in Saudi legal case analysis.

To analyze your case, you can:
1. **Upload a document** - PDF, DOCX, or text file
2. **Paste case text** - directly in the input field

How can I help you today?""",
            "intent": "greeting",
            "suggested_actions": [
                {"label": "📄 Upload Document | رفع مستند", "action": "upload"},
                {"label": "📋 Paste Text | لصق نص", "action": "paste_text"},
                {"label": "ℹ️ Learn More | اعرف المزيد", "action": "learn_more"}
            ]
        }
    
    async def _handle_case_summary(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with case summary."""
        if not analysis:
            return self._handle_general_inquiry(query, analysis)
        
        # Build summary from available analysis data
        clf = analysis.get("classification", {})
        principles = analysis.get("legal_principles", [])
        recommendation = analysis.get("recommendation", {})
        trends = analysis.get("trends", {})
        
        principles_text_ar = "\n".join([f"• {p.get('name_ar', '')} - {p.get('description_ar', '')}" for p in principles[:3]]) if principles else "لم يتم استخراج مبادئ"
        principles_text_en = "\n".join([f"• {p.get('name_en', '')}" for p in principles[:3]]) if principles else "No principles extracted"
        rec_text_ar = recommendation.get("recommendation_ar", "لم تتوفر توصيات") if recommendation else "لم تتوفر توصيات"
        rec_text_en = recommendation.get("recommendation_en", "No recommendations available") if recommendation else "No recommendations available"
        win_rate = trends.get("plaintiff_win_rate", "N/A") if trends else "N/A"
        
        # Format confidence
        conf_val = clf.get('confidence', 0)
        if isinstance(conf_val, float) and conf_val <= 1.0:
            conf_val = round(conf_val * 100)
            
        return {
            "text": f"""[Summary] ملخص التحليل:
            
**نوع القضية:** {clf.get('name_ar', 'غير محدد')}
**درجة الثقة:** {conf_val}%
**نسبة فوز المدعي:** {win_rate}%

**المبادئ القانونية المطبقة:**
{principles_text_ar}

**التوصية:**
{rec_text_ar}

---

[Summary] **Case Analysis Summary:**

**Case Type:** {clf.get('name_en', 'Not determined')}
**Confidence:** {conf_val}%
**Plaintiff Win Rate:** {win_rate}%

**Applicable Legal Principles:**
{principles_text_en}

**Recommendation:**
{rec_text_en}""",
            "intent": "case_summary",
            "suggested_actions": [
                {"label": "📊 Full Details | عرض التفاصيل الكاملة", "action": "show_details"},
                {"label": "🔍 Similar Cases | قضايا مشابهة", "action": "similar_cases"},
                {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
            ]
        }
    
    async def _handle_case_type(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with case classification."""
        if "classification" not in analysis:
            return self._handle_general_inquiry(query, analysis)
        
        clf = analysis["classification"]
        conf_val = clf.get('confidence', 0)
        if isinstance(conf_val, float) and conf_val <= 1.0:
            conf_val = round(conf_val * 100)
            
        sub_types_text = ""
        if clf.get("sub_types"):
            sub_types_text = "\n".join(
                [f"  • {st.get('name_ar', '')}" for st in clf.get("sub_types", [])]
            )
        
        return {
            "text": f"""تصنيف القضية:

**النوع الرئيسي:** {clf.get('name_ar', 'غير معروف')}
**النوع الإنجليزي:** {clf.get('name_en', 'Unknown')}
**درجة التأكد:** {conf_val}%

Sub-types:
{sub_types_text if sub_types_text else 'لا توجد أنواع فرعية'}

---

Case Classification:

**Main Type:** {clf.get('name_ar', 'Unknown')}
**Type (English):** {clf.get('name_en', 'Unknown')}
**Confidence:** {conf_val}%""",
            "intent": "case_type",
            "suggested_actions": [
                {"label": "⚖️ Legal Principles | المبادئ القانونية", "action": "legal_principles"},
                {"label": "🔍 Precedent Cases | قضايا سابقة", "action": "similar_cases"}
            ]
        }
    
    async def _handle_similar_cases(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Provide similar cases from the database."""
        # Check if we have trends (pre-computed similar case stats)
        trends = analysis.get("trends", {})
        classification = analysis.get("classification", {})
        rec = analysis.get("recommendation", {})
        direction = rec.get("direction", "").lower()
        is_judgement = direction == "decided_judgement" or "حكم" in str(rec.get("recommendation_ar", "")).lower()
        
        user_lang = self._detect_language(query)
        
        # Professionalize "N/A" data
        win_rate = trends.get('plaintiff_win_rate', 'N/A')
        avg_compensation = trends.get('avg_compensation', 'N/A')
        reliability = trends.get('reliability', 'N/A')
        
        ar_comp = f"{avg_compensation} ريال" if avg_compensation != 'N/A' else "بيانات التعويض غير كافية حالياً"
        en_comp = f"{avg_compensation} SAR" if avg_compensation != 'N/A' else "Insufficient historical compensation data available"
        
        ar_win_block = f"• نسبة فوز المدعي: {ar_win}" if not is_judgement else "• حالة القضية:تم الحكم فيها (تم التحصيل أو الاعتراض)"
        en_win_block = f"• Plaintiff Win Rate: {en_win}" if not is_judgement else "• Case Status: Already Judged (Enforcement/Appeal phase)"

        text_ar = f"""🔍 نتائج البحث عن قضايا مشابهة:

لقد وجدنا قضايا مرتبطة بنوع: **{classification.get('name_ar', 'قضيتك')}**.

**الإحصائيات المستخلصة من السوابق:**
{ar_win_block}
• متوسط التعويض: {ar_comp}
• درجة موثوقية البيانات: {reliability}%"""

        text_en = f"""🔍 **Similar Case Results:**

We found precedents related to: **{classification.get('name_en', 'your case')}**.

**Extracted Trend Data:**
{en_win_block}
• Average Compensation: {en_comp}
• Data Reliability: {reliability}%"""

        # Adaptive Language response
        if user_lang == "ar":
            final_text = text_ar + "\n\n---\n\n" + text_en
        else:
            final_text = text_en + "\n\n---\n\n" + text_ar

        return {
            "text": final_text,
            "intent": "similar_cases",
            "suggested_actions": [
                {"label": "📊 Full Analysis | تحليل شامل", "action": "full_analysis"},
                {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
            ]
        }
    
    async def _handle_legal_principles(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with legal principles."""
        if "legal_principles" not in analysis or not analysis["legal_principles"]:
            return self._handle_general_inquiry(query, analysis)
        
        principles = analysis["legal_principles"][:5]  # Top 5
        principles_text_ar = "\n".join([
            f"  • **{p.get('name_ar', 'N/A')}** - {p.get('description_ar', '')}"
            for p in principles
        ])
        principles_text_en = "\n".join([
            f"  • **{p.get('name_en', 'N/A')}** (Source: {p.get('source_section', 'N/A')})"
            for p in principles
        ])
        
        return {
            "text": f"""⚖️ المبادئ القانونية ذات الصلة:

{principles_text_ar}

هذه المبادئ تلعب دورًا مهمًا في تحليل قضيتك.

---

⚖️ Relevant Legal Principles:

{principles_text_en}

These principles are important in analyzing your case.""",
            "intent": "legal_principles",
            "suggested_actions": [
                {"label": "💡 Recommendations | التوصيات", "action": "recommendations"},
                {"label": "📊 Full Analysis | تحليل شامل", "action": "full_analysis"}
            ]
        }
    
    async def _handle_trends(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with trend statistics."""
        if "trends" not in analysis:
            return self._handle_general_inquiry(query, analysis)
        
        trends = analysis["trends"]
        return {
            "text": f"""الاتجاهات الإحصائية:

**معدل فوز المدعي:** {trends.get('plaintiff_win_rate', 0)}%
**معدل الرفض:** {trends.get('dismissal_rate', 0)}%
**معدل الاختصاص:** {trends.get('jurisdiction_rate', 0)}%
**موثوقية البيانات:** {trends.get('reliability', 0)}%

---

Trend Statistics:

**Plaintiff Win Rate:** {trends.get('plaintiff_win_rate', 0)}%
**Dismissal Rate:** {trends.get('dismissal_rate', 0)}%
**Jurisdiction Rate:** {trends.get('jurisdiction_rate', 0)}%
**Data Reliability:** {trends.get('reliability', 0)}%""",
            "intent": "trends",
            "suggested_actions": [
                {"label": "💡 Full Recommendations | التوصيات الشاملة", "action": "recommendation"}
            ]
        }
    
    async def _handle_recommendation(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with case recommendation, pivoting if it's already a judgment."""
        rec = analysis.get("recommendation", {})
        classification = analysis.get("classification", {})
        direction = rec.get("direction", "").lower()
        
        # Check if this is a decided judgment
        is_judgement = direction == "decided_judgement" or "حكم" in str(analysis.get("recommendation", {}).get("recommendation_ar", "")).lower()

        # Decisive Execution: If recommendation is generic or we need post-judgment mode, use LLM
        if self.llm:
            try:
                logger.info(f"Generating LLM Recommendation (Judgement Mode: {is_judgement})...")
                case_context = json.dumps({
                    "classification": classification,
                    "is_judgement": is_judgement,
                    "extracted_amount": analysis.get("recommendation", {}).get("award_amount")
                }, ensure_ascii=False)
                
                if is_judgement:
                    system_prompt = """أنت مساعد قانوني خبير في النظام السعودي. الوثيقة المقدمة هي 'حكم قضائي' بالفعل.
يجب أن تركز توصيتك على:
1. إجراءات التنفيذ (محكمة التنفيذ).
2. مواعيد الاعتراض (الاستئناف) - عادة 30 يوماً.
3. الخطوات القادمة لتحصيل المبلغ المحكوم به.
لا تقدم نصائح ما قبل المحاكمة (مثل التحقيق أو جمع الأدلة) لأن القضية حُسمت بالفعل."""
                else:
                    system_prompt = "أنت مساعد قانوني خبير في النظام السعودي. قدم توصية عملية ومباشرة بناءً على وقائع القضية المرفقة."

                prompt = f"بناءً على تحليل القضية: {case_context}\n\nالسؤال: {query}\n\nقدم توصية قانونية عملية واحترافية (بالعربية مع ترجمة إنجليزية ملحقة)."
                generated_rec = self.llm.generate(prompt, system_prompt=system_prompt)
                
                if not generated_rec or len(generated_rec.strip()) < 10:
                    raise ValueError("Empty or too short LLM response")
                
                return {
                    "text": generated_rec,
                    "intent": "recommendation",
                    "suggested_actions": [
                        {"label": "🔍 Similar Cases | قضايا مشابهة", "action": "similar_cases"},
                        {"label": "📊 Full Analysis | تحليل شامل", "action": "full_analysis"}
                    ]
                }
            except Exception as e:
                logger.error(f"LLM Recommendation failed: {e}")

        # Fallback to static if LLM fails
        return {
            "text": str(rec.get("recommendation_ar", "لا توجد توصية محددة حالياً بناءً على البيانات المتوفرة.")),
            "intent": "recommendation",
            "suggested_actions": [
                {"label": "📝 Draft Claim | كتابة لائحة دعوى", "action": "draft_claim"},
                {"label": "🛡️ Draft Defense | كتابة مذكرة دفاع", "action": "draft_defense"},
                {"label": "🔍 Similar Cases | قضايا مشابهة", "action": "similar_cases"}
            ]
        }
    
    async def _handle_full_analysis(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Provide comprehensive case analysis."""
        clf = analysis.get("classification", {})
        trends = analysis.get("trends", {})
        rec = analysis.get("recommendation", {})
        
        conf_val = clf.get('confidence', 0)
        if isinstance(conf_val, float) and conf_val <= 1.0:
            conf_val = round(conf_val * 100)
            
        return {
            "text": f"""تحليل شامل للقضية:

**التصنيف:** {clf.get('name_ar', 'N/A')}
**معدل فوز المدعي:** {trends.get('plaintiff_win_rate', 0)}%
**الاتجاه:** {rec.get('direction', 'N/A')}
**درجة التأكد:** {conf_val}%

---

Comprehensive Case Analysis:

**Classification:** {clf.get('name_en', 'N/A')}
**Plaintiff Win Rate:** {trends.get('plaintiff_win_rate', 0)}%
**Recommendation Direction:** {rec.get('direction', 'N/A')}
**Confidence Level:** {conf_val}%""",
            "intent": "full_analysis",
            "suggested_actions": [
                {"label": "📝 Draft Claim | كتابة لائحة دعوى", "action": "draft_claim"},
                {"label": "🛡️ Draft Defense | كتابة مذكرة دفاع", "action": "draft_defense"}
            ]
        }
    
    async def _handle_draft_request(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Handle draft generation requests."""
        return {
            "text": """نوع المسودة:

اختر نوع المسودة التي تريد إنشاءها:

1. **لائحة دعوى** (Plaintiff Claim) - لتقديم دعوى قضائية
2. **مذكرة دفاع** (Defense Memo) - للدفاع عن موقفك

---

Draft Type Selection:

Choose the type of draft you want to create:

1. **Plaintiff Claim** - To file a legal case
2. **Defense Memo** - To defend your position""",
            "intent": "draft",
            "suggested_actions": [
                {"label": "📝 Plaintiff Claim | لائحة دعوى", "action": "draft_claim"},
                {"label": "🛡️ Defense Memo | مذكرة دفاع", "action": "draft_defense"}
            ]
        }

    async def _handle_draft_claim(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Generate a plaintiff claim draft template (or LLM if available)."""
        clf = analysis.get("classification", {})
        case_type_ar = clf.get("name_ar", "غير محدد")
        
        # Try LLM Generation
        if self.llm:
            try:
                # Fact Sheet extraction for strict grounding
                clf = analysis.get("classification", {})
                case_type_ar = clf.get("name_ar", "غير محدد")
                
                # Extract award/claim amount
                amount = analysis.get("recommendation", {}).get("award_amount", "غير محدد")
                if not amount or amount == 0:
                    # Try to extract from text if missing in structured data
                    match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:ريال|SAR)", self.context.case_text or "")
                    if match:
                        amount = match.group(1)
                
                fact_sheet = {
                    "نوع القضية": case_type_ar,
                    "المبلغ المطالب به": amount,
                    "المحكمة المختصة": "المحكمة العامة (General Court)",
                    "حالة القضية": "حكم صادر" if analysis.get("recommendation", {}).get("direction") == "decided_judgement" else "تحت النظر"
                }
                
                fact_sheet_str = "\n".join([f"- {k}: {v}" for k, v in fact_sheet.items()])

                # Get Legal Context
                legal_context, citations = self._get_legal_context(case_type_ar)

                system_prompt = f"""أنت محامي صياغة قانونية محترف (The Associate). مهمتك هي صياغة المستندات القانونية بدقة متناهية بناءً على البيانات المقدمة ومواد النظام.

قواعد صارمة للصياغة:
1. **لا تستخدم مربعات نصية** مثل [اسم الشخص] أو [التاريخ]. إذا لم تكن المعلومة متوفرة، اترك فراغاً منقوطاً (............).
2. **لا تستخدم placeholders** مثل [بالمليون ريال]. استخدم الأرقام الفعلية المذكورة في 'Fact Sheet' أدناه.
3. **اللغة:** صياغة عربية قانونية رصينة فقط. يُمنع استخدام أي لغات أخرى (مثل الصينية أو الإنجليزية) داخل النص العربي.
4. **الدقة:** لا تبتكر وقائع. استند فقط لما ورد في البيانات.

حقائق القضية (Must use these values):
{fact_sheet_str}"""

                if legal_context:
                    system_prompt += f"\n\n{legal_context}\n\nيجب عليك الاستشهاد بأرقام المواد المذكورة أعلاه في المسودة."
                
                prompt = f"""البيانات المستخرجة (JSON):
{json.dumps(analysis, ensure_ascii=False)}

المطلوب:
قم بصياغة لائحة دعوى قضائية من نوع '{case_type_ar}' بشكل احترافي.
استخدم البيانات أعلاه لصياغة اللائحة.
احرص على الاستناد إلى الأنظمة السعودية ذات الصلة (المذكورة أعلاه).

اجعل الصياغة قانونية ورسمية."""
                
                generated_draft = self.llm.generate(prompt, system_prompt=system_prompt)
                
                # Clean the draft of common hallmarks of hallucination
                generated_draft = self._clean_draft(generated_draft, fact_sheet)
                
                return {
                    "text": f"[Draft] **مسودة لائحة دعوى (Generated by AI):**\n\n{generated_draft}",
                    "intent": "draft_claim",
                    "citations": citations, # Pass citations for explainability
                    "metadata": {"is_draft": True, "draft_type": "claim"},
                    "suggested_actions": [
                        {"label": "🛡️ Draft Defense | كتابة مذكرة دفاع", "action": "draft_defense"},
                        {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
                    ]
                }
            except Exception as e:
                logger.error(f"LLM Draft Error: {e}")
                # Fallback to template below
        
        case_type_en = clf.get("name_en", "Unknown")
        
        return {
            "text": f"""📝 مسودة لائحة دعوى ({case_type_ar}):

**الموضوع:** دعوى {case_type_ar}
**المدعي:** [الاسم]
**المدعى عليه:** [الاسم]

**الوقائع:**
نحيط فضيلتكم علماً بأن... [بناءً على تفاصيل القضية]

**الطلبات:**
1. إلزام المدعى عليه بـ...
2. التعويض عن...

---

📝 Plaintiff Claim Draft ({case_type_en}):

**Subject:** {case_type_en} Claim
**Plaintiff:** [Name]
**Defendant:** [Name]

**Facts:**
We inform your honor that... [Based on case details]

**Requests:**
1. Compel the defendant to...
2. Compensation for...""",
            "intent": "draft_claim",
            "suggested_actions": [
                {"label": "🛡️ Draft Defense | كتابة مذكرة دفاع", "action": "draft_defense"},
                {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
            ]
        }

    async def _handle_draft_defense(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Generate a defense memo draft template (or LLM if available)."""
        clf = analysis.get("classification", {})
        case_type_ar = clf.get("name_ar", "غير محدد")
        
        # Try LLM Generation
        if self.llm:
            try:
                # Fact Sheet extraction for strict grounding
                clf = analysis.get("classification", {})
                case_type_ar = clf.get("name_ar", "غير محدد")
                
                # Extract award/claim amount
                amount = analysis.get("recommendation", {}).get("award_amount", "غير محدد")
                
                fact_sheet = {
                    "نوع القضية": case_type_ar,
                    "المبلغ": amount,
                    "المحكمة المختصة": "المحكمة العامة (General Court)",
                    "حالة القضية": "حكم صادر" if analysis.get("recommendation", {}).get("direction") == "decided_judgement" else "رد على دعوى"
                }
                
                fact_sheet_str = "\n".join([f"- {k}: {v}" for k, v in fact_sheet.items()])

                # Get Legal Context
                legal_context, citations = self._get_legal_context(case_type_ar)

                system_prompt = f"""أنت محامي ردود قانونية خبير. مهمتك صياغة 'مذكرة دفاع' قوية ومحترفة.

قواعد صارمة:
1. **لا تستخدم placeholders** مثل [التاريخ] أو [المادة المبرمجة]. استخدم القيم من 'Fact Sheet' أو اترك فراغاً (............).
2. **اللغة:** عربية قانونية فقط. لا صينية ولا إنجليزية.
3. استخدم مواد النظام الواردة في السياق أدناه.

حقائق القضية (Must use):
{fact_sheet_str}"""

                if legal_context:
                    system_prompt += f"\n\n{legal_context}\n\nيجب عليك الاستشهاد بأرقام المواد المذكورة أعلاه في المسودة."
                
                prompt = f"""البيانات المستخرجة (JSON):
{json.dumps(analysis, ensure_ascii=False)}

المطلوب:
قم بصياغة مذكرة دفاع (رد على دعوى) في قضية من نوع '{case_type_ar}' بشكل احترافي.
استخدم البيانات أعلاه لصياغة الدفوع الشكلية والموضوعية.
فند الادعاءات بناءً على الوقائع المذكورة والمواد النظامية."""
                
                generated_draft = self.llm.generate(prompt, system_prompt=system_prompt)
                
                # Clean the draft
                generated_draft = self._clean_draft(generated_draft, fact_sheet)
                
                return {
                    "text": f"[Draft] **مذكرة دفاع (Generated by AI):**\n\n{generated_draft}",
                    "intent": "draft_defense",
                    "citations": citations, # Pass citations for explainability
                    "metadata": {"is_draft": True, "draft_type": "defense"},
                    "suggested_actions": [
                        {"label": "📝 Draft Claim | كتابة لائحة دعوى", "action": "draft_claim"},
                        {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
                    ]
                }
            except Exception as e:
                logger.error(f"LLM Draft Error: {e}")
                # Fallback to template below

        case_type_en = clf.get("name_en", "Unknown")
        
        return {
            "text": f"""🛡️ مسودة مذكرة دفاع ({case_type_ar}):

**الموضوع:** رد على دعوى {case_type_ar}
**مقدمة من:** [الاسم] (المدعى عليه)

**الدفوع الشكلية:**
نلتمس من فضيلتكم رد الدعوى شكلاً لـ...

**الدفوع الموضوعية:**
ما ذكره المدعي غير صحيح، والصحيح هو...

**الطلبات:**
رفض الدعوى وإلزام المدعي بالمصاريف.

---

🛡️ Defense Memo Draft ({case_type_en}):

**Subject:** Defense Response to {case_type_en}
**Submitted by:** [Name] (Defendant)

**Procedural Defenses:**
We request dismissal based on...

**Substantive Defenses:**
The plaintiff's claims are incorrect; the facts correspond to...

**Requests:**
Dismiss the claim and compel plaintiff to pay costs.""",
            "intent": "draft_defense",
            "suggested_actions": [
                {"label": "📝 Draft Claim | كتابة لائحة دعوى", "action": "draft_claim"},
                {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
            ]
        }
    
    def _clean_draft(self, text: str, facts: Dict) -> str:
        """Helper to remove common LLM hallucinations and placeholders."""
        if not text:
            return ""
            
        # 1. Remove Chinese characters (hallucination hallmark for Qwen 1.5B)
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
        
        # 2. Re-enforce actual amount if [بالمليون ريال] or similar exists
        amount = facts.get("المبلغ المطالب به") or facts.get("المبلغ", "............")
        text = text.replace("[بالمليون ريال]", str(amount))
        text = text.replace("[المبلغ]", str(amount))
        
        # 3. Handle structural hallucinations
        text = text.replace("[المادة المبرمجة]", "المادة ذات الصلة")
        
        # 4. Remove generic placeholders that should be blanks
        placeholders = [
            "[اسم المدعي]", "[اسم المدعى عليه]", "[اسم الشخص]", 
            "[تاريخ]", "[تاريخ الدعوى]", "[التاريخ]",
            "[الجهة المختصة]", "[العدد الزمني]"
        ]
        for p in placeholders:
            text = text.replace(p, "............")
            
        return text.strip()

    async def _handle_outcome(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond about case outcome probability."""
        trends = analysis.get("trends", {})
        win_rate = trends.get("plaintiff_win_rate", 0)
        
        probability_ar = "عالية جداً" if win_rate > 80 else "عالية" if win_rate > 60 else "متوسطة" if win_rate > 40 else "منخفضة"
        probability_en = "Very High" if win_rate > 80 else "High" if win_rate > 60 else "Moderate" if win_rate > 40 else "Low"
        
        user_lang = self._detect_language(query)
        ar_text = f"""احتمالية النجاح:

**معدل فوز المدعي في قضايا مشابهة:** {win_rate}%
**تقييم الاحتمالية:** {probability_ar}

هذه التقديرات مبنية على قضايا مشابهة في قاعدة البيانات."""

        en_text = f"""Success Probability:

**Plaintiff Win Rate in Similar Cases:** {win_rate}%
**Probability Assessment:** {probability_en}

These estimates are based on similar cases in our database."""

        if user_lang == "ar":
            final_text = ar_text + "\n\n---\n\n" + en_text
        else:
            final_text = en_text + "\n\n---\n\n" + ar_text

        return {
            "text": final_text,
            "intent": "outcome",
            "suggested_actions": [
                {"label": "⚠️ More About Risks | المزيد عن المخاطر", "action": "risks"},
                {"label": "💡 Recommendations | التوصيات", "action": "recommendation"}
            ]
        }
    
    async def _handle_compensation(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond about compensation information."""
        trends = analysis.get("trends", {})
        avg_comp = trends.get("average_compensation", 0)
        median_comp = trends.get("median_compensation", 0)
        comp_range = trends.get("compensation_range", {})
        comp_count = trends.get("compensation_count", 0)
        
        user_lang = self._detect_language(query)
        
        if comp_count == 0:
            ar_text = "💰 بيانات التعويضات: لا تتوفر حالياً بيانات مالية كافية لهذه الفئة من القضايا."
            en_text = "💰 Compensation Data: Insufficient financial data available for this case category."
        else:
            ar_text = f"""💰 إحصائيات التعويضات:

**المتوسط:** {avg_comp:,.0f} ر.س
**الوسيط:** {median_comp:,.0f} ر.س
**الحد الأدنى:** {comp_range.get('min', 0):,.0f} ر.س
**الحد الأقصى:** {comp_range.get('max', 0):,.0f} ر.س
**عدد القضايا ذات التعويض:** {comp_count}

هذه البيانات من قضايا مشابهة في قاعدة البيانات."""

            en_text = f"""💰 Compensation Statistics:

**Average:** {avg_comp:,.0f} SAR
**Median:** {median_comp:,.0f} SAR
**Minimum:** {comp_range.get('min', 0):,.0f} SAR
**Maximum:** {comp_range.get('max', 0):,.0f} SAR
**Cases with compensation:** {comp_count}

Based on similar cases in our database."""

        if user_lang == "ar":
            final_text = ar_text + "\n\n---\n\n" + en_text
        else:
            final_text = en_text + "\n\n---\n\n" + ar_text

        return {
            "text": final_text,
            "intent": "compensation",
            "suggested_actions": [
                {"label": "💡 Recommendations | التوصيات", "action": "recommendations"},
                {"label": "📈 Success Rate | نسبة النجاح", "action": "outcome"}
            ]
        }
    
    async def _handle_entities(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond about extracted entities."""
        user_lang = self._detect_language(query)
        
        if "entities" not in analysis or not analysis["entities"]:
            ar_text = "لم يتم العثور على أطراف أو كيانات قانونية محددة في هذا المستند حالياً."
            en_text = "No specific parties or legal entities were identified in this document at this stage."
        else:
            entities = analysis["entities"]
            entities_list = "\n".join([f"  • {e}: {v}" for e, v in entities.items()])
            ar_text = f"الأطراف والكيانات المستخرجة:\n\n{entities_list}"
            en_text = f"Extracted Case Entities:\n\n{entities_list}"

        if user_lang == "ar":
            final_text = ar_text + "\n\n---\n\n" + en_text
        else:
            final_text = en_text + "\n\n---\n\n" + ar_text

        return {
            "text": final_text,
            "intent": "entities",
            "suggested_actions": [
                {"label": "📊 Full Details | تفاصيل كاملة", "action": "full_analysis"}
            ]
        }
    
    async def _handle_general_inquiry(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Handle general inquiries with contextual responses."""
        query_lower = query.lower()
        
        # Determine response based on query content
        if any(word in query_lower for word in ["مرحب", "hello", "hi", "مستقبل"]):
            return {
                "text": """مرحباً بك! 👋

أنا مساعدك القانوني الذكي المتخصص في تحليل القضايا السعودية.

**الخدمات المتاحة:**

1️⃣ **تحليل القضايا** - صنف قضيتك وتعرف على نوعها
2️⃣ **البحث عن سوابق** - جد قضايا مشابهة من قاعدة البيانات
3️⃣ **استخراج المبادئ القانونية** - اكتشف القوانين ذات الصلة
4️⃣ **التحليل الإحصائي** - معرفة معدلات النجاح والتعويضات
5️⃣ **التوصيات الذكية** - احصل على نصائح قانونية مبنية على الذكاء الاصطناعي
6️⃣ **كتابة المسودات** - أنشئ لائحات الدعوى ومذكرات الدفاع

للبدء، يرجى رفع مستند القضية أو وصف حالتك.

---

Hello! 👋

I'm your intelligent legal assistant specializing in Saudi legal case analysis.

**Available Services:**

1️⃣ **Case Analysis** - Classify your case and identify its type
2️⃣ **Precedent Search** - Find similar cases in our database
3️⃣ **Legal Principles** - Discover relevant laws and regulations
4️⃣ **Statistical Analysis** - Learn success rates and compensation trends
5️⃣ **Smart Recommendations** - Get AI-powered legal advice
6️⃣ **Draft Generation** - Create legal pleadings and defense memos

To get started, please upload your case document or describe your situation.""",
                "intent": "greeting",
                "suggested_actions": [
                    {"label": "📁 Upload Document | رفع مستند", "action": "upload"},
                    {"label": "📝 Describe Case | وصف الحالة", "action": "paste_text"}
                ]
            }
        
        if any(word in query_lower for word in ["خدم", "services", "ماذا", "what", "كيف", "how"]):
            return {
                "text": """📋 **الخدمات المتاحة:**

**بدون رفع مستند:**
• الإجابة على الأسئلة القانونية العامة
• شرح أنواع القضايا في النظام السعودي
• معلومات عن الإجراءات القضائية

**مع رفع مستند القضية:**
• تصنيف تلقائي لنوع القضية
• استخراج المبادئ القانونية المطبقة
• إيجاد قضايا مشابهة من قاعدة البيانات
• تحليل احتمالات النجاح بناءً على السوابق
• توصيات قانونية ذكية
• توليد مسودات قانونية (لائحة دعوى، مذكرة دفاع)

---

**Available Services:**

**Without document:**
• General legal Q&A
• Saudi case type explanations
• Court procedure info

**With case document:**
• Automatic classification
• Legal principles extraction
• Precedent search
• Success rate trends
• AI recommendations
• Draft generation""",
                "intent": "general_inquiry",
                "suggested_actions": [
                    {"label": "📁 Upload Document | رفع مستند", "action": "upload"}
                ]
            }

        # PRIORITY: If analysis exists, use LLM for all follow-up logic
        if analysis and self.llm:
            try:
                # Prepare structured context from analysis
                context_str = json.dumps(analysis, ensure_ascii=False, indent=2)
                
                system_prompt = """أنت مساعد قانوني ذكي متخصص في الأنظمة السعودية.
دورك: الإجابة على استفسارات المستخدم بدقة بناءً على بيانات القضية المقدمة (JSON) والمواد النظامية.
إذا سألك المستخدم عن "توصيات" أو "خطوات قادمة"، قدم نصيحة عملية بناءً على نوع القضية والاتجاهات."""

                # Get Legal Context
                legal_context, citations = self._get_legal_context(query)
                if legal_context:
                    system_prompt += f"\n\n{legal_context}\n\nيجب عليك الاستشهاد بأرقام المواد المذكورة أعلاه في إجابتك."

                prompt = f"""بيانات القضية (JSON):
{context_str}

سؤال المستخدم: {query}

الإجابة:"""
                
                generated_response = self.llm.generate(prompt, system_prompt=system_prompt)
                
                return {
                    "text": generated_response,
                    "intent": "general_inquiry",
                    "citations": citations,
                    "suggested_actions": [
                         {"label": "📋 Case Summary | ملخص القضية", "action": "case_summary"},
                         {"label": "💡 Recommendations | التوصيات", "action": "recommendations"}
                    ]
                }
            except Exception as e:
                logger.error(f"LLM General Inquiry Error: {e}")
        
        # 2. TEMPLATES: Fallback for specific keywords if NO analysis
        if any(word in query_lower for word in ["سعودي", "saudi", "نظام", "system", "قانون", "law"]):
            return {
                "text": """⚖️ **النظام القانوني السعودي**

المملكة العربية السعودية تطبق نظاماً قانونياً يعتمد على الشريعة الإسلامية والأنظمة واللوائح الصادرة بمرسوم ملكي.

**المحاكم في السعودية:**
1. المحاكم العامة
2. المحاكم العمالية
3. المحاكم التجارية
4. محاكم الأحوال الشخصية
5. المحاكم الإدارية (ديوان المظالم)

للتحليل التفصيلي لقضيتك، يرجى رفع المستند.

---

**Saudi Legal System**

The Kingdom applies a legal system based on Islamic Law and statutory regulations.

**Courts in KSA:**
1. General Courts
2. Labor Courts
3. Commercial Courts
4. Personal Status Courts
5. Administrative Courts (Board of Grievances)

For detailed analysis, please upload your document.""",
                "intent": "general_inquiry",
                "suggested_actions": [
                    {"label": "📁 Upload Document | رفع مستند", "action": "upload"}
                ]
            }

        # 3. FINAL FALLBACK
        return {
            "text": """مرحباً! كيف يمكنني مساعدتك اليوم؟

للحصول على تحليل قانوني دقيق، يرجى رفع مستند القضية أو وصف حالتك بالتفصيل.

---

Hello! How can I help you today?

For accurate legal analysis, please upload your case document or describe your situation in detail.""",
            "intent": "general_inquiry",
            "suggested_actions": [
                {"label": "📁 Upload Document | رفع مستند", "action": "upload"},
                {"label": "💬 Describe Case | وصف الحالة", "action": "paste_text"}
            ]
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Retrieve conversation history."""
        return self.context.get_last_n_messages(20)
    
    def clear_conversation(self):
        """Clear conversation history and context."""
        self.context.clear()
    
    def get_context_summary(self) -> Dict:
        """Get summary of current context."""
        return {
            "has_analysis": self.context.analysis_data is not None,
            "message_count": len(self.context.messages),
            "analysis_keys": list(self.context.analysis_data.keys()) if self.context.analysis_data else []
        }
