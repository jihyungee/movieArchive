from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# DB 설정 (SQLite)
DATABASE_URL = "sqlite:///./movies.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 모델
class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    release_date = Column(String)
    director = Column(String)
    genre = Column(String)
    poster_url = Column(Text)

    reviews = relationship("Review", back_populates="movie", cascade="all, delete")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String, nullable=True)

    movie = relationship("Movie", back_populates="reviews")

Base.metadata.create_all(bind=engine)

# FastAPI 앱
app = FastAPI()

# 입력 모델
class MovieIn(BaseModel):
    title: str
    release_date: str | None = None
    director: str | None = None
    genre: str | None = None
    poster_url: str | None = None

class ReviewIn(BaseModel):
    movie_id: int
    author: str
    content: str

# 영화 등록
@app.post("/movies/")
def create_movie(m: MovieIn):
    db = SessionLocal()
    movie = Movie(**m.dict())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    db.close()
    return movie

# 영화 전체 조회
@app.get("/movies/")
def list_movies():
    db = SessionLocal()
    movies = db.query(Movie).all()
    db.close()
    return movies

# 특정 영화 조회
@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    db = SessionLocal()
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    db.close()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 특정 영화 삭제
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    db = SessionLocal()
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        db.close()
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    db.close()
    return {"message": "Movie deleted"}

# 리뷰 등록
@app.post("/reviews/")
def create_review(r: ReviewIn):
    db = SessionLocal()
    movie = db.query(Movie).filter(Movie.id == r.movie_id).first()
    if not movie:
        db.close()
        raise HTTPException(status_code=404, detail="Movie not found")
    review = Review(**r.dict())
    db.add(review)
    db.commit()
    db.refresh(review)
    db.close()
    return review

# 특정 영화 리뷰 조회
@app.get("/reviews/{movie_id}")
def list_reviews(movie_id: int):
    db = SessionLocal()
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    db.close()
    return reviews


# 특정 리뷰 삭제
@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):
    db = SessionLocal()
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        db.close()
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    db.close()
    return {"message": "Review deleted"}
