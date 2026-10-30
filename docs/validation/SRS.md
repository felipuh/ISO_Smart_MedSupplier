# Software Requirements Specification

- Backend: Django REST Framework, PostgreSQL in deployment, SQLite-compatible tests.
- Frontend: React, Vite, Tailwind, Axios.
- Authorization shall be enforced server-side before UI filtering.
- Audit events shall include correlation ID, event hash, previous hash, actor, object, reason where required, IP, user-agent, and scope.
- Evidence package exports shall provide JSON MVP and checksum metadata.
- No production secrets or fake production data shall be embedded in code.
