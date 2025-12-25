from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class LearningArticle(Base):
    """Public blog-style articles - everyone can read"""
    __tablename__ = "learning_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    title_bn = Column(String, nullable=True)  # Bangla title
    
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly
    
    content = Column(Text, nullable=False)  # English content (rich text/HTML)
    content_bn = Column(Text, nullable=True)  # Bangla content
    
    excerpt = Column(String, nullable=True)  # Short description
    excerpt_bn = Column(String, nullable=True)
    
    featured_image = Column(String, nullable=True)  # Image URL
    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    category = Column(String, nullable=True)  # e.g. "Safety", "Quality", "Sustainability"
    tags = Column(JSON, nullable=True)  # Array of tags
    
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    views = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)


class Course(Base):
    """Structured courses - may require enrollment"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    title_bn = Column(String, nullable=True)
    
    slug = Column(String, unique=True, index=True, nullable=False)
    
    description = Column(Text, nullable=False)
    description_bn = Column(Text, nullable=True)
    
    thumbnail = Column(String, nullable=True)
    
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Access control
    is_public = Column(Boolean, default=True)  # Free for all
    required_role = Column(String, nullable=True)  # worker, manager, factory_admin
    
    duration_hours = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)  # beginner, intermediate, advanced
    
    is_published = Column(Boolean, default=False)
    
    enrollment_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Module(Base):
    """Modules within a course"""
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    title = Column(String, nullable=False)
    title_bn = Column(String, nullable=True)
    
    description = Column(Text, nullable=True)
    description_bn = Column(Text, nullable=True)
    
    order = Column(Integer, default=0)  # Display order
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Lesson(Base):
    """Individual lessons within modules"""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("course_modules.id"), nullable=False)
    
    title = Column(String, nullable=False)
    title_bn = Column(String, nullable=True)
    
    content = Column(Text, nullable=False)  # Rich text/HTML
    content_bn = Column(Text, nullable=True)
    
    content_type = Column(String, default="text")  # text, video, quiz, document
    
    # For video lessons
    video_url = Column(String, nullable=True)
    
    # For downloadable resources
    attachments = Column(JSON, nullable=True)  # Array of file URLs
    
    duration_minutes = Column(Integer, nullable=True)
    
    order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProgress(Base):
    """Track user progress through courses"""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
