import json
import logging
import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

from .forms import (
    BranchForm,
    BranchInventoryForm,
    InventorySearchForm,
    LoginForm,
    ProductForm,
    StockTransferForm,
)
from .models import Branch, BranchInventory, Category, Product, StockTransfer
from .permissions import (
    filter_branches_for_user,
    filter_inventory_for_user,
    filter_transfers_for_user,
    get_user_branch,
    is_general_admin,
    require_general_admin,
    require_login_branch_access,
    user_can_manage_branch,
)


@require_login_branch_access
def dashboard(request):
    user = request.user
    branches = filter_branches_for_user(Branch.objects.all(), user)
    inventories = filter_inventory_for_user(
        BranchInventory.objects.select_related('branch', 'product'),
        user,
    )
    transfers = filter_transfers_for_user(StockTransfer.objects.all(), user)

    low_stock = [inv for inv in inventories if inv.is_low_stock]
    pending_transfers = transfers.filter(status=StockTransfer.STATUS_PENDING)

    context = {
        'branch_count': branches.count(),
        'product_count': Product.objects.count(),
        'total_inventory': inventories.aggregate(total=Sum('quantity'))['total'] or 0,
        'pending_transfer_count': pending_transfers.count(),
        'low_stock_items': low_stock[:10],
        'recent_transfers': transfers.select_related(
            'from_branch', 'to_branch', 'product'
        )[:5],
    }
    return render(request, 'inventory/dashboard.html', context)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        try:
            user = form.get_user()
            messages.success(
                self.request,
                f'مرحباً {user.get_full_name() or user.username}!',
            )
            return super().form_valid(form)
        except Exception:
            logger.exception('Login form_valid failed')
            raise

    def form_invalid(self, form):
        logger.warning('Login failed for username=%s errors=%s',
                       self.request.POST.get('username'), form.errors)
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception:
            logger.exception('Login POST crashed')
            raise


@require_GET
def healthz(request):
    """فحص سريع لحالة قاعدة البيانات (للتشخيص على Render)."""
    engine = settings.DATABASES['default'].get('ENGINE', '')
    payload = {
        'ok': False,
        'engine': engine.split('.')[-1],
        'render': bool(getattr(settings, 'IS_RENDER', False) or __import__('os').environ.get('RENDER')),
        'debug': settings.DEBUG,
    }
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        User = get_user_model()
        payload['users'] = User.objects.count()
        payload['ok'] = True
    except Exception as exc:
        payload['error'] = f'{type(exc).__name__}: {exc}'
        payload['trace'] = traceback.format_exc().splitlines()[-5:]
        logger.exception('healthz DB check failed')
    status = 200 if payload['ok'] else 503
    return JsonResponse(payload, status=status)


class CustomLogoutView(LogoutView):
    next_page = 'login'


# ─── Branches ───────────────────────────────────────────────

@require_login_branch_access
def branch_list(request):
    branches = filter_branches_for_user(
        Branch.objects.select_related('manager').annotate(
            inventory_total=Sum('inventories__quantity'),
        ),
        request.user,
    )
    return render(request, 'inventory/branches/list.html', {'branches': branches})


