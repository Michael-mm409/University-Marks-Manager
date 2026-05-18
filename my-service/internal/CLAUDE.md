Internal package conventions

Purpose
- Short notes for internal packages: naming, interfaces, dependencies, and tests.

Package naming
- Use short, lowercase names that describe responsibility (e.g., store, svc, auth).
- Keep packages focused — one responsibility per package.

Exports & APIs
- Keep the public surface small. Prefer constructors/factory funcs over exported globals.
- Document exported types/functions with a short sentence.

Interfaces & implementations
- Prefer descriptive interface names: `Repository`, `Authenticator`, `Notifier`.
- Implementation types can end with `Impl` or be package-private when possible.

Dependencies
- Avoid circular dependencies. If two packages depend on each other, extract a small interface into a third package.
- Internal packages should not import top-level presentation or command packages.

Error handling
- Return errors with context. Wrap or annotate errors where it helps debugging.

Testing
- Add unit tests for public behavior of internal packages.
- Use small, focused test fixtures; mock external dependencies as needed.

Small examples (Python-style)
- Factory / constructor pattern:

  def create_repository(db):
	  """Return a repository instance bounded to `db`. Keep implementation private."""
	  return _RepositoryImpl(db)

- Interface example (pseudo):

  class Repository:
	  def get(self, id):
		  raise NotImplementedError

  class _RepositoryImpl(Repository):
	  def __init__(self, db):
		  self._db = db

	  def get(self, id):
		  return self._db.query(...)

Testing tips
- Use dependency injection to pass mocks/fakes. For Python, `pytest` fixtures are handy.
- Example test outline:

  def test_get_returns_none_for_missing(repo_factory):
	  repo = repo_factory(empty_db)
	  assert repo.get(123) is None

Refactoring note
- If you find two packages importing each other, extract a minimal interface package (e.g., `common/iface`) rather than widening existing packages.

Docs & comments
- Keep inline comments short and useful. If behavior is surprising, explain why.
