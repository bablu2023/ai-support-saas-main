from agents.base import BaseAgent, AgentResult
from agents.tools.registry import TOOLS

import json

from agents.llm import call_llm
from agents.prompts import AGENT_SYSTEM_PROMPT



class TaskAgent(BaseAgent):
    name = "task-agent"

    def run(self, input_text):
        steps = [
            f"Understand task: {input_text}",
            "Decide required actions",
            "Prepare execution plan",
        ]

        output = {
            "goal": input_text,
            "steps": steps,
            "status": "planned",
        }

        return AgentResult(
            output=output,
            tokens_used=500,
            actions=steps,
        )
    


class TaskAgent(BaseAgent):
    name = "task-agent"

    def run(self, input_text):
        actions = []

        if "email" in input_text.lower():
            tool = TOOLS["send_email"]
            result = tool.run(
                to="user@example.com",
                subject="Automated message",
                body=input_text,
            )
            actions.append(result.output)

        return AgentResult(
            output={
                "goal": input_text,
                "actions": actions,
            },
            tokens_used=700,
            actions=actions,
        )
    





class TaskAgent(BaseAgent):
    name = "task-agent"

    def run(self, input_text):
        llm_output = call_llm(
            system_prompt=AGENT_SYSTEM_PROMPT,
            user_prompt=input_text,
        )

        plan = json.loads(llm_output)
        actions = []

        action = plan.get("action")

        if action and action != "none":
            tool = TOOLS.get(action)
            if tool:
                result = tool.run(**plan.get("action_input", {}))
                actions.append(result.output)

        return AgentResult(
            output={
                "thought": plan.get("thought"),
                "actions": actions,
            },
            tokens_used=1200,
            actions=actions,
        )


