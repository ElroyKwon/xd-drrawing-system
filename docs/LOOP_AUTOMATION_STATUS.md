# Loop Automation Status

## Current Status

Hook automation is not implemented.

The current project supports a skill-driven manual or agent-led loop:

```text
development-loop-orchestrator
  -> project-bootstrap
  -> feature-docs-scaffold
  -> planning-gate
  -> implementation
  -> validator-loop
  -> evidence-report
```

## What Exists

- Local skills under `.agents/skills`
- Local skills under `.claude/skills`
- Loop documents in the project root
- Next-session handoff in `docs/sessions/NEXT_SESSION.md`
- Initial setup slice feature note

## What Does Not Exist Yet

- Warp pane automation script
- Codex/Claude auto-launch script
- File watcher
- Hook that automatically runs planning gate after document changes
- Hook that automatically runs validation after implementation

## Dependency Check

The machine has command-line entries for:

- `warp`
- `codex`
- `claude`
- `node`
- `npm`
- `git`

These commands make automation possible, but automation is not complete until scripts are written and verified.

## Next Automation Step

After the manual skill loop is proven on the initial setup slice, create a separate automation design for:

1. Warp terminal layout
2. Codex/Claude launch commands
3. File-change watcher
4. Gate result parser
5. Evidence recorder

Do not call the loop "automatic" until this file links to tested scripts and `EVIDENCE.md` contains results.
