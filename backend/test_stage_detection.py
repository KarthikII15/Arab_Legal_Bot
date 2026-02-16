"""
Document Stage Detection Validation Tests
Tests the stage detector with real legal document examples
"""

from document_stage_detector import stage_detector, DocumentStage
from typing import Dict, List, Tuple, Any

# Test cases with expected stages
test_cases = [
    # CLAIM documents (3 cases)
    {
        "id": "claim_001",
        "expected_stage": "claim",
        "text": """
        دعوى رقم 2024/1001
        
        المدعي: محمد أحمد علي
        المدعى عليه: شركة النجم للتجارة
        
        تاريخ رفع الدعوى: 2024-01-15
        
        الموضوع: تعويض عن عدم تنفيذ عقد توريد بضائع
        
        يطلب المدعي من المحكمة الحكم له بالتعويض عن الأضرار الناجمة عن عدم تنفيذ الشركة لعقد التوريد.
        المطالبة: 250,000 ريال مع حساب الفائدة والمصروفات.
        """
    },
    {
        "id": "claim_002",
        "expected_stage": "claim",
        "text": """
        عريضة دعوى أمام المحكمة العامة
        
        الشاكي: فاطمة محمد العتيبي
        المشكو بحقه: أحمد سعود الدعيج
        
        الموضوع: مطالبة بأداء التزام عقدي
        
        تقدم الشاكية بهذه الشكوى طالبة من المحكمة الحكم على المشكو بحقه بدفع مستحقاتها المتأخرة.
        الطلب: الحكم بدفع 150,000 ريال مع الفائدة من تاريخ الاستحقاق.
        """
    },
    {
        "id": "claim_003",
        "expected_stage": "claim", 
        "text": """
        الدعوى رقم 2024/450
        
        استناداً إلى نصوص نظام المرافعات الشرعية والمعاملات المدنية والقانون الكويتي،
        يرفع المدعي هذه الدعوى بطلب الحكم له بالتعويض.
        
        الحقائق: وقع نزاع تجاري بين الطرفين حول عقد شراء.
        المطالب: يطلب المدعي تعويض من 300,000 ريال.
        """
    },
    
    # DEFENSE documents (3 cases)
    {
        "id": "defense_001",
        "expected_stage": "defense",
        "text": """
        جواب الدعوى رقم 2024/1001
        
        المدعى عليه: شركة النجم للتجارة ممثلة بمحاميها
        بتاريخ: 2024-01-22
        
        الموضوع: جواب وأوجه دفاع
        
        ينفي المدعى عليه جميع الادعاءات الواردة في الدعوى برمتها.
        يدفع بعدم صحة المطالبات وبعدم التزامه بالالتزامات المنسوبة إليه.
        يعترض على طلب التعويض المذكور ويطلب رفض الدعوى برمتها.
        """
    },
    {
        "id": "defense_002",
        "expected_stage": "defense",
        "text": """
        رد المدعى عليه على الشكوى رقم 2024/450
        
        المدعى عليه: أحمد الدعيج
        تاريخ الرد: 2024-01-25
        
        يستند هذا الرد أولاً وأساساً إلى أن المدعي قد أخل بالالتزامات المتقابلة.
        ينكر المدعى عليه الادعاءات التالية...
        يرد على دعوة المدعي بقوة القانون والواقع والملابسات.
        """
    },
    {
        "id": "defense_003",
        "expected_stage": "defense",
        "text": """
        جواب دفاع رقم 2024/200
        
        ترد المدعى عليها على الشكوى وتدفع بما يلي:
        - عدم مسؤوليتها عن المطالبات المذكورة
        - استيفاء جميع التزاماتها تجاه المدعية
        - بطلان الدعوى من حيث الاختصاص
        """
    },
    
    # JUDGMENT documents (2 cases)
    {
        "id": "judgment_001",
        "expected_stage": "judgment",
        "text": """
        الحكم رقم 2024/1500
        
        باسم الملك الملك، وسلطة نيابة عن الدين وللدين
        حكمت محكمة الرياض العامة بجلستها المنعقدة بتاريخ 2024-03-15
        تحت رئاسة فضيلة الشيخ القاضي الدكتور...
        
        في القضية المرفوعة من محمد أحمد ضد شركة النجم:
        
        بعد سماع المرافعات وتدقيق الأوراق والمستندات:
        قررت المحكمة: الحكم للمدعي بمبلغ 200,000 ريال مع الفائدة.
        
        هذا الحكم قطعي نهائي.
        رقم الحكم: 2024/1500/ب
        """
    },
    {
        "id": "judgment_002",
        "expected_stage": "judgment",
        "text": """
        القرار الصادر من محكمة التمييز
        
        تاريخ القرار: 2024-04-10
        
        قضت محكمة التمييز برفع الاستئناف وتأييد الحكم الابتدائي بأكمله.
        
        قررت المحكمة:
        1. تأييد الحكم الابتدائي رقم 2024/1500
        2. إدانة المستأنف بالمصروفات والرسوم
        3. نفاذ فوري للحكم
        
        القرار نهائي وملزم.
        """
    },
    
    # APPEAL documents (1 case)
    {
        "id": "appeal_001",
        "expected_stage": "appeal",
        "text": """
        استئناف رقم 2024/220
        
        الطاعن: شركة النجم للتجارة
        ضد القرار: حكم الدرجة الأولى رقم 2024/1500
        
        تاريخ الاستئناف: 2024-03-25
        
        يستأنف الطاعن الحكم الابتدائي السابق ويطلب إلغاء الحكم والحكم برفض الدعوى الأصلية.
        أسباب الاستئناف: أن الحكم قام على أساس خاطئ من الناحية القانونية والواقعية.
        يطلب الطاعن من محكمة الاستئناف التعويض عن الأضرار المترتبة على الحكم الابتدائي.
        تاريخ القصة: كان الحكم الأول صادراً في 2024-03-15 ولم يكن التمييز فيه صحيحاً.
        """
    },
    
    # EVIDENCE document (1 case)
    {
        "id": "evidence_001",
        "expected_stage": "evidence",
        "text": """
        وثيقة الملحق رقم 001
        
        المرفق: صورة من العقد التجاري المبرم بين الطرفين
        التاريخ: 2023-12-01
        
        هذه الوثيقة مرفقة بالدعوى كدليل إثبات على وجود الالتزام المنسوب للمدعى عليه.
        محرر: عقد توريد بضائع ملحق الوثائق رقم 001
        """
    },
    
    # UNKNOWN documents (1 case)
    {
        "id": "unknown_001",
        "expected_stage": "unknown",
        "text": "هذا نص عام لا يتعلق بأي مرحلة قانونية محددة."
    }
]

