class TestRepository:
    """In-memory session store for test results (extend with DB as needed)."""

    def __init__(self):
        self._store = {}

    def save(self, session_id: str, result: dict):
        self._store[session_id] = result

    def find(self, session_id: str):
        return self._store.get(session_id)

    def delete(self, session_id: str):
        self._store.pop(session_id, None)