from langchain.tools import BaseTool
from typing import Optional, Callable
from pydantic import PrivateAttr
import pandas as pd
from agents.pandas_agent import PandasAgent


class PandasTool(BaseTool):
    name: str = "PandasAgentTool"
    description: str = (
        "Use this tool to ask natural language questions about a Pandas DataFrame. "
        "Provide a callback function that returns the DataFrame to analyze. "
        "The tool will use a language model to interpret and execute your query."
    )

    _df_callback: Optional[Callable[[], pd.DataFrame]] = PrivateAttr(default=None)
    variant: str = "default"  # Default variant for the agent
    def __init__(
        self, df_callback: Optional[Callable[[], pd.DataFrame]] = None,verbose=False,variant="default",**kwargs
    ):
        super().__init__(**kwargs)
        self._df_callback = df_callback
        self.verbose = verbose
        self.variant = variant

    def _run(self, query: str) -> str:
        if self._df_callback is None:
            return "No DataFrame callback provided. Please set a callback first."

        try:
            df = self._df_callback()
            if df is None:
                return "Callback did not return a valid DataFrame."

            agent = PandasAgent(df,verbose=self.verbose,variant=self.variant)
            result = agent.invoke(query)
            return str(result)
        except Exception as e:
            return f"Error executing query: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)
