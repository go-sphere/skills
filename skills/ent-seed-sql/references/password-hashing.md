# Password Hashing Notes

Use this reference only when seed data includes credential fields.

## Rule

Infer algorithm from existing code/docs first. Do not guess blindly.

Common patterns:

- bcrypt (`$2a$`, `$2b$`, `$2y$` prefix)
- argon2id (`$argon2id$` prefix)
- pbkdf2 (project-specific format)

## Determinism Model

Salted password hash algorithms (bcrypt/argon2id) produce different outputs on each new hash generation by design.

For deterministic seed SQL, determinism should be applied to the SQL literal value:

- Generate or obtain a valid hash once.
- Pin that hash string in seed SQL.
- Reuse the same pinned hash literal across reruns.

Prefer existing fixture/doc hash samples when available.

## Minimal Hash Generation

If bcrypt is required and Python dependency is available, you can generate a hash once:

```bash
python3 - <<'PY'
import bcrypt
password = b"Passw0rd!"
print(bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode())
PY
```

Treat the command output as a one-time value to pin in SQL. Do not expect repeated runs of this command to return the same string.

If no hash tool is available:

- Prefer reusing known valid hash samples from project fixtures/docs.
- Otherwise stop and request a hash sample from the user rather than outputting invalid plaintext.

## Safety

- Treat all seed credentials as dev/test only.
- Never claim production-grade credential management from seed SQL.
