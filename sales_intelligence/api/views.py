from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.services import resolve_sales_agent_context
from sales_intelligence.services.prioritization import get_prioritized_customers


class CustomerPrioritiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ctx = resolve_sales_agent_context(request.user)
        results = get_prioritized_customers(ctx.tenant, ctx.sales_agent)
        return Response({"results": results})