@require_general_admin
def branch_create(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إنشاء الفرع بنجاح.')
            return redirect('branch_list')
    else:
        form = BranchForm()
    return render(request, 'inventory/branches/form.html', {'form': form, 'title': 'إضافة فرع جديد'})


@require_login_branch_access
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if not user_can_manage_branch(request.user, branch):
        raise PermissionDenied
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الفرع بنجاح.')
            return redirect('branch_list')
    else:
        form = BranchForm(instance=branch)
    return render(request, 'inventory/branches/form.html', {'form': form, 'title': 'تعديل الفرع', 'branch': branch})


@require_general_admin
def branch_delete(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        branch.delete()
        messages.success(request, 'تم حذف الفرع.')
        return redirect('branch_list')
    return render(request, 'inventory/branches/confirm_delete.html', {'branch': branch})


# ─── Products ───────────────────────────────────────────────

@require_login_branch_access
def product_list(request):
    products = Product.objects.select_related('category').all()
    form = InventorySearchForm(request.GET or None)

    branch_filter = None
    if form.is_valid():
        search = form.cleaned_data.get('search')
        branch_filter = form.cleaned_data.get('branch')
        category = form.cleaned_data.get('category')

        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(barcode__icontains=search)
            )
        if category:
            products = products.filter(category=category)

    if not is_general_admin(request.user):
        user_branch = get_user_branch(request.user)
        if branch_filter and user_branch and branch_filter.pk != user_branch.pk:
            branch_filter = user_branch
        elif not branch_filter:
            branch_filter = user_branch

    inventories = filter_inventory_for_user(
        BranchInventory.objects.select_related('branch', 'product'),
        request.user,
    )
    if branch_filter:
        inventories = inventories.filter(branch=branch_filter)

    inv_map = {}
    for inv in inventories:
        key = inv.product_id
        if key not in inv_map:
            inv_map[key] = []
        inv_map[key].append(inv)

    product_data = []
    for product in products:
        product_inventories = inv_map.get(product.id, [])
        if branch_filter and not product_inventories:
            continue
        product_data.append({
            'product': product,
            'inventories': product_inventories,
            'is_low': any(i.is_low_stock for i in product_inventories),
        })

    if not is_general_admin(request.user):
        form.fields['branch'].queryset = filter_branches_for_user(Branch.objects.all(), request.user)

    return render(request, 'inventory/products/list.html', {
        'product_data': product_data,
        'form': form,
        'branch_filter': branch_filter,
    })


@require_general_admin
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المنتج بنجاح.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/products/form.html', {'form': form, 'title': 'إضافة منتج جديد'})


@require_general_admin
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/products/form.html', {'form': form, 'title': 'تعديل المنتج', 'product': product})


@require_general_admin
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'تم حذف المنتج.')
        return redirect('product_list')
    return render(request, 'inventory/products/confirm_delete.html', {'product': product})


# ─── Inventory ──────────────────────────────────────────────

@require_login_branch_access
def inventory_list(request):
    inventories = filter_inventory_for_user(
        BranchInventory.objects.select_related('branch', 'product', 'product__category'),
        request.user,
    )

    branch_id = request.GET.get('branch')
    if branch_id:
        inventories = inventories.filter(branch_id=branch_id)

    search = request.GET.get('search', '')
    if search:
        inventories = inventories.filter(
            Q(product__name__icontains=search) | Q(product__barcode__icontains=search)
        )

    branches = filter_branches_for_user(Branch.objects.all(), request.user)

    return render(request, 'inventory/inventory/list.html', {
        'inventories': inventories,
        'branches': branches,
        'search': search,
        'selected_branch': branch_id,
    })


@require_login_branch_access
def inventory_create(request):
    if request.method == 'POST':
        form = BranchInventoryForm(request.POST)
        if not is_general_admin(request.user):
            form.fields['branch'].queryset = filter_branches_for_user(Branch.objects.all(), request.user)
        if form.is_valid():
            branch = form.cleaned_data['branch']
            if not user_can_manage_branch(request.user, branch):
                raise PermissionDenied
            form.save()
            messages.success(request, 'تم تحديث المخزون بنجاح.')
            return redirect('inventory_list')
    else:
        form = BranchInventoryForm()
        if not is_general_admin(request.user):
            form.fields['branch'].queryset = filter_branches_for_user(Branch.objects.all(), request.user)
    return render(request, 'inventory/inventory/form.html', {'form': form, 'title': 'إضافة/تحديث مخزون'})


@require_login_branch_access
def inventory_edit(request, pk):
    inv = get_object_or_404(BranchInventory, pk=pk)
    if not user_can_manage_branch(request.user, inv.branch):
        raise PermissionDenied
    if request.method == 'POST':
        form = BranchInventoryForm(request.POST, instance=inv)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الكمية بنجاح.')
            return redirect('inventory_list')
    else:
        form = BranchInventoryForm(instance=inv)
        if not is_general_admin(request.user):
            form.fields['branch'].queryset = filter_branches_for_user(Branch.objects.all(), request.user)
    return render(request, 'inventory/inventory/form.html', {'form': form, 'title': 'تعديل المخزون', 'inventory': inv})


