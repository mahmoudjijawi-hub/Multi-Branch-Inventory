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

**لا تحتاج إنشاء قاعدة بيانات يدوياً** إذا نشرت عبر Blueprint:

1. في Render: **New → Blueprint** → اختر المستودع → فرع `main`
2. Render يكتشف `render.yaml` وينشئ:
   - خدمة Web تلقائياً
   - قاعدة بيانات PostgreSQL (`inventory-db`) تلقائياً
   - يربط `DATABASE_URL` تلقائياً
3. `build.sh` يشغّل: migrate + collectstatic + setup_groups + seed_data
4. بعد النشر سجّل الدخول: `admin` / `admin123`

### إذا أنشأت Web Service يدوياً (بدون Blueprint)

1. **New → PostgreSQL** → أنشئ قاعدة باسم أي شيء
2. انسخ **Internal Database URL**
3. في Web Service → Environment → أضف:
   - `DATABASE_URL` = الرابط الذي نسخته
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`
4. Build Command: `bash build.sh`
5. Start Command: `gunicorn inventory_system.wsgi:application --bind 0.0.0.0:$PORT`
6. **Manual Deploy**

### متغيرات البيئة (تُضبط تلقائياً من render.yaml)

| المتغير | القيمة |
|---------|--------|
| SECRET_KEY | يُولَّد تلقائياً |
| DEBUG | False |
| ALLOWED_HOSTS | .onrender.com |
| CSRF_TRUSTED_ORIGINS | https://*.onrender.com |
| DATABASE_URL | من PostgreSQL (تلقائي) |

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
