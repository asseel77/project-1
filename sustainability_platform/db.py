import hashlib
import os
import secrets
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected_hex = stored_hash.split("$", 1)
    except ValueError:
        return False
    candidate = hash_password(password, salt)
    return secrets.compare_digest(candidate, stored_hash)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'editor')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL DEFAULT '',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            short_description TEXT NOT NULL,
            full_content TEXT NOT NULL,
            icon_image TEXT NOT NULL DEFAULT '🌱',
            is_featured INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL DEFAULT 'أخبار المؤسسة',
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            cover_image TEXT NOT NULL DEFAULT '',
            author_id INTEGER,
            status TEXT NOT NULL CHECK(status IN ('draft', 'published')) DEFAULT 'published',
            published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            logo_path TEXT NOT NULL DEFAULT '',
            website_url TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('unread', 'replied', 'archived')) DEFAULT 'unread',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            bio TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    # Seed only if users table is empty
    user_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, role, is_active) VALUES (?, ?, ?, ?, ?)",
            ("أصيل باسم السنوسي", "admin@estidama.sa", hash_password("Admin@123"), "admin", 1),
        )
        admin_id = cur.lastrowid
        cur.execute(
            "INSERT INTO users (name, email, password_hash, role, is_active) VALUES (?, ?, ?, ?, ?)",
            ("سارة المحرر", "editor@estidama.sa", hash_password("Editor@123"), "editor", 1),
        )

        settings_seed = [
            ("site_name", "مؤسسة الاستدامة"),
            ("site_tagline", "حلول بيئية ومؤسسية مبتكرة لمستقبل أكثر استدامة"),
            ("primary_color", "#1b4332"),
            ("accent_color", "#2d6a4f"),
            ("logo_path", "/static/img/logo.svg"),
            ("phone", "+966 11 456 7890"),
            ("email", "info@estidama.sa"),
            ("address", "الرياض، حي العليا، طريق الملك فهد، برج الاستدامة"),
            ("twitter_url", "https://x.com"),
            ("linkedin_url", "https://linkedin.com"),
            ("about_story", "تأسست مؤسسة الاستدامة لتكون شريكاً موثوقاً للقطاعين العام والخاص في تصميم وتنفيذ مبادرات الاستدامة البيئية، وخفض البصمة الكربونية، وتأهيل المنشآت وفق المعايير العالمية."),
            ("vision", "أن نكون المرجع الرقمي والاستشاري الأول في المنطقة لحلول الاستدامة البيئية والتنمية المستدامة."),
            ("mission", "تمكين المؤسسات والمجتمع من تبني ممارسات مستدامة عبر استشارات دقيقة ومشاريع نوعية ذات أثر قابل للقياس."),
            ("values_text", "الشفافية المؤسسية • الابتكار البيئي • الشراكة المجتمعية • الأثر المستدام"),
            ("stat_projects", "+45"),
            ("stat_partners", "+28"),
            ("stat_clients", "+120"),
        ]
        cur.executemany(
            "INSERT INTO site_settings (key, value) VALUES (?, ?)",
            settings_seed,
        )

        services_seed = [
            (
                "استشارات التحول الأخضر",
                "green-transformation",
                "إعداد خطط التحول البيئي للمؤسسات وقياس وتقليل الانبعاثات الكربونية.",
                "نساعد الشركات والجهات الحكومية على بناء خارطة طريق متكاملة للتحول نحو الاقتصاد الأخضر، بدءاً من تدقيق استهلاك الطاقة والمياه وصولاً إلى إعداد تقارير الاستدامة السنوية (ESG) المتوافقة مع المعايير الدولية.",
                "🌿",
                1,
                1,
            ),
            (
                "دراسات تقييم الأثر البيئي",
                "environmental-impact-assessment",
                "دراسات فنية معتمدة لتقييم الآثار البيئية للمشاريع قبل التنفيذ.",
                "تقديم دراسات شاملة لتقييم الأثر البيئي والاجتماعي للمشاريع الصناعية والعمرانية، مع وضع خطط تخفيف المخاطر وضمان الامتثال الكامل للأنظمة والتشريعات البيئية الوطنية.",
                "📊",
                1,
                2,
            ),
            (
                "إدارة النفايات وإعادة التدوير",
                "waste-management-recycling",
                "تصميم منظومات فرز وتدوير النفايات المؤسسية وتحويلها لموارد.",
                "تطوير برامج متكاملة لإدارة النفايات في المجمعات التجارية والمصانع، تشمل مسح كميات الهدر، تصميم نقاط الفرز، والربط مع مصانع إعادة التدوير المعتمدة لتحقيق هدف صفر نفايات.",
                "♻️",
                1,
                3,
            ),
            (
                "برامج التوعية والتدريب البيئي",
                "sustainability-training",
                "ورش عمل وبرامج تدريبية متخصصة لرفع كفاءة الكوادر في الاستدامة.",
                "تصميم وتنفيذ حقائب تدريبية وورش عمل تفاعلية للفرق الإدارية والموظفين حول ممارسات العمل المستدام، ترشيد الموارد، وأهداف التنمية المستدامة.",
                "🎓",
                0,
                4,
            ),
        ]
        cur.executemany(
            """INSERT INTO services
               (title, slug, short_description, full_content, icon_image, is_featured, sort_order)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            services_seed,
        )

        articles_seed = [
            (
                "إطلاق مبادرة المدن الخضراء بالتعاون مع الشركاء",
                "green-cities-initiative-2026",
                "مبادرات",
                "أطلقت مؤسسة الاستدامة برنامجها السنوي لتأهيل الأحياء السكنية والتجارية وفق معايير كفاءة الطاقة والتشجير.",
                "أعلنت مؤسسة الاستدامة اليوم عن إطلاق مبادرة المدن الخضراء لعام 2026 بالشراكة مع عدد من الجهات البلدية وشركات القطاع الخاص.\n\nتهدف المبادرة إلى خفض استهلاك الطاقة بنسبة 25% في المباني المشاركة خلال عامين، وزيادة الغطاء النباتي باستخدام أنظمة ري ذكية موفرة للمياه.\n\nوأكدت الإدارة أن التسجيل متاح للمؤسسات الراغبة في الانضمام عبر صفحة التواصل.",
                "",
                admin_id,
                "published",
                "2026-11-10 10:00:00",
            ),
            (
                "توقيع اتفاقية شراكة استراتيجية في مجال الطاقة النظيفة",
                "clean-energy-partnership",
                "شراكات",
                "اتفاقية جديدة لدعم تحول المنشآت المتوسطة نحو حلول الطاقة الشمسية وخفض التكاليف التشغيلية.",
                "وقعت مؤسسة الاستدامة اتفاقية تعاون مع شركة آفاق للطاقة المتجددة لتقديم حلول تمويلية واستشارية متكاملة للمصانع والمنشآت الراغبة في تركيب ألواح الطاقة الشمسية.\n\nوتشمل الاتفاقية إجراء مسح فني مجاني لأول 20 منشأة متقدمة عبر الموقع الرسمي للمؤسسة.",
                "",
                admin_id,
                "published",
                "2026-11-18 14:30:00",
            ),
            (
                "دليل المؤسسات الناشئة لإعداد تقارير الاستدامة (ESG)",
                "esg-guide-for-startups",
                "مقالات",
                "خطوات عملية ومبسطة تساعد الشركات على قياس أثرها البيئي والاجتماعي والحوكمة.",
                "لم تعد تقارير الاستدامة حكراً على الشركات الكبرى؛ بل أصبحت معياراً أساسياً لجذب المستثمرين وبناء ثقة العملاء.\n\nفي هذا المقال نستعرض أهم 5 مؤشرات يجب على كل مؤسسة ناشئة البدء بقياسها منذ اليوم الأول، وكيفية توثيقها بشكل شفاف.",
                "",
                admin_id,
                "published",
                "2026-11-22 09:15:00",
            ),
            (
                "مسودة التقرير السنوي لإنجازات الربع الرابع",
                "q4-annual-report-draft",
                "إعلانات",
                "مسودة داخلية قيد المراجعة حول مؤشرات الأداء البيئي للمشاريع القائمة.",
                "هذه المقالة محفوظة كمسودة ولا تظهر للزوار في الواجهة العامة حتى يتم اعتمادها ونشرها من لوحة التحكم.",
                "",
                admin_id,
                "draft",
                "2026-11-24 11:00:00",
            ),
        ]
        cur.executemany(
            """INSERT INTO articles
               (title, slug, category, summary, content, cover_image, author_id, status, published_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            articles_seed,
        )

        partners_seed = [
            ("مجموعة الطاقة الخضراء", "شريك استراتيجي في مشاريع الطاقة الشمسية وكفاءة الطاقة.", "", "https://example.com", 1, 1),
            ("هيئة البيئة الوطنية", "شريك تنظيمي وداعم لمبادرات التشجير وحماية الموارد.", "", "https://example.com", 2, 1),
            ("شركة آفاق للتدوير", "شريك تشغيلي في منظومات فرز وإعادة تدوير النفايات.", "", "https://example.com", 3, 1),
            ("مؤسسة التنمية المستدامة", "شريك معرفي في الأبحاث والتدريب وبناء القدرات.", "", "https://example.com", 4, 1),
        ]
        cur.executemany(
            "INSERT INTO partners (name, description, logo_path, website_url, sort_order, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            partners_seed,
        )

        faqs_seed = [
            ("كيف يمكنني طلب استشارة بيئية لمؤسستي؟", "يمكنكم التوجه إلى صفحة التواصل والدعم وتعبئة النموذج مع اختيار نوع الخدمة المطلوبة، وسيتواصل معكم مستشارنا خلال 24 ساعة عمل.", 1, 1),
            ("هل تقدمون خدماتكم خارج مدينة الرياض؟", "نعم، ننفذ مشاريع واستشارات في جميع مناطق المملكة والخليج العربي عبر فرقنا الميدانية والشراكات الإقليمية.", 2, 1),
            ("كم تستغرق دراسة تقييم الأثر البيئي؟", "تعتمد المدة على حجم المشروع ونطاقه، وغالباً ما تتراوح بين أسبوعين إلى 6 أسابيع شاملة الزيارات الميدانية والتقرير النهائي.", 3, 1),
            ("كيف يمكن لشركتنا الانضمام كشريك استراتيجي؟", "نرحب دائماً بالشراكات النوعية؛ يرجى مراسلتنا عبر البريد الرسمي أو نموذج التواصل مع توضيح مجال الشراكة المقترح.", 4, 1),
        ]
        cur.executemany(
            "INSERT INTO faqs (question, answer, sort_order, is_active) VALUES (?, ?, ?, ?)",
            faqs_seed,
        )

        team_seed = [
            ("أصيل باسم السنوسي", "المؤسس والمدير التنفيذي", "خبير في استراتيجيات الاستدامة والتحول المؤسسي الأخضر.", 1),
            ("م. خالد العتيبي", "مدير الدراسات البيئية", "مستشار معتمد في تقييم الأثر البيئي وإدارة الموارد.", 2),
            ("أ. نورة القحطاني", "مديرة الشراكات والمبادرات", "متخصصة في بناء الشراكات المجتمعية وبرامج التوعية.", 3),
        ]
        cur.executemany(
            "INSERT INTO team_members (name, role_title, bio, sort_order) VALUES (?, ?, ?, ?)",
            team_seed,
        )

        messages_seed = [
            ("شركة البناء الحديث", "contact@modernbuild.sa", "0501234567", "طلب دراسة تقييم أثر بيئي", "نرغب في الحصول على عرض سعر لدراسة الأثر البيئي لمشروعنا الصناعي الجديد.", "unread"),
            ("جمعية أصدقاء البيئة", "info@ecofriends.org", "0559876543", "مبادرة تشجير مشتركة", "نشكر لكم تعاونكم المستمر ونتطلع لتنسيق ورشة العمل القادمة.", "replied"),
        ]
        cur.executemany(
            "INSERT INTO contact_messages (sender_name, email, phone, subject, message, status) VALUES (?, ?, ?, ?, ?, ?)",
            messages_seed,
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
