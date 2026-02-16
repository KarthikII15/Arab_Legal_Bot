"""
Comprehensive Classification Validation Suite
Tests all case types with multiple real-world examples
"""

import json
import sys
from typing import Dict, List, Any

# Define case types with improved keywords
CASE_TYPES = {
    "contract_dispute": {
        "name_ar": "نزاع عقدي",
        "name_en": "Contract Dispute",
        "keywords": [
            "مقاول", "صاحب عمل", "مقاولة",
            "صيانة", "إصلاح", "تركيب", "تطوير", 
            "مشروع", "أعمال", "حسب العقد",
            "فسخ العقد", "إنهاء العقد", "مخالفة العقد",
            "إخلال بالتزامات", "عدم التنفيذ"
        ]
    },
    "labor_dispute": {
        "name_ar": "نزاع عمالي",
        "name_en": "Labor Dispute",
        "keywords": [
            "عامل", "عمال", "موظف", "راتب", "رواتب",
            "فصل تعسفي", "إنهاء خدمات", "مكافأة نهاية الخدمة",
            "نظام العمل", "عقد العمل", "ساعات العمل",
            "إجازة", "تأمينات", "كفالة"
        ]
    },
    "commercial_dispute": {
        "name_ar": "نزاع تجاري",
        "name_en": "Commercial Dispute",
        "keywords": [
            "تجاري", "تجارية", "شركة", "سجل تجاري",
            "فاتورة", "فواتير", "بيع", "شراء", "سداد",
            "مبلغ", "ريال", "دفع", "مستحقات", "مديونية",
            "التجارية", "الدائرة التجارية",
            "كمبيالة", "سند لأمر", "شيك",
            "بضاعة", "بضائع", "سلعة", "سلع", "مواد",
            "الموردة", "موردة", "المشتري", "مشتري", "الطرف الثاني",
            "المتأخرات", "السداد"
        ]
    },
    "traffic_accident": {
        "name_ar": "حادث مروري",
        "name_en": "Traffic Accident",
        "keywords": [
            "حادث", "مروري", "سيارة", "مركبة", "قيادة",
            "تصادم", "إصابة", "وفاة", "مرور", "رخصة قيادة",
            "تأمين المركبة", "إتلاف", "حوادث السير"
        ]
    },
    "property_dispute": {
        "name_ar": "نزاع عقاري",
        "name_en": "Property Dispute",
        "keywords": [
            "عقار", "عقارات", "أرض", "أراضي", "منزل", "بيت",
            "دار", "عمارة", "سكن", "سكني", "استئجار", "إيجار",
            "ملكية", "تملك", "بيع عقار", "شراء أرض"
        ]
    },
    "partnership": {
        "name_ar": "نزاع شركة",
        "name_en": "Partnership Dispute",
        "keywords": [
            "شركة", "شريك", "شركاء", "حصة", "حصص", "رأس مال",
            "أرباح", "خسارة", "انسحاب", "فسخ الشركة", "مساهم",
            "مجلس إدارة", "قرار شركة"
        ]
    },
    "compensation": {
        "name_ar": "دعوى تعويض",
        "name_en": "Compensation Claim",
        "keywords": [
            "تعويض", "تعويضات", "دية", "أرش", "إصابة", "ضرر",
            "أضرار", "خسارة مالية", "جرح", "عاهة", "دعوى تعويض"
        ]
    },
    "jurisdictional": {
        "name_ar": "موضوع اختصاص",
        "name_en": "Jurisdictional Issue",
        "keywords": [
            "اختصاص", "عدم اختصاص", "الولاية القضائية", "الاختصاص القضائي",
            "إحالة", "المحكمة المختصة", "اختصاص نوعي", "اختصاص مكاني",
            "دفع بعدم الاختصاص", "عدم اختصاص المحكمة", "محكمة غير مختصة"
        ]
    },
    "unknown": {
        "name_ar": "غير محدد",
        "name_en": "Unknown",
        "keywords": []
    }
}