# ─── Stock Transfers ────────────────────────────────────────

@require_login_branch_access
def transfer_list(request):
    transfers = filter_transfers_for_user(
        StockTransfer.objects.select_related(
            'from_branch', 'to_branch', 'product', 'requested_by', 'reviewed_by'
        ),
        request.user,
    )
    status = request.GET.get('status')
    if status:
        transfers = transfers.filter(status=status)

    return render(request, 'inventory/transfers/list.html', {
        'transfers': transfers,
        'status_filter': status,
    })


@require_login_branch_access
def transfer_create(request):
    if request.method == 'POST':
        form = StockTransferForm(request.POST)
        if not is_general_admin(request.user):
            user_branch = get_user_branch(request.user)
            form.fields['from_branch'].queryset = Branch.objects.filter(pk=user_branch.pk) if user_branch else Branch.objects.none()
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.requested_by = request.user
            transfer.save()
            messages.success(request, 'تم إرسال طلب التحويل بنجاح.')
            return redirect('transfer_list')
    else:
        form = StockTransferForm()
        if not is_general_admin(request.user):
            user_branch = get_user_branch(request.user)
            form.fields['from_branch'].queryset = Branch.objects.filter(pk=user_branch.pk) if user_branch else Branch.objects.none()
    return render(request, 'inventory/transfers/form.html', {'form': form, 'title': 'طلب تحويل مخزون'})


@require_login_branch_access
@require_POST
def transfer_approve(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    if not filter_transfers_for_user(StockTransfer.objects.filter(pk=pk), request.user).exists():
        raise PermissionDenied

    user_branch = get_user_branch(request.user)
    if not is_general_admin(request.user):
        if not user_branch or transfer.to_branch_id != user_branch.pk:
            raise PermissionDenied('فقط الفرع المستلم يمكنه الموافقة على التحويل.')

    try:
        transfer.approve(request.user)
        messages.success(request, 'تمت الموافقة على التحويل وتحديث المخزون.')
    except ValidationError as e:
        messages.error(request, str(e.message) if hasattr(e, 'message') else str(e))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'approved'})
    return redirect('transfer_list')


@require_login_branch_access
@require_POST
def transfer_reject(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    if not filter_transfers_for_user(StockTransfer.objects.filter(pk=pk), request.user).exists():
        raise PermissionDenied

    user_branch = get_user_branch(request.user)
    if not is_general_admin(request.user):
        if not user_branch or transfer.to_branch_id != user_branch.pk:
            raise PermissionDenied('فقط الفرع المستلم يمكنه رفض التحويل.')

    try:
        transfer.reject(request.user)
        messages.success(request, 'تم رفض طلب التحويل.')
    except ValidationError as e:
        messages.error(request, str(e))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'rejected'})
    return redirect('transfer_list')


# ─── Reports ────────────────────────────────────────────────

@require_login_branch_access
def branch_report(request):
    branches = filter_branches_for_user(Branch.objects.all(), request.user)

    report_data = []
    for branch in branches:
        inv_total = BranchInventory.objects.filter(branch=branch).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        transfer_out = StockTransfer.objects.filter(from_branch=branch).count()
        transfer_in = StockTransfer.objects.filter(to_branch=branch).count()
        report_data.append({
            'name': branch.name,
            'inventory_total': inv_total,
            'transfer_out': transfer_out,
            'transfer_in': transfer_in,
            'transfer_total': transfer_out + transfer_in,
        })

    chart_labels = json.dumps([d['name'] for d in report_data], ensure_ascii=False)
    chart_inventory = json.dumps([d['inventory_total'] for d in report_data])
    chart_transfers = json.dumps([d['transfer_total'] for d in report_data])

    return render(request, 'inventory/reports/branch_comparison.html', {
        'report_data': report_data,
        'chart_labels': chart_labels,
        'chart_inventory': chart_inventory,
        'chart_transfers': chart_transfers,
    })


def csrf_failure(request, reason=''):
    return render(request, 'csrf_failure.html', {'reason': reason}, status=403)
