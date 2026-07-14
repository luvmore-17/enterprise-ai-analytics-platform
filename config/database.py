from sqlalchemy import create_engine

DB_USER = "neondb_owner"
DB_PASSWORD = "npg_jX1rOkhwy2Az"
DB_HOST = "ep-delicate-block-atzix4tx-pooler.c-9.us-east-1.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "enterprise_ai_analytics"

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?sslmode=require"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)