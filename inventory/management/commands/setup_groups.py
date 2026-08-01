from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from inventory.models import Branch, BranchInventory, Product, StockTransfer


class Command(BaseCommand):
    help = 'إنشاء مجموعات الصلاحيات وإضافة بيانات تجريبية'

    def handle(self, *args, **options):
        self.setup_groups()
        self.setup_demo_data()
        self.stdout.write(self.style.SUCCESS('تم الإعداد بنجاح!'))

    def setup_groups(self):
        admin_group, _ = Group.objects.get_or_create(name='أدمن عام')
        manager_group, _ = Group.objects.get_or_create(name='مدير فرع')

        models = [Branch, Product, BranchInventory, StockTransfer]
        perms = []
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            perms.extend(Permission.objects.filter(content_type=ct))

        admin_group.permissions.set(perms)

        view_perms = [p for p in perms if 'view' in p.codename or 'change' in p.codename or 'add' in p.codename]
        manager_group.permissions.set(view_perms)

        self.stdout.write('تم إنشاء المجموعات: أدمن عام، مدير فرع')

    def setup_demo_data(self):
        from django.contrib.auth.models import User
        from inventory.models import Category, UserProfile

        if Branch.objects.exists():
            self.stdout.write('البيانات التجريبية موجودة مسبقاً.')
            return

        cat1, _ = Category.objects.get_or_create(name='إلكترونيات')
        cat2, _ = Category.objects.get_or_create(name='مواد غذائية')
        cat3, _ = Category.objects.get_or_create(name='مستلزمات مكتبية')

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        admin_group = Group.objects.get(name='أدمن عام')
        admin_user.groups.add(admin_group)

        manager1, created = User.objects.get_or_create(
            username='manager1',
            defaults={'first_name': 'أحمد', 'last_name': 'العلي', 'email': 'manager1@example.com'},
        )
        if created:
            manager1.set_password('manager123')
            manager1.save()

        manager2, created = User.objects.get_or_create(
            username='manager2',
            defaults={'first_name': 'سارة', 'last_name': 'المحمد', 'email': 'manager2@example.com'},
        )
        if created:
            manager2.set_password('manager123')
            manager2.save()

        manager_group = Group.objects.get(name='مدير فرع')
        manager1.groups.add(manager_group)
        manager2.groups.add(manager_group)

        branch1 = Branch.objects.create(name='فرع الرياض', location='الرياض - حي العليا', manager=manager1)
        branch2 = Branch.objects.create(name='فرع جدة', location='جدة - حي الحمراء', manager=manager2)
        branch3 = Branch.objects.create(name='فرع الدمام', location='الدمام - حي الفيصلية')

        UserProfile.objects.update_or_create(user=manager1, defaults={'branch': branch1})
        UserProfile.objects.update_or_create(user=manager2, defaults={'branch': branch2})

        products = [
            Product(name='لابتوب HP', barcode='1001001001', unit='قطعة', price=3500, category=cat1, min_quantity=5),
            Product(name='ماوس لاسلكي', barcode='1001001002', unit='قطعة', price=85, category=cat1, min_quantity=20),
            Product(name='أرز بسمتي', barcode='2002002001', unit='كيلو', price=25, category=cat2, min_quantity=50),
            Product(name='زيت زيتون', barcode='2002002002', unit='لتر', price=45, category=cat2, min_quantity=30),
            Product(name='دفتر A4', barcode='3003003001', unit='علبة', price=15, category=cat3, min_quantity=100),
            Product(name='قلم حبر', barcode='3003003002', unit='قطعة', price=3, category=cat3, min_quantity=200),
        ]
        Product.objects.bulk_create(products)
        products = list(Product.objects.all())

        inventories = [
            BranchInventory(branch=branch1, product=products[0], quantity=15),
            BranchInventory(branch=branch1, product=products[1], quantity=8),
            BranchInventory(branch=branch1, product=products[2], quantity=120),
            BranchInventory(branch=branch1, product=products[4], quantity=45),
            BranchInventory(branch=branch2, product=products[0], quantity=10),
            BranchInventory(branch=branch2, product=products[2], quantity=80),
            BranchInventory(branch=branch2, product=products[3], quantity=3),
            BranchInventory(branch=branch2, product=products[5], quantity=150),
            BranchInventory(branch=branch3, product=products[1], quantity=25),
            BranchInventory(branch=branch3, product=products[3], quantity=60),
            BranchInventory(branch=branch3, product=products[4], quantity=200),
            BranchInventory(branch=branch3, product=products[5], quantity=15),
        ]
        BranchInventory.objects.bulk_create(inventories)

        self.stdout.write(self.style.SUCCESS(
            'بيانات تجريبية:\n'
            '  admin / admin123 (أدمن عام)\n'
            '  manager1 / manager123 (مدير فرع الرياض)\n'
            '  manager2 / manager123 (مدير فرع جدة)'
        ))