test_cases = [
    # Commercial disputes (3 cases)
    {
        "id": "commercial_001",
        "category": "commercial_dispute",
        "expected": "commercial_dispute",
        "text": "نزاع حول عقد توريد بضائع. شركة النجم للتجارة والشركة الخليج للتوريد. عدم تنفيذ بنود العقد. توريد 500 طن من مواد البناء. المتأخرات: 250,000 ريال"
    },
    {
        "id": "commercial_002",
        "category": "commercial_dispute",
        "expected": "commercial_dispute",
        "text": "مطالبة بسداد فاتورة تجارية. فاتورة شراء بضائع تصنيعية. المشتري: شركة الصناعة والتصدير. الموردة: شركة الآلات الصناعية. المبلغ المستحق: 500,000 ريال"
    },
    {
        "id": "commercial_003",
        "category": "commercial_dispute",
        "expected": "commercial_dispute",
        "text": "نزاع حول عدم دفع قيمة الشحنة. الشركة الأولى باعت سلع لشركة ثانية. الفاتورة: 150,000 ريال. الدفع لم يتم خلال 30 يوم من استلام البضاعة"
    },
    
    # Labor disputes (3 cases)
    {
        "id": "labor_001",
        "category": "labor_dispute",
        "expected": "labor_dispute",
        "text": "نزاع عمالي. الموظف: أحمد محمد علي. شركة النور للتوزيع. فصل تعسفي من العمل. مطالبات: راتب 3 أشهر، مكافأة نهاية الخدمة، تعويض"
    },
    {
        "id": "labor_002",
        "category": "labor_dispute",
        "expected": "labor_dispute",
        "text": "دعوى عمالية. عامل بناء توقف عن إرسال رواتبه المتأخرة. 6 أشهر من الرواتب لم تُدفع. صاحب العمل أغلق المشروع ورفض تسديد حقوق العامل"
    },
    {
        "id": "labor_003",
        "category": "labor_dispute",
        "expected": "labor_dispute",
        "text": "شكوى موظفة إعادة السيدة إلى عملها. تم إنهاء خدماتها بدون مبرر قانوني. مطالبة بمكافأة نهاية الخدمة والرواتب المتأخرة"
    },
    
    # Property disputes (3 cases)
    {
        "id": "property_001",
        "category": "property_dispute",
        "expected": "property_dispute",
        "text": "نزاع عقاري. المالك: فاطمة محمد العتيبي. المستأجر: سعود علي العمري. عدم دفع بدل الإيجار. شقة سكنية. المتأخرات: 9000 ريال (3 أشهر)"
    },
    {
        "id": "property_002",
        "category": "property_dispute",
        "expected": "property_dispute",
        "text": "دعوى إخلاء عقار. نزاع بين مالك الأرض والمستأجر. المستأجر تجاوز فترة العقد ورفض الإخلاء. الأرض الزراعية مساحة 10000 متر"
    },
    {
        "id": "property_003",
        "category": "property_dispute",
        "expected": "property_dispute",
        "text": "نزاع ملكية عقار. تضارب في صكوك الملكية. أرض سكنية في الرياض. يدعي الطرف الأول أنها ملكه والطرف الثاني يدعي ملكيتها"
    },
    
    # Traffic accidents (2 cases)
    {
        "id": "traffic_001",
        "category": "traffic_accident",
        "expected": "traffic_accident",
        "text": "حادث مروري. تصادم سيارة تويوتا مع سيارة هونداي. طريق الخليج، الرياض. إصابة راكب. أضرار المركبات: 50000 ريال. تقرير المرور يسؤول سائق السيارة الثانية"
    },
    {
        "id": "traffic_002",
        "category": "traffic_accident",
        "expected": "traffic_accident",
        "text": "دعوى حادث سير. تصادم سيارتين بسبب عدم الالتزام بإشارات المرور. وفاة راكب في السيارة الأولى. مطالبة بالدية والتعويض"
    },
    
    # Compensation claims (2 cases)
    {
        "id": "compensation_001",
        "category": "compensation",
        "expected": "compensation",
        "text": "دعوى تعويض. ضرر لحق بالممتلكات الشخصية. إتلاف سيارة خاصة بسبب عدم الحفاظ عليها. تقدير الضرر: 80000 ريال"
    },
    {
        "id": "compensation_002",
        "category": "compensation",
        "expected": "compensation",
        "text": "مطالبة بالتعويض عن أضرار. خسارة مالية ناتجة عن عدم تنفيذ التزام. المسؤولية المدنية. المبلغ المطالب به: 300,000 ريال"
    },
    
    # Partnership disputes (2 cases)
    {
        "id": "partnership_001",
        "category": "partnership",
        "expected": "partnership",
        "text": "نزاع شراكة. اختلاف بين الشركاء على توزيع الأرباح. الشريك الأول يعترض على قرار مجلس الإدارة. حصة الشريك: 40% من رأس المال"
    },
    {
        "id": "partnership_002",
        "category": "partnership",
        "expected": "partnership",
        "text": "دعوى فسخ شركة. الشريك الأول يرغب في الانسحاب من الشركة. نزاع حول قيمة الحصة والمحاسبة. رأس مال الشركة: 1,000,000 ريال"
    },
    
    # Jurisdictional issue (1 case)
    {
        "id": "jurisdictional_001",
        "category": "jurisdictional",
        "expected": "jurisdictional",
        "text": "دفع بعدم الاختصاص. هذه المحكمة غير مختصة نوعياً في النظر في الدعوى. يجب إحالة القضية للمحكمة الإدارية المختصة. دفع الاختصاص المكاني"
    }
]

