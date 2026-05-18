
API conventions — short & friendly

Purpose
- Describe REST conventions, error formats, and common response expectations.

URL & resources
- Use plural nouns for resources: /courses, /students, /exams.
- Use nested resources when it makes sense: /courses/{id}/subjects.
- Version in the path: /v1/ when you expect breaking changes.

HTTP methods
- GET: read, return 200 (+ pagination if list).
- POST: create, return 201 with Location header (or 200 with object).
- PUT: idempotent replace/update.
- PATCH: partial update.
- DELETE: remove, return 204 on success.

Status codes & errors
- 200 OK — successful GET/PUT/PATCH when returning data.
- 201 Created — successful resource creation.
- 204 No Content — successful delete or empty response.
- 400 Bad Request — validation or malformed request. Return field-level errors.
- 401 Unauthorized — missing or invalid credentials.
- 403 Forbidden — authenticated but not allowed.
- 404 Not Found — resource doesn't exist.
- 409 Conflict — unique constraint or concurrency conflict.
- 422 Unprocessable Entity — semantic validation failures (optional).
- 429 Too Many Requests — rate limited.
- 500 Internal Server Error — unexpected errors.

Error response format (example)
{
  "error": {
    "code": "invalid_input",
    "message": "Validation failed",
    "details": {"email": "can't be blank"}
  }
}

Common patterns & examples
- Example resource endpoints:
  - `GET /v1/courses` — list courses
  - `GET /v1/courses/{id}` — get single course
  - `POST /v1/courses` — create course
  - `POST /v1/courses/{id}/import` — custom action (e.g. CSV import)

- Sample curl (create):
  curl -X POST -H "Content-Type: application/json" -d '{"name":"Intro"}' \
    http://localhost:8000/v1/courses

- Sample curl (error):
  curl -i http://localhost:8000/v1/courses/does-not-exist

Pagination example (limit/offset)
{
  "data": [ /* items */ ],
  "meta": {"limit":25, "offset":0, "total": 354}
}

Rate limiting / headers
- Consider returning `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` when applicable.

Idempotency
- For non-idempotent operations (like import), accept an `Idempotency-Key` header so retries are safe.

Security
- Use HTTPS for public endpoints. Prefer short-lived tokens and standard `Authorization: Bearer` header.

Testing the API
- Add integration tests for core flows (create -> read -> update -> delete).
- Use fixture data and reset DB between tests to avoid flakiness.

Notes
- Keep responses minimal and predictable. If a client needs more data, add a separate endpoint.
