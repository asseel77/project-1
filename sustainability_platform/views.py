import html


def e(val) -> str:
    if val is None:
        return ""
    return html.escape(str(val), quote=True)


def nl2br(val) -> str:
    return e(val).replace("\n", "<br>")


def render_public_layout(title: str, active: str, settings: dict, content: str) -> str:
    site_name = e(settings.get("site_name", "مؤسسة الاستدامة"))
    logo_path = e(settings.get("logo_path", "/static/img/logo.svg"))
    primary = e(settings.get("primary_color", "#1b4332"))
    accent = e(settings.get("accent_color", "#2d6a4f"))
    phone = e(settings.get("phone", ""))
    email = e(settings.get("email", ""))
    address = e(settings.get("address", ""))
    tagline = e(settings.get("site_tagline", ""))

    nav_items = [
        ("/", "home", "الرئيسية"),
        ("/about", "about", "نبذة عنا"),
        ("/services", "services", "الخدمات"),
        ("/partners", "partners", "الشركاء"),
        ("/news", "news", "الأخبار"),
        ("/contact", "contact", "التواصل والدعم"),
    ]
    nav_html = "\n".join(
        f'<a href="{href}" class="{"active" if active == key else ""}">{label}</a>'
        for href, key, label in nav_items
    )

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)} — {site_name}</title>
  <link rel="stylesheet" href="/static/css/style.css">
  <style>
    :root {{
      --primary: {primary};
      --accent: {accent};
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container nav-wrap">
      <a href="/" class="brand">
        <img src="{logo_path}" alt="{site_name}">
        <span>{site_name}</span>
      </a>
      <nav class="nav-links">
        {nav_html}
        <a href="/admin" class="btn btn-sm">لوحة التحكم</a>
      </nav>
    </div>
  </header>

  <main>
    {content}
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <h4>{site_name}</h4>
          <p style="margin:0; font-size:0.92rem; color:#94a3b8;">{tagline}</p>
        </div>
        <div>
          <h4>روابط سريعة</h4>
          <a href="/">الرئيسية</a>
          <a href="/about">نبذة عن المؤسسة</a>
          <a href="/services">دليل الخدمات</a>
          <a href="/partners">الشركاء</a>
          <a href="/news">الأخبار والمدونة</a>
        </div>
        <div>
          <h4>معلومات الاتصال</h4>
          <p style="margin:0 0 6px 0; font-size:0.9rem;">📞 {phone}</p>
          <p style="margin:0 0 6px 0; font-size:0.9rem;">✉️ {email}</p>
          <p style="margin:0 0 6px 0; font-size:0.9rem;">📍 {address}</p>
          <a href="/contact" style="color:#52b788; margin-top:8px;">تواصل معنا الآن ←</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 {site_name} — جميع الحقوق محفوظة</span>
        <span>إعداد الطالب: أصيل باسم السنوسي</span>
      </div>
    </div>
  </footer>
</body>
</html>"""


def render_home(settings: dict, services: list, partners: list, articles: list) -> str:
    site_name = e(settings.get("site_name", "مؤسسة الاستدامة"))
    tagline = e(settings.get("site_tagline", ""))
    stat_p = e(settings.get("stat_projects", "+45"))
    stat_pa = e(settings.get("stat_partners", "+28"))
    stat_c = e(settings.get("stat_clients", "+120"))

    services_cards = "".join(
        f"""<div class="card">
          <div class="card-icon">{e(s['icon_image'])}</div>
          <h3>{e(s['title'])}</h3>
          <p>{e(s['short_description'])}</p>
          <a href="/services/{e(s['slug'])}" class="btn btn-outline btn-sm">تفاصيل الخدمة</a>
        </div>"""
        for s in services
    )

    partners_cards = "".join(
        f"""<div class="card" style="text-align:center;">
          {f'<img src="{e(p["logo_path"])}" alt="{e(p["name"])}" class="partner-logo">' if p["logo_path"] else '<div class="card-icon">🤝</div>'}
          <h3 style="font-size:1rem;">{e(p['name'])}</h3>
        </div>"""
        for p in partners
    )

    articles_cards = "".join(
        f"""<div class="card">
          <span class="badge">{e(a['category'])}</span>
          <h3 style="margin-top:10px;">{e(a['title'])}</h3>
          <p>{e(a['summary'])}</p>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <small style="color:#64748b;">{e(str(a['published_at'])[:10])}</small>
            <a href="/news/{e(a['slug'])}" class="btn btn-sm">اقرأ المزيد</a>
          </div>
        </div>"""
        for a in articles
    )

    body = f"""
    <section class="hero">
      <div class="container hero-inner">
        <div>
          <h1>{site_name}</h1>
          <p>{tagline}</p>
          <div class="hero-actions">
            <a href="/services" class="btn btn-white">استكشف خدماتنا</a>
            <a href="/contact" class="btn btn-ghost">اطلب استشارة الآن</a>
          </div>
        </div>
        <div class="stats-card">
          <div>
            <div class="stat-num">{stat_p}</div>
            <div class="stat-label">مشروع مستدام</div>
          </div>
          <div>
            <div class="stat-num">{stat_pa}</div>
            <div class="stat-label">شريك نجاح</div>
          </div>
          <div>
            <div class="stat-num">{stat_c}</div>
            <div class="stat-label">جهة مستفيدة</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">أبرز خدماتنا</h2>
            <p class="section-sub">حلول متخصصة تدعم التحول المؤسسي نحو الاستدامة</p>
          </div>
          <a href="/services" class="btn btn-outline btn-sm">عرض جميع الخدمات</a>
        </div>
        <div class="grid-3">{services_cards}</div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">شركاء النجاح</h2>
            <p class="section-sub">نعتز بثقة الجهات الحكومية والشركات الرائدة</p>
          </div>
          <a href="/partners" class="btn btn-outline btn-sm">صفحة الشركاء</a>
        </div>
        <div class="grid-4">{partners_cards}</div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">آخر الأخبار والمستجدات</h2>
            <p class="section-sub">أحدث المبادرات والمقالات من مركزنا الإعلامي</p>
          </div>
          <a href="/news" class="btn btn-outline btn-sm">جميع الأخبار</a>
        </div>
        <div class="grid-3">{articles_cards}</div>
      </div>
    </section>
    """
    return render_public_layout("الرئيسية", "home", settings, body)


def render_about(settings: dict, team: list) -> str:
    team_html = "".join(
        f"""<div class="card" style="text-align:center;">
          <div class="card-icon">👤</div>
          <h3>{e(m['name'])}</h3>
          <span class="badge">{e(m['role_title'])}</span>
          <p style="margin-top:10px;">{e(m['bio'])}</p>
        </div>"""
        for m in team
    )
    body = f"""
    <section class="page-banner">
      <div class="container">
        <h1>نبذة عن {e(settings.get('site_name', 'المؤسسة'))}</h1>
        <p>تعرف على قصتنا، رؤيتنا، قيمنا، وفريق العمل التنفيذي</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="card" style="margin-bottom:20px;">
          <h3>قصة التأسيس</h3>
          <p style="color:var(--text); margin:0;">{nl2br(settings.get('about_story', ''))}</p>
        </div>
        <div class="grid-2" style="margin-bottom:28px;">
          <div class="card">
            <h3>الرؤية</h3>
            <p style="color:var(--text); margin:0;">{nl2br(settings.get('vision', ''))}</p>
          </div>
          <div class="card">
            <h3>الرسالة</h3>
            <p style="color:var(--text); margin:0;">{nl2br(settings.get('mission', ''))}</p>
          </div>
        </div>
        <div class="card" style="margin-bottom:32px; background:var(--mint-soft);">
          <h3>القيم الجوهرية</h3>
          <p style="color:var(--primary); font-weight:600; margin:0;">{e(settings.get('values_text', ''))}</p>
        </div>
        <div class="section-header">
          <div>
            <h2 class="section-title">فريق العمل والخبراء</h2>
            <p class="section-sub">كفاءات متخصصة تقود مشاريع الاستدامة</p>
          </div>
        </div>
        <div class="grid-3">{team_html}</div>
      </div>
    </section>
    """
    return render_public_layout("نبذة عنا", "about", settings, body)


def render_services(settings: dict, services: list) -> str:
    cards = "".join(
        f"""<div class="card">
          <div class="card-icon">{e(s['icon_image'])}</div>
          <h3>{e(s['title'])}</h3>
          <p>{e(s['short_description'])}</p>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <a href="/services/{e(s['slug'])}" class="btn btn-sm">التفاصيل الكاملة</a>
            <a href="/contact?service={e(s['title'])}" class="btn btn-outline btn-sm">طلب الخدمة</a>
          </div>
        </div>"""
        for s in services
    )
    body = f"""
    <section class="page-banner">
      <div class="container">
        <h1>الخدمات والحلول</h1>
        <p>مجموعة متكاملة من الخدمات الاستشارية والتنفيذية في مجال الاستدامة</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="grid-2">{cards if cards else '<p>لا توجد خدمات مضافة حالياً.</p>'}</div>
      </div>
    </section>
    """
    return render_public_layout("الخدمات", "services", settings, body)


def render_service_detail(settings: dict, service: dict) -> str:
    body = f"""
    <section class="page-banner">
      <div class="container">
        <a href="/services" style="font-size:0.9rem;">← العودة إلى جميع الخدمات</a>
        <h1 style="margin-top:8px;">{e(service['icon_image'])} {e(service['title'])}</h1>
        <p>{e(service['short_description'])}</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="card">
          <h3>نطاق العمل والتفاصيل</h3>
          <p style="color:var(--text); font-size:1.02rem;">{nl2br(service['full_content'])}</p>
          <div style="margin-top:20px;">
            <a href="/contact?service={e(service['title'])}" class="btn">اطلب هذه الخدمة الآن</a>
          </div>
        </div>
      </div>
    </section>
    """
    return render_public_layout(service["title"], "services", settings, body)


def render_partners(settings: dict, partners: list) -> str:
    cards = "".join(
        f"""<div class="card" style="text-align:center;">
          {f'<img src="{e(p["logo_path"])}" alt="{e(p["name"])}" class="partner-logo">' if p["logo_path"] else '<div class="card-icon">🤝</div>'}
          <h3>{e(p['name'])}</h3>
          <p>{e(p['description'])}</p>
          {f'<a href="{e(p["website_url"])}" target="_blank" rel="noopener" class="btn btn-outline btn-sm">زيارة الموقع</a>' if p["website_url"] else ''}
        </div>"""
        for p in partners
    )
    body = f"""
    <section class="page-banner">
      <div class="container">
        <h1>الشركاء والرعاة</h1>
        <p>شبكة من الشراكات الاستراتيجية لتعزيز أثر الاستدامة</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="grid-3">{cards if cards else '<p>لا يوجد شركاء مضافون حالياً.</p>'}</div>
      </div>
    </section>
    """
    return render_public_layout("الشركاء", "partners", settings, body)


def render_news(settings: dict, articles: list, query: str = "", category: str = "", categories: list = None) -> str:
    categories = categories or []
    cat_options = "".join(
        f'<option value="{e(c)}" {"selected" if c == category else ""}>{e(c)}</option>'
        for c in categories
    )
    cards = "".join(
        f"""<div class="card">
          {f'<img src="{e(a["cover_image"])}" alt="{e(a["title"])}" style="width:100%; height:170px; object-fit:cover; border-radius:8px; margin-bottom:12px;">' if a["cover_image"] else ''}
          <span class="badge">{e(a['category'])}</span>
          <h3 style="margin-top:10px;">{e(a['title'])}</h3>
          <p>{e(a['summary'])}</p>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <small style="color:#64748b;">{e(str(a['published_at'])[:10])}</small>
            <a href="/news/{e(a['slug'])}" class="btn btn-sm">اقرأ الخبر</a>
          </div>
        </div>"""
        for a in articles
    )
    body = f"""
    <section class="page-banner">
      <div class="container">
        <h1>الأخبار والمدونة</h1>
        <p>آخر المستجدات والمقالات والإعلانات الرسمية</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <form method="GET" action="/news" class="card" style="margin-bottom:24px; display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end;">
          <div style="flex:2; min-width:200px;">
            <label for="q">بحث في الأخبار</label>
            <input type="text" id="q" name="q" value="{e(query)}" placeholder="ابحث بالعنوان أو المحتوى...">
          </div>
          <div style="flex:1; min-width:160px;">
            <label for="cat">التصنيف</label>
            <select id="cat" name="cat">
              <option value="">جميع التصنيفات</option>
              {cat_options}
            </select>
          </div>
          <div>
            <button type="submit" class="btn">تصفية</button>
            <a href="/news" class="btn btn-outline">إعادة ضبط</a>
          </div>
        </form>
        <div class="grid-3">{cards if cards else '<div class="card"><p>لا توجد مقالات مطابقة للبحث.</p></div>'}</div>
      </div>
    </section>
    """
    return render_public_layout("الأخبار", "news", settings, body)


def render_article_detail(settings: dict, article: dict) -> str:
    body = f"""
    <section class="page-banner">
      <div class="container">
        <a href="/news" style="font-size:0.9rem;">← العودة إلى الأخبار</a>
        <div style="margin-top:10px;"><span class="badge">{e(article['category'])}</span></div>
        <h1 style="margin-top:8px;">{e(article['title'])}</h1>
        <p>تاريخ النشر: {e(str(article['published_at'])[:10])}</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="card">
          {f'<img src="{e(article["cover_image"])}" alt="{e(article["title"])}" style="width:100%; max-height:360px; object-fit:cover; border-radius:10px; margin-bottom:18px;">' if article["cover_image"] else ''}
          <p style="font-weight:600; color:var(--primary); font-size:1.05rem;">{e(article['summary'])}</p>
          <hr style="border:none; border-top:1px solid var(--border); margin:16px 0;">
          <div style="color:var(--text); font-size:1.02rem; line-height:1.85;">{nl2br(article['content'])}</div>
        </div>
      </div>
    </section>
    """
    return render_public_layout(article["title"], "news", settings, body)


def render_contact(settings: dict, faqs: list, prefill_subject: str = "", status_msg: str = "", error_msg: str = "") -> str:
    alert_html = ""
    if status_msg:
        alert_html = f'<div class="alert alert-success">{e(status_msg)}</div>'
    elif error_msg:
        alert_html = f'<div class="alert alert-error">{e(error_msg)}</div>'

    faqs_html = "".join(
        f"""<details class="faq-item">
          <summary>{e(f['question'])}</summary>
          <p>{nl2br(f['answer'])}</p>
        </details>"""
        for f in faqs
    )

    body = f"""
    <section class="page-banner">
      <div class="container">
        <h1>التواصل والدعم</h1>
        <p>نسعد باستقبال استفساراتكم وطلبات الخدمات والشراكات</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="grid-2" style="align-items:start;">
          <div class="card">
            <h3>أرسل رسالة</h3>
            {alert_html}
            <form method="POST" action="/contact">
              <div class="form-group">
                <label for="sender_name">الاسم الكامل *</label>
                <input type="text" id="sender_name" name="sender_name" required>
              </div>
              <div class="form-group">
                <label for="email">البريد الإلكتروني *</label>
                <input type="email" id="email" name="email" required>
              </div>
              <div class="form-group">
                <label for="phone">رقم الجوال</label>
                <input type="text" id="phone" name="phone" placeholder="05xxxxxxxx">
              </div>
              <div class="form-group">
                <label for="subject">الموضوع *</label>
                <input type="text" id="subject" name="subject" value="{e(prefill_subject)}" required>
              </div>
              <div class="form-group">
                <label for="message">نص الرسالة *</label>
                <textarea id="message" name="message" rows="4" required></textarea>
              </div>
              <button type="submit" class="btn">إرسال الرسالة</button>
            </form>
          </div>

          <div>
            <div class="card" style="margin-bottom:20px;">
              <h3>معلومات الاتصال المباشرة</h3>
              <p style="color:var(--text);">📞 <b>الهاتف:</b> {e(settings.get('phone', ''))}</p>
              <p style="color:var(--text);">✉️ <b>البريد الإلكتروني:</b> {e(settings.get('email', ''))}</p>
              <p style="color:var(--text); margin-bottom:0;">📍 <b>العنوان:</b> {e(settings.get('address', ''))}</p>
            </div>
            <h3 style="color:var(--primary); margin-bottom:12px;">الأسئلة الشائعة (FAQ)</h3>
            {faqs_html if faqs_html else '<p>لا توجد أسئلة مضافة حالياً.</p>'}
          </div>
        </div>
      </div>
    </section>
    """
    return render_public_layout("التواصل والدعم", "contact", settings, body)


# ---------------- ADMIN VIEWS ----------------

def render_admin_login(settings: dict, error: str = "") -> str:
    site_name = e(settings.get("site_name", "مؤسسة الاستدامة"))
    err_html = f'<div class="alert alert-error">{e(error)}</div>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>تسجيل الدخول — لوحة تحكم {site_name}</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body style="display:flex; align-items:center; justify-content:center; min-height:100vh; padding:20px;">
  <div class="card" style="max-width:420px; width:100%;">
    <div style="text-align:center; margin-bottom:18px;">
      <img src="{e(settings.get('logo_path', '/static/img/logo.svg'))}" alt="{site_name}" style="width:52px; height:52px;">
      <h2 style="margin:10px 0 4px 0; color:var(--primary);">لوحة تحكم {site_name}</h2>
      <p style="margin:0; color:var(--muted); font-size:0.9rem;">يرجى تسجيل الدخول للمتابعة</p>
    </div>
    {err_html}
    <form method="POST" action="/admin/login">
      <div class="form-group">
        <label for="email">البريد الإلكتروني</label>
        <input type="email" id="email" name="email" required placeholder="admin@estidama.sa">
      </div>
      <div class="form-group">
        <label for="password">كلمة المرور</label>
        <input type="password" id="password" name="password" required>
      </div>
      <button type="submit" class="btn" style="width:100%;">دخول للوحة التحكم</button>
    </form>
    <div style="margin-top:16px; padding-top:12px; border-top:1px solid var(--border); font-size:0.83rem; color:var(--muted);">
      <div><b>حساب المدير العام:</b> admin@estidama.sa / Admin@123</div>
      <div><b>حساب المحرر:</b> editor@estidama.sa / Editor@123</div>
      <div style="margin-top:8px;"><a href="/">← العودة إلى الموقع العام</a></div>
    </div>
  </div>
</body>
</html>"""


def render_admin_layout(title: str, active: str, user: dict, settings: dict, content: str, flash: str = "", error: str = "") -> str:
    site_name = e(settings.get("site_name", "مؤسسة الاستدامة"))
    is_admin = user["role"] == "admin"

    links = [
        ("/admin", "dashboard", "📊 نظرة عامة"),
        ("/admin/services", "services", "🌿 إدارة الخدمات"),
        ("/admin/articles", "articles", "📰 إدارة الأخبار"),
        ("/admin/partners", "partners", "🤝 إدارة الشركاء"),
        ("/admin/faqs", "faqs", "❓ الأسئلة الشائعة"),
        ("/admin/team", "team", "👥 فريق العمل"),
        ("/admin/messages", "messages", "✉️ رسائل التواصل"),
    ]
    if is_admin:
        links.append(("/admin/settings", "settings", "⚙️ إعدادات الموقع"))
        links.append(("/admin/users", "users", "🔐 المستخدمون والصلاحيات"))

    nav_html = "\n".join(
        f'<a href="{href}" class="{"active" if active == key else ""}">{label}</a>'
        for href, key, label in links
    )

    flash_html = f'<div class="alert alert-success">{e(flash)}</div>' if flash else ""
    err_html = f'<div class="alert alert-error">{e(error)}</div>' if error else ""
    role_label = "مدير عام (Admin)" if is_admin else "محرر (Editor)"

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)} — لوحة التحكم</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="admin-brand">{site_name}</div>
      {nav_html}
      <div style="margin-top:auto; padding-top:16px; border-top:1px solid rgba(255,255,255,0.16);">
        <a href="/" target="_blank">🌐 معاينة الموقع العام</a>
        <a href="/admin/logout" style="color:#fecaca;">🚪 تسجيل الخروج</a>
      </div>
    </aside>
    <div class="admin-main">
      <div class="admin-topbar">
        <div>
          <h2 style="margin:0; color:var(--primary);">{e(title)}</h2>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <span class="badge">{role_label}</span>
          <span style="font-weight:600;">{e(user['name'])}</span>
        </div>
      </div>
      {flash_html}
      {err_html}
      {content}
    </div>
  </div>
