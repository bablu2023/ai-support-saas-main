from agents.base import BaseAgent, AgentResult

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
