import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

CSV_FOLDER = r"D:\RetailAI_Data"   # <-- Change this

# Change this every time
TABLE = "inventory_movements"
path = os.path.join(CSV_FOLDER, f"{TABLE}.csv")

print(f"Loading {TABLE}...")

df = pd.read_csv(path)

print(df.head())
print(df.columns.tolist())

df.to_sql(
    TABLE,
    engine,
    if_exists="append",
    index=False,
)

print(f"✅ Loaded {len(df)} rows into {TABLE}")