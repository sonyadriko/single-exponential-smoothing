## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management
1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Idempotency & Concurrency

### Idempotency Key Pattern
**ALWAYS use idempotency keys for POST/PUT/DELETE operations** to prevent duplicate processing:

```python
from fastapi import Header, HTTPException
import hashlib
from datetime import datetime, timedelta

@router.post("/bookings")
async def create_booking(
    booking: BookingRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    _: bool = Depends(verify_api_token)
):
    """Create booking with idempotency protection."""
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")

    # Check if this key was already processed
    cached_result = await redis_client.get(f"idempotency:{idempotency_key}")
    if cached_result:
        return json.loads(cached_result)  # Return cached result

    # Process booking
    result = await process_booking(booking)

    # Cache result for 5 minutes
    await redis_client.setex(
        f"idempotency:{idempotency_key}",
        300,
        json.dumps(result)
    )

    return result
```

### Optimistic Locking
**ALWAYS use version-based optimistic locking** for concurrent updates:

```python
@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: int,
    update_data: ScheduleUpdate,
    _: bool = Depends(verify_api_token)
):
    """Update schedule with optimistic locking."""
    with get_db_cursor() as (cursor, conn):
        # Get current version
        cursor.execute(
            "SELECT id, status, version FROM schedules WHERE id = %s",
            (schedule_id,)
        )
        schedule = cursor.fetchone()

        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Update with version check
        cursor.execute(
            """UPDATE schedules
               SET status = %s, version = version + 1, updated_at = NOW()
               WHERE id = %s AND version = %s""",
            (update_data.status, schedule_id, schedule['version'])
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=409,
                detail="Schedule was modified by another user. Please refresh and try again."
            )

        conn.commit()
```

### Database Transactions
**ALWAYS wrap multi-step operations in transactions**:

```python
@router.post("/treatment-booking")
async def create_treatment_booking(booking: TreatmentBookingRequest):
    """Create booking with proper transaction handling."""
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Start transaction
        cursor.execute("START TRANSACTION")

        # Step 1: Check availability
        cursor.execute(
            "SELECT status FROM schedules WHERE id = %s FOR UPDATE",
            (booking.schedule_id,)
        )
        schedule = cursor.fetchone()

        if not schedule or schedule['status'] != 'available':
            raise HTTPException(status_code=409, detail="Slot no longer available")

        # Step 2: Create booking
        cursor.execute(
            "INSERT INTO bookings (...) VALUES (...)",
            (booking.user_id, booking.schedule_id, ...)
        )

        # Step 3: Update schedule status
        cursor.execute(
            "UPDATE schedules SET status = 'booked' WHERE id = %s",
            (booking.schedule_id,)
        )

        # Commit transaction
        conn.commit()

        return {"status": "success", "booking_id": cursor.lastrowid}

    except Exception as e:
        # Rollback on error
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Always cleanup
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

### Race Condition Prevention
**ALWAYS use row-level locking for critical operations**:

```python
# WRONG: Race condition vulnerable
cursor.execute("SELECT * FROM schedules WHERE id = %s", (schedule_id,))
schedule = cursor.fetchone()
# ... validation ...
cursor.execute("UPDATE schedules SET status = 'booked' WHERE id = %s", (schedule_id,))

# CORRECT: Row-level locking
cursor.execute("SELECT * FROM schedules WHERE id = %s FOR UPDATE", (schedule_id,))
schedule = cursor.fetchone()
# ... validation ...
cursor.execute("UPDATE schedules SET status = 'booked' WHERE id = %s", (schedule_id,))
```

## Edge Case Handling

### Null Safety Pattern
**ALWAYS handle None/null values explicitly**:

```python
# WRONG: Assumption-heavy
customer_name = customer['name']  # Fails if customer is None

# CORRECT: Explicit null handling
customer_name = customer['name'] if customer else None

# OR: Use coalesce in SQL
cursor.execute("""
    SELECT COALESCE(u.name, 'Unknown') as name,
           COALESCE(c.phone, '') as phone
    FROM customers c
    LEFT JOIN users u ON u.id = c.user_id
""")
```

### Boundary Condition Validation
**ALWAYS validate input boundaries**:

```python
@router.post("/bookings")
async def create_booking(booking: BookingRequest):
    """Create booking with comprehensive validation."""

    # Date boundary checks
    if booking.date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book in the past")

    if booking.date > date.today() + timedelta(days=30):
        raise HTTPException(status_code=400, detail="Cannot book more than 30 days ahead")

    # Time boundary checks
    if booking.start_time < "09:00" or booking.start_time > "20:00":
        raise HTTPException(status_code=400, detail="Booking hours are 09:00-20:00")

    # Capacity boundary checks
    cursor.execute(
        "SELECT COUNT(*) as count FROM bookings WHERE date = %s AND hour = %s",
        (booking.date, booking.hour)
    )
    count = cursor.fetchone()['count']
    if count >= MAX_BOOKINGS_PER_HOUR:
        raise HTTPException(status_code=409, detail="Slot fully booked")
