import json
from agents.base import BaseAgent, AgentResult
from agents.llm import call_llm
from agents.prompts import WORKFLOW_SYSTEM_PROMPT
from agents.tools.registry import TOOLS
from agents.realtime import push_agent_status
from agents.models import AgentApproval


class WorkflowAgent(BaseAgent):
    name = "workflow-agent"

    def run(self, input_text, resume=False):
        llm_output = call_llm(
            system_prompt=WORKFLOW_SYSTEM_PROMPT,
            user_prompt=input_text,
        )

        plan = json.loads(llm_output)

        # 🔁 Load already executed tools if resuming
        execution_log = []
        executed_tools = set()

        if resume and self.run_obj and self.run_obj.actions:
            execution_log = self.run_obj.actions.copy()
            for a in execution_log:
                executed_tools.add(a.get("tool"))

        member = self.organization.members.get(user=self.user)
        user_role = member.role

        for step in plan.get("steps", []):
            tool_name = step.get("tool")

            if tool_name in ("none", None):
                continue

            # 🔁 Skip already completed tools
            if tool_name in executed_tools:
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
                break

            # 🔐 ROLE CHECK
            if not tool.is_allowed_for(user_role):
                execution_log.append({
                    "tool": tool_name,
                    "status": "denied",
                    "error": f"Role '{user_role}' not allowed",
                })
                break

            # ⏸️ APPROVAL REQUIRED
            if getattr(tool, "requires_approval", False):
                approval = AgentApproval.objects.create(
                    run=self.run_obj,
                    tool_name=tool_name,
                    requested_by=self.user,
                )

                execution_log.append({
                    "tool": tool_name,
                    "status": "approval_required",
                    "approval_id": approval.id,
                })

                # persist progress before pause
                if self.run_obj:
                    self.run_obj.actions = execution_log
                    self.run_obj.save(update_fields=["actions"])

                push_agent_status(self.user.id, {
                    "status": "approval_required",
                    "tool": tool_name,
                    "approval_id": approval.id,
                })

                return AgentResult(
                    output={
                        "message": "Approval required",
                        "tool": tool_name,
                        "approval_id": approval.id,
                    },
                    tokens_used=0,
                    actions=execution_log,
                )

            # ▶️ EXECUTE TOOL
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

            # persist after each step (for resume safety)
            if self.run_obj:
                self.run_obj.actions = execution_log
                self.run_obj.save(update_fields=["actions"])

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
