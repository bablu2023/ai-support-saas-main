
    
class ToolResult:
    def __init__(self, output, success=True, error=None):
        self.output = output
        self.success = success
        self.error = error


class BaseTool:
    name = "base"
    description = ""
    allowed_roles = []  # 👈 NEW

    def is_allowed_for(self, role):
        return role in self.allowed_roles

    def run(self, **kwargs):
        raise NotImplementedError