```

### External API Resilience
**ALWAYS handle external API failures gracefully**:

```python
async def fetch_with_fallback(url: str, params: dict, timeout: float = 5.0):
    """Fetch from external API with fallback handling."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        logger.warning(f"External API timeout: {url}")
        # Return empty result or cached data
        return {}

    except httpx.HTTPStatusError as e:
        logger.error(f"External API error {e.response.status_code}: {url}")
        # Fallback to local data
        return await get_local_fallback_data(params)

    except Exception as e:
        logger.exception(f"Unexpected error fetching from {url}")
        return {}
```

### Graceful Degradation
**ALWAYS design for partial failure**:

```python
@router.get("/dashboard")
async def get_dashboard():
    """Get dashboard with graceful degradation."""
    data = {
        'bookings': [],
        'revenue': None,
        'staff_performance': None
    }

    # Try to fetch bookings (critical)
    try:
        data['bookings'] = await fetch_today_bookings()
    except Exception as e:
        logger.error(f"Failed to fetch bookings: {e}")
        data['bookings'] = []  # Empty but valid

    # Try to fetch revenue (nice-to-have)
    try:
        data['revenue'] = await fetch_today_revenue()
    except Exception as e:
        logger.warning(f"Failed to fetch revenue: {e}")
        data['revenue'] = None  # Accept None

    # Try to fetch performance (nice-to-have)
    try:
        data['staff_performance'] = await fetch_staff_performance()
    except Exception as e:
        logger.warning(f"Failed to fetch performance: {e}")
        data['staff_performance'] = None

    return data
```

## Transaction Management Patterns

### Transaction Wrapping
**USE context managers for automatic cleanup**:

```python
from contextlib import contextmanager

@contextmanager
def db_transaction():
    """Context manager for database transactions."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("START TRANSACTION")
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

# Usage
with db_transaction() as cursor:
    cursor.execute("INSERT INTO bookings ...")
    cursor.execute("UPDATE schedules SET status = 'booked' ...")
    # Auto commit on success, rollback on error
```

### Isolation Levels
**CHOOSE appropriate isolation level for your use case**:

```python
# READ COMMITTED (default, good for most cases)
cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")

# REPEATABLE READ (prevents phantom reads, use for reports)
cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")

# SERIALIZABLE (highest consistency, lowest concurrency)
cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
```

### Connection Cleanup
**ALWAYS cleanup connections in finally blocks**:

```python
conn = None
cursor = None

try:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # ... operations ...
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
```

## Concurrency Best Practices

1. **ALWAYS use row-level locking (FOR UPDATE) for updates**
2. **ALWAYS wrap multi-step operations in transactions**
3. **ALWAYS use optimistic locking for concurrent updates**
4. **ALWAYS implement idempotency for state-changing operations**
5. **ALWAYS validate boundaries before making changes**
6. **ALWAYS handle external API failures gracefully**
7. **NEVER assume external state won't change between check and use**
8. **NEVER trust client-side validation alone**
9. **ALWAYS log race conditions when they occur**
10. **ALWAYS provide meaningful error messages for conflicts**

## Shared Application Instances

### CRITICAL Rule: Never Create Duplicate App-Wide Services
**ALWAYS check for existing instances before creating new application-wide services** (limiters, loggers, caches, etc.).

### The slowapi Rate Limiter Pattern
**WRONG - Creating duplicate limiter instance:**
```python
# In app/routers/accounting/api/v1/auth.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)  # ❌ WRONG!

@router.post("/login")
@limiter.limit("5/minute")  # ❌ BREAKS! No request context
async def login_accounting(...):
    pass
```

**CORRECT - Using shared limiter instance:**
```python
# In app/main.py - create ONE limiter instance
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter  # Register with app state
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In app/routers/accounting/api/v1/auth.py - import the shared instance
from fastapi import Request, Depends
from app.main import limiter  # ✅ Import shared instance

@router.post("/login")
@limiter.limit("5/minute")  # ✅ Works! Uses shared request context
async def login_accounting(
    request: Request,  # ✅ Required for slowapi
    login_data: LoginRequest
):
    pass
```

### Why This Matters
- **Request Context Injection**: slowapi needs the Request object to extract IP addresses and track limits
- **App State Registration**: Only the limiter registered with `app.state.limiter` has proper middleware integration
- **Shared Storage**: Rate limits must be tracked across all endpoints using the same storage backend

### Other Shared Services to Watch For
```python
# ❌ WRONG - Creating new instances
logger = logging.getLogger(__name__)  # In each module separately
redis_client = redis.Redis()  # New connection per module

# ✅ CORRECT - Using shared instances
from app.core.logging import get_logger
logger = get_logger(__name__)

from app.core.cache import redis_client
# Use the shared redis_client from core
```

### Checklist Before Adding New Services
1. **Check main.py** - Is there already a limiter/logger/cache instance?
2. **Check config.py** - Are there shared configuration objects?
3. **Check core/** - Are there shared utilities in the core module?
4. **Import, Don't Create** - Always import existing instances instead of creating new ones

### Rate Limiting Best Practices for FastAPI
```python
# In main.py - Set up once
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In any router - Use the shared instance
from app.main import limiter
from fastapi import Request

@router.post("/sensitive-endpoint")
@limiter.limit("10/minute")  # Uses shared limiter
async def sensitive_operation(request: Request):
    # Request parameter is required for slowapi to work
    return {"status": "ok"}
```