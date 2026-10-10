---
description: Commit files in logical groups
model: haiku
allowed-tools: Bash(git:*)
---

Commit files in logical groups

Before committing, verify the staged set matches the intended logical group (`git diff --cached --stat`): edits made by file tools land in the working tree, not the index — stage them explicitly when the group includes them.
