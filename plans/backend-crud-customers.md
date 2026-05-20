Source: issue 12
Notion page: 3659ebdf202a80cc8cd6df183422d4a6

# Backend CRUD API for Customers (In-Memory)

## Summary

Add 5 REST endpoints for customer management with an in-memory store, update CORS, and write a full pytest suite.

## Architecture Decisions

- **Store**: Module-level `customers: dict[str, dict]` in `backend/app/main.py`
- **IDs**: `uuid.uuid4()` (str) auto-generated on create
- **Schema**: id (str), name (str, required), email (str, required), phone (str|None), company (str|None), address (str|None)
- **No Pydantic models**: Return plain `dict[str, str | None]` consistent with existing style
- **CORS**: Expand `allow_methods` to `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`
- **Test isolation**: pytest fixture clears `app.main.customers` before each test

## Routes

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | /api/customers | 200 | List all customers |
| POST | /api/customers | 201 | Create a customer |
| GET | /api/customers/{id} | 200/404 | Get one customer |
| PUT | /api/customers/{id} | 200/404 | Update a customer |
| DELETE | /api/customers/{id} | 204/404 | Delete a customer |

## Tracer-Bullet Phases (TDD order)

### Phase 1: GET /api/customers returns empty list
- Red: test_list_customers_initially_empty
- Green: add in-memory store + list endpoint

### Phase 2: POST /api/customers creates a customer
- Red: test_create_customer_returns_201
- Green: add create endpoint with UUID

### Phase 3: GET /api/customers/{id}
- Red: test_get_customer_returns_200 + test_get_customer_unknown_returns_404
- Green: add get-by-id endpoint

### Phase 4: PUT /api/customers/{id}
- Red: test_update_customer_returns_200 + test_update_customer_unknown_returns_404
- Green: add update endpoint

### Phase 5: DELETE /api/customers/{id}
- Red: test_delete_customer_returns_204 + test_delete_customer_unknown_returns_404
- Green: add delete endpoint

### Phase 6: CORS
- Red: test_cors_allows_post_method (options preflight)
- Green: update allow_methods in CORSMiddleware

### Phase 7: Refactor
- Review for duplication, clarify docstrings, ensure consistency
