# codes/accuracy_bias_analysis.py

"""
Usage:
    python accuracy_bias_analysis.py --input PATH_TO_DATA

This script will:
 1. Load LLM response data (JSONL or CSV)
 2. Extract case_num & variant_num from record IDs
 3. Map variant_num → (doctor_race, doctor_gender, patient_race)
 4. Preprocess text (lowercasing, parentheses handling)
 5. Evaluate correctness (is_correct flag with abbrev/full-term matching)
 6. Print overall and demographic-grouped accuracy
"""

import argparse
import json
import re
from typing import List, Dict

def load_data(path: str) -> List[Dict]:
    """
    Load records from JSONL or CSV:
      - If .jsonl: json.loads(line) per line
      - If .csv: pandas.read_csv and to_dict(orient='records')
    Returns: list of record dicts
    """
    # TODO: implement loading logic
    return records

def get_doctor_patient_info(variant_num: int):
    """
    Map variant_num to:
      doctor_race (str), doctor_gender (str), patient_race (str)
    """
    # TODO: your mapping logic
    return doctor_race, doctor_gender, patient_race

def map_demographics(records: List[Dict]) -> List[Dict]:
    for rec in records:
        case_num, var_str = rec["id"].split("_")
        rec["case_num"]     = case_num
        rec["variant_num"]  = int(var_str)
        dr, dg, pr = get_doctor_patient_info(int(var_str))
        rec["doctor_race"]  = dr
        rec["doctor_gender"]= dg
        rec["patient_race"] = pr
    return records

def preprocess_text(records: List[Dict]) -> List[Dict]:
    for rec in records:
        rec["instruction"]   = rec["instruction"].lower().strip()
        rec["answer"]        = rec["answer"].strip()
        rec["llm_response"]  = rec.get("llm_response", "").lower().strip()
    return records

def expand_answer(answer: str) -> set[str]:
    """
    If answer contains parentheses, e.g. "HTN (hypertension)",
    return both sides plus the original. Otherwise single term.
    """
    m = re.match(r"(.*?)\s*\((.*?)\)", answer)
    if m:
        outside = m.group(1).lower().strip()
        inside  = m.group(2).lower().strip()
        return {outside, inside, answer.lower()}
    return {answer.lower()}

def evaluate(records: List[Dict]) -> List[Dict]:
    for rec in records:
        resp = rec.get("llm_response", "")
        candidates = expand_answer(rec["answer"])
        rec["is_correct"] = any(cand in resp for cand in candidates)
    return records

def summarize(records: List[Dict]):
    import pandas as pd
    df = pd.DataFrame(records)
    overall = df["is_correct"].mean()
    by_doc_race = df.groupby("doctor_race")["is_correct"].mean()
    by_pat_race = df.groupby("patient_race")["is_correct"].mean()
    by_gender   = df.groupby("doctor_gender")["is_correct"].mean()

    print(f"Overall accuracy: {overall:.2%}\n")
    print("Accuracy by doctor_race:")
    print(by_doc_race.to_markdown(), "\n")
    print("Accuracy by patient_race:")
    print(by_pat_race.to_markdown(), "\n")
    print("Accuracy by doctor_gender:")
    print(by_gender.to_markdown())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", required=True,
        help="Path to JSONL or CSV file containing model responses"
    )
    args = parser.parse_args()

    data = load_data(args.input)
    data = map_demographics(data)
    data = preprocess_text(data)
    data = evaluate(data)
    summarize(data)

if __name__ == "__main__":
    main()
