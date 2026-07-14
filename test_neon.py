from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://neondb_owner:npg_jX1rOkhwy2Az@ep-delicate-block-atzix4tx-pooler.c-9.us-east-1.aws.neon.tech/enterprise_ai_analytics?sslmode=require"
)

with engine.connect() as conn:
    version = conn.execute(text("SELECT version();")).scalar()
    print(version)

print("✅ Connected to Neon successfully!")