</body>
</html>"""


def render_admin_dashboard(user: dict, settings: dict, stats: dict, recent_messages: list) -> str:
    rows = "".join(
        f"""<tr>
          <td>{e(m['sender_name'])}</td>
          <td>{e(m['subject'])}</td>
          <td><span class="badge badge-{e(m['status'])}">{e(m['status'])}</span></td>
          <td>{e(str(m['created_at'])[:16])}</td>
        </tr>"""
        for m in recent_messages
    )
    body = f"""
    <div class="grid-4" style="margin-bottom:24px;">
      <div class="card">
        <div style="color:var(--muted); font-size:0.9rem;">الخدمات</div>
        <div style="font-size:1.8rem; font-weight:800; color:var(--primary);">{stats['services']}</div>
      </div>
      <div class="card">
        <div style="color:var(--muted); font-size:0.9rem;">الأخبار (منشور / الكل)</div>
        <div style="font-size:1.8rem; font-weight:800; color:var(--primary);">{stats['articles_published']} / {stats['articles_total']}</div>
      </div>
      <div class="card">
        <div style="color:var(--muted); font-size:0.9rem;">الشركاء النشطون</div>
        <div style="font-size:1.8rem; font-weight:800; color:var(--primary);">{stats['partners']}</div>
      </div>
      <div class="card">
        <div style="color:var(--muted); font-size:0.9rem;">رسائل غير مقروءة</div>
        <div style="font-size:1.8rem; font-weight:800; color:var(--danger);">{stats['unread_messages']}</div>
      </div>
    </div>
    <div class="card">
      <div class="section-header" style="margin-bottom:12px;">
        <h3 style="margin:0;">أحدث رسائل التواصل</h3>
        <a href="/admin/messages" class="btn btn-sm">إدارة جميع الرسائل</a>
      </div>
      <table class="data-table">
        <thead>
          <tr><th>المرسل</th><th>الموضوع</th><th>الحالة</th><th>التاريخ</th></tr>
        </thead>
        <tbody>{rows if rows else '<tr><td colspan="4">لا توجد رسائل</td></tr>'}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("نظرة عامة", "dashboard", user, settings, body)


