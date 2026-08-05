# Calculations API

A FastAPI application where a registered user can create and manage
calculations. Authentication uses JWT, data is stored in PostgreSQL through
SQLAlchemy, and the browser pages cover the full set of operations.

## Authentication and ownership

Registering or logging in returns a signed JWT. The front-end stores it in
localStorage and sends it as a bearer token on every request. All calculation
routes require a valid token, and each one filters by the user it belongs to,
so browse returns only your own rows and another user's calculation returns a
404 rather than revealing that it exists.

## Endpoints

    GET    /register            registration page
    GET    /login               login page
    GET    /dashboard           calculations page

    POST   /users/register      create a user, returns a JWT
    POST   /users/login         verify credentials, returns a JWT, 401 on failure

    GET    /calculations        browse the current user's calculations
    GET    /calculations/{id}   read one calculation
    POST   /calculations        add, result computed on creation
    PUT    /calculations/{id}   edit, result recomputed
    DELETE /calculations/{id}   delete

## Run the application

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    docker compose up -d
    uvicorn main:app --reload

Register at http://127.0.0.1:8000/register, then log in at
http://127.0.0.1:8000/login, which redirects to the dashboard. The dashboard
lists your calculations, adds new ones through the form, and edits or deletes
any row. Operands are checked for numeric values and the operation type is
checked against the four supported types before a request is sent, and
division by zero is refused in the browser as well as by the server. The
interactive API documentation is at http://127.0.0.1:8000/docs.

## Run the tests

    pytest

Unit tests cover password hashing, the schemas, the operation factory, and
JWT encoding and decoding. Integration tests exercise every route against
PostgreSQL, including ownership: requests without a token, with an invalid
token, or for another user's record are all rejected. End-to-end tests drive
a real browser through registration, login, and the full add, browse, edit,
and delete cycle, along with invalid input and an unauthenticated dashboard.

## CI/CD

Every push runs the full suite in GitHub Actions against a PostgreSQL service
container, browser tests included. If tests pass on main, the image is built
and pushed to Docker Hub:

https://hub.docker.com/r/chima765432/m14-python-calculator

    docker pull chima765432/m14-python-calculator:latest
