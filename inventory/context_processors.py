from .permissions import filter_inventory_for_user, is_general_admin
from .models import BranchInventory


def low_stock_count(request):
    if not request.user.is_authenticated:
        return {'low_stock_count': 0}

    qs = filter_inventory_for_user(BranchInventory.objects.select_related('product'), request.user)
    count = sum(1 for inv in qs if inv.is_low_stock)
    return {
        'low_stock_count': count,
        'is_general_admin': is_general_admin(request.user),
    }