def render_admin_settings(user: dict, settings: dict, flash: str = "", error: str = "") -> str:
    body = f"""
    <form method="POST" action="/admin/settings" enctype="multipart/form-data" class="card">
      <div class="grid-2">
        <div class="form-group">
          <label>اسم المؤسسة</label>
          <input type="text" name="site_name" value="{e(settings.get('site_name', ''))}" required>
        </div>
        <div class="form-group">
          <label>الشعار النصي (Tagline)</label>
          <input type="text" name="site_tagline" value="{e(settings.get('site_tagline', ''))}">
        </div>
        <div class="form-group">
          <label>اللون الأساسي</label>
          <input type="color" name="primary_color" value="{e(settings.get('primary_color', '#1b4332'))}">
        </div>
        <div class="form-group">
          <label>اللون الثانوي</label>
          <input type="color" name="accent_color" value="{e(settings.get('accent_color', '#2d6a4f'))}">
        </div>
        <div class="form-group">
          <label>رقم الهاتف</label>
          <input type="text" name="phone" value="{e(settings.get('phone', ''))}">
        </div>
        <div class="form-group">
          <label>البريد الإلكتروني الرسمي</label>
          <input type="email" name="email" value="{e(settings.get('email', ''))}">
        </div>
        <div class="form-group">
          <label>العنوان</label>
          <input type="text" name="address" value="{e(settings.get('address', ''))}">
        </div>
        <div class="form-group">
          <label>رفع شعار جديد (اختياري PNG/SVG/JPG)</label>
          <input type="file" name="logo_file" accept="image/*">
        </div>
      </div>

      <h3 style="margin-top:16px;">محتوى نبذة عنا والإحصائيات</h3>
      <div class="form-group">
        <label>قصة التأسيس</label>
        <textarea name="about_story" rows="3">{e(settings.get('about_story', ''))}</textarea>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label>الرؤية</label>
          <textarea name="vision" rows="2">{e(settings.get('vision', ''))}</textarea>
        </div>
        <div class="form-group">
          <label>الرسالة</label>
          <textarea name="mission" rows="2">{e(settings.get('mission', ''))}</textarea>
        </div>
      </div>
      <div class="form-group">
        <label>القيم الجوهرية</label>
        <input type="text" name="values_text" value="{e(settings.get('values_text', ''))}">
      </div>
      <div class="grid-3">
        <div class="form-group">
          <label>إحصائية المشاريع</label>
          <input type="text" name="stat_projects" value="{e(settings.get('stat_projects', ''))}">
        </div>
        <div class="form-group">
          <label>إحصائية الشركاء</label>
          <input type="text" name="stat_partners" value="{e(settings.get('stat_partners', ''))}">
        </div>
        <div class="form-group">
          <label>إحصائية المستفيدين</label>
          <input type="text" name="stat_clients" value="{e(settings.get('stat_clients', ''))}">
        </div>
      </div>
      <button type="submit" class="btn">حفظ الإعدادات</button>
    </form>
    """
    return render_admin_layout("إعدادات الموقع والهوية", "settings", user, settings, body, flash, error)


