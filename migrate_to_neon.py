from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# -----------------------------
# LOCAL DATABASE
# -----------------------------
local_engine = create_engine(
    "postgresql://postgres:Luvmore123@localhost:5432/enterprise_ai_analytics"
)

# -----------------------------
# NEON DATABASE
# -----------------------------
neon_engine = create_engine(
    "postgresql://neondb_owner:npg_jX1rOkhwy2Az@ep-delicate-block-atzix4tx-pooler.c-9.us-east-1.aws.neon.tech/enterprise_ai_analytics?sslmode=require"
)

# -----------------------------
# Get ONLY base tables
# -----------------------------
with local_engine.connect() as conn:
    tables = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='analytics'
        AND table_type='BASE TABLE'
        ORDER BY table_name
    """)).fetchall()

print(f"\nFound {len(tables)} tables.\n")

# -----------------------------
# Copy each table
# -----------------------------
for (table,) in tables:

    print("=" * 60)
    print(f"Copying: {table}")

    try:

        # Check table exists in Neon
        with neon_engine.connect() as conn:

            exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema='analytics'
                    AND table_name=:tbl
                )
            """), {"tbl": table}).scalar()

        if not exists:
            print(f"Skipped {table} (table not found in Neon)")
            continue

        # Read rows from local
        with local_engine.connect() as src:
            rows = src.execute(
                text(f'SELECT * FROM analytics."{table}"')
            ).mappings().all()

        if len(rows) == 0:
            print("Table is empty.")
            continue

        columns = list(rows[0].keys())

        column_names = ", ".join(f'"{c}"' for c in columns)
        placeholders = ", ".join(f":{c}" for c in columns)

        insert_sql = text(f"""
            INSERT INTO analytics."{table}"
            ({column_names})
            VALUES ({placeholders})
        """)

        with neon_engine.begin() as dst:
            dst.execute(insert_sql, rows)

        print(f"Copied {len(rows)} rows.")

    except SQLAlchemyError as e:
        print(f"Failed on {table}")
        print(e)

print("\nMigration finished.")