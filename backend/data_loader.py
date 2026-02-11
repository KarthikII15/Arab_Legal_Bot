import json
import os
from typing import List, Dict
from models import Case

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/saudi_general_court_judgments.json")

def load_cases(filter_real_only: bool = False) -> List[Case]:
    """
    Load cases from the JSON dataset.
    
    Args:
        filter_real_only (bool): If True, return only cases where is_real is True.
    
    Returns:
        List[Case]: List of Case objects.
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
        
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cases = []
    for item in data:
        # Ensure is_real is present, default to True if missing (for older data structures)
        if "is_real" not in item:
            item["is_real"] = True
            
        case = Case(**item)
        
        if filter_real_only and not case.is_real:
            continue
            
        cases.append(case)
        
    return cases

if __name__ == "__main__":
    # Test loading
    try:
        all_cases = load_cases()
        real_cases = load_cases(filter_real_only=True)
        print(f"Total cases: {len(all_cases)}")
        print(f"Real cases: {len(real_cases)}")
    except Exception as e:
        print(f"Error: {e}")
