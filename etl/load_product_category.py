import pandas as pd
from database.connection import engine

df = pd.read_csv(
    "datasets/raw/dim_product_category.csv",
    encoding="cp1252"
)

print(df.head())
print(df.shape)

df.to_sql(
    name="stg_product_category",
    con=engine,
    schema="staging",
    if_exists="replace",
    index=False
)

print("✅ product category loaded successfully!")