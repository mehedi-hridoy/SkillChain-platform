#!/bin/bash

# Test DPP creation
echo "Getting token..."
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@newtestco.com", "password": "secure123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

echo "Token: ${TOKEN:0:20}..."

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  exit 1
fi

echo -e "\nCreating product..."
curl -X POST http://localhost:8000/dpp/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "sku": "TEST-'$(date +%s)'",
    "name": "Test Product",
    "description": "Test Description",
    "category": "T-Shirt",
    "materials": [{"material": "Cotton", "percentage": 100, "origin": "India", "certification": "GOTS"}],
    "origin_country": "Bangladesh",
    "raw_material_source": "Shahbag",
    "carbon_footprint_kg": 3,
    "water_usage_liters": 3434,
    "recycled_content_percentage": 22,
    "certifications": ["dadf"],
    "manufactured_date": "2025-12-26"
  }'
