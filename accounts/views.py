from rest_framework.response import Response
from rest_framework.views import APIView

from .services import resolve_sales_agent_context


class CurrentUserView(APIView):
    def get(self, request):
        ctx = resolve_sales_agent_context(request.user)
        user = request.user

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "tenant": {
                    "id": ctx.tenant.id,
                    "code": ctx.tenant.code,
                    "name": ctx.tenant.name,
                },
                "sales_agent": {
                    "id": ctx.sales_agent.id,
                    "is_active": ctx.sales_agent.is_active,
                },
            }
        )
