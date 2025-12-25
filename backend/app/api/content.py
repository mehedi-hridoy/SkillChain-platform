from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from slugify import slugify

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.content import Article, Course, Category, CourseModule, Lesson, CourseEnrollment
from app.models.user import User
from app.services.file_upload import FileUploadService

router = APIRouter(prefix="/content", tags=["Content Management"])

# ============= SCHEMAS =============

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    slug: str
    order: int
    
    class Config:
        from_attributes = True


class ArticleCreate(BaseModel):
    title: str
    excerpt: Optional[str] = None
    content: str
    category_id: int
    tags: Optional[List[str]] = None
    language: str = "en"
    is_featured: bool = False
    status: str = "draft"

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    content: str
    featured_image: Optional[str]
    author_id: int
    author_name: str
    category_id: int
    category_name: str
    status: str
    is_featured: bool
    tags: Optional[List[str]]
    reading_time: Optional[int]
    views: int
    language: str
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LessonCreate(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    is_free: bool = False

class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    lessons: List[LessonCreate] = []

class CourseCreate(BaseModel):
    title: str
    description: str
    category_id: int
    level: str = "beginner"
    language: str = "en"
    tags: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    price: int = 0
    status: str = "draft"
    is_featured: bool = False

class CourseResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    featured_image: Optional[str]
    instructor_id: int
    instructor_name: str
    category_id: int
    category_name: str
    status: str
    level: str
    duration: int
    language: str
    price: int
    enrollment_count: int
    rating: int
    is_featured: bool
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= CATEGORY ENDPOINTS =============

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin"]))
):
    """Create a new content category"""
    slug = slugify(category.name)
    
    # Check if slug exists
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = Category(
        name=category.name,
        slug=slug,
        description=category.description,
        icon=category.icon
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """Get all categories (public)"""
    categories = db.query(Category).order_by(Category.order, Category.name).all()
    return categories


# ============= ARTICLE ENDPOINTS =============

@router.post("/articles", response_model=ArticleResponse)
async def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    """Create a new article/blog post"""
    slug = slugify(article.title)
    
    # Make slug unique
    existing = db.query(Article).filter(Article.slug == slug).first()
    if existing:
        slug = f"{slug}-{datetime.utcnow().timestamp()}"
    
    # Calculate reading time (avg 200 words per minute)
    word_count = len(article.content.split())
    reading_time = max(1, round(word_count / 200))
    
    new_article = Article(
        title=article.title,
        slug=slug,
        excerpt=article.excerpt,
        content=article.content,
        author_id=current_user.id,
        category_id=article.category_id,
        tags=article.tags or [],
        reading_time=reading_time,
        language=article.language,
        is_featured=article.is_featured,
        status=article.status,
        published_at=datetime.utcnow() if article.status == "published" else None
    )
    
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    # Add author and category info
    category = db.query(Category).filter(Category.id == article.category_id).first()
    
    return {
        **new_article.__dict__,
        "author_name": current_user.name,
        "category_name": category.name if category else ""
    }


@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    language: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List articles with filters (published only for public)"""
    query = db.query(Article)
    
    # Default to published for public access
    if status:
        query = query.filter(Article.status == status)
    else:
        query = query.filter(Article.status == "published")
    
    if category_id:
        query = query.filter(Article.category_id == category_id)
    
    if language:
        query = query.filter(Article.language == language)
    
    if search:
        query = query.filter(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.excerpt.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%")
            )
        )
    
    articles = query.order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    
    # Enrich with author and category names
    result = []
    for article in articles:
        author = db.query(User).filter(User.id == article.author_id).first()
        category = db.query(Category).filter(Category.id == article.category_id).first()
        
        result.append({
            **article.__dict__,
            "author_name": author.name if author else "Unknown",
            "category_name": category.name if category else ""
        })
    
    return result


@router.get("/articles/{slug}")
def get_article(slug: str, db: Session = Depends(get_db)):
    """Get article by slug (public)"""
    article = db.query(Article).filter(Article.slug == slug).first()
    
    if not article or article.status != "published":
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment views
    article.views += 1
    db.commit()
    
    author = db.query(User).filter(User.id == article.author_id).first()
    category = db.query(Category).filter(Category.id == article.category_id).first()
    
    return {
        **article.__dict__,
        "author_name": author.name if author else "Unknown",
        "category_name": category.name if category else ""
    }


@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    """Update an article"""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check ownership
    if current_user.role != "platform_admin" and article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = article_update.dict(exclude_unset=True)
    
    # Update slug if title changed
    if "title" in update_data:
        update_data["slug"] = slugify(update_data["title"])
    
    # Set published_at if status changed to published
    if update_data.get("status") == "published" and article.status != "published":
        update_data["published_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(article, field, value)
    
    db.commit()
    db.refresh(article)
    
    author = db.query(User).filter(User.id == article.author_id).first()
    category = db.query(Category).filter(Category.id == article.category_id).first()
    
    return {
        **article.__dict__,
        "author_name": author.name if author else "Unknown",
        "category_name": category.name if category else ""
    }


@router.post("/articles/{article_id}/upload-image")
async def upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    """Upload featured image for article"""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if current_user.role != "platform_admin" and article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    file_service = FileUploadService()
    result = await file_service.save_file(file, "articles")
    
    article.featured_image = result["url"]
    db.commit()
    
    return {"url": result["url"]}


@router.delete("/articles/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin"]))
):
    """Delete an article"""
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(article)
    db.commit()
    
    return {"message": "Article deleted successfully"}


# ============= COURSE ENDPOINTS =============

@router.post("/courses", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    """Create a new course"""
    slug = slugify(course.title)
    
    existing = db.query(Course).filter(Course.slug == slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    new_course = Course(
        title=course.title,
        slug=slug,
        description=course.description,
        instructor_id=current_user.id,
        category_id=course.category_id,
        level=course.level,
        language=course.language,
        tags=course.tags or [],
        learning_outcomes=course.learning_outcomes or [],
        prerequisites=course.prerequisites or [],
        price=course.price,
        status=course.status,
        is_featured=course.is_featured,
        published_at=datetime.utcnow() if course.status == "published" else None
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    category = db.query(Category).filter(Category.id == course.category_id).first()
    
    return {
        **new_course.__dict__,
        "instructor_name": current_user.name,
        "category_name": category.name if category else ""
    }


@router.get("/courses", response_model=List[CourseResponse])
def list_courses(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    level: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List courses with filters"""
    query = db.query(Course)
    
    if status:
        query = query.filter(Course.status == status)
    else:
        query = query.filter(Course.status == "published")
    
    if category_id:
        query = query.filter(Course.category_id == category_id)
    
    if level:
        query = query.filter(Course.level == level)
    
    if language:
        query = query.filter(Course.language == language)
    
    courses = query.order_by(Course.published_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for course in courses:
        instructor = db.query(User).filter(User.id == course.instructor_id).first()
        category = db.query(Category).filter(Category.id == course.category_id).first()
        
        result.append({
            **course.__dict__,
            "instructor_name": instructor.name if instructor else "Unknown",
            "category_name": category.name if category else ""
        })
    
    return result


@router.get("/courses/{slug}")
def get_course(slug: str, db: Session = Depends(get_db)):
    """Get course details with modules and lessons"""
    course = db.query(Course).filter(Course.slug == slug).first()
    
    if not course or course.status != "published":
        raise HTTPException(status_code=404, detail="Course not found")
    
    instructor = db.query(User).filter(User.id == course.instructor_id).first()
    category = db.query(Category).filter(Category.id == course.category_id).first()
    modules = db.query(CourseModule).filter(CourseModule.course_id == course.id).order_by(CourseModule.order).all()
    
    modules_data = []
    for module in modules:
        lessons = db.query(Lesson).filter(Lesson.module_id == module.id).order_by(Lesson.order).all()
        modules_data.append({
            **module.__dict__,
            "lessons": [lesson.__dict__ for lesson in lessons]
        })
    
    return {
        **course.__dict__,
        "instructor_name": instructor.name if instructor else "Unknown",
        "category_name": category.name if category else "",
        "modules": modules_data
    }


@router.post("/courses/{course_id}/modules")
def add_course_module(
    course_id: int,
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    """Add a module to a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if current_user.role != "platform_admin" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get next order number
    max_order = db.query(func.max(CourseModule.order)).filter(CourseModule.course_id == course_id).scalar() or 0
    
    new_module = CourseModule(
        course_id=course_id,
        title=module.title,
        description=module.description,
        order=max_order + 1
    )
    
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    
    # Add lessons
    for idx, lesson_data in enumerate(module.lessons):
        new_lesson = Lesson(
            module_id=new_module.id,
            title=lesson_data.title,
            content=lesson_data.content,
            video_url=lesson_data.video_url,
            duration=lesson_data.duration,
            is_free=lesson_data.is_free,
            order=idx + 1
        )
        db.add(new_lesson)
    
    # Update course duration
    total_duration = db.query(func.sum(Lesson.duration)).join(CourseModule).filter(
        CourseModule.course_id == course_id
    ).scalar() or 0
    course.duration = total_duration
    
    db.commit()
    
    return {"message": "Module added successfully", "module_id": new_module.id}


@router.post("/courses/{course_id}/upload-image")
async def upload_course_image(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    """Upload featured image for course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if current_user.role != "platform_admin" and course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    file_service = FileUploadService()
    result = await file_service.save_file(file, "courses")
    
    course.featured_image = result["url"]
    db.commit()
    
    return {"url": result["url"]}
