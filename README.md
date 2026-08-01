# نظام إدارة المخزون متعدد الفروع

نظام إدارة مخزون متعدد الفروع مبني بـ Django، جاهز للنشر على Render.

## المميزات

- إدارة فروع متعددة مع مدير لكل فرع
- إدارة منتجات مع باركود وتصنيفات
- مخزون منفصل لكل فرع
- تحويل مخزون بين الفروع مع موافقة/رفض
- نظام صلاحيات (أدمن عام / مدير فرع)
- تقارير مقارنة مع رسوم بيانية Chart.js
- تنبيهات المخزون المنخفض
- واجهة عربية RTL كاملة

## التشغيل المحلي

```bash
# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ ملف البيئة
cp .env.example .env

# تشغيل migrations وإعداد البيانات
python manage.py migrate
python manage.py setup_groups

# تشغيل السيرفر
python manage.py runserver
```

## حسابات تجريبية

| المستخدم | كلمة المرور | الدور |
|----------|-------------|-------|
| admin | admin123 | أدمن عام |
| manager1 | manager123 | مدير فرع الرياض |
| manager2 | manager123 | مدير فرع جدة |

## النشر على Render

1. ارفع المشروع إلى GitHub
2. أنشئ حساب على [Render](https://render.com)
3. اختر **New > Blueprint** واربط مستودع GitHub
4. Render سيكتشف `render.yaml` تلقائياً
5. بعد النشر، شغّل من Shell:
   ```bash
   python manage.py setup_groups
   ```

## هيكل المشروع

```
├── manage.py
├── requirements.txt
├── build.sh
├── render.yaml
├── .env.example
├── inventory_system/       # إعدادات Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/              # التطبيق الرئيسي
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── permissions.py
│   ├── urls.py
│   ├── templates/
│   └── management/commands/
└── static/
    ├── css/style.css
    └── js/main.js
```
