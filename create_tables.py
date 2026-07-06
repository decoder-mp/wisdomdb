from core.database import engine, Base
import models.user
import models.wisdom

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")
print("You can now register users.")