# Role Mapping Configuration
# Maps frontend role names to backend role names

ROLE_MAPPING = {
    # Frontend -> Backend
    "Factory Owner": "factory_admin",
    "Compliance Manager": "manager",
    "Buyer/Brand Representative": "buyer",
    "Consultant": "platform_admin",  # Consultants get platform admin access
    "Other": "buyer",  # Default to buyer for "Other"
    
    # Backend roles (keep for backward compatibility)
    "factory_admin": "factory_admin",
    "manager": "manager",
    "worker": "worker",
    "buyer": "buyer",
    "platform_admin": "platform_admin",
}

REVERSE_ROLE_MAPPING = {
    # Backend -> Frontend display
    "factory_admin": "Factory Owner",
    "manager": "Compliance Manager",
    "worker": "Worker",
    "buyer": "Buyer/Brand Representative",
    "platform_admin": "Consultant",
}

# Roles that can create/manage content
CONTENT_CREATOR_ROLES = ["factory_admin", "manager", "platform_admin"]

# Roles that can manage products
PRODUCT_MANAGER_ROLES = ["factory_admin", "manager", "platform_admin"]

# Roles that can manage compliance
COMPLIANCE_MANAGER_ROLES = ["factory_admin", "manager", "platform_admin"]

# Roles that require factory_id
FACTORY_ROLES = ["factory_admin", "manager", "worker"]

def normalize_role(role: str) -> str:
    """Convert any role format to backend format"""
    return ROLE_MAPPING.get(role, role)

def display_role(role: str) -> str:
    """Convert backend role to display name"""
    return REVERSE_ROLE_MAPPING.get(role, role)
