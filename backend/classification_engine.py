"""
Case Type Classification Engine for Arabic Legal Cases.

Uses keyword/pattern matching to classify cases into legal categories.
No ML model needed — transparent, auditable, explainable.

Supported case types:
- نزاع عقدي (Contract Dispute)
- نزاع عمالي (Labor Dispute)
- حادث مروري (Traffic Accident)
- نزاع تجاري (Commercial Dispute)
- نزاع عقاري (Property Dispute)
- مضاربة / شراكة (Partnership)
- تعويض (Compensation Claim)
- اختصاص قضائي (Jurisdictional)
"""

import re
from typing import Dict, List, Tuple


# ── Case Type Definitions ──────────────────────────────────────────────
# Each type has: Arabic name, English name, keywords, weight multipliers

CASE_TYPES = {
    "contract_dispute": {
        "name_ar": "نزاع عقدي",
        "name_en": "Contract Dispute",
        "keywords": [
            "عقد", "العقد", "التعاقد", "تعاقد", "إخلال بالعقد",
            "بنود العقد", "شروط العقد", "الالتزامات التعاقدية",
            "فسخ العقد", "إنهاء العقد", "مخالفة العقد",
            "الطرف الأول", "الطرف الثاني", "أطراف العقد",
            "توريد", "تسليم", "مقاولة", "صيانة"
        ],
        "strong_indicators": [
            "إخلال بالعقد", "فسخ العقد", "الالتزامات التعاقدية",
            "بنود العقد", "شروط العقد"
        ]
    },
    "labor_dispute": {
        "name_ar": "نزاع عمالي",
        "name_en": "Labor Dispute",
        "keywords": [
            "عامل", "عمال", "موظف", "راتب", "رواتب",
            "فصل تعسفي", "إنهاء خدمات", "مكافأة نهاية الخدمة",
            "نظام العمل", "عقد العمل", "ساعات العمل",
            "إجازة", "تأمينات", "كفالة", "نقل كفالة"
        ],
        "strong_indicators": [
            "فصل تعسفي", "مكافأة نهاية الخدمة", "نظام العمل",
            "عقد العمل", "إنهاء خدمات"
        ]
    },
    "traffic_accident": {
        "name_ar": "حادث مروري",
        "name_en": "Traffic Accident",
        "keywords": [
            "حادث", "مروري", "سيارة", "مركبة", "قيادة",
            "تصادم", "إصابة", "وفاة", "مرور", "رخصة قيادة",
            "تأمين المركبة", "إتلاف", "حوادث السير"
        ],
        "strong_indicators": [
            "حادث مروري", "حوادث السير", "تصادم", "إتلاف السيارة"
        ]
    },
    "commercial_dispute": {
        "name_ar": "نزاع تجاري",
        "name_en": "Commercial Dispute",
        "keywords": [
            "تجاري", "تجارية", "شركة", "سجل تجاري",
            "فاتورة", "فواتير", "بيع", "شراء", "سداد",
            "مبلغ", "ريال", "دفع", "مستحقات", "مديونية",
            "المحكمة التجارية", "الدائرة التجارية",
            "كمبيالة", "سند لأمر", "شيك"
        ],
        "strong_indicators": [
            "المحكمة التجارية", "سجل تجاري", "سند لأمر",
            "كمبيالة"
        ]
    },
    "property_dispute": {
        "name_ar": "نزاع عقاري",
        "name_en": "Property Dispute",
        "keywords": [
            "عقار", "عقارات", "أرض", "مبنى", "شقة",
            "إيجار", "تأجير", "مستأجر", "مؤجر",
            "إخلاء", "صك", "ملكية", "بيع عقار"
        ],
        "strong_indicators": [
            "إخلاء", "عقد إيجار", "صك ملكية", "نزاع عقاري"
        ]
    },
    "partnership": {
        "name_ar": "مضاربة / شراكة",
        "name_en": "Partnership / Mudharaba",
        "keywords": [
            "شراكة", "شريك", "مضاربة", "رأس المال",
            "حصة", "أرباح", "خسائر", "توزيع الأرباح",
            "شركة مضاربة", "رأس مال"
        ],
        "strong_indicators": [
            "شركة مضاربة", "مضاربة", "رأس المال", "توزيع الأرباح"
        ]
    },
    "compensation": {
        "name_ar": "تعويض",
        "name_en": "Compensation Claim",
        "keywords": [
            "تعويض", "ضرر", "أضرار", "تعويض عن",
            "جبر الضرر", "المسؤولية المدنية", "إتلاف"
        ],
        "strong_indicators": [
            "تعويض عن أضرار", "جبر الضرر", "المسؤولية المدنية"
        ]
    },
    "jurisdictional": {
        "name_ar": "اختصاص قضائي",
        "name_en": "Jurisdictional",
        "keywords": [
            "اختصاص", "عدم اختصاص", "الولاية القضائية",
            "إحالة", "المحكمة المختصة", "اختصاص نوعي"
        ],
        "strong_indicators": [
            "عدم اختصاص", "الولاية القضائية", "اختصاص نوعي"
        ]
    }
}


