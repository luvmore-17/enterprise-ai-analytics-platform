import pandas as pd
from database.connection import engine

df = pd.read_csv(
    "datasets/raw/dim_customer.csv",
    encoding="cp1252"
)

print(df.head())
print(df.shape)

df.to_sql(
    name="stg_customer",
    con=engine,
    schema="staging",
    if_exists="replace",
    index=False
)

print("✅ Customer loaded successfully!")