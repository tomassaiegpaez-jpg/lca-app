# LCA Assistant - API Reference

Complete API documentation for the LCA Assistant backend.

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Health & Status](#health--status)
5. [Database Endpoints](#database-endpoints)
6. [Conversational LCA](#conversational-lca)
7. [Direct Calculation](#direct-calculation)
8. [Goal & Scope Management](#goal--scope-management)
9. [Knowledge Base Access](#knowledge-base-access)
10. [Legacy Analysis](#legacy-analysis)
11. [Error Handling](#error-handling)
12. [Rate Limits](#rate-limits)

## Overview

The LCA Assistant API is built with FastAPI and provides RESTful endpoints for:

- Life Cycle Impact Assessment (LCIA) calculations
- Multi-database LCA process search
- AI-powered conversational interface
- Goal & Scope management
- Knowledge base access for methods and databases

**API Version**: 0.2.0
**Base Technology**: FastAPI + OpenLCA IPC
**AI Provider**: Anthropic Claude API

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your production URL.

## Authentication

**Current Status**: No authentication required (development mode)

**Planned**: API key authentication for production deployments
```http
Authorization: Bearer YOUR_API_KEY
```

## Health & Status

### GET /

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "LCA API is running",
  "version": "0.2.0"
}
```

**Status Codes:**
- `200 OK` - Service is running

**Example:**
```bash
curl http://localhost:8000/
```

## Database Endpoints

### GET /api/databases

List all configured databases with availability status.

**Query Parameters:**
None

**Response:**
```json
{
  "databases": [
    {
      "id": "elcd",
      "name": "ELCD 3.2",
      "description": "European Life Cycle Database",
      "port": 8080,
      "host": "172.26.192.1",
      "available": true,
      "capabilities": {
        "has_product_systems": true,
        "has_lcia_methods": true,
        "regions": ["EU"]
      }
    },
    {
      "id": "agribalyse",
      "name": "Agribalyse 3.1",
      "description": "French food and agriculture database",
      "port": 8081,
      "host": "172.26.192.1",
      "available": false,
      "capabilities": {
        "has_product_systems": true,
        "has_lcia_methods": true,
        "regions": ["FR", "Global"]
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:8000/api/databases
```

---

### GET /api/databases/{database_id}/processes

List all processes in a specific database.

**Path Parameters:**
- `database_id` (string, required) - Database identifier (e.g., "elcd", "agribalyse")

**Query Parameters:**
- `limit` (integer, optional) - Maximum number of results (default: 100)

**Response:**
```json
{
  "database_id": "elcd",
  "count": 3841,
  "processes": [
    {
      "id": "abc-123-def",
      "name": "Glass fiber mat production",
      "category": "Materials/Glass",
      "location": "RER"
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Database not found or unavailable
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl "http://localhost:8000/api/databases/elcd/processes?limit=10"
```

---

### POST /api/databases/{database_id}/processes/search

Search for processes in a specific database.

**Path Parameters:**
- `database_id` (string, required) - Database identifier

**Request Body:**
```json
{
  "query": "glass fiber",
  "limit": 10
}
```

**Response:**
```json
{
  "database_id": "elcd",
  "query": "glass fiber",
  "count": 8,
  "results": [
    {
      "id": "abc-123-def",
      "name": "Glass fiber mat production",
      "category": "Materials/Glass",
      "location": "RER",
      "description": "Production of glass fiber reinforcement materials"
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success (may return empty results)
- `400 Bad Request` - Invalid request body
- `404 Not Found` - Database not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/databases/elcd/processes/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "glass fiber", "limit": 10}'
```

---

### GET /api/databases/{database_id}/product-systems

List all product systems in a specific database.

**Path Parameters:**
- `database_id` (string, required) - Database identifier

**Query Parameters:**
- `limit` (integer, optional) - Maximum number of results (default: 100)

**Response:**
```json
{
  "database_id": "elcd",
  "count": 156,
  "product_systems": [
    {
      "id": "xyz-789-uvw",
      "name": "Portland cement, at plant",
      "category": "Materials/Cement",
      "target_process": "Portland cement production",
      "target_amount": 1.0,
      "target_unit": "kg"
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Database not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl "http://localhost:8000/api/databases/elcd/product-systems?limit=20"
```

---

### POST /api/databases/{database_id}/product-systems/search

Search for product systems in a specific database.

**Path Parameters:**
- `database_id` (string, required) - Database identifier

**Request Body:**
```json
{
  "query": "cement",
  "limit": 10
}
```

**Response:**
```json
{
  "database_id": "elcd",
  "query": "cement",
  "count": 5,
  "results": [
    {
      "id": "xyz-789-uvw",
      "name": "Portland cement, at plant",
      "category": "Materials/Cement",
      "description": "Complete supply chain for Portland cement production"
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request body
- `404 Not Found` - Database not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/databases/elcd/product-systems/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "cement", "limit": 10}'
```

---

### GET /api/databases/{database_id}/impact-methods

Get available LCIA methods for a specific database.

**Path Parameters:**
- `database_id` (string, required) - Database identifier

**Response:**
```json
{
  "database_id": "elcd",
  "methods": [
    {
      "id": "method-id-1",
      "name": "ReCiPe 2016 Midpoint (H)",
      "description": "Hierarchist version of ReCiPe 2016",
      "impact_categories": [
        "Climate change",
        "Ozone depletion",
        "Terrestrial acidification",
        ...
      ]
    },
    {
      "id": "method-id-2",
      "name": "ILCD 2011 Midpoint",
      "description": "EU Joint Research Centre methodology",
      "impact_categories": [...]
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Database not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl "http://localhost:8000/api/databases/elcd/impact-methods"
```

## Conversational LCA

### POST /api/lca/chat

Main conversational interface with AI-powered workflow execution.

**Features:**
- Multi-turn conversation loop (max 5 iterations)
- Automatic fallback (product systems → processes)
- Hallucination prevention
- Auto/Interactive mode support
- Knowledge-based guidance

**Request Body:**
```json
{
  "message": "Calculate the environmental impact of 2kg of glass fiber",
  "conversation_id": "optional-conv-id",
  "database_id": "elcd",
  "method_id": "optional-method-id",
  "method_selection_mode": "auto",
  "mode": "auto"
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | Yes | - | User's natural language query |
| `conversation_id` | string | No | auto-generated | Conversation session ID |
| `database_id` | string | No | "elcd" | Database to use for searches |
| `method_id` | string | No | null | Specific LCIA method (if manual mode) |
| `method_selection_mode` | string | No | "auto" | "auto" or "manual" |
| `mode` | string | No | "auto" | "auto" or "interactive" |

**Response:**
```json
{
  "conversation_id": "conv-abc-123",
  "message": "Here are the LCIA results for 2 kg of glass fiber mat production (Europe), using ReCiPe 2016:\n\nClimate change: 4.2 kg CO2 eq\nOzone depletion: 3.8e-07 kg CFC-11 eq\n...",
  "action": {
    "type": "calculate_lcia",
    "process_id": "abc-123-def",
    "process_name": "Glass fiber mat production",
    "amount": 2.0,
    "unit": "kg",
    "method_id": "recipe-2016",
    "method_name": "ReCiPe 2016 Midpoint (H)",
    "results": {
      "calculation_id": "calc-xyz-789",
      "goal_scope": {
        "goal": "Assess the environmental impact of 2 kg of glass fiber mat production",
        "functional_unit": "2.0 kg of glass fiber mat",
        "system_boundary": "Cradle-to-gate",
        "lcia_methodology": "ReCiPe 2016 Midpoint (H)",
        ...
      },
      "impacts": [
        {
          "category": "Climate change",
          "value": 4.2,
          "unit": "kg CO2 eq"
        },
        ...
      ],
      "product_system": {
        "id": "ps-created-id",
        "name": "Product system for glass fiber mat",
        "target_process": "Glass fiber mat production",
        "created": true
      },
      "metadata": {
        "database": "ELCD 3.2",
        "process_location": "RER",
        "calculation_type": "LCI result",
        "timestamp": "2025-11-02T14:30:00Z"
      }
    }
  },
  "context": {
    "database_id": "elcd",
    "method_id": "recipe-2016",
    "mode": "auto",
    "method_selection_mode": "auto"
  }
}
```

**Action Types:**

Response may include different action types:

1. **search_processes** - Process search results
```json
{
  "type": "search_processes",
  "query": "glass fiber",
  "count": 8,
  "results": [...]
}
```

2. **search_product_systems** - Product system search results
```json
{
  "type": "search_product_systems",
  "query": "cement",
  "count": 5,
  "results": [...]
}
```

3. **calculate_lcia** - LCIA calculation results (shown above)

4. **calculate_lcia_ps** - Product system LCIA results (similar to calculate_lcia)

5. **search_failed** - Honest error after empty searches
```json
{
  "type": "search_failed",
  "query": "unicorn horn",
  "attempts": 2,
  "suggestions": [
    "Try a different search term",
    "Switch to Agribalyse for food products",
    "Switch to NEEDS for energy systems"
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request body or parameters
- `404 Not Found` - Conversation or database not found
- `500 Internal Server Error` - Server or OpenLCA error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/lca/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate impact of 2kg glass fiber",
    "database_id": "elcd",
    "mode": "auto"
  }'
```

**Multi-Turn Behavior:**

The endpoint executes up to 5 AI actions automatically:

```
Turn 1: Search product systems for "glass fiber"
        → 0 results

Turn 2: Fallback search processes for "glass fiber"
        → 8 results found

Turn 3: Select best match (in auto mode)
        → "Glass fiber mat production" selected

Turn 4: Calculate LCIA for 2kg
        → Results obtained

Turn 5: Format final response
        → Complete
```

All turns execute within a single API call, returning the final result.

## Direct Calculation

### POST /api/lca/calculate_lcia

Calculate LCIA for a specific process (creates product system automatically).

**Request Body:**
```json
{
  "process_id": "abc-123-def",
  "amount": 2.0,
  "method_id": "recipe-2016",
  "database_id": "elcd",
  "goal_scope": {
    "goal": "Optional custom goal",
    "assumptions": ["Custom assumption 1"]
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `process_id` | string | Yes | Process UUID |
| `amount` | number | Yes | Functional unit amount |
| `method_id` | string | Yes | LCIA method UUID |
| `database_id` | string | No | Database ID (default: "elcd") |
| `goal_scope` | object | No | Custom Goal & Scope fields |

**Response:**
```json
{
  "calculation_id": "calc-xyz-789",
  "goal_scope": {
    "goal": "Assess environmental impact of 2.0 kg of glass fiber mat",
    "functional_unit": "2.0 kg of glass fiber mat",
    ...
  },
  "impacts": [
    {
      "category": "Climate change",
      "value": 4.2,
      "unit": "kg CO2 eq"
    },
    ...
  ],
  "product_system": {
    "id": "ps-auto-created",
    "name": "Product system for glass fiber mat",
    "created": true
  },
  "metadata": {
    "database": "ELCD 3.2",
    "process_name": "Glass fiber mat production",
    "process_location": "RER",
    "method": "ReCiPe 2016 Midpoint (H)",
    "timestamp": "2025-11-02T14:45:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Calculation successful
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Process or method not found
- `500 Internal Server Error` - Calculation error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/lca/calculate_lcia" \
  -H "Content-Type: application/json" \
  -d '{
    "process_id": "abc-123-def",
    "amount": 2.0,
    "method_id": "recipe-2016",
    "database_id": "elcd"
  }'
```

---

### POST /api/lca/calculate_lcia_ps

Calculate LCIA for an existing product system.

**Request Body:**
```json
{
  "product_system_id": "ps-xyz-789",
  "amount": 1.0,
  "method_id": "recipe-2016",
  "database_id": "elcd",
  "goal_scope": {
    "goal": "Optional custom goal"
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_system_id` | string | Yes | Product system UUID |
| `amount` | number | Yes | Functional unit amount (multiplier) |
| `method_id` | string | Yes | LCIA method UUID |
| `database_id` | string | No | Database ID |
| `goal_scope` | object | No | Custom Goal & Scope fields |

**Response:**
```json
{
  "calculation_id": "calc-abc-456",
  "goal_scope": {...},
  "impacts": [...],
  "product_system": {
    "id": "ps-xyz-789",
    "name": "Portland cement, at plant",
    "created": false
  },
  "metadata": {...}
}
```

**Status Codes:**
- `200 OK` - Calculation successful
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Product system or method not found
- `500 Internal Server Error` - Calculation error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/lca/calculate_lcia_ps" \
  -H "Content-Type: application/json" \
  -d '{
    "product_system_id": "ps-xyz-789",
    "amount": 5.0,
    "method_id": "recipe-2016",
    "database_id": "elcd"
  }'
```

## Goal & Scope Management

### POST /api/goal-scope

Create or update manual Goal & Scope definition.

**Request Body:**
```json
{
  "study_id": "optional-study-id",
  "goal": "Assess environmental impact of product X for marketing claims",
  "functional_unit": "1 unit of product X",
  "system_boundary": "Cradle-to-grave including end-of-life",
  "lcia_methodology": "ReCiPe 2016 Midpoint (H)",
  "intended_audience": "Marketing team and external stakeholders",
  "assumptions": [
    "Average European electricity mix",
    "Transportation distance of 500 km"
  ],
  "limitations": [
    "Excludes capital goods",
    "Uses proxy data for packaging"
  ],
  "other_fields": {}
}
```

**Response:**
```json
{
  "study_id": "study-abc-123",
  "goal_scope": {
    "goal": "Assess environmental impact...",
    "functional_unit": "1 unit of product X",
    ...
  },
  "created_at": "2025-11-02T15:00:00Z"
}
```

**Status Codes:**
- `201 Created` - New Goal & Scope created
- `200 OK` - Existing Goal & Scope updated
- `400 Bad Request` - Invalid request body

**Example:**
```bash
curl -X POST "http://localhost:8000/api/goal-scope" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Assess product X environmental impact",
    "functional_unit": "1 unit of product X"
  }'
```

---

### GET /api/goal-scope/{study_id}

Retrieve Goal & Scope for a specific study.

**Path Parameters:**
- `study_id` (string, required) - Study identifier

**Response:**
```json
{
  "study_id": "study-abc-123",
  "goal_scope": {
    "goal": "Assess environmental impact...",
    ...
  },
  "created_at": "2025-11-02T15:00:00Z",
  "last_updated": "2025-11-02T15:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Study not found

**Example:**
```bash
curl "http://localhost:8000/api/goal-scope/study-abc-123"
```

---

### PUT /api/goal-scope/{study_id}

Update existing Goal & Scope.

**Path Parameters:**
- `study_id` (string, required) - Study identifier

**Request Body:**
```json
{
  "goal": "Updated goal statement",
  "assumptions": ["Updated assumption"]
}
```

**Response:**
```json
{
  "study_id": "study-abc-123",
  "goal_scope": {
    "goal": "Updated goal statement",
    ...
  },
  "last_updated": "2025-11-02T16:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Updated successfully
- `404 Not Found` - Study not found
- `400 Bad Request` - Invalid request body

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/goal-scope/study-abc-123" \
  -H "Content-Type: application/json" \
  -d '{"goal": "Updated goal"}'
```

## Knowledge Base Access

### GET /api/methods/knowledge

Get expert knowledge about all LCIA methods.

**Query Parameters:**
None

**Response:**
```json
{
  "methods": {
    "recipe_2016": {
      "name": "ReCiPe 2016 Midpoint (H)",
      "description": "Comprehensive hierarchist impact assessment method",
      "pros": [
        "Covers 18 impact categories",
        "Global applicability",
        "Well-documented methodology"
      ],
      "cons": [
        "Complex for beginners",
        "Requires careful interpretation"
      ],
      "best_for": [
        "Comprehensive product LCA",
        "Academic research",
        "Comparative studies"
      ],
      "geographic_scope": "Global",
      "impact_categories": 18,
      "references": [
        "Huijbregts et al. 2017"
      ]
    },
    ...
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Error loading knowledge base

**Example:**
```bash
curl "http://localhost:8000/api/methods/knowledge"
```

---

### GET /api/methods/recommend

Get AI-powered method recommendation.

**Query Parameters:**
- `database_id` (string, required) - Current database
- `query` (string, optional) - User query for context
- `region` (string, optional) - Geographic region (e.g., "US", "EU")

**Response:**
```json
{
  "recommended_method": {
    "id": "recipe-2016",
    "name": "ReCiPe 2016 Midpoint (H)",
    "reason": "Comprehensive method with global applicability, well-suited for ELCD database and European context"
  },
  "alternatives": [
    {
      "id": "ilcd-2011",
      "name": "ILCD 2011 Midpoint",
      "reason": "EU-specific method, good for policy studies"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Missing required parameters

**Example:**
```bash
curl "http://localhost:8000/api/methods/recommend?database_id=elcd&query=cement+production&region=EU"
```

## Legacy Analysis

### POST /api/analyze/process/{id}

AI analysis of a single process (legacy endpoint).

**Path Parameters:**
- `id` (string, required) - Process UUID

**Query Parameters:**
- `database_id` (string, optional) - Database ID (default: "elcd")

**Response:**
```json
{
  "process_id": "abc-123-def",
  "process_name": "Glass fiber mat production",
  "analysis": "This process represents glass fiber mat production in Europe (RER). It includes...",
  "key_inputs": [
    "Silica sand",
    "Energy (electricity)",
    "Natural gas"
  ],
  "key_outputs": [
    "Glass fiber mat (1 kg)"
  ],
  "environmental_hotspots": [
    "Energy consumption during melting",
    "Natural gas combustion emissions"
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Process not found

**Note**: Consider using `/api/lca/chat` for more comprehensive analysis.

---

### POST /api/analyze/compare

Compare multiple processes (legacy endpoint).

**Request Body:**
```json
{
  "process_ids": ["id-1", "id-2"],
  "database_id": "elcd"
}
```

**Response:**
```json
{
  "comparison": "Process 1 (glass fiber) has higher energy consumption than Process 2 (carbon fiber) but lower...",
  "processes": [
    {
      "id": "id-1",
      "name": "Glass fiber mat"
    },
    {
      "id": "id-2",
      "name": "Carbon fiber"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request (e.g., < 2 processes)
- `404 Not Found` - One or more processes not found

**Note**: Consider using `/api/lca/chat` with comparison queries for richer analysis.

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "OPTIONAL_ERROR_CODE",
  "timestamp": "2025-11-02T16:30:00Z"
}
```

### Common Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| `400 Bad Request` | Invalid request parameters | Missing required fields, invalid JSON, wrong types |
| `404 Not Found` | Resource not found | Invalid IDs, database offline, process doesn't exist |
| `422 Unprocessable Entity` | Validation error | FastAPI request validation failed |
| `500 Internal Server Error` | Server error | OpenLCA connection issues, calculation errors, AI API errors |

### Example Error Responses

**Database Not Available:**
```json
{
  "detail": "Database 'agribalyse' is not available. Please check that OpenLCA IPC server is running on port 8081.",
  "error_code": "DATABASE_UNAVAILABLE"
}
```

**Process Not Found:**
```json
{
  "detail": "Process with ID 'invalid-id' not found in database 'elcd'",
  "error_code": "PROCESS_NOT_FOUND"
}
```

**Calculation Error:**
```json
{
  "detail": "LCIA calculation failed: Product system could not be created. Check that the process has a valid quantitative reference.",
  "error_code": "CALCULATION_FAILED"
}
```

**AI API Error:**
```json
{
  "detail": "Claude API error: Rate limit exceeded. Please try again in 60 seconds.",
  "error_code": "AI_API_ERROR"
}
```

## Rate Limits

**Current**: No rate limits (development mode)

**Planned** for production:
- **Chat Endpoint**: 60 requests/minute per IP
- **Calculation Endpoints**: 30 requests/minute per IP
- **Search Endpoints**: 120 requests/minute per IP
- **Other Endpoints**: 300 requests/minute per IP

Rate limit headers (planned):
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699123456
```

## OpenAPI Specification

Full OpenAPI specification available at:
```
http://localhost:8000/docs
```

Interactive API documentation (Swagger UI):
```
http://localhost:8000/docs
```

ReDoc documentation:
```
http://localhost:8000/redoc
```

## SDK / Client Libraries

**Python Client** (coming soon):
```python
from lca_assistant import LCAClient

client = LCAClient(base_url="http://localhost:8000")

# Chat interface
response = client.chat(
    message="Calculate impact of 2kg glass fiber",
    database_id="elcd",
    mode="auto"
)

# Direct calculation
results = client.calculate_lcia(
    process_id="abc-123",
    amount=2.0,
    method_id="recipe-2016"
)
```

**JavaScript Client** (coming soon):
```javascript
import { LCAClient } from 'lca-assistant-js';

const client = new LCAClient({ baseURL: 'http://localhost:8000' });

// Chat interface
const response = await client.chat({
  message: 'Calculate impact of 2kg glass fiber',
  databaseId: 'elcd',
  mode: 'auto'
});
```

## Webhooks

**Status**: Not yet implemented

**Planned**: Webhooks for long-running calculations
- Register webhook URL
- Receive notifications when calculations complete
- Useful for batch processing

## Changelog

### v0.2.0 (November 2025)
- Added multi-database support
- Added multi-turn conversation loop
- Added hallucination prevention
- Added auto/interactive modes
- Added knowledge base endpoints

### v0.1.0 (October 2025)
- Initial API release
- Basic LCIA calculations
- Single database (ELCD)
- Simple chat interface

## Support

For API issues or questions:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [FEATURES.md](FEATURES.md) for feature details
3. Open an issue on GitHub with:
   - API endpoint called
   - Request body (sanitize sensitive data)
   - Response received
   - Expected behavior

## External References

- **OpenLCA IPC API**: https://greendelta.github.io/openLCA-ApiDoc/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Anthropic API**: https://docs.anthropic.com/

---

**Last Updated**: November 2, 2025
**API Version**: 0.2.0
