from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Branch(models.Model):
    name = models.CharField('اسم الفرع', max_length=200)
    location = models.CharField('الموقع', max_length=500)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_branches',
        verbose_name='المدير المسؤول',
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'فرع'
        verbose_name_plural = 'الفروع'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_inventory(self):
        return self.inventories.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def transfer_count(self):
        return self.transfers_out.count() + self.transfers_in.count()


class Category(models.Model):
    name = models.CharField('اسم التصنيف', max_length=100, unique=True)

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('قطعة', 'قطعة'),
        ('كيلو', 'كيلو'),
        ('لتر', 'لتر'),
        ('علبة', 'علبة'),
        ('متر', 'متر'),
        ('كرتون', 'كرتون'),
    ]

    name = models.CharField('اسم المنتج', max_length=200)
    barcode = models.CharField('الباركود', max_length=100, unique=True)
    unit = models.CharField('وحدة القياس', max_length=50, choices=UNIT_CHOICES, default='قطعة')
    price = models.DecimalField('السعر', max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='التصنيف',
    )
    min_quantity = models.PositiveIntegerField('الحد الأدنى للمخزون', default=10)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['name']

    def __str__(self):
        return self.name


class BranchInventory(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name='الفرع',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='branch_inventories',
        verbose_name='المنتج',
    )
    quantity = models.PositiveIntegerField('الكمية', default=0)

    class Meta:
        verbose_name = 'مخزون فرع'
        verbose_name_plural = 'مخزونات الفروع'
        unique_together = ['branch', 'product']
        ordering = ['branch', 'product']

    def __str__(self):
        return f'{self.branch.name} - {self.product.name}: {self.quantity}'

    @property
    def is_low_stock(self):
        return self.quantity <= self.product.min_quantity


class StockTransfer(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'قيد الانتظار'),
        (STATUS_APPROVED, 'موافق عليه'),
        (STATUS_REJECTED, 'مرفوض'),
    ]

    from_branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='transfers_out',
        verbose_name='الفرع المرسل',
    )
    to_branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='transfers_in',
        verbose_name='الفرع المستلم',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='transfers',
        verbose_name='المنتج',
    )
    quantity = models.PositiveIntegerField('الكمية')
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfer_requests',
        verbose_name='مقدم الطلب',
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_reviews',
        verbose_name='المراجع',
    )
    notes = models.TextField('ملاحظات', blank=True)
    created_at = models.DateTimeField('تاريخ الطلب', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    class Meta:
        verbose_name = 'تحويل مخزون'
        verbose_name_plural = 'تحويلات المخزون'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.from_branch.name} → {self.to_branch.name}: {self.product.name} ({self.quantity})'

    def clean(self):
        if self.from_branch_id and self.to_branch_id and self.from_branch_id == self.to_branch_id:
            raise ValidationError('لا يمكن التحويل لنفس الفرع.')

    @transaction.atomic
    def approve(self, reviewer):
        if self.status != self.STATUS_PENDING:
            raise ValidationError('لا يمكن الموافقة على طلب غير معلق.')

        from_inv = BranchInventory.objects.select_for_update().filter(
            branch=self.from_branch,
            product=self.product,
        ).first()

        if not from_inv or from_inv.quantity < self.quantity:
            raise ValidationError('الكمية المتوفرة في الفرع المرسل غير كافية.')

        from_inv.quantity -= self.quantity
        from_inv.save()

        to_inv, _ = BranchInventory.objects.select_for_update().get_or_create(
            branch=self.to_branch,
            product=self.product,
            defaults={'quantity': 0},
        )
        to_inv.quantity += self.quantity
        to_inv.save()

        self.status = self.STATUS_APPROVED
        self.reviewed_by = reviewer
        self.save()

    @transaction.atomic
    def reject(self, reviewer):
        if self.status != self.STATUS_PENDING:
            raise ValidationError('لا يمكن رفض طلب غير معلق.')
        self.status = self.STATUS_REJECTED
        self.reviewed_by = reviewer
        self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='المستخدم',
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
        verbose_name='الفرع',
    )

    class Meta:
        verbose_name = 'ملف مستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

    def __str__(self):
        return f'{self.user.username} - {self.branch or "بدون فرع"}'

    @property
    def is_general_admin(self):
        return self.user.is_superuser or self.user.groups.filter(name='أدمن عام').exists()

    @property
    def is_branch_manager(self):
        return self.user.groups.filter(name='مدير فرع').exists()
