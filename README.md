# نظام إدارة المخزون متعدد الفروع

نظام إدارة مخزون لشركة مواد غذائية — مبني بـ Django، جاهز للنشر على Render بنقرة واحدة.

## المميزات

- إدارة فروع متعددة مع مدير لكل فرع
- إدارة منتجات غذائية مع باركود وتصنيفات
- مخزون منفصل لكل فرع
- تحويل مخزون بين الفروع مع موافقة/رفض
- نظام صلاحيات (أدمن عام / مدير فرع)
- تقارير مقارنة مع رسوم بيانية Chart.js
- تنبيهات المخزون المنخفض
- واجهة عربية RTL مع Sidebar

## التشغيل المحلي

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py setup_groups
python manage.py seed_data
python manage.py runserver
```

## حسابات تجريبية

| المستخدم | كلمة المرور | الدور |
|----------|-------------|-------|
| admin | admin123 | أدمن عام |
| grocery | grocery123 | أدمن عام |
| manager1 | manager123 | مدير فرع الرياض |
| manager2 | manager123 | مدير فرع جدة |

## النشر على Render (تلقائي بالكامل)

1. اربط المستودع على GitHub: `mahmoudjijawi-hub/Multi-Branch-Inventory`
2. في Render: **New → Blueprint** → اختر المستودع → فرع `main`
3. Render يكتشف `render.yaml` وينشر تلقائياً
4. `build.sh` يشغّل تلقائياً: migrate + setup_groups + seed_data + collectstatic
5. **لا حاجة لأي أوامر يدوية** — البيانات والحسابات تُنشأ عند أول نشر

### متغيرات البيئة (تُضبط تلقائياً من render.yaml)

| المتغير | القيمة |
|---------|--------|
| SECRET_KEY | يُولَّد تلقائياً |
| DEBUG | False |
| ALLOWED_HOSTS | .onrender.com |
| CSRF_TRUSTED_ORIGINS | https://*.onrender.com |
| DATABASE_URL | من PostgreSQL |

## هيكل المشروع

```
├── manage.py
├── requirements.txt
├── build.sh              # يشغّل كل شيء تلقائياً عند النشر
├── render.yaml           # إعداد Render جاهز
├── inventory_system/
├── inventory/
└── static/
```