def render_admin_services(user: dict, settings: dict, services: list, edit_item: dict | None = None, flash: str = "", error: str = "") -> str:
    item = edit_item or {}
    action_label = "تحديث الخدمة" if edit_item else "إضافة خدمة جديدة"
    rows = "".join(
        f"""<tr>
          <td>{e(s['icon_image'])} {e(s['title'])}</td>
          <td><code>{e(s['slug'])}</code></td>
          <td>{"⭐ نعم" if s['is_featured'] else "لا"}</td>
          <td>{e(s['sort_order'])}</td>
          <td style="white-space:nowrap;">
            <a href="/admin/services?edit={s['id']}" class="btn btn-sm btn-outline">تعديل</a>
            <form method="POST" action="/admin/services" style="display:inline;" onsubmit="return confirm('حذف الخدمة؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{s['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>
          </td>
        </tr>"""
        for s in services
    )
    body = f"""
    <div class="card" style="margin-bottom:22px;">
      <h3>{action_label}</h3>
      <form method="POST" action="/admin/services">
        <input type="hidden" name="action" value="{"update" if edit_item else "create"}">
        {f'<input type="hidden" name="id" value="{item["id"]}">' if edit_item else ''}
        <div class="grid-3">
          <div class="form-group">
            <label>عنوان الخدمة *</label>
            <input type="text" name="title" value="{e(item.get('title', ''))}" required>
          </div>
          <div class="form-group">
            <label>المعرف اللطيف (Slug) *</label>
            <input type="text" name="slug" value="{e(item.get('slug', ''))}" required placeholder="green-consulting">
          </div>
          <div class="form-group">
            <label>الأيقونة (إيموجي)</label>
            <input type="text" name="icon_image" value="{e(item.get('icon_image', '🌱'))}">
          </div>
        </div>
        <div class="form-group">
          <label>وصف مختصر *</label>
          <input type="text" name="short_description" value="{e(item.get('short_description', ''))}" required>
        </div>
        <div class="form-group">
          <label>التفاصيل الكاملة *</label>
          <textarea name="full_content" rows="3" required>{e(item.get('full_content', ''))}</textarea>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>الترتيب</label>
            <input type="number" name="sort_order" value="{e(item.get('sort_order', 1))}">
          </div>
          <div class="form-group" style="display:flex; align-items:center; gap:8px; padding-top:24px;">
            <input type="checkbox" id="is_featured" name="is_featured" value="1" style="width:auto;" {"checked" if item.get("is_featured") else ""}>
            <label for="is_featured" style="margin:0;">عرض في الصفحة الرئيسية (خدمة مميزة)</label>
          </div>
        </div>
        <button type="submit" class="btn">{action_label}</button>
        {f'<a href="/admin/services" class="btn btn-outline">إلغاء التعديل</a>' if edit_item else ''}
      </form>
    </div>

    <div class="card">
      <h3>قائمة الخدمات ({len(services)})</h3>
      <table class="data-table">
        <thead><tr><th>الخدمة</th><th>Slug</th><th>مميزة</th><th>الترتيب</th><th>إجراءات</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("إدارة الخدمات", "services", user, settings, body, flash, error)


def render_admin_articles(user: dict, settings: dict, articles: list, edit_item: dict | None = None, flash: str = "", error: str = "") -> str:
    item = edit_item or {}
    action_label = "تحديث المقال" if edit_item else "نشر خبر / مقال جديد"
    rows = "".join(
        f"""<tr>
          <td>{e(a['title'])}</td>
          <td>{e(a['category'])}</td>
          <td><span class="badge {"badge-draft" if a['status']=='draft' else ""}">{e(a['status'])}</span></td>
          <td>{e(str(a['published_at'])[:10])}</td>
          <td style="white-space:nowrap;">
            <a href="/admin/articles?edit={a['id']}" class="btn btn-sm btn-outline">تعديل</a>
            <form method="POST" action="/admin/articles" style="display:inline;" onsubmit="return confirm('حذف المقال؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{a['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>
          </td>
        </tr>"""
        for a in articles
    )
    body = f"""
    <div class="card" style="margin-bottom:22px;">
      <h3>{action_label}</h3>
      <form method="POST" action="/admin/articles" enctype="multipart/form-data">
        <input type="hidden" name="action" value="{"update" if edit_item else "create"}">
        {f'<input type="hidden" name="id" value="{item["id"]}">' if edit_item else ''}
        <div class="grid-3">
          <div class="form-group">
            <label>عنوان الخبر *</label>
            <input type="text" name="title" value="{e(item.get('title', ''))}" required>
          </div>
          <div class="form-group">
            <label>المعرف اللطيف (Slug) *</label>
            <input type="text" name="slug" value="{e(item.get('slug', ''))}" required placeholder="news-slug">
          </div>
          <div class="form-group">
            <label>التصنيف</label>
            <input type="text" name="category" value="{e(item.get('category', 'أخبار المؤسسة'))}">
          </div>
        </div>
        <div class="form-group">
          <label>ملخص الخبر *</label>
          <input type="text" name="summary" value="{e(item.get('summary', ''))}" required>
        </div>
        <div class="form-group">
          <label>المحتوى الكامل *</label>
          <textarea name="content" rows="4" required>{e(item.get('content', ''))}</textarea>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label>حالة النشر</label>
            <select name="status">
              <option value="published" {"selected" if item.get('status') != 'draft' else ""}>منشور (Published)</option>
              <option value="draft" {"selected" if item.get('status') == 'draft' else ""}>مسودة (Draft)</option>
            </select>
          </div>
          <div class="form-group">
            <label>صورة الغلاف (اختياري)</label>
            <input type="file" name="cover_file" accept="image/*">
          </div>
        </div>
        <button type="submit" class="btn">{action_label}</button>
        {f'<a href="/admin/articles" class="btn btn-outline">إلغاء التعديل</a>' if edit_item else ''}
      </form>
    </div>

    <div class="card">
      <h3>جميع الأخبار والمقالات ({len(articles)})</h3>
      <table class="data-table">
        <thead><tr><th>العنوان</th><th>التصنيف</th><th>الحالة</th><th>التاريخ</th><th>إجراءات</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("إدارة الأخبار والمدونة", "articles", user, settings, body, flash, error)


