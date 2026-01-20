from agents.tools.base import BaseTool, ToolResult

class EmailTool(BaseTool):
    name = "send_email"
    description = "Send an email to a user"

    def run(self, to, subject, body):
        # For now just simulate (safe)
        print(f"[EMAIL] To: {to}, Subject: {subject}")

        return ToolResult(
            output={
                "to": to,
                "subject": subject,
                "status": "sent",
            }
        )