def run_validation_tests() -> Dict[str, Any]:
    """Run all stage detection validation tests."""
    print("\n" + "="*80)
    print("ISSUE 3: DOCUMENT STAGE DETECTION VALIDATION")
    print("="*80 + "\n")
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "by_stage": {},
        "failures": []
    }
    
    for test_case in test_cases:
        test_id = test_case["id"]
        expected_stage = test_case["expected_stage"]
        text = test_case["text"]
        
        # Run detection
        result = stage_detector.detect_stage(text)
        actual_stage = result["stage"]
        confidence = result["confidence"]
        
        # Check result
        is_pass = actual_stage == expected_stage
        
        # Track by stage
        if expected_stage not in results["by_stage"]:
            results["by_stage"][expected_stage] = {"total": 0, "passed": 0}
        results["by_stage"][expected_stage]["total"] += 1
        
        if is_pass:
            results["passed"] += 1
            results["by_stage"][expected_stage]["passed"] += 1
            status = "✓"
        else:
            results["failed"] += 1
            status = "✗"
            results["failures"].append({
                "test_id": test_id,
                "expected": expected_stage,
                "actual": actual_stage,
                "confidence": confidence
            })
        
        print(f"{status} {test_id:20} | Expected: {expected_stage:12} Got: {actual_stage:12} | Conf: {confidence:.0%}")
    
    # Print summary by stage
    print("\n" + "="*80)
    print("ACCURACY BY STAGE:")
    print("="*80 + "\n")
    
    for stage in sorted(results["by_stage"].keys()):
        stats = results["by_stage"][stage]
        accuracy = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✓" if accuracy >= 90 else "✗" if accuracy == 0 else "⚠"
        print(f"{status} {stage:15} | {stats['passed']}/{stats['total']} | {accuracy:.0f}%")
    
    # Overall result
    print("\n" + "="*80)
    print("OVERALL SUMMARY:")
    print("="*80)
    print(f"\nTotal Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    overall_accuracy = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    if results['failures']:
        print("\nFailed Tests:")
        for failure in results['failures']:
            print(f"  - {failure['test_id']}: Expected {failure['expected']}, got {failure['actual']} ({failure['confidence']:.0%})")
    
    if overall_accuracy >= 85:
        print(f"\n✓ VALIDATION PASSED: Stage detection accuracy {overall_accuracy:.0f}% >= 85%")
    else:
        print(f"\n✗ VALIDATION NEEDS WORK: Stage detection accuracy {overall_accuracy:.0f}% < 85%")
    
    print("\n" + "="*80 + "\n")
    
    return results


if __name__ == "__main__":
    results = run_validation_tests()
