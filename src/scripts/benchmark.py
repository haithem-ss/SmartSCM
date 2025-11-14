import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

import pandas as pd
import argparse
from langsmith import traceable, Client
from typing import Callable, List, Dict, Any
import uuid
from dotenv import load_dotenv
import random
import string

load_dotenv()

def invoke(query: str) -> str:

    from agents.orchestrator import LLMOrchestrator

    pandas_agent=LLMOrchestrator(disable_callbacks=True,variant="defauly")
    return pandas_agent.orchestrate(query,prefix_prompt="if you cant answer for any reason please output this 'The system cannot answer this question'")

def generate_agent_answers(invoke_callback: Callable[[str], str], dataset: List[Dict[str, Any]]) -> pd.DataFrame:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    filename = f"run_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    total = len(dataset)
    print(f"🔍 Starting threaded answer generation on {total} dataset entries...\n")
    
    results = []

    def process_entry(entry_idx: int, entry: Dict[str, Any]) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        print(f"➡️  [{entry_idx+1}/{total}] Running entry with name: {run_id}")
        
        @traceable(name=run_id, project_name="PFE")
        def orchestrate(input: str) -> str:
            return invoke_callback(input)

        input_str = entry["questions"]
        output = orchestrate(input=input_str)

        return {
            "run_id": run_id,
            "question": input_str,
            "generated_answer": output["output"],
            "plan":output["plan"]
        }

    # Use ThreadPoolExecutor to parallelize execution
    with ThreadPoolExecutor(max_workers=16) as executor:
        # Submit all jobs
        futures = [executor.submit(process_entry, i, entry) for i, entry in enumerate(dataset)]
        
        # Gather results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "run_id": None,
                    "question": None,
                    "generated_answer": "There was an error",
                    "plan": None,
                })

    
    print(f"✅ Finished all threads. Results saved to {filename}")
    return pd.DataFrame(results)


def get_langsmith_data(results: List[Dict[str, Any]]) -> pd.DataFrame:
    run_ids = {r["run_id"] for r in results}  # Use set for faster lookup
    print(f"📡 Fetching LangSmith run data for {len(run_ids)} runs...\n")
    start_date =datetime.datetime.now() - datetime.timedelta(hours=2)
    runs = list(langsmith_client.list_runs(project_name="PFE", execution_order=1,  start_time=start_date  ))
    print(f"📊 Found {len(runs)} runs in LangSmith...\n")
    data = []
    run_id_to_r = {r["run_id"]: r for r in results}
    for run in runs:
        if run.name in run_id_to_r:
            r = run_id_to_r[run.name]
            data.append({
                "run_id": run.id,
                "duration (sec)": (run.end_time - run.start_time).total_seconds()
                if run.end_time and run.start_time else None,
                "error": run.error,
                "total_tokens": run.total_tokens,
                "question": r.get("question"),
                "generated_answer": r.get("generated_answer"),
            })
    print(f"📊 Assembling results into DataFrame...\n")
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    langsmith_client = Client()

    parser = argparse.ArgumentParser(description="Read a CSV file and print its columns.")
    parser.add_argument("--original", action="store_true", help="Use reformulated answer if set, otherwise use original answer")
    parser.add_argument("--name", type=str, default=None, help="Optional name for the benchmark run (used as filename)")
    args = parser.parse_args()    

    dataset = pd.read_csv("dataset.csv")

    answers= generate_agent_answers(dataset=dataset.to_dict(orient="records"), invoke_callback=invoke)
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".csv" if args.name is None else args.name + ".csv"
    try:
        final_df = get_langsmith_data(results=answers.to_dict(orient="records"))
        final_df.to_csv("runs/"+file_name, index=False)
    except Exception as e:
        answers.to_csv("runs/"+file_name, index=False)
    print(f"✅ Answers saved to {file_name}")