def render_admin_partners(user: dict, settings: dict, partners: list, edit_item: dict | None = None, flash: str = "", error: str = "") -> str:
    item = edit_item or {}
    action_label = "تحديث الشريك" if edit_item else "إضافة شريك جديد"
    rows = "".join(
        f"""<tr>
          <td>{e(p['name'])}</td>
          <td>{e(p['description'])}</td>
          <td>{"نشط" if p['is_active'] else "مخفي"}</td>
          <td style="white-space:nowrap;">
            <a href="/admin/partners?edit={p['id']}" class="btn btn-sm btn-outline">تعديل</a>
            <form method="POST" action="/admin/partners" style="display:inline;" onsubmit="return confirm('حذف الشريك؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{p['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>
          </td>
        </tr>"""
        for p in partners
    )
    body = f"""
    <div class="card" style="margin-bottom:22px;">
      <h3>{action_label}</h3>
      <form method="POST" action="/admin/partners" enctype="multipart/form-data">
        <input type="hidden" name="action" value="{"update" if edit_item else "create"}">
        {f'<input type="hidden" name="id" value="{item["id"]}">' if edit_item else ''}
        <div class="grid-2">
          <div class="form-group">
            <label>اسم الشريك *</label>
            <input type="text" name="name" value="{e(item.get('name', ''))}" required>
          </div>
          <div class="form-group">
            <label>رابط الموقع الإلكتروني</label>
            <input type="url" name="website_url" value="{e(item.get('website_url', ''))}">
          </div>
        </div>
        <div class="form-group">
          <label>وصف الشراكة</label>
          <input type="text" name="description" value="{e(item.get('description', ''))}">
        </div>
        <div class="grid-3">
          <div class="form-group">
            <label>شعار الشريك (اختياري)</label>
            <input type="file" name="logo_file" accept="image/*">
          </div>
          <div class="form-group">
            <label>الترتيب</label>
            <input type="number" name="sort_order" value="{e(item.get('sort_order', 1))}">
          </div>
          <div class="form-group" style="display:flex; align-items:center; gap:8px; padding-top:24px;">
            <input type="checkbox" id="is_active" name="is_active" value="1" style="width:auto;" {"checked" if item.get("is_active", 1) else ""}>
            <label for="is_active" style="margin:0;">مفعل</label>
          </div>
        </div>
        <button type="submit" class="btn">{action_label}</button>
        {f'<a href="/admin/partners" class="btn btn-outline">إلغاء</a>' if edit_item else ''}
      </form>
    </div>

    <div class="card">
      <h3>قائمة الشركاء ({len(partners)})</h3>
      <table class="data-table">
        <thead><tr><th>الاسم</th><th>الوصف</th><th>الحالة</th><th>إجراءات</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("إدارة الشركاء", "partners", user, settings, body, flash, error)


def render_admin_faqs(user: dict, settings: dict, faqs: list, flash: str = "", error: str = "") -> str:
    rows = "".join(
        f"""<tr>
          <td>{e(f['question'])}</td>
          <td>{e(f['answer'])}</td>
          <td>
            <form method="POST" action="/admin/faqs" onsubmit="return confirm('حذف السؤال؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{f['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>
          </td>
        </tr>"""
        for f in faqs
    )
    body = f"""
    <div class="card" style="margin-bottom:22px;">
      <h3>إضافة سؤال شائع</h3>
      <form method="POST" action="/admin/faqs">
        <input type="hidden" name="action" value="create">
        <div class="form-group">
          <label>السؤال *</label>
          <input type="text" name="question" required>
        </div>
        <div class="form-group">
          <label>الإجابة *</label>
          <textarea name="answer" rows="3" required></textarea>
        </div>
        <button type="submit" class="btn">إضافة</button>
      </form>
    </div>
    <div class="card">
      <h3>الأسئلة الشائعة ({len(faqs)})</h3>
      <table class="data-table">
        <thead><tr><th>السؤال</th><th>الإجابة</th><th>إجراء</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("إدارة الأسئلة الشائعة", "faqs", user, settings, body, flash, error)


