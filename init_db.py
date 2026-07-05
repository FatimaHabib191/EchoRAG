from auth.database import Base
from auth.database import engine

import auth.models

Base.metadata.create_all(bind=engine)

print("Database created successfully!")