import json
from agents.base import BaseAgent, AgentResult
from agents.llm import call_llm
from agents.prompts import WORKFLOW_SYSTEM_PROMPT
from agents.tools.registry import TOOLS
from agents.realtime import push_agent_status
from organizations.constants import ORG_OWNER, ORG_ADMIN, ORG_MEMBER


class WorkflowAgent(BaseAgent):
    name = "workflow-agent"

    def run(self, input_text):
        llm_output = call_llm(
            system_prompt=WORKFLOW_SYSTEM_PROMPT,
            user_prompt=input_text,
        )

        plan = json.loads(llm_output)
        execution_log = []

        member = self.organization.members.get(user=self.user)
        user_role = member.role

        for step in plan.get("steps", []):
            tool_name = step.get("tool")

            if tool_name == "none":
                continue

            # 🔔 TOOL START
            push_agent_status(self.user.id, {
                "status": "tool_start",
                "tool": tool_name,
            })

            tool = TOOLS.get(tool_name)
            if not tool:
                execution_log.append({
                    "tool": tool_name,
                    "status": "failed",
                    "error": "Unknown tool",
                })

                push_agent_status(self.user.id, {
                    "status": "tool_failed",
                    "tool": tool_name,
                    "reason": "unknown_tool",
                })
                break

            # 🔐 ROLE CHECK
            if not tool.is_allowed_for(user_role):
                execution_log.append({
                    "tool": tool_name,
                    "status": "denied",
                    "error": f"Role '{user_role}' not allowed",
                })

                push_agent_status(self.user.id, {
                    "status": "tool_denied",
                    "tool": tool_name,
                    "role": user_role,
                })
                break

            # ✅ Execute tool
            result = tool.run(**step.get("input", {}))

            execution_log.append({
                "tool": tool_name,
                "status": "success" if result.success else "failed",
                "output": result.output,
            })

            # 🔔 TOOL END
            push_agent_status(self.user.id, {
                "status": "tool_done",
                "tool": tool_name,
                "success": result.success,
            })

            if not result.success:
                break

        return AgentResult(
            output={
                "thought": plan.get("thought"),
                "execution": execution_log,
            },
            tokens_used=2000,
            actions=execution_log,
        )