def classify_case(text: str) -> Dict:
    """
    Classify a legal case based on keyword matching.
    
    Returns dict with:
        - case_type: str (key)
        - name_ar: str
        - name_en: str
        - confidence: float (0.0 - 1.0)
        - matched_keywords: list of matched keywords
        - sub_types: list of secondary classifications
    """
    text_lower = text.strip()
    scores = {}
    matched_keywords_map = {}
    
    for type_key, type_info in CASE_TYPES.items():
        score = 0
        matched = []
        
        # Check regular keywords (1 point each)
        for kw in type_info["keywords"]:
            count = text_lower.count(kw)
            if count > 0:
                score += count
                matched.append(kw)
        
        # Check strong indicators (3 points each)
        for kw in type_info["strong_indicators"]:
            count = text_lower.count(kw)
            if count > 0:
                score += count * 3  # Strong indicators worth 3x
                if kw not in matched:
                    matched.append(kw)
        
        scores[type_key] = score
        matched_keywords_map[type_key] = matched
    
    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    if ranked[0][1] == 0:
        # No keywords matched at all
        return {
            "case_type": "unknown",
            "name_ar": "غير محدد",
            "name_en": "Unknown",
            "confidence": 0.0,
            "matched_keywords": [],
            "sub_types": []
        }
    
    # Primary classification
    primary_type = ranked[0][0]
    primary_score = ranked[0][1]
    
    # Confidence: normalize based on total keyword matches
    # Higher score = higher confidence, capped at 0.98
    total_possible = len(CASE_TYPES[primary_type]["keywords"]) + len(CASE_TYPES[primary_type]["strong_indicators"]) * 3
    raw_confidence = min(primary_score / max(total_possible * 0.3, 1), 1.0)
    confidence = round(min(raw_confidence, 0.98), 2)
    
    # Secondary classifications (types with >30% of primary score)
    sub_types = []
    for type_key, type_score in ranked[1:4]:
        if type_score > 0 and type_score >= primary_score * 0.3:
            sub_types.append({
                "case_type": type_key,
                "name_ar": CASE_TYPES[type_key]["name_ar"],
                "name_en": CASE_TYPES[type_key]["name_en"],
                "relevance": round(type_score / primary_score, 2)
            })
    
    return {
        "case_type": primary_type,
        "name_ar": CASE_TYPES[primary_type]["name_ar"],
        "name_en": CASE_TYPES[primary_type]["name_en"],
        "confidence": confidence,
        "matched_keywords": matched_keywords_map[primary_type],
        "sub_types": sub_types
    }


if __name__ == "__main__":
    # Test with sample case
    test_text = """الوقائع:
تقدم المدعي بدعوى أمام المحكمة العامة يطالب فيها بإلزام المدعى عليه بسداد مبلغ وقدره 75,000 ريال سعودي، 
وذلك نتيجة إخلاله بالعقد المبرم بين الطرفين والمتعلق بتنفيذ أعمال صيانة في أحد العقارات.

الأسباب:
وحيث إن المحكمة بعد الاطلاع على أوراق الدعوى تبين لها وجود عقد صحيح وموقع بين الطرفين، 
وثبوت قيام المدعي بتنفيذ التزاماته التعاقدية.

منطوق الحكم:
حكمت المحكمة بإلزام المدعى عليه بسداد مبلغ 75,000 ريال سعودي للمدعي، وتحميله المصاريف القضائية."""
    
    result = classify_case(test_text)
    print(f"Case Type: {result['name_ar']} ({result['name_en']})")
    print(f"Confidence: {result['confidence']}")
    print(f"Matched Keywords: {', '.join(result['matched_keywords'])}")
    if result['sub_types']:
        print(f"Sub-types: {[s['name_ar'] for s in result['sub_types']]}")