class SimpleClassifier:
    """Simple keyword-based classifier"""
    
    def classify_case(self, text: str) -> Dict[str, Any]:
        """Classify using keywords only"""
        text_lower = text.lower()
        scores = {}
        
        for case_type, data in CASE_TYPES.items():
            if case_type == "unknown":
                continue
            
            # Count keyword matches
            matches = sum(1 for kw in data["keywords"] if kw in text_lower)
            score = min(matches / 5.0, 1.0) if matches > 0 else 0.0
            scores[case_type] = score
        
        # Find best match
        if not scores or max(scores.values()) < 0.15:
            return {
                "case_type": "unknown",
                "name_ar": "غير محدد",
                "name_en": "Unknown",
                "confidence": 0.0,
            }
        
        primary_type = max(scores, key=scores.get)
        primary_score = scores[primary_type]
        
        # Map score to confidence
        display_confidence = min(max((primary_score - 0.0) / 1.0 * 0.6 + 0.4, 0.4), 0.95)
        
        return {
            "case_type": primary_type,
            "name_ar": CASE_TYPES[primary_type]["name_ar"],
            "name_en": CASE_TYPES[primary_type]["name_en"],
            "confidence": round(display_confidence, 2),
            "raw_score": round(primary_score, 4)
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ISSUE 2: COMPREHENSIVE CLASSIFICATION VALIDATION")
    print("="*80 + "\n")
    
    classifier = SimpleClassifier()
    
    # Test all cases
    passed = 0
    failed = 0
    results_by_category = {}
    
    for test_case in test_cases:
        result = classifier.classify_case(test_case["text"])
        expected = test_case["expected"]
        actual = result["case_type"]
        
        # Track by category
        if expected not in results_by_category:
            results_by_category[expected] = {"total": 0, "passed": 0}
        results_by_category[expected]["total"] += 1
        
        is_pass = actual == expected
        if is_pass:
            passed += 1
            results_by_category[expected]["passed"] += 1
        else:
            failed += 1
        
        status = "✓" if is_pass else "✗"
        print(f"{status} {test_case['id']:25} | Expected: {expected:18} Got: {actual:18} | Confidence: {result['confidence']:.0%}")
    
    # Print category summary
    print("\n" + "="*80)
    print("ACCURACY BY CATEGORY:")
    print("="*80 + "\n")
    
    for category in sorted(results_by_category.keys()):
        stats = results_by_category[category]
        accuracy = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✓" if accuracy >= 90 else "✗"
        print(f"{status} {category:25} | {stats['passed']}/{stats['total']} | {accuracy:.0f}%")
    
    # Overall summary
    total = passed + failed
    overall_accuracy = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*80)
    print("OVERALL SUMMARY:")
    print("="*80)
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 90:
        print("\n✓ VALIDATION PASSED: Classification accuracy >= 90%")
    else:
        print(f"\n✗ VALIDATION FAILED: Classification accuracy {overall_accuracy:.1f}% < 90%")
    
    print("\n" + "="*80 + "\n")