def render_admin_team(user: dict, settings: dict, team: list, flash: str = "", error: str = "") -> str:
    rows = "".join(
        f"""<tr>
          <td>{e(m['name'])}</td>
          <td>{e(m['role_title'])}</td>
          <td>{e(m['bio'])}</td>
          <td>
            <form method="POST" action="/admin/team" onsubmit="return confirm('حذف العضو؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{m['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>
          </td>
        </tr>"""
        for m in team
    )
    body = f"""
    <div class="card" style="margin-bottom:22px;">
      <h3>إضافة عضو لفريق العمل</h3>
      <form method="POST" action="/admin/team">
        <input type="hidden" name="action" value="create">
        <div class="grid-2">
          <div class="form-group">
            <label>الاسم *</label>
            <input type="text" name="name" required>
          </div>
          <div class="form-group">
            <label>المسمى الوظيفي *</label>
            <input type="text" name="role_title" required>
          </div>
        </div>
        <div class="form-group">
          <label>نبذة مختصرة</label>
          <input type="text" name="bio">
        </div>
        <button type="submit" class="btn">إضافة عضو</button>
      </form>
    </div>
    <div class="card">
      <h3>فريق العمل ({len(team)})</h3>
      <table class="data-table">
        <thead><tr><th>الاسم</th><th>المسمى</th><th>النبذة</th><th>إجراء</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("إدارة فريق العمل", "team", user, settings, body, flash, error)


def render_admin_messages(user: dict, settings: dict, messages: list, flash: str = "", error: str = "") -> str:
    rows = "".join(
        f"""<tr>
          <td><b>{e(m['sender_name'])}</b><br><small>{e(m['email'])}</small><br><small>{e(m['phone'])}</small></td>
          <td><b>{e(m['subject'])}</b><br><small style="color:var(--muted);">{nl2br(m['message'])}</small></td>
          <td><span class="badge badge-{e(m['status'])}">{e(m['status'])}</span></td>
          <td>{e(str(m['created_at'])[:16])}</td>
          <td style="white-space:nowrap;">
            <form method="POST" action="/admin/messages" style="display:inline-flex; gap:4px;">
              <input type="hidden" name="action" value="status">
              <input type="hidden" name="id" value="{m['id']}">
              <select name="status" style="width:auto; padding:4px 6px; font-size:0.82rem;">
                <option value="unread" {"selected" if m['status']=='unread' else ""}>جديدة</option>
                <option value="replied" {"selected" if m['status']=='replied' else ""}>تم الرد</option>
                <option value="archived" {"selected" if m['status']=='archived' else ""}>مؤرشفة</option>
              </select>
              <button type="submit" class="btn btn-sm">حفظ</button>
            </form>
            <form method="POST" action="/admin/messages" style="display:inline;" onsubmit="return confirm('حذف الرسالة؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{m['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>
          </td>
        </tr>"""
        for m in messages
    )
    body = f"""
    <div class="card">
      <h3>صندوق رسائل التواصل والدعم ({len(messages)})</h3>
      <table class="data-table">
        <thead><tr><th>المرسل</th><th>الموضوع والرسالة</th><th>الحالة</th><th>التاريخ</th><th>إجراءات</th></tr></thead>
        <tbody>{rows if rows else '<tr><td colspan="5">لا توجد رسائل واردة.</td></tr>'}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("رسائل التواصل", "messages", user, settings, body, flash, error)


