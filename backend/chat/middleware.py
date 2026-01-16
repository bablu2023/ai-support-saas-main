from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from organizations.models import Organization
from auth.jwt import decode_jwt


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope["query_string"].decode())
        token = query.get("token")

        scope["user"] = AnonymousUser()
        scope["organization"] = None

        if token:
            try:
                payload = decode_jwt(token[0])
                scope["user_id"] = payload.get("user_id")
                scope["organization"] = await self.get_org(payload.get("org_id"))
            except Exception:
                pass

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_org(self, org_id):
        return Organization.objects.get(id=org_id)
