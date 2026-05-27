import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # Your Neon connection string

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, ssl="require")
    return _pool


async def get_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def create_tables():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id          SERIAL PRIMARY KEY,
                name        TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email       TEXT,
                phone       TEXT,
                address     TEXT,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS projects (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                name         TEXT NOT NULL,
                client       TEXT,
                client_phone TEXT,
                client_email TEXT,
                start_date   DATE,
                end_date     DATE,
                contract_value NUMERIC(14,2) DEFAULT 0,
                budget       NUMERIC(14,2) DEFAULT 0,
                progress     INT DEFAULT 0,
                status       TEXT DEFAULT 'active',
                location     TEXT,
                latitude     NUMERIC(10,8),
                longitude    NUMERIC(11,8),
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS bills (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                description  TEXT NOT NULL,
                amount       NUMERIC(14,2) NOT NULL,
                bill_type    TEXT NOT NULL CHECK (bill_type IN ('expense','income')),
                category     TEXT,
                status       TEXT DEFAULT 'pending',
                file_url     TEXT,
                bill_date    DATE DEFAULT CURRENT_DATE,
                gst_number   TEXT,
                shop_name    TEXT,
                ocr_data     JSONB,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS workers (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                name         TEXT NOT NULL,
                role         TEXT,
                phone        TEXT,
                daily_wage   NUMERIC(10,2) DEFAULT 0,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id           SERIAL PRIMARY KEY,
                worker_id    INT REFERENCES workers(id) ON DELETE CASCADE,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                date         DATE NOT NULL DEFAULT CURRENT_DATE,
                status       TEXT NOT NULL CHECK (status IN ('present','absent','holiday')),
                hours_worked NUMERIC(5,2) DEFAULT 8,
                UNIQUE (worker_id, date)
            );

            CREATE TABLE IF NOT EXISTS labour_payments (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                worker_id    INT REFERENCES workers(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                amount       NUMERIC(14,2) NOT NULL,
                payment_type TEXT CHECK (payment_type IN ('daily','weekly','monthly')),
                from_date    DATE,
                to_date      DATE,
                payment_date DATE DEFAULT CURRENT_DATE,
                status       TEXT DEFAULT 'paid',
                notes        TEXT,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS materials (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                name         TEXT NOT NULL,
                category     TEXT,
                unit         TEXT,
                total_quantity NUMERIC(14,2) DEFAULT 0,
                used_quantity NUMERIC(14,2) DEFAULT 0,
                remaining_quantity NUMERIC(14,2) DEFAULT 0,
                unit_price   NUMERIC(10,2) DEFAULT 0,
                supplier_name TEXT,
                supplier_phone TEXT,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS material_usage (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                material_id  INT REFERENCES materials(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                quantity     NUMERIC(14,2) NOT NULL,
                usage_date   DATE DEFAULT CURRENT_DATE,
                purpose      TEXT,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS client_payments (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                amount       NUMERIC(14,2) NOT NULL,
                payment_type TEXT CHECK (payment_type IN ('advance','milestone','final')),
                payment_date DATE DEFAULT CURRENT_DATE,
                status       TEXT DEFAULT 'pending',
                due_date     DATE,
                description  TEXT,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS contracts (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                title        TEXT NOT NULL,
                file_url     TEXT,
                contract_type TEXT,
                start_date   DATE,
                end_date     DATE,
                status       TEXT DEFAULT 'active',
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                title        TEXT NOT NULL,
                message      TEXT,
                type         TEXT CHECK (type IN ('payment','material','labour','general')),
                is_read      BOOLEAN DEFAULT FALSE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS daily_logs (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                log_date     DATE DEFAULT CURRENT_DATE,
                weather      TEXT,
                activities   TEXT,
                issues       TEXT,
                progress     INT DEFAULT 0,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS uploads (
                id           SERIAL PRIMARY KEY,
                company_id   INT REFERENCES companies(id) ON DELETE CASCADE,
                project_id   INT REFERENCES projects(id) ON DELETE SET NULL,
                file_name    TEXT NOT NULL,
                file_url     TEXT NOT NULL,
                file_type    TEXT,
                category     TEXT,
                uploaded_at  TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_bills_company ON bills(company_id);
            CREATE INDEX IF NOT EXISTS idx_bills_project ON bills(project_id);
            CREATE INDEX IF NOT EXISTS idx_workers_company ON workers(company_id);
            CREATE INDEX IF NOT EXISTS idx_attendance_worker ON attendance(worker_id);
            CREATE INDEX IF NOT EXISTS idx_materials_company ON materials(company_id);
            CREATE INDEX IF NOT EXISTS idx_payments_company ON client_payments(company_id);
            CREATE INDEX IF NOT EXISTS idx_notifications_company ON notifications(company_id);
        """)
