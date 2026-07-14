import pandas as pd
from database.connection import engine

df = pd.read_csv(
    "datasets/raw/dim_territory.csv",
    encoding="cp1252"
)

print(df.head())
print(df.shape)

df.to_sql(
    name="stg_territory",
    con=engine,
    schema="staging",
    if_exists="replace",
    index=False
)

print("✅ territory loaded successfully!")