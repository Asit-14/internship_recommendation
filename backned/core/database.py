from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.config import settings

# PostgreSQL connection string should use psycopg driver
# Ensure DATABASE_URL uses: postgresql://user:password@host:port/database
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,
    echo=False,  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

Base = declarative_base()


def ensure_internship_table_columns(engine) -> None:
    inspector = inspect(engine)
    if "internships" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("internships")}

    statements: list[str] = []

    def add_column(column_name: str, ddl: str) -> None:
        if column_name not in existing_columns:
            statements.append(f"ALTER TABLE internships ADD COLUMN {ddl}")

    add_column("created_by", "created_by INTEGER")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_application_table_columns(engine) -> None:
    inspector = inspect(engine)
    if "applications" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("applications")}

    statements: list[str] = []

    def add_column(column_name: str, ddl: str) -> None:
        if column_name not in existing_columns:
            statements.append(f"ALTER TABLE applications ADD COLUMN {ddl}")

    add_column("resume_url", "resume_url VARCHAR(512)")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_user_table_columns(engine) -> None:
    # Lightweight dev-time safety net; production should use migrations.
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}

    if engine.dialect.name == "postgresql":
        json_type = "JSONB"
        json_default = "DEFAULT '[]'::jsonb"
        timestamp_type = "TIMESTAMPTZ"
        created_at_default = "DEFAULT NOW()"
        bool_default = "DEFAULT false"
        enum_migration_sql = """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_enum e
                    JOIN pg_type t ON e.enumtypid = t.oid
                    WHERE t.typname = 'user_role' AND e.enumlabel = 'company'
                ) THEN
                    ALTER TYPE user_role ADD VALUE 'company';
                END IF;
            END IF;
        END $$;
        """
    else:
        json_type = "JSON"
        json_default = "DEFAULT '[]'"
        timestamp_type = "TIMESTAMP"
        created_at_default = "DEFAULT CURRENT_TIMESTAMP"
        bool_default = "DEFAULT 0"
        enum_migration_sql = None

    statements: list[str] = []

    def add_column(column_name: str, ddl: str) -> None:
        if column_name not in existing_columns:
            statements.append(f"ALTER TABLE users ADD COLUMN {ddl}")

    add_column("phone", "phone VARCHAR(20)")
    add_column("location", "location VARCHAR(255)")
    add_column("education", "education VARCHAR(120)")
    add_column("college_name", "college_name VARCHAR(255)")
    add_column("branch", "branch VARCHAR(120)")
    add_column("graduation_year", "graduation_year INTEGER")
    add_column("skills", f"skills {json_type} NOT NULL {json_default}")
    add_column("resume_filename", "resume_filename VARCHAR(255)")
    add_column("otp_hash", "otp_hash VARCHAR(255)")
    add_column("otp_expiry", f"otp_expiry {timestamp_type}")
    add_column("is_verified", f"is_verified BOOLEAN NOT NULL {bool_default}")
    add_column("is_active", f"is_active BOOLEAN NOT NULL {bool_default.replace('false', 'true').replace('0', '1')}")
    add_column("deleted_at", f"deleted_at {timestamp_type}")
    add_column(
        "created_at",
        f"created_at {timestamp_type} NOT NULL {created_at_default}",
    )

    if not statements:
        if enum_migration_sql is None:
            return

    with engine.begin() as connection:
        if enum_migration_sql:
            connection.execute(text(enum_migration_sql))
        for statement in statements:
            connection.execute(text(statement))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
