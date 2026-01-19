class AgentResult:
    def __init__(self, output, tokens_used=0, actions=None):
        self.output = output
        self.tokens_used = tokens_used
        self.actions = actions or []


class BaseAgent:
    name = "base"

    def __init__(self, organization, user):
        self.organization = organization
        self.user = user

    def run(self, input_text):
        raise NotImplementedError
