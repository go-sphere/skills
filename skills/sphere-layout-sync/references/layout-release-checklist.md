# Layout Release Checklist

Use this when the change is to a **layout repository itself**, not to a generated project.

- [ ] README capabilities and `make help` output are accurate.
- [ ] `.sphere/layout.json` ownership patterns do not overlap.
- [ ] All derived outputs were regenerated after schema, proto, or Wire changes.
- [ ] `make check` and `make build` pass from a clean checkout.
- [ ] Provider-specific dependencies exist only in provider-specific layouts.
- [ ] Breaking template changes are documented.
- [ ] No database deletion migration is applied automatically to downstream apps.

A layout repository is a clean-checkout generator, not an ordinary library. Verify from a fresh
clone, because ignored generated files can otherwise mask a missing initialization step.
