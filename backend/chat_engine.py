"""
Chat Engine: Manages conversational interactions with the legal analysis system.
Maintains context and routes user messages to appropriate analysis engines.
"""

import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


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
        
    def _initialize_intents(self) -> Dict[str, List[str]]:
        """Define intent detection keywords in Arabic and English."""
        return {
            "case_summary": ["ملخص", "summary", "ملخص القضية", "summarize", "اختصار"],
            "case_type": ["النوع", "type", "classification", "التصنيف", "نوع القضية"],
            "similar_cases": ["حالات مشابهة", "similar", "precedent", "similar cases", "قضايا شبيهة", "قضايا مشابهة", "مشابهة"],
            "legal_principles": ["المبادئ", "principles", "قانونية", "legal", "قواعد قانونية"],
            "trends": ["الاتجاهات", "trends", "statistics", "إحصائيات", "معدلات"],
            "recommendation": ["توصية", "advice", "recommendation", "رأي", "اقتراح"],
            "full_analysis": ["تحليل", "analyze", "analysis", "تحليل شامل", "اشرح"],
            "draft": ["مسودة", "draft", "لائحة", "مذكرة", "write a draft"],
            "outcome": ["النتيجة", "outcome", "result", "probability", "احتمالية"],
            "compensation": ["تعويض", "compensation", "damages", "amount", "مبلغ"],
            "entities": ["الأطراف", "parties", "entities", "من", "شخصيات"]
        }
    
    def detect_intent(self, query: str) -> str:
        """Detect user's intent from their message."""
        query_lower = query.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return highest scoring intent, or "general_inquiry" if none match
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return "general_inquiry"
    
    def process_message(
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
            
            # Detect intent
            intent = self.detect_intent(user_message)
            
            # Generate response based on intent and current analysis
            response = self._generate_response(user_message, intent)
            
            # Add assistant response to history
            self.context.add_message("assistant", response["text"], 
                                    metadata={"intent": intent})
            
            return response
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}", exc_info=True)
            return {
                "text": "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مجدداً.\nSorry, an error occurred. Please try again.",
                "intent": "error",
                "suggested_actions": [],
                "error": str(e)
            }
    
    def _generate_response(self, user_message: str, intent: str) -> Dict[str, Any]:
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
            "outcome": self._handle_outcome,
            "compensation": self._handle_compensation,
            "entities": self._handle_entities,
        }
        
        # If intent requires analysis but we don't have it, ask for case file
        if intent in has_analysis_handlers and not analysis:
            return self._handle_no_analysis(user_message)
        
        # If we have analysis, use appropriate handler
        if analysis:
            handler = has_analysis_handlers.get(intent, self._handle_general_inquiry)
            return handler(user_message, analysis)
        
        # If no analysis but general inquiry, provide helpful responses
        return self._handle_general_inquiry(user_message, {})
    
    def _handle_no_analysis(self, user_message: str) -> Dict[str, Any]:
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
                {"label": "📄 رفع مستند", "action": "upload"},
                {"label": "📋 لصق نص", "action": "paste_text"},
                {"label": "ℹ️ اعرف المزيد", "action": "learn_more"}
            ]
        }
    
    def _handle_case_summary(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with case summary."""
        if not analysis:
            return self._handle_general_inquiry(query, analysis)
        
        # If we have a summary field, use it
        if "summary" in analysis:
            summary = analysis["summary"]
            return {
                "text": f"""ملخص القضية:

{summary.get('summary_ar', 'N/A')}

---

Case Summary:

{summary.get('summary_en', 'N/A')}""",
                "intent": "case_summary",
                "suggested_actions": [
                    {"label": "عرض التفاصيل الكاملة", "action": "full_analysis"},
                    {"label": "ايجاد قضايا مشابهة", "action": "find_similar"}
                ]
            }
        
        # Otherwise, build summary from available analysis data
        clf = analysis.get("classification", {})
        principles = analysis.get("legal_principles", [])
        recommendation = analysis.get("recommendation", {})
        
        principles_text = "\n".join([f"• {p.get('name_ar', '')} - {p.get('description_ar', '')}" for p in principles[:3]]) if principles else "لم يتم استخراج مبادئ"
        rec_text = recommendation.get("summary_ar", "") if recommendation else "لم تتوفر توصيات"
        
        return {
            "text": f"""ملخص التحليل:

**نوع القضية:** {clf.get('name_ar', 'غير محدد')}

**المبادئ القانونية المطبقة:**
{principles_text}

**التوصيات:**
{rec_text}

---

**Case Analysis Summary:**

**Case Type:** {clf.get('name_en', 'Not determined')}

**Applicable Legal Principles:**
{chr(10).join([f"• {p.get('name_en', '')} - {p.get('description_en', '')}" for p in principles[:3]]) if principles else "No principles extracted"}

**Recommendations:**
{recommendation.get('summary_en', 'No recommendations available') if recommendation else 'No recommendations available'}""",
            "intent": "case_summary",
            "suggested_actions": [
                {"label": "عرض التفاصيل الكاملة", "action": "full_analysis"},
                {"label": "ايجاد قضايا مشابهة", "action": "similar_cases"}
            ]
        }
    
    def _handle_case_type(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with case classification."""
        if "classification" not in analysis:
            return self._handle_general_inquiry(query, analysis)
        
        clf = analysis["classification"]
        sub_types_text = ""
        if clf.get("sub_types"):
            sub_types_text = "\n".join(
                [f"  • {st.get('name_ar', '')}" for st in clf.get("sub_types", [])]
            )
        
        return {
            "text": f"""تصنيف القضية:

**النوع الرئيسي:** {clf.get('name_ar', 'غير معروف')}
**النوع الإنجليزي:** {clf.get('name_en', 'Unknown')}
**درجة التأكد:** {clf.get('confidence', 0)}%

Sub-types:
{sub_types_text if sub_types_text else 'لا توجد أنواع فرعية'}

---

Case Classification:

**Main Type:** {clf.get('name_ar', 'Unknown')}
**Type (English):** {clf.get('name_en', 'Unknown')}
**Confidence:** {clf.get('confidence', 0)}%""",
            "intent": "case_type",
            "suggested_actions": [
                {"label": "المبادئ القانونية", "action": "legal_principles"},
                {"label": "قضايا سابقة", "action": "similar_cases"}
            ]
        }
    
    def _handle_similar_cases(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with similar cases information."""
        if not analysis:
            return self._handle_general_inquiry(query, analysis)
        
        # If we have similar_cases data, use it
        if "similar_cases" in analysis and analysis["similar_cases"]:
            similar = analysis["similar_cases"][:3]  # Top 3
            cases_text = "\n".join([
                f"  • القضية {i+1}: درجة التشابه {case.get('similarity_score', 0)}%"
                for i, case in enumerate(similar)
            ])
            
            return {
                "text": f"""قضايا مشابهة من قاعدة البيانات:

{cases_text}

يمكنك اطلاع هذه القضايا لفهم كيفية تعامل النظام القانوني مع حالات مشابهة.

---

Similar Cases from Database:

{cases_text}

Review these cases to understand how the legal system handled similar situations.""",
                "intent": "similar_cases",
                "suggested_actions": []
            }
        
        # If no similar cases data, provide helpful info
        clf = analysis.get("classification", {})
        case_type = clf.get("name_ar", "هذا النوع من القضايا")
        
        return {
            "text": f"""البحث عن قضايا مشابهة:

لديك قضية من نوع: **{case_type}**

من خلال تحليل قضيتك، يمكننا البحث في قاعدة البيانات عن قضايا مشابهة من نوع "{case_type}" لمساعدتك على فهم كيفية تعامل النظام القانوني مع حالات متشابهة.

**المزايا:**
• فهم السوابق القضائية
• معرفة نسب نجاح القضايا المشابهة
• استخلاص أفضل الممارسات القانونية

---

Searching for Similar Cases:

Your case is classified as: **{case_type}**

Based on your case analysis, we can search for similar cases in our database to help you understand how the legal system handles related matters.

**Benefits:**
• Understand legal precedents
• Learn success rates for similar cases
• Extract best legal practices""",
            "intent": "similar_cases",
            "suggested_actions": [
                {"label": "🔍 ابحث عن قضايا مشابهة", "action": "search_similar"},
                {"label": "📋 عد إلى التحليل", "action": "case_summary"}
            ]
        }
    
    def _handle_legal_principles(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with legal principles."""
        if "legal_principles" not in analysis or not analysis["legal_principles"]:
            return self._handle_general_inquiry(query, analysis)
        
        principles = analysis["legal_principles"][:5]  # Top 5
        principles_text = "\n".join([
            f"  • {p.get('principle_ar', 'N/A')}"
            for p in principles
        ])
        
        return {
            "text": f"""المبادئ القانونية ذات الصلة:

{principles_text}

هذه المبادئ تلعب دورًا مهمًا في تحليل قضيتك.

---

Relevant Legal Principles:

{principles_text}

These principles are important in analyzing your case.""",
            "intent": "legal_principles",
            "suggested_actions": [
                {"label": "التوصيات", "action": "recommendation"},
                {"label": "تحليل شامل", "action": "full_analysis"}
            ]
        }
    
    def _handle_trends(self, query: str, analysis: Dict) -> Dict[str, Any]:
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
                {"label": "التوصيات الشاملة", "action": "recommendation"}
            ]
        }
    
    def _handle_recommendation(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond with case recommendation."""
        if "recommendation" not in analysis:
            return self._handle_general_inquiry(query, analysis)
        
        rec = analysis["recommendation"]
        return {
            "text": f"""التوصية:

**الاتجاه:** {rec.get('direction', 'غير معروف')}
**درجة التأكد:** {rec.get('confidence', 0)}%

{rec.get('recommendation_ar', 'N/A')}

---

Recommendation:

**Direction:** {rec.get('direction', 'Unknown')}
**Confidence:** {rec.get('confidence', 0)}%

{rec.get('recommendation_en', 'N/A')}""",
            "intent": "recommendation",
            "suggested_actions": [
                {"label": "كتابة مسودة", "action": "generate_draft"},
                {"label": "استفسارات اخرى", "action": "more_questions"}
            ]
        }
    
    def _handle_full_analysis(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Provide comprehensive case analysis."""
        clf = analysis.get("classification", {})
        trends = analysis.get("trends", {})
        rec = analysis.get("recommendation", {})
        
        return {
            "text": f"""تحليل شامل للقضية:

**التصنيف:** {clf.get('name_ar', 'N/A')}
**معدل فوز المدعي:** {trends.get('plaintiff_win_rate', 0)}%
**الاتجاه:** {rec.get('direction', 'N/A')}
**درجة التأكد:** {rec.get('confidence', 0)}%

---

Comprehensive Case Analysis:

**Classification:** {clf.get('name_en', 'N/A')}
**Plaintiff Win Rate:** {trends.get('plaintiff_win_rate', 0)}%
**Recommendation Direction:** {rec.get('direction', 'N/A')}
**Confidence Level:** {rec.get('confidence', 0)}%""",
            "intent": "full_analysis",
            "suggested_actions": [
                {"label": "كتابة لائحة دعوى", "action": "draft_claim"},
                {"label": "كتابة مذكرة دفاع", "action": "draft_defense"}
            ]
        }
    
    def _handle_draft_request(self, query: str, analysis: Dict) -> Dict[str, Any]:
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
                {"label": "لائحة دعوى", "action": "draft_claim"},
                {"label": "مذكرة دفاع", "action": "draft_defense"}
            ]
        }
    
    def _handle_outcome(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond about case outcome probability."""
        trends = analysis.get("trends", {})
        win_rate = trends.get("plaintiff_win_rate", 0)
        
        probability_ar = "عالية جداً" if win_rate > 80 else "عالية" if win_rate > 60 else "متوسطة" if win_rate > 40 else "منخفضة"
        probability_en = "Very High" if win_rate > 80 else "High" if win_rate > 60 else "Moderate" if win_rate > 40 else "Low"
        
        return {
            "text": f"""احتمالية النجاح:

**معدل فوز المدعي في قضايا مشابهة:** {win_rate}%
**تقييم الاحتمالية:** {probability_ar}

هذه التقديرات مبنية على قضايا مشابهة في قاعدة البيانات.

---

Success Probability:

**Plaintiff Win Rate in Similar Cases:** {win_rate}%
**Probability Assessment:** {probability_en}

These estimates are based on similar cases in our database.""",
            "intent": "outcome",
            "suggested_actions": [
                {"label": "المزيد عن المخاطر", "action": "risks"},
                {"label": "التوصيات", "action": "recommendation"}
            ]
        }
    
    def _handle_compensation(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond about compensation information."""
        trends = analysis.get("trends", {})
        comp_stats = trends.get("compensation_stats", {})
        
        return {
            "text": f"""احصائيات التعويضات:

**المتوسط:** {comp_stats.get('average', 0):,.0f} رس
**الحد الأدنى:** {comp_stats.get('min', 0):,.0f} رس
**الحد الأقصى:** {comp_stats.get('max', 0):,.0f} رس

هذه البيانات من قضايا مشابهة.

---

Compensation Statistics:

**Average:** {comp_stats.get('average', 0):,.0f} SAR
**Minimum:** {comp_stats.get('min', 0):,.0f} SAR
**Maximum:** {comp_stats.get('max', 0):,.0f} SAR

Based on similar cases in our database.""",
            "intent": "compensation",
            "suggested_actions": [
                {"label": "عوامل التعويض", "action": "compensation_factors"}
            ]
        }
    
    def _handle_entities(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Respond about extracted entities."""
        if "entities" not in analysis or not analysis["entities"]:
            return {
                "text": "لم يتم العثور على أطراف محددة في القضية.\nNo specific entities were extracted from the case.",
                "intent": "entities",
                "suggested_actions": []
            }
        
        entities = analysis["entities"]
        entities_text = "\n".join([
            f"  • {e}: {v}" for e, v in entities.items()
        ])
        
        return {
            "text": f"""الأطراف والكيانات:

{entities_text}

---

Case Entities:

{entities_text}""",
            "intent": "entities",
            "suggested_actions": [
                {"label": "تفاصيل كاملة", "action": "full_analysis"}
            ]
        }
    
    def _handle_general_inquiry(self, query: str, analysis: Dict) -> Dict[str, Any]:
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
                    {"label": "📁 رفع مستند", "action": "upload"},
                    {"label": "📝 وصف الحالة", "action": "paste_text"}
                ]
            }
        
        elif any(word in query_lower for word in ["خدم", "services", "ماذا", "what", "كيف", "how"]):
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
• توصيات قانونية مبنية على الذكاء الاصطناعي
• توليد مسودات قانونية (لائحة دعوى، مذكرة دفاع)

---

**Available Services:**

**Without uploading a document:**
• Answer general legal questions
• Explain types of cases in Saudi law
• Information about court procedures

**With case document uploaded:**
• Automatic case type classification
• Extraction of applicable legal principles
• Finding similar precedent cases
• Success probability analysis based on precedents
• AI-powered legal recommendations
• Legal draft generation (claims, defense memos)""",
                "intent": "general_inquiry",
                "suggested_actions": [
                    {"label": "📁 رفع مستند", "action": "upload"},
                    {"label": "💬 اسأل عن حالة", "action": "paste_text"}
                ]
            }
        
        elif any(word in query_lower for word in ["سعودي", "saudi", "نظام", "system", "قانون", "law"]):
            return {
                "text": """⚖️ **النظام القانوني السعودي**

المملكة العربية السعودية تطبق نظاماً قانونياً يعتمد على:
• **الشريعة الإسلامية** - المصدر الأساسي
• **الأنظمة واللوائح** - تنظم جوانب معينة
• **الأوامر الملكية** - تصدرها الحكومة

**أنواع القضايا:**
- قضايا عمالية (تتعلق بالعمل والعمال)
- قضايا تجارية (العقود والتجارة)
- قضايا أحوال شخصية (الزواج والطلاق والميراث)
- قضايا إدارية (تتعلق بالحكومة)
- قضايا جنائية (الجرائم)

للتحليل التفصيلي لقضيتك، يرجى رفع المستند.

---

**Saudi Legal System**

The Kingdom applies a legal system based on:
• **Islamic Law** - The primary source
• **Regulations and Bylaws** - Regulate specific areas
• **Royal Orders** - Issued by government

**Types of Cases:**
- Labor cases (Employment)
- Commercial cases (Contracts, trade)
- Personal status cases (Marriage, divorce, inheritance)
- Administrative cases (Government-related)
- Criminal cases (Crimes)

For detailed analysis of your case, please upload the document.""",
                "intent": "general_inquiry",
                "suggested_actions": [
                    {"label": "📁 رفع مستند", "action": "upload"}
                ]
            }
        
        else:
            # Default response mentioning what we can do
            return {
                "text": f"""شكراً على سؤالك: "{query}"

يمكنني مساعدتك بـ:

**إذا كان لديك مستند قضية:**
✅ تحليل نوع القضية
✅ استخراج القوانين ذات الصلة
✅ البحث عن قضايا مشابهة
✅ توقع نسبة النجاح
✅ تقديم توصيات قانونية
✅ كتابة مسودات قانونية

**إذا لم يكن لديك مستند:**
📚 الإجابة على الأسئلة القانونية
📚 شرح المفاهيم القانونية
📚 معلومات عن النظام السعودي

يرجى رفع مستندك أو اطرح سؤالاً محدداً!

---

Thank you for your question: "{query}"

I can help you with:

**If you have a case document:**
✅ Analyze case type
✅ Extract relevant laws
✅ Find similar cases
✅ Predict success probability
✅ Provide legal recommendations
✅ Generate legal drafts

**If you don't have a document:**
📚 Answer legal questions
📚 Explain legal concepts
📚 Information about Saudi law

Please upload your document or ask a specific question!""",
                "intent": "general_inquiry",
                "suggested_actions": [
                    {"label": "📁 رفع مستند", "action": "upload"},
                    {"label": "📋 لصق نص", "action": "paste_text"}
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
