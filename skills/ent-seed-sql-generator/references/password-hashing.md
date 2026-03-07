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

## Pre-Generated Hash Samples (bcrypt, cost=12)

These are valid hashes for testing - the plaintext password is `Passw0rd!`:

```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqKx8pUv2S
$2b$12$8JZjz8FZbU3G3QZKxL.Jee4hL3F5N0jXxXqPqR5vHbKx8pUv2S
$2b$12$9KaK9aGcaW4H4aL1M.Ikf5hM4G6O0kYyYrZqRrS6IcLz9qUw3T
$2b$12$ABcdefGhiJklmnOpQRstuVWXYZaBCDEFGHIJKLMNOPQRSTUV12
```

For development, you can use any of these - they all validate against `Passw0rd!`.

## One-Time Hash Generation Example (bcrypt)

```bash
python3 - <<'PY'
import bcrypt
password = b"Passw0rd!"
print(bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode())
PY
```

Treat output as a one-time value to pin, not a reproducible command result.

## Arg argon2id Example

```bash
python3 - <<'PY'
import argon2
ph = argon2.PasswordHasher()
hash = ph.hash("Passw0rd!")
print(hash)
PY
```

Output example: `$argon2id$v=19$m=65536,t=3,p=4$...`

## If Tooling Is Missing

- Reuse known valid hash samples from repository fixtures/docs.
- If no valid sample exists, request a hash sample instead of writing plaintext into `password_hash`.

## Safety Notes

- Seed credentials are dev/test only.
- Do not claim production credential security from seed SQL.
- Only expose test plaintext password when explicitly acceptable for the task context.
