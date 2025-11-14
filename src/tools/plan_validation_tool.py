from typing import Callable
from langchain.tools import BaseTool
from pydantic import PrivateAttr
from agents.planning_validator_agent import PlanValidatorAgent


class PlanValidationTool(BaseTool):
    name: str = "PlanValidatorTool"
    description: str = (
        "Validates a step-by-step plan for solving a given problem using available tools."
    )

    # Use PrivateAttr for non-Pydantic fields (callbacks)
    _get_problem: Callable[[], str] = PrivateAttr()
    _get_tools: Callable[[], list] = PrivateAttr()

    def __init__(
        self,
        get_problem: Callable[[], str],
        get_tools: Callable[[], list],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._get_problem = get_problem
        self._get_tools = get_tools

    def _run(self, plan: str) -> str:
        try:
            validator = PlanValidatorAgent()
            output = validator.validate(
                problem=self._get_problem(), tools=self._get_tools(), plan=plan
            )
            return (
                "✅ Valid plan."
                if output.get("valid")
                else f"❌ Invalid plan:\n{output.get('comment', 'No comment provided')}"
            )
        except Exception as e:
            return f"❌ Error during validation: {str(e)}"

    async def _arun(self, plan: str) -> str:
        return self._run(plan)
