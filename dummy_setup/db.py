from sqlalchemy import create_engine, MetaData

# Replace with your actual database URL
DATABASE_URL =  f"postgresql://postgres:wordpress@localhost:5432/rental-mgt"

engine = create_engine(DATABASE_URL)

# Create a MetaData instance
metadata = MetaData()

# Reflect the tables
metadata.reflect(bind=engine)

# Drop all tables
metadata.drop_all(bind=engine)
