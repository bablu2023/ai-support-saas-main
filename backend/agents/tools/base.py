class ToolResult:
    def __init__(self, output, success=True, error=None):
        self.output = output
        self.success = success
        self.error = error


class BaseTool:
    name = "base"
    description = ""

    allowed_roles = []          # role-based access
    requires_approval = False   # 👈 NEW (human-in-the-loop)

    def is_allowed_for(self, role):
        return role in self.allowed_roles

    def run(self, **kwargs):
        raise NotImplementedError
    
class BaseAgent:
    def __init__(self, organization, user, run_obj=None):
        self.organization = organization
        self.user = user
        self.run_obj = run_obj

