# SkillChain Role System Documentation

## Overview
SkillChain uses a simplified 4-role system designed for the textile supply chain. Each role has specific permissions based on their responsibilities.

## The 4 Roles

### 1. Factory Owner (Backend: `factory_admin`)
**Who should use this:** Factory owners, CEOs, Managing Directors

**Full Access To:**
- ✅ Create and manage products
- ✅ Generate Digital Product Passports (DPP)
- ✅ Record compliance events
- ✅ Manage workers and staff
- ✅ Upload educational content (articles & courses)
- ✅ View all factory data and analytics
- ✅ Generate QR codes for products
- ✅ Configure factory settings

**Dashboard:** `/dashboard/factory`

---

### 2. Compliance Manager (Backend: `manager`)
**Who should use this:** Compliance officers, Quality managers, Production managers

**Access To:**
- ✅ Create and manage products
- ✅ Generate Digital Product Passports (DPP)
- ✅ Record compliance events
- ✅ Upload educational content (articles & courses)
- ✅ View factory compliance data
- ✅ Generate QR codes for products
- ❌ Cannot manage workers
- ❌ Cannot change factory settings

**Dashboard:** `/dashboard/factory`

---

### 3. Buyer/Brand Representative (Backend: `buyer`)
**Who should use this:** Buyers, Brand representatives, Retailers, Auditors

**Access To:**
- ✅ View public product information
- ✅ Scan and verify QR codes
- ✅ Access DPP information
- ✅ Access learning content (articles & courses)
- ❌ Cannot create products
- ❌ Cannot record compliance events
- ❌ Cannot upload content

**Dashboard:** `/dashboard/buyer`

---

### 4. Consultant (Backend: `platform_admin`)
**Who should use this:** Platform administrators, System consultants, Training managers

**Full Platform Access:**
- ✅ All Factory Owner permissions
- ✅ Create content categories
- ✅ Manage all users across factories
- ✅ System administration
- ✅ Platform-wide analytics

**Dashboard:** `/dashboard/admin`

---

## Role Mapping

The system automatically translates user-friendly role names to backend role codes:

| Frontend Display | Backend Code | Factory Required |
|-----------------|--------------|------------------|
| Factory Owner | `factory_admin` | Yes |
| Compliance Manager | `manager` | Yes |
| Buyer/Brand Representative | `buyer` | No |
| Consultant | `platform_admin` | No |

---

## Permission Matrix

| Feature | Factory Owner | Compliance Manager | Buyer/Brand | Consultant |
|---------|--------------|-------------------|-------------|------------|
| Create Products & DPPs | ✅ | ✅ | ❌ | ✅ |
| Record Compliance Events | ✅ | ✅ | ❌ | ✅ |
| Upload Learning Content | ✅ | ✅ | ❌ | ✅ |
| Manage Workers | ✅ | ❌ | ❌ | ✅ |
| View Public DPPs | ✅ | ✅ | ✅ | ✅ |
| Scan QR Codes | ✅ | ✅ | ✅ | ✅ |
| Create Categories | ❌ | ❌ | ❌ | ✅ |
| System Administration | ❌ | ❌ | ❌ | ✅ |

---

## Registration Flow

1. **User visits `/register`**
2. **Selects role** (with clear descriptions and permissions)
3. **Fills form** (name, email, company, password)
4. **Account created instantly** (no approval needed)
5. **Redirect to login** (can login immediately)

### Role-Specific Requirements

**Factory Roles (Owner & Compliance Manager):**
- Must provide company name
- System creates factory automatically
- Gets assigned factory_id

**Non-Factory Roles (Buyer & Consultant):**
- Company name optional
- No factory_id assigned
- Immediate full access

---

## Technical Implementation

### Frontend Role Display
```tsx
// Registration form uses user-friendly names
<option value="Factory Owner">Factory Owner</option>
<option value="Compliance Manager">Compliance Manager</option>
<option value="Buyer/Brand Representative">Buyer/Brand</option>
<option value="Consultant">Consultant</option>
```

### Backend Role Storage
```python
# Automatically normalized in demo_requests.py
from app.core.roles import normalize_role

normalized_role = normalize_role(request.role_requested)
# "Factory Owner" → "factory_admin"
# "Compliance Manager" → "manager"
# etc.
```

### Role Checking in APIs
```python
# Content creation (articles/courses)
@router.post("/content/articles")
def create_article(
    current_user: User = Depends(require_role(["platform_admin", "factory_admin", "manager"]))
):
    # Only these 3 roles can create content
```

---

## API Endpoints

### Public Endpoints (No Auth)
- `POST /demo-request/submit` - Register account
- `POST /auth/login` - Login
- `GET /dpp/verify/{qr_code}` - Verify DPP by QR code

### Factory Owner/Manager Endpoints
- `POST /dpp/products` - Create product
- `POST /compliance/events` - Record compliance
- `POST /content/articles` - Create article
- `POST /content/courses` - Create course

### Buyer Endpoints
- `GET /dpp/products` - View products
- `GET /learn/articles` - View articles
- `GET /learn/courses` - View courses

### Platform Admin Only
- `POST /content/categories` - Create categories
- `GET /demo-request/list` - View all registrations
- System administration endpoints

---

## User Journey Examples

### Example 1: Factory Owner
```
1. Register as "Factory Owner"
2. Login with credentials
3. Navigate to /dashboard/factory
4. Create products at /products/create
5. Generate DPPs with QR codes
6. Record compliance events
7. Upload training articles
```

### Example 2: Compliance Manager
```
1. Register as "Compliance Manager"
2. Login with credentials
3. Navigate to /dashboard/factory
4. Create products and DPPs
5. Record compliance events
6. Upload training content
7. View analytics (no worker management)
```

### Example 3: Buyer
```
1. Register as "Buyer/Brand Representative"
2. Login with credentials
3. Navigate to /dashboard/buyer
4. View products list
5. Scan QR codes to verify DPPs
6. Access learning content
```

### Example 4: Consultant
```
1. Register as "Consultant"
2. Login with credentials
3. Navigate to /dashboard/admin
4. Full platform access
5. Create content categories
6. Manage content across all factories
7. System administration
```

---

## Security Notes

1. **Role Validation:** All API endpoints validate roles on every request
2. **Factory Isolation:** Factory users can only see their own factory data
3. **Ownership Rules:** Users can only edit their own content (except platform_admin)
4. **Public Data:** Only approved DPPs are publicly accessible via QR codes
5. **Password Security:** Minimum 8 characters, bcrypt hashing

---

## Common Questions

**Q: Can I change my role after registration?**
A: Contact platform administrator. Role changes require admin action.

**Q: Do I need approval after registration?**
A: No, accounts are activated immediately. You can login right away.

**Q: Can Compliance Managers add workers?**
A: No, only Factory Owners can manage workers.

**Q: Can Buyers create products?**
A: No, Buyers can only view and verify products.

**Q: Who can upload learning content?**
A: Factory Owners, Compliance Managers, and Consultants.

**Q: What's the difference between Consultant and Factory Owner?**
A: Consultants have platform-wide access. Factory Owners are limited to their factory.

---

## Support

For technical support or role-related questions:
- Email: support@skillchain.com
- Documentation: https://docs.skillchain.com
- Visit: `/roles` for detailed permission comparison
