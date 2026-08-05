# Calculations API

A FastAPI REST API for users and calculations, backed by PostgreSQL through
SQLAlchemy, with JWT authentication and browser pages for registration and
login.

## Authentication

Registering or logging in returns a signed JWT alongside the user record. The
token carries the user's email and an expiry, and is signed with a secret key,
so it can be read but not forged. The front-end stores it in localStorage.

## Endpoints

    GET    /register            registration page
    GET    /login               login page

    POST   /users/register      create a user, returns a JWT
    POST   /users/login         verify credentials, returns a JWT, 401 on failure

    GET    /calculations        browse
    GET    /calculations/{id}   read
    POST   /calculations        add, result computed on creation
    PUT    /calculations/{id}   edit, result recomputed
    DELETE /calculations/{id}   delete

Password hashes never appear in a response, because every response is shaped
by a Pydantic schema that has no such field.

## Run the front-end

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    docker compose up -d
    uvicorn main:app --reload

Open http://127.0.0.1:8000/register or http://127.0.0.1:8000/login. Both
pages validate email format and password length in the browser before any
request is sent, and show the server's message when it rejects a request.
The interactive API documentation is at http://127.0.0.1:8000/docs.

## Run the tests

    pytest

Unit tests cover hashing, schemas, the operation factory, and JWT encoding
and decoding. Integration tests hit every route against PostgreSQL.
End-to-end tests drive a real browser through registration and login,
covering both success paths and two failure paths: a password that is too
short, caught in the browser, and a wrong password, rejected by the server.

## CI/CD

Every push runs the full suite in GitHub Actions against a PostgreSQL service
container, browser tests included. If tests pass on main, the image is built
and pushed to Docker Hub:

https://hub.docker.com/r/chima765432/m14-python-calculator

    docker pull chima765432/m14-python-calculator:latest
