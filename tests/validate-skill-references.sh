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

[ "${#skill_dirs[@]}" -eq 20 ] || fail "expected 20 skill directories, found ${#skill_dirs[@]}"

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
done < <(grep -rhoE '`/[a-z0-9-]+`' "$prompt_doc" "$ROOT_DIR/references/prompt" | tr -d '`/' | sort -u)
pass "every slash command in the prompt guide resolves to a real skill"

# 5a. Every prompt-guide chapter must be reachable from references/prompt.md.
prompt_chapters=0
while IFS= read -r chapter; do
  prompt_chapters=$((prompt_chapters + 1))
  grep -q "](prompt/$(basename "$chapter"))" "$prompt_doc" ||
    fail "prompt guide chapter is not linked from references/prompt.md: $(display_path "$chapter")"
done < <(find "$ROOT_DIR/references/prompt" -type f -name '*.md' | sort)
[ "$prompt_chapters" -gt 0 ] || fail "references/prompt/ contains no chapters"
pass "all $prompt_chapters prompt-guide chapters are linked from references/prompt.md"

# 6. Role-to-skill mappings in the dev guide must resolve to real skills.
dev_doc="$ROOT_DIR/references/dev.md"
[ -f "$dev_doc" ] || fail "missing references/dev.md"
while IFS= read -r token; do
  [ -n "$token" ] || continue
  resolve_token "$token" || fail "the dev guide maps a role to an unknown skill: $token"
done < <(grep -rhoE '已有 `[a-z0-9-]+` skill' "$ROOT_DIR/references" | grep -oE '`[a-z0-9-]+`' | tr -d '`' | sort -u)
pass "the dev guide role table maps only real skills"

# 6a. Every dev-guide chapter must be reachable from references/dev.md, and its links must resolve.
dev_chapters=0
while IFS= read -r chapter; do
  dev_chapters=$((dev_chapters + 1))
  grep -q "](dev/$(basename "$chapter"))" "$dev_doc" ||
    fail "dev guide chapter is not linked from references/dev.md: $(display_path "$chapter")"
done < <(find "$ROOT_DIR/references/dev" -type f -name '*.md' | sort)
[ "$dev_chapters" -gt 0 ] || fail "references/dev/ contains no chapters"
while IFS= read -r link; do
  [ -n "$link" ] || continue
  [ -f "$ROOT_DIR/references/$link" ] ||
    fail "references/dev.md links a missing chapter: $link"
done < <(grep -oE '\]\(dev/[^)#]+\.md' "$dev_doc" | sed -E 's/^\]\(//')
pass "all $dev_chapters dev-guide chapters are linked from references/dev.md"

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
# Budgets are documented in references/skill-authoring.md.
SKILL_LINE_BUDGET=150
REFERENCE_LINE_BUDGET=200
DESCRIPTION_CHAR_BUDGET=400

for name in "${skill_dirs[@]}"; do
  file="$SKILLS_DIR/$name/SKILL.md"
  lines="$(wc -l < "$file" | tr -d '[:space:]')"
  [ "$lines" -le "$SKILL_LINE_BUDGET" ] ||
    fail "SKILL.md exceeds $SKILL_LINE_BUDGET lines ($lines): $(display_path "$file")"
done
pass "every SKILL.md is within the $SKILL_LINE_BUDGET-line budget"

# 12. Reference files stay small enough to load one at a time.
for name in "${skill_dirs[@]}"; do
  ref_dir="$SKILLS_DIR/$name/references"
  [ -d "$ref_dir" ] || continue
  while IFS= read -r ref; do
    lines="$(wc -l < "$ref" | tr -d '[:space:]')"
    [ "$lines" -le "$REFERENCE_LINE_BUDGET" ] ||
      fail "reference exceeds $REFERENCE_LINE_BUDGET lines ($lines): $(display_path "$ref")"
  done < <(find "$ref_dir" -type f -name '*.md' | sort)
done
pass "every reference file is within the $REFERENCE_LINE_BUDGET-line budget"

# 13. Descriptions stay cheap: one line, under budget, and they say when to use the skill.
for name in "${skill_dirs[@]}"; do
  file="$SKILLS_DIR/$name/SKILL.md"
  desc_lines="$(grep -c '^description:' "$file")"
  [ "$desc_lines" -eq 1 ] ||
    fail "expected exactly one 'description:' line, found $desc_lines: $(display_path "$file")"
  # A continued (multi-line) description would leave a non-key line before the closing '---'.
  awk 'NR>1 && /^---$/ {exit} /^description:/{found=1; next} found && !/^[a-z_]+:/ {exit 1}' "$file" ||
    fail "description spans multiple lines: $(display_path "$file")"
  desc="$(sed -n 's/^description:[[:space:]]*//p' "$file" | head -n 1)"
  chars="$(printf '%s' "$desc" | wc -m | tr -d '[:space:]')"
  [ "$chars" -le "$DESCRIPTION_CHAR_BUDGET" ] ||
    fail "description exceeds $DESCRIPTION_CHAR_BUDGET characters ($chars): $(display_path "$file")"
  case "$desc" in
    *"Use when"*|*"Use to"*|*"Use for"*|*"Use at"*|*"Use whenever"*) ;;
    *) fail "description never says when to use the skill: $(display_path "$file")" ;;
  esac
done
pass "every description is one line, within $DESCRIPTION_CHAR_BUDGET characters, and states when to use the skill"

# 14. Progressive disclosure: every reference file is reachable from its SKILL.md.
for name in "${skill_dirs[@]}"; do
  ref_dir="$SKILLS_DIR/$name/references"
  [ -d "$ref_dir" ] || continue
  file="$SKILLS_DIR/$name/SKILL.md"
  while IFS= read -r ref; do
    rel="references/${ref#"$ref_dir"/}"
    grep -q "]($rel)" "$file" ||
      fail "reference file is not linked from $(display_path "$file"): $rel"
  done < <(find "$ref_dir" -type f -name '*.md' | sort)
  grep -q '^## Reference Map$' "$file" ||
    fail "SKILL.md has reference files but no '## Reference Map' section: $(display_path "$file")"
done
pass "every reference file is linked from its skill's Reference Map"

# 15. Reference files must not dangle: relative links between them have to resolve.
for name in "${skill_dirs[@]}"; do
  ref_dir="$SKILLS_DIR/$name/references"
  [ -d "$ref_dir" ] || continue
  while IFS= read -r ref; do
    while IFS= read -r link; do
      [ -n "$link" ] || continue
      target="${link%%#*}"
      [ -f "$(dirname "$ref")/$target" ] ||
        fail "reference links a missing file: $(display_path "$ref") -> $link"
    done < <(grep -oE '\]\([a-z0-9][a-z0-9./-]*\.md' "$ref" | sed -E 's/^\]\(//')
  done < <(find "$ref_dir" -type f -name '*.md' | sort)
done
pass "every relative link between reference files resolves"

echo "All skill reference checks passed."
