from langchain_experimental.agents import create_pandas_dataframe_agent as create_default_agent
from langchain.agents.agent_types import AgentType
import pandas as pd
from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()



PREFIX = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
You should use the tools below to answer the question posed of you:"""

SUFFIX_NO_DF = """
Begin!
Question: {input}
{agent_scratchpad}"""

SUFFIX_WITH_DF = """
Here is the documentation for the dataframe:
{df_doc}

Begin!
Question: {input}
{agent_scratchpad}"""

import warnings
from typing import Any, Dict, List, Literal, Optional, Sequence, Union, cast
import pandas as pd

from langchain.agents import (
    AgentType,
    create_react_agent,
)
from langchain.agents.agent import (
    AgentExecutor,
    BaseMultiActionAgent,
    BaseSingleActionAgent,
    RunnableAgent,
)
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS

from langchain_core.callbacks import BaseCallbackManager
from langchain_core.language_models import LanguageModelLike
from langchain_core.prompts import (
    BasePromptTemplate,
    PromptTemplate,
)
from langchain_core.tools import BaseTool
from langchain_core.utils.interactive_env import is_interactive_env

from langchain_experimental.tools.python.tool import PythonAstREPLTool

from tools.rag_tool import RAGTool


def _get_single_prompt(
    df: Any,
    *,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    include_df_in_prompt: Optional[bool] = True,
    number_of_head_rows: int = 5,
) -> BasePromptTemplate:
    if suffix is not None:
        suffix_to_use = suffix
    elif include_df_in_prompt:
        suffix_to_use = SUFFIX_WITH_DF
    else:
        suffix_to_use = SUFFIX_NO_DF
    prefix = prefix if prefix is not None else PREFIX

    template = "\n\n".join([prefix, "{tools}", FORMAT_INSTRUCTIONS, suffix_to_use])
    prompt = PromptTemplate.from_template(template)

    partial_prompt = prompt.partial()

    return partial_prompt


def _get_prompt(df: Any, **kwargs: Any) -> BasePromptTemplate:
    return _get_single_prompt(df, **kwargs)


def create_custom_rag_pandas_dataframe_agent(
    llm: LanguageModelLike,
    df: Any,
    agent_type: Union[
        AgentType, Literal["openai-tools", "tool-calling"]
    ] = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    input_variables: Optional[List[str]] = None,
    verbose: bool = False,
    return_intermediate_steps: bool = False,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    include_df_in_prompt: Optional[bool] = True,
    number_of_head_rows: int = 5,
    extra_tools: Sequence[BaseTool] = (),
    engine: Literal["pandas", "modin"] = "pandas",
    allow_dangerous_code: bool = False,
    **kwargs: Any,
) -> AgentExecutor:
    if not allow_dangerous_code:
        raise ValueError(
            "This agent relies on access to a python repl tool which can execute "
            "arbitrary code. This can be dangerous and requires a specially sandboxed "
            "environment to be safely used. Please read the security notice in the "
            "doc-string of this function. You must opt-in to use this functionality "
            "by setting allow_dangerous_code=True."
            "For general security guidelines, please see: "
            "https://python.langchain.com/docs/security/"
        )
    if is_interactive_env():
        pd.set_option("display.max_columns", None)

    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected pandas DataFrame, got {type(df)}")

    if input_variables:
        kwargs = kwargs or {}
        kwargs["input_variables"] = input_variables
    if kwargs:
        warnings.warn(
            f"Received additional kwargs {kwargs} which are no longer supported."
        )

    df_locals = {}

    df_locals["df"] = df
    tools = [PythonAstREPLTool(locals=df_locals),RAGTool()]

    if include_df_in_prompt is not None and suffix is not None:
        raise ValueError("If suffix is specified, include_df_in_prompt should not be.")
    prompt = _get_prompt(
        df,
        prefix=prefix,
        suffix=suffix,
        include_df_in_prompt=include_df_in_prompt,
        number_of_head_rows=number_of_head_rows,
    )

    agent: Union[BaseSingleActionAgent, BaseMultiActionAgent] = RunnableAgent(
        runnable=create_react_agent(llm, tools, prompt),  # type: ignore
        input_keys_arg=["input"],
        return_keys_arg=["output"],
    )
    return AgentExecutor(
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        return_intermediate_steps=return_intermediate_steps,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        **(agent_executor_kwargs or {}),
    )


class PandasAgent:
    """
    A class to encapsulate the creation and invocation of a Pandas DataFrame agent.
    This class interacts with an LLM and a Pandas DataFrame to perform operations.
    """

    def __init__(self, df: pd.DataFrame,variant:str="default", verbose: bool = False):
        """
        Initializes the PandasAgent with the given DataFrame using DeepSeek Chat model.

        Args:
            df (pd.DataFrame): The DataFrame to work with.
        """
        self.df = df
        self.llm = BaseChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com",
            max_tokens=8192,
        )

        self.agent = self._create_agent(verbose=verbose,variant=variant)

    def _create_agent(self, variant: str = "default", verbose: bool = False):
        """
        Creates the Pandas DataFrame agent using the LLM and the DataFrame.

        Args:
            variant (str): The type of agent to create. Options are "default" or "rag".
            verbose (bool): Whether to run in verbose mode.

        Returns:
            The created agent instance.
        """
        if variant == "rag":
            return create_custom_rag_pandas_dataframe_agent(
                self.llm,
                self.df,
                verbose=verbose,
                allow_dangerous_code=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                include_df_in_prompt=False
            )
        else:
            return create_default_agent(
                self.llm,
                self.df,
                verbose=verbose,
                allow_dangerous_code=True,
                handle_parsing_errors=True,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                
            )
        """
        Creates the Pandas DataFrame agent using the LLM and the DataFrame.

        Returns:
            The created agent instance.
        """
        return create_default_agent(
            self.llm,
            self.df,
            verbose=verbose,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )

    def invoke(self, query: str):
        """
        Invokes the agent with the given query and returns the result.

        Args:
            query (str): The query to execute on the DataFrame.

        Returns:
            The result of the query execution.
        """
        return self.agent.invoke(query)

