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

## Go-Sphere Default

`sphere/utils/secure` hashes with `bcrypt.GenerateFromPassword(pwd, bcrypt.DefaultCost)`,
so go-sphere projects produce **bcrypt cost 10** hashes with a `$2a$` prefix.
Match that unless the project shows other evidence.

## Validating a Hash Before You Pin It

Two independent checks. **The first is necessary but not sufficient** — do both.

**1. Shape.** A bcrypt hash is exactly 60 characters: `$2a$`/`$2b$`/`$2y$` +
2-digit cost + `$` + 22-char salt + 31-char digest. Anything shorter is not a
bcrypt hash and will never validate.

```bash
printf '%s' "$HASH" | wc -c   # must print 60
```

**2. Verification against the claimed plaintext.** A well-formed hash still
proves nothing — plenty of 60-character placeholders circulate that parse
correctly and match no password at all. Only `CompareHashAndPassword` /
`bcrypt.checkpw` settles it:

```bash
python3 - <<'PY'
import bcrypt
h = b"<hash>"
print(bcrypt.checkpw(b"Passw0rd!", h))   # must print True
PY
```

Never invent a hash by hand, copy one from documentation without verifying it, or
pattern-match the shape. An unverified literal produces seed accounts that
silently cannot log in, and the failure surfaces far from its cause.

## Pre-Generated Hash Samples (bcrypt, cost 10)

Generated with Go's `golang.org/x/crypto/bcrypt` and verified with
`CompareHashAndPassword`. Plaintext is `Passw0rd!`:

```
$2a$10$0Ah2j61iId12kpgsbARXoevqxQrR0FLxJoQJJ9hDiPle0C2a6I.te
$2a$10$W3FcrSZnV.psQmTu7BJefONNj96XOp5dBqKma33YspReNkakKdyxy
```

Cost 12 variants of the same plaintext, if the project uses a higher cost:

```
$2a$12$8uB7AdGGW2KR4zs4U4YzXe525AH04C1sV87cln9HMkx7cZzgsbT7a
$2a$12$IPpMHSrC9f5bofr975aEJ.iDrNSIE.epZT7h9ADNrG95Rf8EXHxFu
```

Each line is independently valid — pick one and reuse that exact literal.

## One-Time Hash Generation Example (bcrypt)

Preferred in a go-sphere repo, since it matches the runtime exactly and verifies
the result:

```bash
cat > /tmp/genhash/main.go <<'GO'
package main

import (
	"fmt"

	"golang.org/x/crypto/bcrypt"
)

func main() {
	pw := []byte("Passw0rd!")
	h, err := bcrypt.GenerateFromPassword(pw, bcrypt.DefaultCost)
	if err != nil {
		panic(err)
	}
	if err := bcrypt.CompareHashAndPassword(h, pw); err != nil {
		panic(err)
	}
	fmt.Println(string(h))
}
GO
go run /tmp/genhash
```

Python equivalent when the `bcrypt` package is available:

```bash
python3 - <<'PY'
import bcrypt
password = b"Passw0rd!"
h = bcrypt.hashpw(password, bcrypt.gensalt(rounds=10))
assert bcrypt.checkpw(password, h)
print(h.decode())
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

- Reuse known valid hash samples from repository fixtures/docs, or the verified
  samples above.
- If no valid sample exists, request a hash sample instead of writing plaintext
  into `password_hash`.
- Never fabricate a hash literal to fill the gap.

## Safety Notes

- Seed credentials are dev/test only.
- Do not claim production credential security from seed SQL.
- Only expose test plaintext password when explicitly acceptable for the task context.
