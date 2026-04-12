from .models import SalesAgent


def get_user_tenant(user):
    try:
        return SalesAgent.objects.get(user=user).tenant
    except SalesAgent.DoesNotExist:
        return None