# Multi-User Setup Guide

This guide explains how to add multi-user functionality to Marks Manager so different users can have different courses.

## Changes Made

### 1. Database Models Added

Two new models have been added to `src/infrastructure/db/models.py`:

- **User**: Stores user credentials
  - `id`: Primary key
  - `username`: Unique username
  - `email`: Unique email address
  - `password_hash`: Hashed password (use bcrypt or similar)
  - `user_courses`: Relationship to courses they have access to

- **UserCourse**: Association table linking users to courses
  - `user_id`: Foreign key to User
  - `course_id`: Foreign key to Course
  - `is_default`: Boolean flag for their default/active course
  - Unique constraint on (user_id, course_id)

### 2. Database Migration Required

Create a migration in `db/migrations/` to add these tables:

```sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL
);

-- Create user_courses table
CREATE TABLE user_courses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, course_id)
);

-- Create index for faster lookups
CREATE INDEX idx_user_courses_user_id ON user_courses(user_id);
CREATE INDEX idx_user_courses_course_id ON user_courses(course_id);
```

### 3. Implementation Steps

#### Step 1: Authentication
Add an authentication router:
```python
# src/presentation/web/auth_views.py
from fastapi import APIRouter, Form, Session, Depends
from sqlmodel import select
from src.infrastructure.db.models import User
from src.presentation.api.deps import get_session
import bcrypt

router = APIRouter()

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == username)).first()
    if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        # Store user_id in session
        request.session["user_id"] = user.id
        return RedirectResponse(url="/", status_code=303)
    # Invalid credentials
    return {"error": "Invalid username or password"}

@router.post("/logout")
def logout(request: Request):
    request.session.pop("user_id", None)
    return RedirectResponse(url="/login", status_code=303)
```

#### Step 2: User Context
Add user_id to session:
```python
# In views.py
sess = request.session
user_id = sess.get("user_id")  # Add this to all queries

if not user_id:
    return RedirectResponse(url="/login", status_code=303)
```

#### Step 3: Filter Queries by User
Update CourseManager and other managers to filter by user:
```python
# In CourseManager
def get_user_courses(self, user_id: int) -> list[Course]:
    """Get all courses for a specific user."""
    from src.infrastructure.db.models import UserCourse
    user_courses = self.session.exec(
        select(UserCourse).where(UserCourse.user_id == user_id)
    ).all()
    return [uc.course for uc in user_courses if uc.course]

def get_default_course(self, user_id: int) -> Optional[Course]:
    """Get user's default course."""
    from src.infrastructure.db.models import UserCourse
    user_course = self.session.exec(
        select(UserCourse)
        .where(UserCourse.user_id == user_id, UserCourse.is_default == True)
    ).first()
    return user_course.course if user_course else None
```

#### Step 4: Update Views
Modify `_render_home_body()` to use user's courses:
```python
def _render_home_body(request: Request, session: Session, parsed_year: Optional[int]) -> HTMLResponse:
    sess = request.session
    user_id = sess.get("user_id")
    
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    cm = CourseManager(session)
    
    # Get only courses for this user
    user_courses = cm.get_user_courses(user_id)
    
    # Get active course from session, or default to user's default course
    active_course_id = sess.get("current_course_id")
    if not active_course_id:
        default = cm.get_default_course(user_id)
        if default:
            active_course_id = default.id
    
    # Verify course belongs to user
    if active_course_id:
        course = session.get(Course, active_course_id)
        user_course = session.exec(
            select(UserCourse)
            .where(UserCourse.user_id == user_id, UserCourse.course_id == active_course_id)
        ).first()
        if not user_course:
            # User doesn't have access to this course
            active_course_id = None
    
    # ... rest of function
```

#### Step 5: Update Course Selector
Add a course dropdown that only shows user's courses:
```html
<!-- In template -->
<select name="course" onchange="selectCourse(this.value)">
    {% for uc in user_courses %}
        <option value="{{ uc.course.id }}" {% if uc.course.id == current_course_id %}selected{% endif %}>
            {{ uc.course.name }}
        </option>
    {% endfor %}
</select>
```

### 4. Security Considerations

1. **Password Hashing**: Use bcrypt or argon2 to hash passwords
   ```python
   import bcrypt
   hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   ```

2. **Session Security**: 
   - Use HTTPS in production
   - Set secure cookie flags
   - Add CSRF protection
   - Validate session user_id on every request

3. **Access Control**:
   - Always verify user owns the resource they're accessing
   - Filter all queries by user_id
   - Use middleware to check authentication on protected routes

4. **SQL Injection Prevention**:
   - Use parameterized queries (already done with SQLModel)
   - Never concatenate user input into queries

### 5. Example: Protected Route Middleware

```python
from fastapi import Request, status
from fastapi.responses import RedirectResponse

async def verify_user_session(request: Request):
    """Middleware to verify user is logged in."""
    user_id = request.session.get("user_id")
    if not user_id and request.url.path not in ["/login", "/signup"]:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return None
```

### 6. Future Enhancements

- **Role-based Access**: Admin, instructor, student roles
- **Course Sharing**: Allow users to share courses/data
- **Audit Logging**: Track who made changes
- **Two-Factor Authentication**: Enhanced security
- **OAuth Integration**: Google/Microsoft login

---

## Next Steps

1. Run the SQL migration to create the tables
2. Implement the auth_views.py router
3. Update views.py to include user_id filtering
4. Update CourseManager with user-aware methods
5. Add login/signup templates
6. Update course selector UI
7. Add user middleware for session validation
