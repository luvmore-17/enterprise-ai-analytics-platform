from sqlalchemy import text
from config.database import engine

with engine.connect() as conn:
    print(conn.execute(text("SELECT current_database();")).scalar())