def render_admin_users(user: dict, settings: dict, users: list, flash: str = "", error: str = "") -> str:
    rows = "".join(
        f"""<tr>
          <td>{e(u['name'])}</td>
          <td>{e(u['email'])}</td>
          <td><span class="badge">{e(u['role'])}</span></td>
          <td>{"نشط" if u['is_active'] else "معطل"}</td>
          <td>
            {f'''<form method="POST" action="/admin/users" style="display:inline;" onsubmit="return confirm('حذف المستخدم؟');">
              <input type="hidden" name="action" value="delete">
              <input type="hidden" name="id" value="{u['id']}">
              <button type="submit" class="btn btn-sm btn-danger">حذف</button>
            </form>''' if u['id'] != user['id'] else '<small style="color:var(--muted);">حسابك الحالي</small>'}
          </td>
        </tr>"""
        for u in users
    )
    body = f"""
    <div class="card" style="margin-bottom:22px;">
      <h3>إضافة مستخدم جديد</h3>
      <form method="POST" action="/admin/users">
        <input type="hidden" name="action" value="create">
        <div class="grid-4">
          <div class="form-group">
            <label>الاسم *</label>
            <input type="text" name="name" required>
          </div>
          <div class="form-group">
            <label>البريد الإلكتروني *</label>
            <input type="email" name="email" required>
          </div>
          <div class="form-group">
            <label>كلمة المرور *</label>
            <input type="password" name="password" required minlength="6">
          </div>
          <div class="form-group">
            <label>الصلاحية *</label>
            <select name="role">
              <option value="editor">محرر (Editor)</option>
              <option value="admin">مدير عام (Admin)</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn">إنشاء الحساب</button>
      </form>
    </div>

    <div class="card">
      <h3>حسابات لوحة التحكم ({len(users)})</h3>
      <table class="data-table">
        <thead><tr><th>الاسم</th><th>البريد</th><th>الدور</th><th>الحالة</th><th>إجراء</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return render_admin_layout("المستخدمون والصلاحيات", "users", user, settings, body, flash, error)


def render_error_page(settings: dict, code: int, title: str, message: str) -> str:
    body = f"""
    <section class="section">
      <div class="container">
        <div class="card" style="text-align:center; max-width:540px; margin:40px auto;">
          <h1 style="color:var(--primary); font-size:3rem; margin:0;">{code}</h1>
          <h2>{e(title)}</h2>
          <p>{e(message)}</p>
          <a href="/" class="btn">العودة للرئيسية</a>
        </div>
      </div>
    </section>
    """
    return render_public_layout(title, "", settings, body)
