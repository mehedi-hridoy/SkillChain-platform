"""
Seed script to create default content categories
Run this once to populate initial categories
"""

import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.content import Category
from slugify import slugify

def seed_categories():
    db: Session = SessionLocal()
    
    categories = [
        {
            "name": "Compliance & Standards",
            "description": "Articles about compliance, certifications, and industry standards",
            "icon": "📋"
        },
        {
            "name": "Sustainability",
            "description": "Environmental impact, sustainable practices, and green manufacturing",
            "icon": "🌱"
        },
        {
            "name": "Supply Chain",
            "description": "Supply chain management, transparency, and traceability",
            "icon": "🔗"
        },
        {
            "name": "Worker Welfare",
            "description": "Worker rights, safety, and fair labor practices",
            "icon": "👷"
        },
        {
            "name": "Technology & Innovation",
            "description": "Digital transformation, Industry 4.0, and manufacturing technology",
            "icon": "💡"
        },
        {
            "name": "Quality Management",
            "description": "Quality control, testing, and product excellence",
            "icon": "✅"
        },
        {
            "name": "Best Practices",
            "description": "Industry best practices, case studies, and success stories",
            "icon": "⭐"
        },
        {
            "name": "Regulations & Policy",
            "description": "Legal requirements, trade policies, and regulatory updates",
            "icon": "📜"
        }
    ]
    
    created_count = 0
    
    try:
        for cat_data in categories:
            slug = slugify(cat_data["name"])
            
            # Check if already exists
            existing = db.query(Category).filter(Category.slug == slug).first()
            if existing:
                print(f"⏭️  Category '{cat_data['name']}' already exists, skipping...")
                continue
            
            # Create new category
            category = Category(
                name=cat_data["name"],
                slug=slug,
                description=cat_data["description"],
                icon=cat_data["icon"],
                order=created_count
            )
            db.add(category)
            created_count += 1
            print(f"✅ Created category: {cat_data['name']}")
        
        db.commit()
        print(f"\n🎉 Successfully created {created_count} categories!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding content categories...\n")
    seed_categories()
