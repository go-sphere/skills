# Password Hashing Notes

Use this reference only when seed rows include credential fields.

## Algorithm Detection First

Determine hashing format from project evidence before generating anything:

- auth code paths
- existing fixtures/seeds
- docs/config conventions

Common signatures:

- bcrypt: `$2a$`, `$2b$`, `$2y$`
- argon2id: `$argon2id$`
- pbkdf2: project-specific tagged format

Do not guess the algorithm.

## Determinism Rule

Salted algorithms generate different outputs each run. Seed determinism should be enforced by pinning a literal hash value:

1. generate or obtain one valid hash
2. store that exact hash string in SQL
3. reuse the same literal on reruns

Prefer existing fixture/documented hash literals when available.

## One-Time Hash Generation Example (bcrypt)

```bash
python3 - <<'PY'
import bcrypt
password = b"Passw0rd!"
print(bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode())
PY
```

Treat output as a one-time value to pin, not a reproducible command result.

## If Tooling Is Missing

- Reuse known valid hash samples from repository fixtures/docs.
- If no valid sample exists, request a hash sample instead of writing plaintext into `password_hash`.

## Safety Notes

- Seed credentials are dev/test only.
- Do not claim production credential security from seed SQL.
- Only expose test plaintext password when explicitly acceptable for the task context.
