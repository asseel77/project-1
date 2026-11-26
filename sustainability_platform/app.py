from datetime import datetime, timedelta, timezone
from email.parser import BytesParser
from email.policy import default as email_policy
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
import os
import secrets
from urllib.parse import parse_qs, unquote, urlparse

import db
import views

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}


def get_settings(conn) -> dict:
    rows = conn.execute("SELECT key, value FROM site_settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


def save_uploaded_file(file_info: dict | None) -> str:
    if not file_info or not file_info.get("filename") or not file_info.get("data"):
        return ""
    ext = os.path.splitext(file_info["filename"])[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return ""
    safe_name = f"{secrets.token_hex(12)}{ext}"
    dest = os.path.join(UPLOAD_DIR, safe_name)
    with open(dest, "wb") as f:
        f.write(file_info["data"])
    return f"/static/uploads/{safe_name}"


class SustainabilityHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

    def send_html(self, html_str: str, status: int = 200, headers: dict | None = None):
        data = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, location: str, headers: dict | None = None):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()

    def serve_static(self, rel_path: str):
        clean_rel = os.path.normpath(unquote(rel_path)).lstrip("\\/")
        full_path = os.path.abspath(os.path.join(STATIC_DIR, clean_rel))
        if not full_path.startswith(os.path.abspath(STATIC_DIR)) or not os.path.isfile(full_path):
            self.send_error(404, "File not found")
            return
        ctype, _ = mimetypes.guess_type(full_path)
        if full_path.endswith(".svg"):
            ctype = "image/svg+xml"
        elif not ctype:
            ctype = "application/octet-stream"
        with open(full_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def parse_post_data(self) -> tuple[dict, dict]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length > 0 else b""
        content_type = self.headers.get("Content-Type", "")
        fields: dict[str, str] = {}
        files: dict[str, dict] = {}

        if content_type.startswith("multipart/form-data"):
            raw_mime = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
            msg = BytesParser(policy=email_policy).parsebytes(raw_mime)
            for part in msg.iter_parts():
                name = part.get_param("name", header="content-disposition")
                if not name:
                    continue
                filename = part.get_filename()
                payload = part.get_payload(decode=True) or b""
                if filename:
                    files[name] = {"filename": filename, "data": payload}
                else:
                    fields[name] = payload.decode("utf-8", errors="replace").strip()
        else:
            parsed = parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
            fields = {k: v[0].strip() for k, v in parsed.items()}

        return fields, files

    def get_current_user(self, conn):
        cookie_hdr = self.headers.get("Cookie", "")
        if not cookie_hdr:
            return None
        cookie = SimpleCookie()
        cookie.load(cookie_hdr)
        if "session_token" not in cookie:
            return None
        token = cookie["session_token"].value
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        row = conn.execute(
            """SELECT u.id, u.name, u.email, u.role, u.is_active
               FROM sessions s
               JOIN users u ON s.user_id = u.id
               WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1""",
            (token, now_iso),
        ).fetchone()
        return dict(row) if row else None

    def require_auth(self, conn, admin_only: bool = False):
        user = self.get_current_user(conn)
        if not user:
            self.redirect("/admin/login")
            return None
        if admin_only and user["role"] != "admin":
            settings = get_settings(conn)
            self.send_html(
                views.render_error_page(
                    settings, 403, "غير مصرح بالوصول", "هذه الصفحة متاحة للمدير العام (Admin) فقط."
                ),
                status=403,
            )
            return None
        return user

    # ---------------- GET ----------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path.startswith("/static/"):
            self.serve_static(path[len("/static/"):])
            return

        conn = db.get_connection()
        try:
            settings = get_settings(conn)

            # Public routes
            if path == "/":
                services = conn.execute(
                    "SELECT * FROM services WHERE is_featured = 1 ORDER BY sort_order ASC, id ASC LIMIT 3"
                ).fetchall()
                partners = conn.execute(
                    "SELECT * FROM partners WHERE is_active = 1 ORDER BY sort_order ASC, id ASC LIMIT 4"
                ).fetchall()
                articles = conn.execute(
                    "SELECT * FROM articles WHERE status = 'published' ORDER BY published_at DESC LIMIT 3"
                ).fetchall()
                self.send_html(views.render_home(settings, services, partners, articles))
                return

            if path == "/about":
                team = conn.execute("SELECT * FROM team_members ORDER BY sort_order ASC, id ASC").fetchall()
                self.send_html(views.render_about(settings, team))
                return

            if path == "/services":
                services = conn.execute("SELECT * FROM services ORDER BY sort_order ASC, id ASC").fetchall()
                self.send_html(views.render_services(settings, services))
                return

            if path.startswith("/services/"):
                slug = unquote(path[len("/services/"):]).strip("/")
                service = conn.execute("SELECT * FROM services WHERE slug = ?", (slug,)).fetchone()
                if not service:
                    self.send_html(views.render_error_page(settings, 404, "الخدمة غير موجودة", "لم يتم العثور على الخدمة المطلوبة."), 404)
                    return
                self.send_html(views.render_service_detail(settings, service))
                return

            if path == "/partners":
                partners = conn.execute(
                    "SELECT * FROM partners WHERE is_active = 1 ORDER BY sort_order ASC, id ASC"
                ).fetchall()
                self.send_html(views.render_partners(settings, partners))
                return

            if path == "/news":
                q = qs.get("q", [""])[0].strip()
                cat = qs.get("cat", [""])[0].strip()
                sql = "SELECT * FROM articles WHERE status = 'published'"
                params = []
                if q:
                    sql += " AND (title LIKE ? OR summary LIKE ? OR content LIKE ?)"
                    like_q = f"%{q}%"
                    params.extend([like_q, like_q, like_q])
                if cat:
                    sql += " AND category = ?"
                    params.append(cat)
                sql += " ORDER BY published_at DESC"
                articles = conn.execute(sql, params).fetchall()
                cat_rows = conn.execute(
                    "SELECT DISTINCT category FROM articles WHERE status = 'published'"
                ).fetchall()
                categories = [r["category"] for r in cat_rows]
                self.send_html(views.render_news(settings, articles, q, cat, categories))
                return

            if path.startswith("/news/"):
                slug = unquote(path[len("/news/"):]).strip("/")
                article = conn.execute(
                    "SELECT * FROM articles WHERE slug = ? AND status = 'published'", (slug,)
                ).fetchone()
                if not article:
                    self.send_html(views.render_error_page(settings, 404, "الخبر غير موجود", "لم يتم العثور على المقال المطلوب."), 404)
                    return
                self.send_html(views.render_article_detail(settings, article))
                return

            if path == "/contact":
                faqs = conn.execute("SELECT * FROM faqs WHERE is_active = 1 ORDER BY sort_order ASC, id ASC").fetchall()
                prefill = qs.get("service", [""])[0]
                if prefill:
                    prefill = f"طلب خدمة: {prefill}"
                status_msg = "تم إرسال رسالتك بنجاح! سيتواصل معك فريقنا قريباً." if qs.get("sent") else ""
                self.send_html(views.render_contact(settings, faqs, prefill, status_msg))
                return

            # Admin auth routes
            if path == "/admin/login":
                if self.get_current_user(conn):
                    self.redirect("/admin")
                    return
                self.send_html(views.render_admin_login(settings))
                return

            if path == "/admin/logout":
                cookie_hdr = self.headers.get("Cookie", "")
                if cookie_hdr:
                    c = SimpleCookie()
                    c.load(cookie_hdr)
                    if "session_token" in c:
                        conn.execute("DELETE FROM sessions WHERE token = ?", (c["session_token"].value,))
                        conn.commit()
                self.redirect("/admin/login", {"Set-Cookie": "session_token=; Path=/; Max-Age=0; HttpOnly"})
                return

            # Protected admin routes
            if path == "/admin":
                user = self.require_auth(conn)
                if not user:
                    return
                stats = {
                    "services": conn.execute("SELECT COUNT(*) FROM services").fetchone()[0],
                    "articles_published": conn.execute("SELECT COUNT(*) FROM articles WHERE status='published'").fetchone()[0],
                    "articles_total": conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0],
                    "partners": conn.execute("SELECT COUNT(*) FROM partners WHERE is_active=1").fetchone()[0],
                    "unread_messages": conn.execute("SELECT COUNT(*) FROM contact_messages WHERE status='unread'").fetchone()[0],
                }
                recent = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT 5").fetchall()
                self.send_html(views.render_admin_dashboard(user, settings, stats, recent))
                return

            if path == "/admin/settings":
                user = self.require_auth(conn, admin_only=True)
                if not user:
                    return
                flash = "تم حفظ إعدادات الموقع بنجاح." if qs.get("saved") else ""
                self.send_html(views.render_admin_settings(user, settings, flash=flash))
                return

            if path == "/admin/services":
                user = self.require_auth(conn)
                if not user:
                    return
                services = conn.execute("SELECT * FROM services ORDER BY sort_order ASC, id ASC").fetchall()
                edit_id = qs.get("edit", [""])[0]
                edit_item = conn.execute("SELECT * FROM services WHERE id = ?", (edit_id,)).fetchone() if edit_id.isdigit() else None
                flash = "تم تنفيذ العملية بنجاح." if qs.get("ok") else ""
                self.send_html(views.render_admin_services(user, settings, services, dict(edit_item) if edit_item else None, flash=flash))
                return

            if path == "/admin/articles":
                user = self.require_auth(conn)
                if not user:
                    return
                articles = conn.execute("SELECT * FROM articles ORDER BY published_at DESC, id DESC").fetchall()
                edit_id = qs.get("edit", [""])[0]
                edit_item = conn.execute("SELECT * FROM articles WHERE id = ?", (edit_id,)).fetchone() if edit_id.isdigit() else None
                flash = "تم حفظ المقال بنجاح." if qs.get("ok") else ""
                self.send_html(views.render_admin_articles(user, settings, articles, dict(edit_item) if edit_item else None, flash=flash))
                return

            if path == "/admin/partners":
                user = self.require_auth(conn)
                if not user:
                    return
                partners = conn.execute("SELECT * FROM partners ORDER BY sort_order ASC, id ASC").fetchall()
                edit_id = qs.get("edit", [""])[0]
                edit_item = conn.execute("SELECT * FROM partners WHERE id = ?", (edit_id,)).fetchone() if edit_id.isdigit() else None
                flash = "تم تحديث بيانات الشركاء." if qs.get("ok") else ""
                self.send_html(views.render_admin_partners(user, settings, partners, dict(edit_item) if edit_item else None, flash=flash))
                return

            if path == "/admin/faqs":
                user = self.require_auth(conn)
                if not user:
                    return
                faqs = conn.execute("SELECT * FROM faqs ORDER BY sort_order ASC, id ASC").fetchall()
                flash = "تم تحديث الأسئلة الشائعة." if qs.get("ok") else ""
                self.send_html(views.render_admin_faqs(user, settings, faqs, flash=flash))
                return

            if path == "/admin/team":
                user = self.require_auth(conn)
                if not user:
                    return
                team = conn.execute("SELECT * FROM team_members ORDER BY sort_order ASC, id ASC").fetchall()
                flash = "تم تحديث فريق العمل." if qs.get("ok") else ""
                self.send_html(views.render_admin_team(user, settings, team, flash=flash))
                return

            if path == "/admin/messages":
                user = self.require_auth(conn)
                if not user:
                    return
                messages = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC, id DESC").fetchall()
                flash = "تم تحديث حالة الرسالة." if qs.get("ok") else ""
                self.send_html(views.render_admin_messages(user, settings, messages, flash=flash))
                return

            if path == "/admin/users":
                user = self.require_auth(conn, admin_only=True)
                if not user:
                    return
                users = conn.execute("SELECT id, name, email, role, is_active, created_at FROM users ORDER BY id ASC").fetchall()
                flash = "تم تحديث حسابات المستخدمين." if qs.get("ok") else ""
                self.send_html(views.render_admin_users(user, settings, users, flash=flash))
                return

            self.send_html(views.render_error_page(settings, 404, "الصفحة غير موجودة", "الرابط المطلوب غير متوفر."), 404)
        finally:
            conn.close()

    # ---------------- POST ----------------
    def do_POST(self):
        path = urlparse(self.path).path
        fields, files = self.parse_post_data()
        conn = db.get_connection()
        try:
            settings = get_settings(conn)

            # Public contact form submission
            if path == "/contact":
                sender = fields.get("sender_name", "")
                email = fields.get("email", "")
                phone = fields.get("phone", "")
                subject = fields.get("subject", "")
                message = fields.get("message", "")
                if not sender or not email or not subject or not message:
                    faqs = conn.execute("SELECT * FROM faqs WHERE is_active = 1 ORDER BY sort_order ASC").fetchall()
                    self.send_html(views.render_contact(settings, faqs, subject, error_msg="يرجى تعبئة جميع الحقول المطلوبة."), 400)
                    return
                conn.execute(
                    "INSERT INTO contact_messages (sender_name, email, phone, subject, message) VALUES (?, ?, ?, ?, ?)",
                    (sender, email, phone, subject, message),
                )
                conn.commit()
                self.redirect("/contact?sent=1")
                return

            # Admin login
            if path == "/admin/login":
                email = fields.get("email", "").lower()
                password = fields.get("password", "")
                row = conn.execute("SELECT * FROM users WHERE LOWER(email) = ? AND is_active = 1", (email,)).fetchone()
                if not row or not db.verify_password(password, row["password_hash"]):
                    self.send_html(views.render_admin_login(settings, "بيانات الدخول غير صحيحة."), 401)
                    return
                token = secrets.token_urlsafe(32)
                expires = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, row["id"], expires))
                conn.commit()
                self.redirect("/admin", {"Set-Cookie": f"session_token={token}; Path=/; HttpOnly; SameSite=Lax"})
                return

            # Admin settings (Admin only)
            if path == "/admin/settings":
                user = self.require_auth(conn, admin_only=True)
                if not user:
                    return
                keys = [
                    "site_name", "site_tagline", "primary_color", "accent_color",
                    "phone", "email", "address", "about_story", "vision",
                    "mission", "values_text", "stat_projects", "stat_partners", "stat_clients",
                ]
                for k in keys:
                    if k in fields:
                        conn.execute(
                            "INSERT INTO site_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                            (k, fields[k]),
                        )
                uploaded_logo = save_uploaded_file(files.get("logo_file"))
                if uploaded_logo:
                    conn.execute(
                        "INSERT INTO site_settings (key, value) VALUES ('logo_path', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                        (uploaded_logo,),
                    )
                conn.commit()
                self.redirect("/admin/settings?saved=1")
                return

            # Services CRUD
            if path == "/admin/services":
                user = self.require_auth(conn)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    conn.execute("DELETE FROM services WHERE id = ?", (int(fields["id"]),))
                elif act in ("create", "update"):
                    title = fields.get("title", "")
                    slug = fields.get("slug", "") or f"service-{secrets.token_hex(4)}"
                    short_desc = fields.get("short_description", "")
                    full_content = fields.get("full_content", "")
                    icon_img = fields.get("icon_image", "🌱") or "🌱"
                    is_featured = 1 if fields.get("is_featured") == "1" else 0
                    sort_order = int(fields.get("sort_order", "0") or 0)
                    if act == "create":
                        conn.execute(
                            """INSERT INTO services (title, slug, short_description, full_content, icon_image, is_featured, sort_order)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (title, slug, short_desc, full_content, icon_img, is_featured, sort_order),
                        )
                    else:
                        conn.execute(
                            """UPDATE services SET title=?, slug=?, short_description=?, full_content=?, icon_image=?, is_featured=?, sort_order=?
                               WHERE id=?""",
                            (title, slug, short_desc, full_content, icon_img, is_featured, sort_order, int(fields["id"])),
                        )
                conn.commit()
                self.redirect("/admin/services?ok=1")
                return

            # Articles CRUD
            if path == "/admin/articles":
                user = self.require_auth(conn)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    conn.execute("DELETE FROM articles WHERE id = ?", (int(fields["id"]),))
                elif act in ("create", "update"):
                    title = fields.get("title", "")
                    slug = fields.get("slug", "") or f"post-{secrets.token_hex(4)}"
                    category = fields.get("category", "أخبار المؤسسة")
                    summary = fields.get("summary", "")
                    content = fields.get("content", "")
                    status = fields.get("status", "published")
                    if status not in ("draft", "published"):
                        status = "published"
                    cover = save_uploaded_file(files.get("cover_file"))
                    if act == "create":
                        conn.execute(
                            """INSERT INTO articles (title, slug, category, summary, content, cover_image, author_id, status)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (title, slug, category, summary, content, cover, user["id"], status),
                        )
                    else:
                        if cover:
                            conn.execute(
                                """UPDATE articles SET title=?, slug=?, category=?, summary=?, content=?, cover_image=?, status=? WHERE id=?""",
                                (title, slug, category, summary, content, cover, status, int(fields["id"])),
                            )
                        else:
                            conn.execute(
                                """UPDATE articles SET title=?, slug=?, category=?, summary=?, content=?, status=? WHERE id=?""",
                                (title, slug, category, summary, content, status, int(fields["id"])),
                            )
                conn.commit()
                self.redirect("/admin/articles?ok=1")
                return

            # Partners CRUD
            if path == "/admin/partners":
                user = self.require_auth(conn)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    conn.execute("DELETE FROM partners WHERE id = ?", (int(fields["id"]),))
                elif act in ("create", "update"):
                    name = fields.get("name", "")
                    description = fields.get("description", "")
                    website_url = fields.get("website_url", "")
                    sort_order = int(fields.get("sort_order", "0") or 0)
                    is_active = 1 if fields.get("is_active") == "1" else 0
                    logo = save_uploaded_file(files.get("logo_file"))
                    if act == "create":
                        conn.execute(
                            """INSERT INTO partners (name, description, logo_path, website_url, sort_order, is_active)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (name, description, logo, website_url, sort_order, is_active),
                        )
                    else:
                        if logo:
                            conn.execute(
                                """UPDATE partners SET name=?, description=?, logo_path=?, website_url=?, sort_order=?, is_active=? WHERE id=?""",
                                (name, description, logo, website_url, sort_order, is_active, int(fields["id"])),
                            )
                        else:
                            conn.execute(
                                """UPDATE partners SET name=?, description=?, website_url=?, sort_order=?, is_active=? WHERE id=?""",
                                (name, description, website_url, sort_order, is_active, int(fields["id"])),
                            )
                conn.commit()
                self.redirect("/admin/partners?ok=1")
                return

            # FAQs CRUD
            if path == "/admin/faqs":
                user = self.require_auth(conn)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    conn.execute("DELETE FROM faqs WHERE id = ?", (int(fields["id"]),))
                elif act == "create":
                    conn.execute(
                        "INSERT INTO faqs (question, answer) VALUES (?, ?)",
                        (fields.get("question", ""), fields.get("answer", "")),
                    )
                conn.commit()
                self.redirect("/admin/faqs?ok=1")
                return

            # Team CRUD
            if path == "/admin/team":
                user = self.require_auth(conn)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    conn.execute("DELETE FROM team_members WHERE id = ?", (int(fields["id"]),))
                elif act == "create":
                    conn.execute(
                        "INSERT INTO team_members (name, role_title, bio) VALUES (?, ?, ?)",
                        (fields.get("name", ""), fields.get("role_title", ""), fields.get("bio", "")),
                    )
                conn.commit()
                self.redirect("/admin/team?ok=1")
                return

            # Messages management
            if path == "/admin/messages":
                user = self.require_auth(conn)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    conn.execute("DELETE FROM contact_messages WHERE id = ?", (int(fields["id"]),))
                elif act == "status" and fields.get("id", "").isdigit():
                    st = fields.get("status", "unread")
                    if st in ("unread", "replied", "archived"):
                        conn.execute("UPDATE contact_messages SET status = ? WHERE id = ?", (st, int(fields["id"])))
                conn.commit()
                self.redirect("/admin/messages?ok=1")
                return

            # Users management (Admin only)
            if path == "/admin/users":
                user = self.require_auth(conn, admin_only=True)
                if not user:
                    return
                act = fields.get("action", "")
                if act == "delete" and fields.get("id", "").isdigit():
                    uid = int(fields["id"])
                    if uid != user["id"]:
                        conn.execute("DELETE FROM users WHERE id = ?", (uid,))
                elif act == "create":
                    name = fields.get("name", "")
                    email = fields.get("email", "").lower()
                    password = fields.get("password", "")
                    role = fields.get("role", "editor")
                    if role not in ("admin", "editor"):
                        role = "editor"
                    if name and email and len(password) >= 6:
                        conn.execute(
                            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                            (name, email, db.hash_password(password), role),
                        )
                conn.commit()
                self.redirect("/admin/users?ok=1")
                return

            self.send_error(404, "Endpoint not found")
        finally:
            conn.close()


def run(host: str = "127.0.0.1", port: int = 8000):
    db.init_db()
    server = ThreadingHTTPServer((host, port), SustainabilityHandler)
    print(f"Sustainability Platform running at http://{host}:{port}")
    print(f"Admin Dashboard: http://{host}:{port}/admin")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    run()
