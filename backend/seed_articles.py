"""
Seed script to create sample articles for the learning hub
Run this to populate the homepage with sample content
"""

import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.content import Article, Category
from app.models.user import User
from slugify import slugify
from datetime import datetime

def seed_articles():
    db: Session = SessionLocal()
    
    try:
        # Get the first platform_admin user
        admin_user = db.query(User).filter(User.role == "platform_admin").first()
        if not admin_user:
            print("❌ No platform_admin user found. Please create one first.")
            return
        
        # Get categories
        compliance_cat = db.query(Category).filter(Category.slug == "compliance-standards").first()
        sustainability_cat = db.query(Category).filter(Category.slug == "sustainability").first()
        supply_chain_cat = db.query(Category).filter(Category.slug == "supply-chain").first()
        
        if not all([compliance_cat, sustainability_cat, supply_chain_cat]):
            print("❌ Required categories not found. Please run seed_categories.py first.")
            return
        
        articles_data = [
            {
                "title": "Understanding EU Digital Product Passports: A Complete Guide for RMG Manufacturers",
                "excerpt": "The European Union's Digital Product Passport regulation is reshaping the textile industry. Learn how to prepare your factory for compliance and turn it into a competitive advantage.",
                "content": """The European Union's Digital Product Passport (DPP) regulation represents one of the most significant changes in textile manufacturing compliance in recent decades. As the 2026 deadline approaches, RMG manufacturers must understand and implement these requirements to maintain access to EU markets.

## What is a Digital Product Passport?

A Digital Product Passport is a digital record that contains comprehensive information about a product's lifecycle, including materials, manufacturing processes, environmental impact, and social compliance. Think of it as a complete biography of every garment you produce.

## Key Requirements for RMG Manufacturers

1. **Material Traceability**: Every component must be tracked from source to finished product
2. **Environmental Data**: Carbon footprint, water usage, and waste generation must be documented
3. **Social Compliance**: Worker conditions, training records, and safety measures must be verified
4. **Digital Accessibility**: All information must be accessible via QR codes or digital identifiers

## Implementation Steps

### Step 1: Assess Current Systems
Evaluate your existing tracking and compliance systems. Most factories find gaps in:
- Material origin documentation
- Environmental impact measurement
- Worker training records
- Digital infrastructure

### Step 2: Invest in Technology
Modern DPP compliance requires:
- Digital tracking systems
- QR code generation capabilities
- Cloud-based data storage
- API integrations with buyer systems

### Step 3: Train Your Team
Every stakeholder needs training:
- Factory managers on system usage
- Compliance teams on data collection
- Workers on new processes
- IT staff on maintenance

### Step 4: Build Supplier Partnerships
Your DPP is only as good as your supply chain. Work with:
- Fabric suppliers for material certifications
- Dye houses for chemical documentation
- Trim suppliers for component tracking
- Logistics partners for transportation data

## The Competitive Advantage

While compliance is mandatory, forward-thinking manufacturers are using DPPs as a marketing tool:
- **Transparency builds trust** with premium buyers
- **Data insights** improve operational efficiency
- **Sustainability metrics** attract conscious consumers
- **Digital infrastructure** enables future innovations

## Common Challenges and Solutions

**Challenge**: Manual record-keeping is overwhelming
**Solution**: Automated data collection at production stages

**Challenge**: Suppliers don't provide required documentation
**Solution**: Partner only with compliant suppliers or help them upgrade

**Challenge**: Workers resist new digital processes
**Solution**: Comprehensive training and clear communication about benefits

## Timeline to Compliance

- **Month 1-2**: System assessment and vendor selection
- **Month 3-4**: Technology implementation and testing
- **Month 5-6**: Team training and process refinement
- **Month 7-8**: Pilot batch production and validation
- **Month 9-12**: Full implementation and optimization

## Conclusion

EU Digital Product Passports are not just a compliance requirement—they're an opportunity to modernize your operations and demonstrate leadership in sustainable manufacturing. Start your DPP journey today to ensure seamless EU market access tomorrow.

*Need help with DPP implementation? Contact our compliance experts for a personalized assessment.*""",
                "category_id": compliance_cat.id,
                "tags": ["EU DPP", "Compliance", "Digital Transformation", "Sustainability"],
                "reading_time": 8,
                "is_featured": True
            },
            {
                "title": "10 Sustainable Practices That Reduce Costs While Improving Compliance",
                "excerpt": "Sustainability and profitability aren't mutually exclusive. Discover proven practices that leading RMG manufacturers use to cut costs while exceeding environmental standards.",
                "content": """Sustainable manufacturing isn't just about meeting regulations—it's about building a more efficient, profitable, and resilient business. Here are ten practices that deliver both environmental and financial benefits.

## 1. Water Recycling Systems

**Impact**: Reduce water consumption by 40-60%
**Payback Period**: 18-24 months

Modern water treatment systems allow you to reuse water in multiple production stages:
- Washing processes
- Cooling systems
- Dyeing operations

**Case Study**: A Dhaka-based manufacturer reduced monthly water costs by $15,000 while improving compliance with local discharge regulations.

## 2. LED Lighting Upgrade

**Impact**: 60-70% reduction in lighting costs
**Payback Period**: 12-18 months

Simple but effective:
- Lower electricity bills
- Reduced heat generation
- Better working conditions
- Longer bulb life

## 3. Solar Panel Installation

**Impact**: 30-50% reduction in electricity costs
**Payback Period**: 3-5 years

With declining solar costs and rising electricity prices, rooftop solar is increasingly attractive:
- Government incentives available in many countries
- Reliable power during outages
- Marketing benefit for sustainability claims

## 4. Chemical Management Systems

**Impact**: 20-30% reduction in chemical costs
**Payback Period**: 6-12 months

Proper chemical management reduces waste:
- Accurate measurement systems
- Closed-loop processes
- Regular equipment maintenance
- Staff training on proper usage

## 5. Fabric Waste Optimization

**Impact**: 10-15% reduction in material costs
**Payback Period**: Immediate

Better cutting practices and waste management:
- Digital marker making
- Automated cutting systems
- Waste fabric recycling programs
- Upcycling partnerships

## 6. Energy Monitoring Systems

**Impact**: 15-25% reduction in energy costs
**Payback Period**: 12-18 months

Real-time monitoring identifies waste:
- Peak load management
- Equipment inefficiencies
- Unnecessary consumption
- Optimization opportunities

## 7. Preventive Maintenance

**Impact**: 25-35% reduction in equipment downtime
**Payback Period**: 3-6 months

Scheduled maintenance saves money:
- Fewer emergency repairs
- Longer equipment life
- Consistent production quality
- Better energy efficiency

## 8. Employee Training Programs

**Impact**: 20-30% reduction in quality issues
**Payback Period**: 6-12 months

Well-trained workers:
- Make fewer mistakes
- Waste less material
- Operate equipment more efficiently
- Suggest improvements

## 9. Compressed Air Management

**Impact**: 30-40% reduction in compressed air costs
**Payback Period**: 12-24 months

Often overlooked but significant:
- Fix air leaks
- Optimize pressure settings
- Improve piping systems
- Regular maintenance

## 10. Green Chemistry Alternatives

**Impact**: 15-25% reduction in chemical costs
**Payback Period**: 18-24 months

New eco-friendly chemicals often work better:
- Lower water temperatures required
- Shorter processing times
- Less water needed
- Safer for workers

## Measuring Success

Track these KPIs to measure impact:
- Cost savings per month
- Environmental metrics (water, energy, emissions)
- Compliance scores
- Worker satisfaction
- Buyer sustainability ratings

## Implementation Roadmap

**Phase 1 (Months 1-3)**: Quick wins
- LED lighting
- Water leak repairs
- Basic training

**Phase 2 (Months 4-9)**: Medium investments
- Energy monitoring
- Chemical management
- Preventive maintenance

**Phase 3 (Months 10-18)**: Major projects
- Water recycling
- Solar installation
- Process optimization

## Conclusion

Sustainable practices aren't a cost—they're an investment that pays dividends in reduced expenses, improved compliance, and enhanced reputation. Start with quick wins to build momentum and fund larger initiatives.

*Ready to start your sustainability journey? Our experts can help identify the highest-impact opportunities for your factory.*""",
                "category_id": sustainability_cat.id,
                "tags": ["Sustainability", "Cost Reduction", "Best Practices", "ROI"],
                "reading_time": 10,
                "is_featured": True
            },
            {
                "title": "Supply Chain Transparency: Why Buyers Are Demanding More Than Ever",
                "excerpt": "Major brands are requiring unprecedented visibility into their supply chains. Learn what information buyers need, how to collect it, and why transparency is becoming a non-negotiable requirement.",
                "content": """The days of opaque supply chains are over. Today's buyers—from fast fashion to luxury brands—demand complete visibility into how and where their products are made. Here's what you need to know.

## The Transparency Revolution

Recent legislation and consumer pressure have fundamentally changed buyer expectations:
- **German Supply Chain Act**: Requires due diligence on human rights and environmental standards
- **EU Corporate Sustainability Due Diligence Directive**: Mandates supply chain transparency
- **Uyghur Forced Labor Prevention Act**: Requires proof of ethical sourcing
- **Consumer Awareness**: 73% of consumers willing to pay more for transparent products

## What Buyers Are Asking For

Modern RFQs now include extensive supply chain questions:

### Tier 1 Information (Your Factory)
- Facility certifications
- Worker demographics and wages
- Environmental compliance data
- Energy and water usage
- Chemical management practices
- Grievance mechanisms

### Tier 2 Information (Your Suppliers)
- Fabric mill certifications
- Fiber origin documentation
- Dye house environmental data
- Trim supplier compliance
- Subcontractor relationships

### Tier 3+ Information (Raw Materials)
- Cotton farm locations
- Synthetic fiber production
- Chemical ingredient sourcing
- Recycled content verification

## Why Transparency Matters

Beyond compliance, transparency offers strategic advantages:

### Risk Management
- Early identification of supply chain vulnerabilities
- Faster response to disruptions
- Better quality control
- Reduced legal exposure

### Competitive Advantage
- Preferred supplier status
- Higher order values
- Long-term partnerships
- Marketing opportunities

### Operational Excellence
- Better supplier relationships
- Improved efficiency
- Data-driven decisions
- Continuous improvement culture

## Building a Transparent Supply Chain

### Step 1: Map Your Supply Chain
Create a complete map of all suppliers:
- Direct material suppliers
- Subcontractors
- Service providers
- Transportation partners

**Tool**: Supply chain mapping software or spreadsheets

### Step 2: Collect Baseline Data
Gather essential information from each supplier:
- Certifications and licenses
- Facility locations
- Worker information
- Environmental data
- Compliance records

**Tool**: Supplier questionnaires and audit reports

### Step 3: Implement Tracking Systems
Deploy technology for real-time visibility:
- Digital product passports
- Blockchain for traceability
- IoT sensors for environmental data
- Cloud-based documentation

**Tool**: Integrated supply chain platforms

### Step 4: Verify and Validate
Don't just collect data—verify it:
- Third-party audits
- Surprise inspections
- Worker interviews
- Cross-reference multiple sources

**Tool**: Audit management systems

### Step 5: Share Information
Make data accessible to buyers:
- Online portals
- API integrations
- Regular reports
- QR code access

**Tool**: Buyer collaboration platforms

## Common Objections and Responses

**"It's too expensive"**
Consider the cost of losing orders due to lack of transparency. Most systems pay for themselves within a year through increased orders and efficiency.

**"Our suppliers won't cooperate"**
Transparency is becoming industry standard. Suppliers who resist are liability risks. Help compliant suppliers upgrade or find new partners.

**"It reveals our competitive advantages"**
Buyers sign NDAs and only share necessary information. Your processes remain confidential while demonstrating compliance.

**"We don't have the technology"**
Start simple with spreadsheets and basic tracking. Upgrade systems as ROI becomes clear.

## Case Studies

### Case Study 1: Mid-Size Manufacturer
- **Challenge**: Losing orders to more transparent competitors
- **Solution**: Implemented digital tracking and supplier certification program
- **Result**: 30% increase in orders from premium buyers within 6 months

### Case Study 2: Large Factory Group
- **Challenge**: Buyer concerns about subcontractor compliance
- **Solution**: Created supplier transparency portal with real-time data
- **Result**: Became preferred supplier for major European brands

## The Future of Supply Chain Transparency

Expect requirements to increase:
- Real-time data sharing
- Worker voice platforms
- Blockchain verification
- AI-powered risk detection
- Integrated buyer systems

## Getting Started Checklist

- [ ] Map all Tier 1 suppliers
- [ ] Collect basic compliance documents
- [ ] Implement a supplier database
- [ ] Conduct baseline audits
- [ ] Create a data sharing portal
- [ ] Train team on new processes
- [ ] Communicate benefits to suppliers
- [ ] Set up buyer access systems

## Conclusion

Supply chain transparency is no longer optional—it's a business necessity. Manufacturers who embrace transparency will thrive; those who resist will lose market access. Start building your transparent supply chain today.

*Need help implementing transparency systems? Our supply chain experts can guide you through every step of the process.*""",
                "category_id": supply_chain_cat.id,
                "tags": ["Supply Chain", "Transparency", "Buyer Requirements", "Traceability"],
                "reading_time": 12,
                "is_featured": True
            }
        ]
        
        created_count = 0
        
        for article_data in articles_data:
            slug = slugify(article_data["title"])
            
            # Check if already exists
            existing = db.query(Article).filter(Article.slug == slug).first()
            if existing:
                print(f"⏭️  Article '{article_data['title'][:50]}...' already exists, skipping...")
                continue
            
            # Create new article
            article = Article(
                title=article_data["title"],
                slug=slug,
                excerpt=article_data["excerpt"],
                content=article_data["content"],
                author_id=admin_user.id,
                category_id=article_data["category_id"],
                status="published",
                published_at=datetime.utcnow(),
                language="en",
                tags=article_data["tags"],
                reading_time=article_data["reading_time"],
                is_featured=article_data.get("is_featured", False),
                views=0
            )
            db.add(article)
            created_count += 1
            print(f"✅ Created article: {article_data['title'][:60]}...")
        
        db.commit()
        print(f"\n🎉 Successfully created {created_count} articles!")
        print("\n📝 Articles are published and will appear on the homepage!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("📚 Seeding sample articles...\n")
    seed_articles()
