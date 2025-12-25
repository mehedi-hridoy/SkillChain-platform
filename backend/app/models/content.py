from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base

class ContentType(str, enum.Enum):
    ARTICLE = "article"
    COURSE = "course"
    VIDEO = "video"
    TUTORIAL = "tutorial"

class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String)  # Icon name or URL
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = relationship("Article", back_populates="category")
    courses = relationship("Course", back_populates="category")


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    excerpt = Column(Text)
    content = Column(Text, nullable=False)
    featured_image = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    status = Column(String, default=ContentStatus.DRAFT.value)
    is_featured = Column(Boolean, default=False)
    
    tags = Column(JSON)  # Array of tags
    reading_time = Column(Integer)  # Minutes
    views = Column(Integer, default=0)
    
    language = Column(String, default="en")  # en or bn
    
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text)
    featured_image = Column(String)
    thumbnail = Column(String)
    
    instructor_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    status = Column(String, default=ContentStatus.DRAFT.value)
    is_featured = Column(Boolean, default=False)
    
    level = Column(String)  # beginner, intermediate, advanced
    duration = Column(Integer)  # Total duration in minutes
    language = Column(String, default="en")
    
    tags = Column(JSON)
    learning_outcomes = Column(JSON)  # Array of learning outcomes
    prerequisites = Column(JSON)  # Array of prerequisites
    
    price = Column(Integer, default=0)  # 0 means free
    enrollment_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # Average rating * 10
    
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = relationship("User", back_populates="courses")
    category = relationship("Category", back_populates="courses")
    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")


class CourseModule(Base):
    __tablename__ = "course_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("course_modules.id"))
    title = Column(String, nullable=False)
    content = Column(Text)
    video_url = Column(String)
    duration = Column(Integer)  # Duration in minutes
    order = Column(Integer, default=0)
    
    is_free = Column(Boolean, default=False)  # Free preview
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = relationship("CourseModule", back_populates="lessons")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    
    progress = Column(Integer, default=0)  # Percentage
    completed_lessons = Column(JSON)  # Array of lesson IDs
    
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime, default=datetime.utcnow)
