# Chat Summary — 2026-04-04

## Session 1: CLAUDE.md Setup

### What was done

- Created root-level [CLAUDE.md](../../CLAUDE.md) for the repo. It covers setup, key entry points, submodule descriptions, configuration, and the session summary convention.
- Assessed whether the submodule CLAUDE.md files (`youtube-downloader-app/CLAUDE.md` and `ytdownload/CLAUDE.md`) were still necessary — concluded yes, because Claude Code loads them hierarchically and they contain implementation-level detail not in the root (CLI flags, API internals, quota costs, hallucination filter thresholds, etc.).
- Removed the duplicate **Session Summaries** section from both submodule CLAUDE.md files, since it is now covered at the root level.
- Discussed the `CLAUDE_CODE_NEW_INIT=1` flag, which enables an interactive multi-phase `/init` flow (artifact selection, subagent codebase exploration, gap-filling questions, reviewable proposal before writing). Covered how to set it temporarily via `CLAUDE_CODE_NEW_INIT=1 claude` or permanently via `claude config set env.CLAUDE_CODE_NEW_INIT 1`, and for VS Code via `terminal.integrated.env.osx` in settings JSON.

## Session 2: Skills, Hooks, and Repo Fixes

- Fixed `ytdownload/claude.md` git tracking: renamed to `ytdownload/CLAUDE.md` via `git mv` so git tracks the correct case.
- Confirmed `.gitignore` is respected — verified no ignored files were touched or suggested for commit.
- Discussed `Stop` vs `SessionEnd` hooks for a session summary reminder: `Stop` fires after every response (too noisy); `SessionEnd` fires at session close but can't accept user input. Decided against a hook.
- Created `/summary` skill at `~/.claude/skills/summary/SKILL.md` — writes today's session summary to `_doc/claude_summaries/chat-summary_YYYY-MM-DD.md`, appending a new numbered section if the file already exists.
- Diagnosed why `/summary` wasn't appearing: wrong directory (`~/.claude/skills/` flat file), wrong filename, then missing frontmatter. Key finding: VS Code extension requires a full restart to pick up new skills — live reload does not work.

**What worked — correct steps to add a user-level skill:**

1. `mkdir -p ~/.claude/skills/<skill-name>`
2. Create `~/.claude/skills/<skill-name>/SKILL.md` with YAML frontmatter followed by instructions:

   ```yaml
   ---
   name: skill-name
   description: One-line description of what it does and when to use it
   ---
   Instructions here...
   ```

3. Quit and restart VS Code entirely — the VS Code extension does not pick up new skills via live reload.

## Session 3: Docs and Notes

- Added entry to `_doc/programming_notes.md` covering Claude Code custom skills: project vs user level, `SKILL.md` format, creation steps, documentation link, and how to prompt Claude to suggest skills for a project.

## Session 4: CLAUDE.md Updates and /docupdate Skill

- Added three rules to root `CLAUDE.md` based on `/insights` recommendations:
  - **General Rules** (top): check existing code/files before suggesting external tools
  - **After Every Change**: update CHANGELOG, README, CLAUDE.md, and chat summary after any code change
  - **Development Environment**: target macOS bash 3.2; avoid bash 4+ features
- Created `/docupdate` skill (`~/.claude/skills/docupdate/SKILL.md`) — project-level initially, moved to user-level. Triggers a full doc update pass (CHANGELOG, README, CLAUDE.md, chat summary) with user confirmation before writing. Has `disable-model-invocation: true` so it only runs when explicitly invoked.
