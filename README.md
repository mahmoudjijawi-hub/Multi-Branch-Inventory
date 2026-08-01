# نظام إدارة المخزون متعدد الفروع

نظام إدارة مخزون لشركة مواد غذائية — مبني بـ Django، جاهز للنشر على Render بنقرة واحدة.

يستخدم **SQLite** المدمج — بدون PostgreSQL وبدون إعداد قاعدة بيانات يدوي.

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

## النشر على Render

1. في Render: **New → Blueprint** → اختر المستودع → فرع `main`
2. أو على خدمة موجودة: **Manual Deploy → Deploy latest commit**
3. لا تحتاج إنشاء PostgreSQL — النظام يستخدم SQLite تلقائياً
4. عند التشغيل يتم إنشاء الجداول والبيانات التجريبية تلقائياً
5. سجّل الدخول: `admin` / `admin123`

### مهم إذا كان عندك DATABASE_URL قديم

احذف متغير `DATABASE_URL` من Environment في Render (إن وُجد)،  
أو اتركه — الكود يتجاهله ويستخدم SQLite فقط.

### متغيرات البيئة

| المتغير | القيمة |
|---------|--------|
| SECRET_KEY | يُولَّد تلقائياً |
| DEBUG | False |
| ALLOWED_HOSTS | .onrender.com |
| CSRF_TRUSTED_ORIGINS | https://*.onrender.com |

## هيكل المشروع

```
├── manage.py
├── requirements.txt
├── build.sh              # تثبيت + collectstatic عند البناء
├── start.sh              # migrate + seed + تشغيل الخادم
├── render.yaml           # إعداد Render (SQLite فقط)
├── inventory_system/
├── inventory/
└── static/
```
