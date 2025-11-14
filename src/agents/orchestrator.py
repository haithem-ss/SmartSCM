from datetime import datetime
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.base import BaseCallbackManager
from paths import LOGS_DIR

class UIStreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, step_callback):
        self.step_callback = step_callback

    def on_agent_action(self, action, **kwargs):
        if action.tool=="PlanValidatorTool":
            self.step_callback(f"Validating the plan")
        if action.tool=="data_vizualization":
            self.step_callback(f"Visualizing data")
        if action.tool=="data_loader":
            self.step_callback(f"Loading data")
        if action.tool=="PandasAgentTool":
            self.step_callback(f"Performing data analysis on the data")

    def on_agent_finish(self, finish, **kwargs):
        self.step_callback(f"Finished executing the plan.")

class LogStreamingCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that appends log messages to a provided list for default log saving.
    """
    def __init__(self, log_steps):
        self.log_steps = log_steps

    def on_agent_action(self, action, **kwargs):
        step_info = {"action": str(action), "kwargs": kwargs}
        if action.tool == "PlanValidatorTool":
            step_info["message"] = "Validating the plan"
        if action.tool == "data_vizualization":
            step_info["message"] = "Visualizing data"
        if action.tool == "data_loader":
            step_info["message"] = "Loading data"
        if action.tool == "PandasAgentTool":
            step_info["message"] = "Performing data analysis on the data"
        self.log_steps.append(step_info)

    def on_agent_finish(self, finish, **kwargs):
        self.log_steps.append("Finished executing the plan.")

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.agents import  initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_groq import ChatGroq

from tools.data_loader_tool import DataLoadingTool
from tools.data_vizualization_tool import DataVisualizationTool, OneInputSchema
from tools.pandas_tool import PandasTool
from tools.plan_validation_tool import PlanValidationTool
from memory.short_term_memory import agent_short_term_memory

load_dotenv()


# ---- Output Schema ----
class OrchestratorOutput(BaseModel):
    output: str = Field(
        ...,
        description="The output to show to the user in markdown format so it is readable",
    )
    plan: str = Field(..., description="The plan / steps to follow to do the task")

input_schema: str = JsonOutputParser(
    pydantic_object=OneInputSchema
).get_format_instructions()

# ---- Orchestrator Class ----
class LLMOrchestrator:
    def __init__(self, step_callback=None, verbose=False, variant: str = "default", disable_callbacks: bool = False):
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = run_id  # Save run_id for later use
        self.verbose = verbose
        self.variant = variant
        self.disable_callbacks = disable_callbacks
        self._log_steps = []
        self._log_dir = LOGS_DIR
        if not self.disable_callbacks:
            if step_callback:
                handler = UIStreamingCallbackHandler(step_callback)
                callback_manager = BaseCallbackManager(handlers=[handler])
                self._step_callback = step_callback
                self.log_step_callback = None  # No log_step_callback in this case
            else:
                os.makedirs(self._log_dir, exist_ok=True)
                handler = LogStreamingCallbackHandler(self._log_steps)
                callback_manager = BaseCallbackManager(handlers=[handler])
                self._step_callback = None
                self.log_step_callback = handler
        else:
            callback_manager = None
            self._step_callback = None
            self.log_step_callback = None

        self.df = None
        self.current_problem = None

        self.llm = BaseChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com",
            max_tokens=2048,
        )
 
        self.output_parser = JsonOutputParser(pydantic_object=OrchestratorOutput)
        self.tools = self.create_tools()
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            memory=agent_short_term_memory,
            verbose=verbose,
            callback_manager=callback_manager,
        )

    def save_log(self):
        # Save log as JSON with input, output, and steps
        import json
        def make_serializable(obj):
            try:
                json.dumps(obj)
                return obj
            except (TypeError, OverflowError):
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [make_serializable(i) for i in obj]
                else:
                    return str(obj)
        log_path = os.path.join(self._log_dir, f"{self.run_id}.json")
        log_data = {
            "input": self.current_problem,
            "output": make_serializable(getattr(self, "last_output", None)),
            "steps": make_serializable(self._log_steps),
        }
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

    # You should call this at the end of the run if step_callback was not provided
    def orchestrate(self, problem: str, prefix_prompt: str = ""):
        self.current_problem = problem
        prompt = self.build_prompt(problem, prefix_prompt=prefix_prompt)
        raw_response = self.agent.run(prompt)
        fixed_parser = OutputFixingParser.from_llm(
            parser=self.output_parser, llm=self.llm
        )
        parsed = fixed_parser.parse(raw_response)
        self.last_output = parsed  # Store output for logging
        if not self.disable_callbacks and (self.log_step_callback is not None):
            self.save_log()
        return parsed

    def set_df(self, df: pd.DataFrame):
        self.df = df

    def get_df(self) -> pd.DataFrame:
        return self.df

    def create_tools(self):
        return [
            PandasTool(self.get_df,verbose=self.verbose,variant=self.variant),
            DataLoadingTool(self.set_df),
            DataVisualizationTool(),
            PlanValidationTool(
                get_problem=lambda: self.current_problem,
                get_tools=lambda: self.tools,
            ),
        ]

    def build_prompt(self, problem: str,prefix_prompt:str="") -> str:
        start_date = "2024-12-01"
        end_date = "2025-05-20"
        template = PromptTemplate(
            input_variables=["problem","prefix_prompt"],
            partial_variables={
                "output_format": self.output_parser.get_format_instructions(),
                "tools": "\n".join(
                    [f"- {tool.name}: {tool.description}" for tool in self.tools]
                ),
                "input_schema": input_schema,
                "start_date": start_date,
                "end_date": end_date,
            },
            template="""
                You are an intelligent assistant that can perform two things:

                    1. Help users with **supply chain data analysis**, using the available tools.

                Use the tools when appropriate, and keep conversations natural and helpful.

                ---

                ## Data available :
                you have access to data from {start_date} to {end_date}.

                ---

                ## 🛠️ Tool Details

                {tools}
                **DataVisualizationTool** expects input in the following format:  
                {input_schema}

                ---

                ## 🎯 Task

                **{problem}**

                ---

                ## ✅ Instructions (for data analysis tasks)

                1. **Understand the Problem**  
                Ask clarifying questions if needed. Identify the key goals, relevant data, and any constraints.

                2. **Validate the Plan**  
                Summarize the plan for the user to confirm before proceeding.

                3. **Execute the Plan**  
                Perform the steps using the appropriate tools.  
                Share progress and results clearly with the user.

                4. **Format the Output**  
                Make sure your Markdown output is clear, well-organized, and visually appealing. Use headings, lists, tables, and emphasis to improve readability.

                ---

                ## 📤 Output Format

                {output_format}

                ---

                ## Extra Instructions:
                {prefix_prompt}
            """,
        )
        prompt = template.format(problem=problem,prefix_prompt=prefix_prompt)
        return prompt

