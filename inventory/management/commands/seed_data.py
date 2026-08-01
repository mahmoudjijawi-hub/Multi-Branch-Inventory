"""
بيانات تجريبية لشركة مواد غذائية.
تشغيل: python manage.py seed_data

مستخدم تجريبي:
  username: grocery
  password: grocery123

أدمن:
  username: admin
  password: admin123
"""
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from inventory.models import (
    Branch,
    BranchInventory,
    Category,
    Product,
    StockTransfer,
    UserProfile,
)

GROUP_ADMIN = 'أدمن عام'
GROUP_MANAGER = 'مدير فرع'

CATEGORIES = [
    'منتجات ألبان',
    'لحوم ودواجن',
    'خضار وفواكه',
    'معلبات',
    'مواد جافة وحبوب',
    'مخبوزات',
    'مشروبات',
    'مجمدات',
    'حلويات ووجبات خفيفة',
    'بهارات وتوابل',
]

PRODUCTS_BY_CATEGORY = {
    'منتجات ألبان': [
        ('حليب كامل الدسم 1 لتر', 'DAIRY-001', 'لتر', 6.50, 40),
        ('حليب قليل الدسم 1 لتر', 'DAIRY-002', 'لتر', 6.00, 35),
        ('لبن زبادي طبيعي 500غ', 'DAIRY-003', 'علبة', 4.25, 30),
        ('جبنة بيضاء 400غ', 'DAIRY-004', 'علبة', 12.00, 20),
        ('جبنة شيدر شرائح 200غ', 'DAIRY-005', 'علبة', 14.50, 18),
        ('زبدة غنمي 400غ', 'DAIRY-006', 'علبة', 18.00, 15),
        ('كريمة طبخ 200مل', 'DAIRY-007', 'علبة', 8.75, 25),
        ('لبنة كريمية 250غ', 'DAIRY-008', 'علبة', 7.50, 22),
        ('حليب مجفف 400غ', 'DAIRY-009', 'علبة', 22.00, 12),
        ('جبنة موزاريلا 250غ', 'DAIRY-010', 'علبة', 16.00, 15),
    ],
    'لحوم ودواجن': [
        ('لحم بقري مفروم طازج', 'MEAT-001', 'كيلو', 45.00, 15),
        ('لحم غنمي طازج', 'MEAT-002', 'كيلو', 55.00, 12),
        ('صدور دجاج طازجة', 'MEAT-003', 'كيلو', 22.00, 20),
        ('أفخاذ دجاج', 'MEAT-004', 'كيلو', 16.50, 25),
        ('كبدة دجاج', 'MEAT-005', 'كيلو', 12.00, 10),
        ('برجر بقري مجمد', 'MEAT-006', 'كيلو', 38.00, 18),
        ('نقانق دجاج', 'MEAT-007', 'كيلو', 24.00, 15),
        ('لحم مفروم خليط', 'MEAT-008', 'كيلو', 35.00, 20),
        ('دجاج كامل مجمد', 'MEAT-009', 'قطعة', 18.00, 12),
        ('لحم عجل ستيك', 'MEAT-010', 'كيلو', 65.00, 8),
        ('كفتة جاهزة', 'MEAT-011', 'كيلو', 32.00, 14),
        ('سجق بقري', 'MEAT-012', 'كيلو', 28.00, 16),
    ],
    'خضار وفواكه': [
        ('طماطم طازجة', 'PROD-001', 'كيلو', 5.50, 50),
        ('خيار', 'PROD-002', 'كيلو', 4.00, 40),
        ('بطاطس', 'PROD-003', 'كيلو', 3.50, 80),
        ('بصل أحمر', 'PROD-004', 'كيلو', 3.00, 60),
        ('جزر', 'PROD-005', 'كيلو', 4.50, 35),
        ('تفاح أحمر', 'PROD-006', 'كيلو', 8.00, 30),
        ('موز', 'PROD-007', 'كيلو', 6.50, 40),
        ('برتقال', 'PROD-008', 'كيلو', 5.00, 35),
        ('ليمون', 'PROD-009', 'كيلو', 4.00, 25),
        ('خس روماني', 'PROD-010', 'قطعة', 5.50, 20),
        ('فلفل ألوان', 'PROD-011', 'كيلو', 9.00, 18),
        ('عنب أحمر', 'PROD-012', 'كيلو', 12.00, 15),
    ],
    'معلبات': [
        ('تونة قطع في زيت', 'CAN-001', 'علبة', 9.50, 30),
        ('فول مدمس حبة كبيرة', 'CAN-002', 'علبة', 3.50, 50),
        ('حمص جاهز', 'CAN-003', 'علبة', 4.00, 40),
        ('ذرة حلوة', 'CAN-004', 'علبة', 5.50, 35),
        ('معجون طماطم', 'CAN-005', 'علبة', 4.25, 45),
        ('حلاوة طحينية', 'CAN-006', 'علبة', 12.00, 20),
        ('زيتون أخضر شرائح', 'CAN-007', 'علبة', 8.00, 25),
        ('فاصوليا بيضاء', 'CAN-008', 'علبة', 4.50, 30),
        ('صلصة بيتزا', 'CAN-009', 'علبة', 6.00, 22),
        ('انشوجة في زيت', 'CAN-010', 'علبة', 11.00, 15),
        ('مشروم قطع', 'CAN-011', 'علبة', 7.50, 18),
        ('جبنة فيتا معلبة', 'CAN-012', 'علبة', 14.00, 12),
    ],
    'مواد جافة وحبوب': [
        ('أرز بسمتي فاخر', 'DRY-001', 'كيلو', 18.00, 60),
        ('أرز مصري', 'DRY-002', 'كيلو', 8.50, 80),
        ('عدس أصفر', 'DRY-003', 'كيلو', 7.00, 40),
        ('حمص مجفف', 'DRY-004', 'كيلو', 9.00, 35),
        ('فاصوليا بيضاء مجففة', 'DRY-005', 'كيلو', 8.00, 30),
        ('طحين أبيض', 'DRY-006', 'كيلو', 3.50, 50),
        ('سكر أبيض', 'DRY-007', 'كيلو', 4.00, 55),
        ('مكرونة سباغيتي', 'DRY-008', 'علبة', 5.50, 45),
        ('شعيرية رفيعة', 'DRY-009', 'علبة', 4.00, 40),
        ('برغل خشن', 'DRY-010', 'كيلو', 6.50, 35),
        ('شوفان', 'DRY-011', 'كيلو', 12.00, 20),
        ('ذرة للفشار', 'DRY-012', 'كيلو', 5.00, 25),
    ],
    'مخبوزات': [
        ('خبز عربي طازج', 'BAKE-001', 'قطعة', 1.50, 100),
        ('خبز توست أبيض', 'BAKE-002', 'قطعة', 5.00, 40),
        ('خبز برجر', 'BAKE-003', 'قطعة', 6.50, 30),
        ('كرواسون زبدة', 'BAKE-004', 'قطعة', 3.00, 25),
        ('معمول تمر', 'BAKE-005', 'علبة', 18.00, 15),
        ('كعك سادة', 'BAKE-006', 'علبة', 12.00, 18),
        ('فطيرة جبنة', 'BAKE-007', 'قطعة', 4.50, 20),
        ('خبز أسمر', 'BAKE-008', 'قطعة', 6.00, 25),
        ('بسكويت شاي', 'BAKE-009', 'علبة', 8.00, 30),
        ('كيك شوكولاتة', 'BAKE-010', 'قطعة', 15.00, 12),
        ('خبز صامولي', 'BAKE-011', 'قطعة', 2.00, 50),
        ('مافن بلوبيري', 'BAKE-012', 'قطعة', 5.50, 15),
    ],
    'مشروبات': [
        ('ماء معدني 600مل', 'BEV-001', 'علبة', 1.50, 120),
        ('عصير برتقال 1 لتر', 'BEV-002', 'لتر', 8.00, 40),
        ('عصير تفاح 1 لتر', 'BEV-003', 'لتر', 8.00, 35),
        ('حليب شوكولاتة 200مل', 'BEV-004', 'علبة', 3.50, 50),
        ('قهوة عربية مطحونة', 'BEV-005', 'علبة', 25.00, 20),
        ('شاي أحمر 100 كيس', 'BEV-006', 'علبة', 12.00, 30),
        ('نسكافيه 200غ', 'BEV-007', 'علبة', 28.00, 18),
        ('مشروب طاقة', 'BEV-008', 'علبة', 6.00, 35),
        ('عصير مانجو 1 لتر', 'BEV-009', 'لتر', 9.50, 25),
        ('مشروب غازي كولا', 'BEV-010', 'علبة', 2.50, 80),
        ('عصير رمان 1 لتر', 'BEV-011', 'لتر', 14.00, 15),
        ('شاي أخضر', 'BEV-012', 'علبة', 15.00, 20),
    ],
    'مجمدات': [
        ('بطاطس مقلية مجمدة', 'FRZ-001', 'كيلو', 14.00, 25),
        ('خضار مشكلة مجمدة', 'FRZ-002', 'كيلو', 12.00, 20),
        ('بيتزا مجمدة عائلية', 'FRZ-003', 'قطعة', 22.00, 15),
        ('سمبوسة لحم مجمدة', 'FRZ-004', 'علبة', 18.00, 18),
        ('آيس كريم فانيلا', 'FRZ-005', 'علبة', 16.00, 12),
        ('دجاج ناجتس مجمد', 'FRZ-006', 'كيلو', 20.00, 20),
        ('برياني مجمد جاهز', 'FRZ-007', 'علبة', 24.00, 10),
        ('فواكه مشكلة مجمدة', 'FRZ-008', 'كيلو', 15.00, 14),
        ('معجنات بالجبن مجمدة', 'FRZ-009', 'علبة', 19.00, 12),
        ('برجر دجاج مجمد', 'FRZ-010', 'كيلو', 18.00, 16),
        ('بازلاء مجمدة', 'FRZ-011', 'كيلو', 8.00, 22),
        ('كبة مجمدة', 'FRZ-012', 'كيلو', 28.00, 10),
    ],
    'حلويات ووجبات خفيفة': [
        ('شوكولاتة بالحليب', 'SNK-001', 'قطعة', 4.50, 40),
        ('شيبس بطاطس ملح', 'SNK-002', 'علبة', 5.00, 50),
        ('بسكويت شوكولاتة', 'SNK-003', 'علبة', 7.50, 35),
        ('مكسرات مشكلة', 'SNK-004', 'كيلو', 45.00, 12),
        ('تمر مجدول فاخر', 'SNK-005', 'كيلو', 35.00, 20),
        ('حلوى أطفال', 'SNK-006', 'علبة', 6.00, 30),
        ('فشار جاهز', 'SNK-007', 'علبة', 4.00, 25),
        ('ويفر شوكولاتة', 'SNK-008', 'علبة', 5.50, 40),
        ('لوز محمص', 'SNK-009', 'كيلو', 55.00, 10),
        ('كيك باكيت', 'SNK-010', 'علبة', 9.00, 22),
        ('ذرة مفلفلة', 'SNK-011', 'علبة', 3.50, 35),
        ('عسل طبيعي 500غ', 'SNK-012', 'علبة', 38.00, 8),
    ],
    'بهارات وتوابل': [
        ('ملح طعام ناعم', 'SPC-001', 'كيلو', 2.50, 40),
        ('فلفل أسود مطحون', 'SPC-002', 'علبة', 8.00, 20),
        ('كمون مطحون', 'SPC-003', 'علبة', 6.50, 18),
        ('كركم مطحون', 'SPC-004', 'علبة', 7.00, 15),
        ('قرفة مطحونة', 'SPC-005', 'علبة', 9.00, 12),
        ('بهارات مشكلة', 'SPC-006', 'علبة', 10.00, 20),
        ('زعتر مجفف', 'SPC-007', 'علبة', 5.50, 15),
        ('زعفران أصلي', 'SPC-008', 'علبة', 45.00, 5),
        ('هيل حب', 'SPC-009', 'علبة', 18.00, 8),
        ('صلصة صويا', 'SPC-010', 'علبة', 8.50, 22),
        ('خل أبيض', 'SPC-011', 'لتر', 4.00, 30),
        ('زيت زيتون بكر', 'SPC-012', 'لتر', 32.00, 15),
    ],
}

