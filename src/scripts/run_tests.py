import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

import pandas as pd
import argparse
from langsmith import  Client
from typing import  List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from testing.llm_as_a_judge import AnswerJudge
from dotenv import load_dotenv

load_dotenv()

langsmith_client = Client()


judge = AnswerJudge()

def benchmark_and_judge(results: List[Dict[str, Any]], max_workers: int = None) -> pd.DataFrame:
    df = pd.DataFrame(results)

    if max_workers is None:
        max_workers = os.cpu_count() * 4  # Ideal for I/O bound

    records = df.to_dict(orient="records")
    print(f"🔍 Starting verdict generation on {len(records)} records with {max_workers} workers...\n")

    def process_row(row: Dict[str, Any]) -> Dict[str, Any]:
       
        output = judge.evaluate(
            question=row.get("question"),
            reference_answer=row.get("reference_answer"),
            generated_answer=row.get("generated_answer"),
        )
        row["verdict"] = output.get("verdict")
        row["raw_judge_output"] = output
        return row

    results_with_verdicts = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_row, row): i for i, row in enumerate(records, 1)}
        for count, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results_with_verdicts.append(result)
            print(f"✅ Completed {count}/{len(records)}")

    print("\n🎉 All verdicts generated.")
    return pd.DataFrame(results_with_verdicts)


def summarize_test_results(df) -> None:
    print("📊 Summary of Test Results:\n")
    print("Total Runs:", len(df))
    print(
        "Successful Runs:",
        df["error"].fillna("No Error").value_counts().get("No Error", 0),
    )
    print("Average Duration:", df["duration (sec)"].mean(), "seconds")
    print("Total Tokens Used:", df["total_tokens"].sum(), "tokens")
    print(
        "Accuracy:", df["verdict"].value_counts(normalize=True).get(True, 0) * 100, "%"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests and benchmarks.")
    parser.add_argument("--run", metavar="RUN_ID", type=str, help="Specify the run ID (CSV filename without extension) to load answers from.")
    parser.add_argument("--use_reformulated", action="store_true", help="Use reformulated dataset if set.")
    args = parser.parse_args()

    answers = pd.read_csv(f"runs/{args.run}.csv")
    dataset_path = "dataset_reformulated.csv" if args.use_reformulated else "dataset.csv"
    dataset = pd.read_csv(dataset_path)

    answers = answers.merge(dataset, left_on="question", right_on="questions", how="left")
    answers = answers.drop(columns=["questions"])
    answers = answers.rename(columns={"answers": "reference_answer"})
    benchmark_results = benchmark_and_judge(results=answers.to_dict(orient="records"), max_workers=16)
    suffix = "_reformulated" if args.use_reformulated else ""
    benchmark_results.to_csv(f"benchmarks/benchmark_results_{args.run}{suffix}.csv", index=False)
    os.system('clear' if os.name == 'posix' else 'cls')
    summarize_test_results(benchmark_results)