from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Text, DateTime, func
#from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pgvector.sqlalchemy import Vector
#from sentence_transformers import SentenceTransformer

Base = declarative_base()



class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    created_at = Column(DateTime, default=func.now())

class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    chapter_number = Column(Integer, nullable=False)
    title = Column(String)
    full_text = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=func.now())

    #full_text_vector = Column(Vector(768))
    #summary_vector = Column(Vector(768))

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    relationship_type = Column(String)
    is_bidirectional = Column(String)
    

class WikiPage(Base):
    __tablename__ = 'wiki_pages'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    chapter_id = Column(Integer, ForeignKey('chapters.id'))
    content = Column(Text, nullable=False)
    previous_state = Column(Integer, ForeignKey('wiki_pages.id'))
    #vector = Column(Vector(768))


#model = SentenceTransformer('all-MiniLM-L6-v2')

DATABASE_URL = 'postgresql://postgres:146@localhost:5432/shuscribe'
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# book = Book(title="Pokemon", author="jimmy")
# session.add(book)
# session.commit()

# summary = 'Protagonist is isekai\'d from a Pokemon Emulator'

# chapter = Chapter(
#     book_id = book.id,
#     chapter_number = 1,
#     title = 'Isekai\'d from Pokemon Emulator',
#     summary = 'The protagonist is playing a Pokemon ROM hack on their phone and is hit by a truck. The protagonist is rebirthed as Amber and encounters Dr. Fuji and Mewtwo.'
# )
# session.add(chapter)
# session.commit()


