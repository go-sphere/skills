#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$ROOT_DIR/skills"
ROUTER="$SKILLS_DIR/using-sphere-workflow/SKILL.md"

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

pass() {
  echo "[PASS] $1"
}

display_path() {
  local path="$1"
  echo "${path#"$ROOT_DIR"/}"
}

# Names that may appear in backticks inside a Related Skills block without being skills.
NON_SKILL_REFERENCES=" vueuse-functions sphere-workflow go-sphere "
STALE_NAMES=(ent-schema-generator pure-admin-crud-generator)

# Print the lines of a `## Heading` section, stopping at the next `## ` heading.
section() {
  local file="$1"
  local heading="$2"
  awk -v heading="$heading" '
    $0 == heading { inside = 1; next }
    inside && /^## / { exit }
    inside { print }
  ' "$file"
}

# A backticked token is a valid skill reference when a real skill directory exists.
resolve_token() {
  local token="$1"
  case "$NON_SKILL_REFERENCES" in
    *" $token "*) return 0 ;;
  esac
  [ -f "$SKILLS_DIR/$token/SKILL.md" ]
}

# 1. Skill inventory: every directory has a SKILL.md whose frontmatter name matches.
skill_dirs=()
while IFS= read -r dir; do
  skill_dirs+=("$(basename "$dir")")
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

[ "${#skill_dirs[@]}" -eq 19 ] || fail "expected 19 skill directories, found ${#skill_dirs[@]}"

for name in "${skill_dirs[@]}"; do
  file="$SKILLS_DIR/$name/SKILL.md"
  [ -f "$file" ] || fail "missing SKILL.md for skill: $name"
  grep -Eq "^name:[[:space:]]*$name[[:space:]]*$" "$file" ||
    fail "frontmatter name does not match directory name: $(display_path "$file")"
done
pass "found ${#skill_dirs[@]} skills, each with a matching frontmatter name"

# 2. The router Workflow Map must cover every stage skill and name only real ones.
map_names="$(section "$ROUTER" "## Workflow Map" | grep -oE '^- `[a-z0-9-]+`' | sed -E 's/^- `(.*)`$/\1/' | sort -u)"
[ -n "$map_names" ] || fail "router Workflow Map lists no skills"

while IFS= read -r name; do
  [ -n "$name" ] || continue
  if [ "$name" = "using-sphere-workflow" ]; then
    fail "router Workflow Map must not list the router itself"
  fi
  resolve_token "$name" || fail "router Workflow Map names an unknown skill: $name"
done <<<"$map_names"

for name in "${skill_dirs[@]}"; do
  if [ "$name" = "using-sphere-workflow" ]; then
    continue
  fi
  printf '%s\n' "$map_names" | grep -Fxq "$name" || fail "router Workflow Map omits skill: $name"
done
pass "router Workflow Map covers all $((${#skill_dirs[@]} - 1)) stage skills and names only real ones"

# 3. Every stage skill carries a complete Related Skills block.
for name in "${skill_dirs[@]}"; do
  if [ "$name" = "using-sphere-workflow" ]; then
    continue
  fi
  file="$SKILLS_DIR/$name/SKILL.md"
  block="$(section "$file" "## Related Skills")"
  [ -n "$block" ] || fail "missing '## Related Skills' section: $(display_path "$file")"
  for label in Upstream Downstream Boundary Companion; do
    printf '%s\n' "$block" | grep -q "^- $label" ||
      fail "Related Skills block is missing the '$label' bullet: $(display_path "$file")"
  done
  printf '%s\n' "$block" | grep -q "not installed" ||
    fail "Related Skills block is missing the not-installed fallback: $(display_path "$file")"
done
pass "every stage skill has a Related Skills block with Upstream, Downstream, Boundary, Companion, and a fallback"

grep -q '^## Stage Handoffs$' "$ROUTER" || fail "router is missing the '## Stage Handoffs' section"
section "$ROUTER" "## Stage Handoffs" | grep -q "do not stall" ||
  fail "router Stage Handoffs section is missing the do-not-stall rule"
pass "router carries the Stage Handoffs contract"

# 4. Every skill named inside a Related Skills block must exist.
for name in "${skill_dirs[@]}"; do
  if [ "$name" = "using-sphere-workflow" ]; then
    continue
  fi
  file="$SKILLS_DIR/$name/SKILL.md"
  while IFS= read -r token; do
    [ -n "$token" ] || continue
    resolve_token "$token" || fail "Related Skills names an unknown skill '$token': $(display_path "$file")"
  done < <(section "$file" "## Related Skills" | grep -oE '`[a-z][a-z0-9-]*`' | tr -d '`' | sort -u)
