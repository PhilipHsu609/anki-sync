# Obsidian Integration for Anki Sync

Multiple ways to sync from within Obsidian.

---

## Option 1: Templater Auto-sync

```javascript
<%*
// Auto-sync when note is created/modified
const exec = require('child_process').exec;
const syncPath = "/path/to/anki-sync";
const filePath = tp.file.path(true);

// This runs when template is applied
setTimeout(() => {
  exec(`cd ${syncPath} && python sync_to_anki.py "${filePath}"`,
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Sync error: ${error}`);
        return;
      }
      console.log(`Synced to Anki: ${stdout}`);
    }
  );
}, 2000); // Wait 2 seconds after save
%>
```

---

## Option 2: Shell Commands Plugin

1. **Settings → Shell Commands → New Command**
2. **Command:**
   ```bash
   cd /path/to/anki-sync && python sync_to_anki.py "{{file_path:absolute}}"
   ```
3. **Alias:** `Sync to Anki`
4. **Icon:** 📤
5. **Add to command palette:** ✓

Usage: `Ctrl+P` → "Sync to Anki"

---

## Option 3: Obsidian URI Handler

```
obsidian://shell-commands/?vault=YourVault&execute=sync-to-anki
```

---

## Option 4: Git Hook Integration

Create: `.git/hooks/post-commit`

```bash
#!/bin/bash

# Get changed files
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD)

# Filter LeetCode problems (adjust pattern to your structure)
LEETCODE_FILES=$(echo "$CHANGED_FILES" | grep "LeetCode/.*\.md$")

if [ -n "$LEETCODE_FILES" ]; then
    echo "🔄 Syncing LeetCode notes to Anki..."
    VAULT_PATH="/path/to/vault"
    SYNC_PATH="/path/to/anki-sync"

    cd "$SYNC_PATH"

    while IFS= read -r file; do
        python sync_to_anki.py "$VAULT_PATH/$file"
    done <<< "$LEETCODE_FILES"

    echo "✅ Anki sync complete"
fi
```

Make executable:
```bash
chmod +x .git/hooks/post-commit
```
