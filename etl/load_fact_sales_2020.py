import pandas as pd
from database.connection import engine

df = pd.read_csv(
    "datasets/raw/fact_sales_2020.csv",
    encoding="cp1252"
)

print(df.head())
print(df.shape)

df.to_sql(
    name="stg_fact_sales_2020",
    con=engine,
    schema="staging",
    if_exists="replace",
    index=False
)

print("✅ fact sales 2020 loaded successfully!")