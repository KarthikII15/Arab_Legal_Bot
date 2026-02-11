import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_cases
from trend_analyzer import extract_compensation_amount

def main():
    try:
        cases = load_cases()
        print(f"Loaded {len(cases)} cases.")
        
        huge_amounts = []
        all_amounts = []
        
        for case in cases:
            # Check judgment
            amt = extract_compensation_amount(case.judgment)
            if not amt:
                # Check facts
                amt = extract_compensation_amount(case.facts)
            
            if amt:
                all_amounts.append(amt)
                if amt > 1000000:
                    huge_amounts.append((case.case_id, amt, case.judgment[:100]))

        print(f"Total extracted amounts: {len(all_amounts)}")
        print(f"Average amount: {sum(all_amounts)/len(all_amounts) if all_amounts else 0}")
        print(f"Max amount: {max(all_amounts) if all_amounts else 0}")

        print("\n--- HUGE AMOUNTS (> 1 Million) ---")
        for case_id, amt, excerpt in huge_amounts:
            print(f"Case {case_id}: {amt:,.2f} SAR")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
