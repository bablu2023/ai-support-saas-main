from agents.tools.email_tool import EmailTool
from agents.tools.base import BaseTool, ToolResult
from organizations.constants import ORG_OWNER, ORG_ADMIN

TOOLS = {
    EmailTool.name: EmailTool(),
}



class EmailTool(BaseTool):
    name = "send_email"
    description = "Send an email to a user"
    allowed_roles = [ORG_OWNER, ORG_ADMIN]  # 👈 IMPORTANT

    def run(self, to, subject, body):
        print(f"[EMAIL] To={to}, Subject={subject}")

        return ToolResult(
            output={
                "to": to,
                "subject": subject,
                "status": "sent",
            }
        )

