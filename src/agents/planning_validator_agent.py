from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from tools.data_documentation_tool import get_data_description
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

class Output(BaseModel):
    valid: bool = Field(..., description="Is the plan valid?")
    comment: str = Field(..., description="Comment on the plan's validity.")


class PlanValidatorAgent:
    def __init__(self):
        self.parser = JsonOutputParser(pydantic_object=Output)
        self.validator_llm = BaseChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com",
            max_tokens=2 * 1024,
        )
       
        self.output_parser = OutputFixingParser.from_llm(
            parser=self.parser, llm=self.validator_llm
        )

        self.validator_template = PromptTemplate(
            input_variables=["problem", "data_description", "tools", "plan"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
            template="""
            You are a strategy analyst. Your role is to strictly validate a plan against the constraints below. The plan is **valid only if all constraints are satisfied** — no exceptions.

            ---

            ### Constraints for Plan Validity:

            - **C1: Data Loading First** — The first step must load or access the required data.
            - **C2: Tool Usage Match** — Every tool must be used within the scope of its defined functionality.
            - **C3: Logical Sequence** — Each step must follow logically and depend only on previous steps.
            - **C4: Problem Alignment** — Each step must directly contribute to solving the problem.
            - **C5: All Tools Defined** — Only tools listed may be referenced in the plan.

            ---

            ### Problem:
            {problem}

            ---

            ### Data Description:
            {data_description}

            ---

            ### Available Tools:
            {tools}

            ---

            ### Plan:
            {plan}

            ---

            ### Task:
            Evaluate the plan based strictly on the above constraints. If **all** constraints are satisfied, return `true`. If **any** constraint is violated, return `false`.

            ### Output format : 
            {format_instructions}
            """,
        )

        self.data_description = get_data_description()
        self.validator_chain = LLMChain(
            llm=self.validator_llm, prompt=self.validator_template
        )

    def validate(self, problem, plan,tools):
        tools_description = "\n".join(
            [f"- {t.name}: {t.description}" for t in tools]
        )

        response = self.validator_chain.run(
            {
                "problem": problem,
                "data_description": self.data_description,
                "tools": tools_description,
                "plan": plan,
            }
        )

        return self.output_parser.parse(response)
