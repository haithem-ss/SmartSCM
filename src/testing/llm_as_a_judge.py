from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
import os
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_sbert_score(generated, reference):


    # Compute embeddings
    embedding1 = model.encode(generated, convert_to_tensor=True)
    embedding2 = model.encode(reference, convert_to_tensor=True)

    # Compute cosine similarity
    cosine_score = util.pytorch_cos_sim(embedding1, embedding2)

    return cosine_score.item()

class SimpleOutput(BaseModel):
    verdict: bool = Field(
        ..., description="Is the generated answer and the reference answer similar?"
    )


class AnswerJudge:

    def __init__(self):
        self.parser = JsonOutputParser(pydantic_object=SimpleOutput)

        prompt_template = """
                You are an expert evaluator. Given a question, a reference answer, and a generated answer, decide if the generated answer is factually consistent with the reference answer and correctly answers the question.

                Use the following evaluation criteria with an emphasis on overall semantic equivalence rather than strict word-for-word matching:
                1. Factual Accuracy: Ensure there are no direct contradictions between the generated and reference answers. Minor differences in wording or phrasing are acceptable if the meaning aligns.
                2. Completeness: The generated answer should address the main points relevant to the question, but it does not have to mention every detail found in the reference.
                3. Relevance: The answer should be focused on the question and not stray into unrelated topics.
                4. Clarity: The answer should be understandable and logically structured.
                5. Terminology: Use appropriate language but allow for synonyms and paraphrases.

                Important:
                - If the generated answer contradicts the reference answer on any factual point, return verdict=False.
                - If the generated answer is self-contradictory, return verdict=False.
                - However, if the generated answer conveys the same core information or conclusion as the reference answer, even if some details differ or are omitted, return verdict=True.

                Return your output **as a JSON object only** in the following format:
                    - verdict: true or false (boolean)
                ⚠️ Do not include any additional commentary or explanation outside the JSON block.

                Question: {question}
                Reference Answer: {reference_answer}
                Generated Answer: {generated_answer}
        """

        self.llm=Ollama(model="cas/nous-hermes-2-mistral-7b-dpo:latest")

        self.prompt = PromptTemplate(
            input_variables=["question", "reference_answer", "generated_answer"],
            template=prompt_template,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        self.chain = LLMChain(
            llm=self.llm, prompt=self.prompt, output_parser=self.parser
        )

    def evaluate(self, question: str, reference_answer: str, generated_answer: str):
        score = compute_sbert_score(generated_answer, reference_answer)

        # Shortcut if SBERT is strong enough
        if score > 0.8:
            return {
                "verdict": True,
                "explanation": f"The generated answer is similar to the reference answer based on SBERT score of {score:.2f}",
                "method": "SBERT"
            }

        try:
            # 1. Generate raw output string from LLM
            raw_output = self.chain.run(
                question=question,
                reference_answer=reference_answer,
                generated_answer=generated_answer,
            )

            # 2. Try direct parsing first
            try:
                if isinstance(raw_output, dict) and "verdict" in raw_output:
                    return {
                        "verdict": raw_output["verdict"],
                        "method": "LLM-as-a-judge"
                    }
                else:
                    raise ValueError("Output is not a valid JSON object")
                
            except Exception as e:
                print("Initial parse failed, trying OutputFixingParser:", str(e))
                fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
                fixed_output = fixing_parser.parse(raw_output)
                return {
                "verdict": fixed_output.get("verdict", False),
                "method": "LLM-as-a-judge"
            }

        except Exception as e:
            print(f"Final error during evaluation: {str(e)}")
            return {
                "verdict": False,
                "explanation": f"Error during evaluation: {str(e)}",
                "method": "LLM-as-a-judge"
            }