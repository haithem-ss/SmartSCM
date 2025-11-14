import argparse
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import os
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()

class AnswerReformulator:
    def __init__(self, model_name="gemma3:latest"):
        self.llm = Ollama(model=model_name)
        self.prompt = PromptTemplate(
            input_variables=["question", "answer"],
            template="""
            You are a helpful assistant. Given the question: '{question}' and a corresponding raw output from pandas code: '{answer}', rewrite the answer in a concise, human-readable form that directly answers the question. Avoid code syntax or unnecessary technical terms unless relevant. Provide only one clear, natural-sounding response.
            """        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def reformulate(self, question, answer):
        return self.chain.run({'question': question, 'answer': answer})



def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def reformulate_answers(questions, answers, max_workers=4, verbose=True):
    reformulator = AnswerReformulator()
    def reformulate_pair(pair):
        question, answer = pair
        return reformulator.reformulate(question, answer)

    results = []
    total = len(questions)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        iterable = zip(questions, answers)
        if verbose:
            print(f"Reformulating {total} questions...")
        for idx, result in enumerate(executor.map(reformulate_pair, iterable), 1):
            results.append(result)
            if verbose and idx % 10 == 0:
                clear_terminal()
                print(f"Reformulating {total} questions...\nProcessed {idx}/{total}")
    return results

def parse_evaluation_dataset_notebook():
    import nbformat
    import re

    with open(EVALUATION_DATASET_NOTEBOOK_PATH) as f:
        nb = nbformat.read(f, as_version=4)

    question, answers, code,difficulty = [], [], [],[]

    questions_started = False
    difficulties = ["easy", "medium", "hard"]
    current_difficulty = 0

    for cell in nb.cells:
        if cell.cell_type == "markdown" and cell.source.startswith("# Questions"):
            questions_started = True
            continue
        if cell.cell_type == "markdown" and cell.source.startswith("#"):
            if cell.source.startswith("# 33 Medium question") or cell.source.startswith("# 33 Hard questions"):
                current_difficulty += 1
            questions_started = True
        if cell.cell_type == "markdown" and not cell.source.startswith("#"):
            q = cell.source.strip()
            q = re.sub(r'^\d+\.?\s*', '', q)  # Clean leading numbers
            question.append(q)
            difficulty.append(difficulties[current_difficulty])
        elif cell.cell_type == "code" and questions_started:
            source = cell.source.strip()
            if source:
                code.append(source)
            ans = [i.data["text/plain"].strip() for i in cell.outputs if "text/plain" in i.data]
            if ans:
                answers.append(ans[0])
    
    return pd.DataFrame({"questions": question, "answers": answers, "code": code, "type": "Ordinary","difficulty":difficulty})

def parse_oos_questions_notebook():
    import nbformat

    with open(EVALUATION_DATASET_NOTEBOOK_PATH) as f:
        nb = nbformat.read(f, as_version=4)

    question, answers = [], []
    oos_started = False

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            if cell.source.startswith("# OOS"):
                oos_started = True
                continue
            if oos_started:
                items = [line.strip() for line in cell.source.strip().replace("###", "").split("\n") if line.strip()]
                if len(items) >= 2:
                    question.append(items[0])
                    answers.append(items[1])
    return pd.DataFrame({"questions": question, "answers": answers, "type": "OOS"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and optionally reformulate dataset.")
    parser.add_argument("--reformulate", action="store_true", help="Reformulate answers if set.")
    args = parser.parse_args()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EVALUATION_DATASET_NOTEBOOK_PATH = os.path.join(BASE_DIR, "notebooks", "Evaluation","Evaluation_dataset.ipynb")

    df = parse_evaluation_dataset_notebook()
    oos_df = parse_oos_questions_notebook()
    print(f"Total questions: {len(df)+len(oos_df)}")
    if args.reformulate:
        reformulated = reformulate_answers(df["questions"], df["answers"], max_workers=16, verbose=True)
        df["answers"] = reformulated
        df = pd.concat([df, oos_df], ignore_index=True)
        print("✅ Reformulation complete.")
    else:
        print("⚠️ Reformulation skipped (use --reformulate to enable).")

    output_path ="dataset.csv" if not args.reformulate else "dataset_reformulated.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Dataset saved to '{output_path}'")