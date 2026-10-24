# DEVNEST API (FastAPI)

A Q&A platform for freshers, students and graduates: register, ask questions,
answer, accept the best answer, upvote/downvote, profiles and an admin panel.

## Run it
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for the interactive Swagger UI.
Default admin: `admin@example.com` / `admin12345` (set ADMIN_EMAIL, ADMIN_PASSWORD, SECRET_KEY env vars for real use).

In /docs: register -> login (click **Authorize**, put your email in the username box) -> try the endpoints.

## Test it
```bash
pytest
```

## Structure
```
app/
  main.py        app + startup (creates tables, first admin)
  database.py    DB connection and session
  models.py      tables: User, Question, Answer, Vote
  schemas.py     request/response shapes (Pydantic)
  security.py    bcrypt hashing, JWT, current-user/admin checks
  routers/       auth, users, questions, answers, admin
tests/test_api.py
```

## Endpoints
| Method | Path | Who |
|---|---|---|
| POST | /auth/register, /auth/login | anyone |
| GET/PUT | /users/me | logged in |
| GET | /users/{id} | anyone (public profile) |
| POST | /questions | logged in |
| GET | /questions?q=&answered=&skip=&limit= | anyone |
| GET | /questions/{id} | anyone |
| DELETE | /questions/{id} | owner or admin |
| POST | /questions/{id}/answers | logged in |
| POST | /answers/{id}/accept | question owner only |
| POST | /answers/{id}/vote  `{"value": 1 or -1}` | logged in, not own answer |
| DELETE | /answers/{id} | author or admin |
| GET/POST | /admin/users | admin |
| DELETE | /admin/users/{id} | admin |

## Next steps
Tags, email verification, Alembic migrations, PostgreSQL + Docker, rate limiting on login, deployment (Render/Railway).


---
## Author

**Jaswanth Roy Gorre**

Python Backend Developer | AI/ML Enthusiast

This project was designed and developed by **Jaswanth Roy**.

- GitHub:   https://github.com/jaswanthroyg
- LinkedIn: https://www.linkedin.com/in/jaswanthroyg?

---

⭐ If you found this project interesting, consider giving the repository a star!