done
pass "every skill named in a Related Skills block resolves to a real skill"

# 5. Slash commands in the prompt guide must resolve to real skills.
prompt_doc="$ROOT_DIR/references/prompt.md"
[ -f "$prompt_doc" ] || fail "missing references/prompt.md"
while IFS= read -r token; do
  [ -n "$token" ] || continue
  resolve_token "$token" || fail "references/prompt.md invokes an unknown skill: /$token"
done < <(grep -oE '`/[a-z0-9-]+`' "$prompt_doc" | tr -d '`/' | sort -u)
pass "every slash command in references/prompt.md resolves to a real skill"

# 6. Role-to-skill mappings in the dev guide must resolve to real skills.
dev_doc="$ROOT_DIR/references/dev.md"
[ -f "$dev_doc" ] || fail "missing references/dev.md"
while IFS= read -r token; do
  [ -n "$token" ] || continue
  resolve_token "$token" || fail "references/dev.md maps a role to an unknown skill: $token"
done < <(grep -oE '已有 `[a-z0-9-]+` skill' "$dev_doc" | grep -oE '`[a-z0-9-]+`' | tr -d '`' | sort -u)
pass "references/dev.md role table maps only real skills"

# 7. Description boundary clauses must point at real skills.
for name in "${skill_dirs[@]}"; do
  file="$SKILLS_DIR/$name/SKILL.md"
  while IFS= read -r token; do
    [ -n "$token" ] || continue
    resolve_token "$token" || fail "description boundary clause names an unknown skill '$token': $(display_path "$file")"
  done < <(grep -oE 'that is `[a-z0-9-]+`' "$file" | grep -oE '`[a-z0-9-]+`' | tr -d '`' | sort -u)
done
pass "every description boundary clause points at a real skill"

# 8. Known-renamed skill names must not survive anywhere.
for stale in "${STALE_NAMES[@]}"; do
  hits="$(grep -rn --exclude="$(basename "$0")" "$stale" \
    "$SKILLS_DIR" "$ROOT_DIR/references" "$ROOT_DIR/docs" \
    "$ROOT_DIR/README.md" "$ROOT_DIR/hooks" "$ROOT_DIR/tests" 2>/dev/null || true)"
  [ -z "$hits" ] || fail "stale skill name '$stale' is still referenced:
$hits"
done
pass "no stale skill names remain"

# 9. Every reference link inside a SKILL.md must resolve to an existing file.
for name in "${skill_dirs[@]}"; do
  file="$SKILLS_DIR/$name/SKILL.md"
  while IFS= read -r link; do
    [ -n "$link" ] || continue
    target="${link%%#*}"
    [ -f "$SKILLS_DIR/$name/$target" ] ||
      fail "SKILL.md links a missing reference file: $(display_path "$file") -> $link"
  done < <(grep -oE '\]\(references/[^)#]+\.md' "$file" | sed -E 's/^\]\(//')
done
pass "every SKILL.md reference link resolves to a file"

# 10. Framework packs must be linked from their skill's SKILL.md, and linked packs must exist.
pack_count=0
for name in "${skill_dirs[@]}"; do
  pack_dir="$SKILLS_DIR/$name/references/frameworks"
  [ -d "$pack_dir" ] || continue
  file="$SKILLS_DIR/$name/SKILL.md"
  while IFS= read -r pack; do
    [ -n "$pack" ] || continue
    pack_count=$((pack_count + 1))
    grep -q "](references/frameworks/$pack)" "$file" ||
      fail "framework pack is not linked from $(display_path "$file"): $pack"
  done < <(find "$pack_dir" -maxdepth 1 -type f -name '*.md' -exec basename {} \; | sort)
  grep -q '](references/frameworks/' "$file" ||
    fail "SKILL.md links no framework pack: $(display_path "$file")"
done
[ "$pack_count" -gt 0 ] || fail "no framework packs found under any skill"
pass "framework packs and their SKILL.md links stay in sync ($pack_count packs)"

# 11. SKILL.md stays within the progressive-disclosure size budget.
for name in "${skill_dirs[@]}"; do
  file="$SKILLS_DIR/$name/SKILL.md"
  lines="$(wc -l < "$file" | tr -d '[:space:]')"
  [ "$lines" -le 500 ] || fail "SKILL.md exceeds 500 lines ($lines): $(display_path "$file")"
done
pass "every SKILL.md is within the 500-line budget"

echo "All skill reference checks passed."
