import pandas as pd
from database.connection import engine

df = pd.read_csv(
    "datasets/raw/fact_returns.csv",
    encoding="cp1252"
)

print(df.head())
print(df.shape)

df.to_sql(
    name="stg_fact_returns",
    con=engine,
    schema="staging",
    if_exists="replace",
    index=False
)

print("✅ fact returns loaded successfully!")