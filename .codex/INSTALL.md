# Installing sphere-workflow for Codex

Enable the `sphere-workflow` plugin in Codex via native skill discovery.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/go-sphere/skills.git ~/.codex/sphere-workflow
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/sphere-workflow/skills ~/.agents/skills/sphere-workflow
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\sphere-workflow" "$env:USERPROFILE\.codex\sphere-workflow\skills"
   ```

3. **Restart Codex** so it rediscovers the plugin skills.

## Verify

```bash
ls -la ~/.agents/skills/sphere-workflow
```

You should see a symlink or junction pointing to `~/.codex/sphere-workflow/skills`.

## Usage

- Let Codex discover the plugin automatically for go-sphere work.
- Or explicitly ask for `using-sphere-workflow` to bootstrap routing into the bundled skills.

## Updating

```bash
cd ~/.codex/sphere-workflow && git pull
```

## Uninstalling

```bash
rm ~/.agents/skills/sphere-workflow
```

Optionally delete the clone:

```bash
rm -rf ~/.codex/sphere-workflow
```
