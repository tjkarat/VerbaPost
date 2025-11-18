from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# 1. Setup the Database "Engine" (The connection)
# This creates a file named 'verbapost.db' in your folder
engine = create_engine('sqlite:///verbapost.db', echo=True)

# 2. The Base Class (All our tables inherit from this)
Base = declarative_base()

# 3. Define the "User" Table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # Relationship: A user can have many letters
    letters = relationship("Letter", back_populates="author")

    def __repr__(self):
        return f"<User(name={self.username})>"

# 4. Define the "Letter" Table
class Letter(Base):
    __tablename__ = 'letters'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False) # The transcribed text
    status = Column(String, default="Draft") # Draft, Sent, Delivered
    created_at = Column(DateTime, default=datetime.now)
    
    # Foreign Key: Links back to the User
    user_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="letters")

    def __repr__(self):
        return f"<Letter(status={self.status}, created={self.created_at})>"

# 5. The "Init" Function
# This actually builds the tables when you run the script
def init_db():
    Base.metadata.create_all(engine)
    print("Database created successfully!")

if __name__ == "__main__":
    init_db()