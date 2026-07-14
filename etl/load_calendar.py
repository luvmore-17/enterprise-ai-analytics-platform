import pandas as pd
from database.connection import engine

# Read the CSV
df = pd.read_csv("datasets/raw/dim_calendar.csv")

print(df.head())
print(f"Rows: {len(df)}")

# Load to PostgreSQL
df.to_sql(
    name="stg_calendar",
    con=engine,
    schema="staging",
    if_exists="replace",
    index=False
)

print("✅ Calendar loaded successfully!")