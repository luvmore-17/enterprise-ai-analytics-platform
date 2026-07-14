from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql://postgres:Luvmore123@localhost:5432/enterprise_ai_analytics"
)

with engine.connect() as conn:
    print(conn.execute(text("SELECT current_database();")).scalar())