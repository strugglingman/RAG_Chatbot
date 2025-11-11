# Backend Refactored Structure

## Directory Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── app.py                  # Application factory
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration settings
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # Authentication middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoints
│   │   ├── upload.py           # Upload endpoints (TODO)
│   │   ├── ingest.py           # Ingest endpoints (TODO)
│   │   └── files.py            # File management endpoints (TODO)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vector_db.py        # ChromaDB wrapper
│   │   ├── document_processor.py # Document processing
│   │   ├── retrieval.py        # RAG retrieval logic (TODO)
│   │   └── prompt_builder.py   # Prompt construction (TODO)
│   └── utils/
│       ├── __init__.py
│       ├── sanitizer.py        # Input sanitization
│       ├── file_utils.py       # File handling utilities
│       └── helpers.py          # General helpers (TODO)
├── tests/
│   └── ...
├── app.py                      # Legacy entry point (keep for now)
├── safety.py                   # Safety checks
├── requirements.txt
└── README.md
```

## Module Descriptions

### Config (`src/config/`)
- **settings.py**: Centralized configuration management
  - Multiple environment configs (dev, test, prod)
  - All environment variables in one place
  - Type-safe configuration access

### Middleware (`src/middleware/`)
- **auth.py**: Authentication and authorization
  - JWT token validation
  - Identity loading
  - Route protection decorators

### Routes (`src/routes/`)
- **chat.py**: Chat-related endpoints
  - `/chat` - Chat with RAG
- **upload.py**: File upload endpoints (TODO)
- **ingest.py**: Document ingestion endpoints (TODO)
- **files.py**: File management endpoints (TODO)

### Services (`src/services/`)
- **vector_db.py**: ChromaDB wrapper
  - Embeddings management
  - Vector search operations
- **document_processor.py**: Document processing
  - Text extraction from PDF, DOCX, CSV, JSON
  - Chunking with overlap
  - Sentence splitting
- **retrieval.py**: RAG retrieval logic (TODO)
  - Semantic search
  - Hybrid search (BM25 + semantic)
  - Reranking
- **prompt_builder.py**: Prompt construction (TODO)
  - System prompt templates
  - Context formatting
  - Citation instructions

### Utils (`src/utils/`)
- **sanitizer.py**: Input sanitization
  - XSS prevention
  - Prompt injection detection
  - Text cleaning
- **file_utils.py**: File operations
  - File validation
  - Path handling
  - Directory management

## Migration Plan

### Phase 1: Core Infrastructure (DONE)
- ✅ Create directory structure
- ✅ Config module
- ✅ Middleware module
- ✅ Utility modules
- ✅ Service modules (partial)
- ✅ Route modules (partial)
- ✅ Application factory

### Phase 2: Complete Service Layer (TODO)
- [ ] Finish retrieval service
- [ ] Create prompt builder service
- [ ] Move BM25 logic to service
- [ ] Move reranking to service

### Phase 3: Complete Routes (TODO)
- [ ] Upload routes
- [ ] Ingest routes
- [ ] Files routes
- [ ] Org structure routes

### Phase 4: Testing (TODO)
- [ ] Update test imports
- [ ] Add unit tests for services
- [ ] Add integration tests

### Phase 5: Deployment (TODO)
- [ ] Update main entry point
- [ ] Update Docker configuration
- [ ] Update documentation

## Usage

### Running the New Structure (After Migration)

```python
from src.app import create_app

app, limiter = create_app('development')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### Configuration

Set environment with `FLASK_ENV`:
```bash
export FLASK_ENV=production  # or development, testing
```

### Benefits of New Structure

1. **Separation of Concerns**
   - Config separate from logic
   - Routes separate from business logic
   - Clear service boundaries

2. **Testability**
   - Services can be tested independently
   - Easy to mock dependencies
   - Clear interfaces

3. **Maintainability**
   - Easy to locate code
   - Clear responsibility for each module
   - Easier to onboard new developers

4. **Scalability**
   - Easy to add new endpoints
   - Services can be extracted to microservices
   - Clear dependency management

5. **Security**
   - Centralized sanitization
   - Consistent authentication
   - Clear security boundaries

## Next Steps

1. Complete the remaining service modules
2. Migrate remaining routes from `app.py`
3. Update tests to use new structure
4. Create new entry point file
5. Deprecate old `app.py`