BRANCHES = [
    ('فرع الرياض', 'الرياض - حي العليا', 'manager1'),
    ('فرع جدة', 'جدة - حي الحمراء', 'manager2'),
    ('فرع الدمام', 'الدمام - حي الفيصلية', 'manager3'),
    ('فرع مكة', 'مكة - حي العزيزية', 'manager4'),
]

# كميات منخفضة قصداً (barcode, branch_name, quantity)
LOW_STOCK = [
    ('MEAT-010', 'فرع جدة', 3),
    ('SPC-008', 'فرع الرياض', 2),
    ('SNK-012', 'فرع الدمام', 4),
    ('FRZ-007', 'فرع مكة', 5),
    ('BEV-011', 'فرع جدة', 6),
    ('PROD-012', 'فرع الرياض', 8),
    ('DAIRY-009', 'فرع الدمام', 5),
    ('MEAT-001', 'فرع مكة', 7),
    ('BAKE-010', 'فرع جدة', 4),
    ('CAN-012', 'فرع الرياض', 6),
]


class Command(BaseCommand):
    help = 'إضافة بيانات تجريبية لشركة مواد غذائية (idempotent)'

    def handle(self, *args, **options):
        counts = {}
        counts['categories'] = self._seed_categories()
        counts['users'] = self._seed_users()
        counts['branches'] = self._seed_branches()
        counts['products'] = self._seed_products()
        counts['inventory'] = self._seed_inventory()
        counts['transfers'] = self._seed_transfers()

        self.stdout.write(self.style.SUCCESS('\n✅ تم إدخال البيانات بنجاح!\n'))
        self.stdout.write('─── ملخص ───')
        for key, val in counts.items():
            self.stdout.write(f'  {key}: {val}')
        self.stdout.write(self.style.WARNING(
            '\nحسابات الدخول:\n'
            '  admin / admin123 (أدمن عام)\n'
            '  grocery / grocery123 (أدمن عام)\n'
            '  manager1 / manager123 (مدير فرع الرياض)\n'
            '  manager2 / manager123 (مدير فرع جدة)\n'
        ))

    def _seed_categories(self):
        created = 0
        for name in CATEGORIES:
            _, was_created = Category.objects.get_or_create(name=name)
            if was_created:
                created += 1
        return f'{Category.objects.count()} (جديد: {created})'

    def _seed_users(self):
        admin_group, _ = Group.objects.get_or_create(name=GROUP_ADMIN)
        manager_group, _ = Group.objects.get_or_create(name=GROUP_MANAGER)
        created = 0

        users_data = [
            ('admin', 'admin123', True, True, GROUP_ADMIN, None),
            ('grocery', 'grocery123', True, False, GROUP_ADMIN, None),
            ('manager1', 'manager123', False, False, GROUP_MANAGER, 'أحمد'),
            ('manager2', 'manager123', False, False, GROUP_MANAGER, 'سارة'),
            ('manager3', 'manager123', False, False, GROUP_MANAGER, 'خالد'),
            ('manager4', 'manager123', False, False, GROUP_MANAGER, 'نورة'),
        ]

        for username, password, is_super, is_staff, group_name, first in users_data:
            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@grocery.sa',
                    'is_superuser': is_super,
                    'is_staff': is_staff or is_super,
                    'first_name': first or '',
                },
            )
            if was_created:
                user.set_password(password)
                user.save()
                created += 1
            group = admin_group if group_name == GROUP_ADMIN else manager_group
            user.groups.add(group)
            UserProfile.objects.get_or_create(user=user)

        return f'{User.objects.count()} (جديد: {created})'

    def _seed_branches(self):
        created = 0
        for name, location, manager_username in BRANCHES:
            manager = User.objects.filter(username=manager_username).first()
            branch, was_created = Branch.objects.get_or_create(
                name=name,
                defaults={'location': location, 'manager': manager},
            )
            if was_created:
                created += 1
            if manager:
                UserProfile.objects.update_or_create(
                    user=manager,
                    defaults={'branch': branch},
                )
        return f'{Branch.objects.count()} (جديد: {created})'

    def _seed_products(self):
        created = 0
        for cat_name, products in PRODUCTS_BY_CATEGORY.items():
            category = Category.objects.get(name=cat_name)
            for name, barcode, unit, price, min_qty in products:
                _, was_created = Product.objects.get_or_create(
                    barcode=barcode,
                    defaults={
                        'name': name,
                        'unit': unit,
                        'price': Decimal(str(price)),
                        'category': category,
                        'min_quantity': min_qty,
                    },
                )
                if was_created:
                    created += 1
        return f'{Product.objects.count()} (جديد: {created})'

    def _seed_inventory(self):
        created = 0
        branches = list(Branch.objects.all())
        products = list(Product.objects.all())

        for branch in branches:
            for i, product in enumerate(products):
                low_entry = next(
                    (q for p, bn, q in LOW_STOCK if p == product.barcode and bn == branch.name),
                    None,
                )
                qty = low_entry if low_entry is not None else 30 + (i * 7 + hash(branch.name) % 20) % 80

                _, was_created = BranchInventory.objects.get_or_create(
                    branch=branch,
                    product=product,
                    defaults={'quantity': qty},
                )
                if was_created:
                    created += 1

        return f'{BranchInventory.objects.count()} (جديد: {created})'

    def _seed_transfers(self):
        created = 0
        admin = User.objects.filter(username='admin').first()
        transfers_data = [
            ('فرع الرياض', 'فرع جدة', 'DRY-001', 20, StockTransfer.STATUS_APPROVED),
            ('فرع جدة', 'فرع الدمام', 'DAIRY-001', 15, StockTransfer.STATUS_PENDING),
            ('فرع الدمام', 'فرع مكة', 'PROD-001', 30, StockTransfer.STATUS_PENDING),
            ('فرع مكة', 'فرع الرياض', 'BEV-001', 50, StockTransfer.STATUS_APPROVED),
            ('فرع الرياض', 'فرع مكة', 'MEAT-003', 10, StockTransfer.STATUS_REJECTED),
        ]

        for from_name, to_name, barcode, qty, status in transfers_data:
            from_b = Branch.objects.filter(name=from_name).first()
            to_b = Branch.objects.filter(name=to_name).first()
            product = Product.objects.filter(barcode=barcode).first()
            if not all([from_b, to_b, product]):
                continue

            exists = StockTransfer.objects.filter(
                from_branch=from_b,
                to_branch=to_b,
                product=product,
                quantity=qty,
            ).exists()
            if not exists:
                StockTransfer.objects.create(
                    from_branch=from_b,
                    to_branch=to_b,
                    product=product,
                    quantity=qty,
                    status=status,
                    requested_by=admin,
                    notes='تحويل تجريبي',
                )
                created += 1

        return f'{StockTransfer.objects.count()} (جديد: {created})'
