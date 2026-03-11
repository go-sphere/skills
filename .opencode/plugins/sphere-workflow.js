/**
 * sphere-workflow plugin for OpenCode.ai
 *
 * Injects the using-sphere-workflow bootstrap context at session start.
 * All other skills are discovered through OpenCode's native skill system.
 */

import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatterStr = match[1];
  const body = match[2];
  const frontmatter = {};

  for (const line of frontmatterStr.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
      frontmatter[key] = value;
    }
  }

  return { frontmatter, content: body };
};

const normalizePath = (value, homeDir) => {
  if (!value || typeof value !== 'string') return null;

  let normalized = value.trim();
  if (!normalized) return null;

  if (normalized === '~') {
    normalized = homeDir;
  } else if (normalized.startsWith('~/')) {
    normalized = path.join(homeDir, normalized.slice(2));
  }

  return path.resolve(normalized);
};

export const SphereWorkflowPlugin = async () => {
  const homeDir = os.homedir();
  const bundledSkillsDir = path.resolve(__dirname, '../../skills');
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');

  const getBootstrapContent = () => {
    const skillPath = path.join(bundledSkillsDir, 'using-sphere-workflow', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;

    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);

    const toolMapping = `**Tool Mapping for OpenCode:**
When bundled skills reference tools you do not have, substitute OpenCode equivalents:
- \`TodoWrite\` -> \`update_plan\`
- \`Task\` with subagents -> OpenCode subagents via \`@mention\`
- \`Skill\` tool -> OpenCode's native \`skill\` tool
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` -> your native tools

**Skills location:**
Bundled sphere-workflow skills are in \`${configDir}/skills/sphere-workflow/\`
Use OpenCode's native \`skill\` tool to load follow-up skills after bootstrap.`;

    return `<EXTREMELY_IMPORTANT>
You have sphere workflow.

**IMPORTANT: The using-sphere-workflow skill content is included below. It is already loaded bootstrap context. Do not load using-sphere-workflow again unless the user explicitly asks for it.**

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    'experimental.chat.system.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (bootstrap) {
        (output.system ||= []).push(bootstrap);
      }
    }
  };
};
