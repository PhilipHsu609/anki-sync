# Obsidian Note Structure

This document describes the expected YAML frontmatter and markdown structure for LeetCode notes that will be synced to Anki.

---

## File Naming Convention

```
<number>. <title>.md
```

Example: `239. Sliding Window Maximum.md`

- The number is extracted as the problem number
- The title is extracted as the problem title

---

## Required YAML Frontmatter

```yaml
---
tags:
  - algorithm/two-pointer
  - data-structure/array
---
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tags` | list | ✓ | Tags with configured prefixes (e.g., `algorithm/`, `data-structure/`) |

**Note:** Only tags with configured prefixes (from `config.yaml`) will be displayed on the Anki card as pattern tags.

---

## Markdown Content Structure

The sync tool extracts specific sections from your markdown content:

### 1. LeetCode Link (Required)

```markdown
🔗 [LeetCode](https://leetcode.com/problems/trapping-rain-water/description)
```

- Must contain a link with text "LeetCode" pointing to the problem URL
- This URL is used to fetch problem description, examples, and constraints from LeetCode API

### 2. Key Insight (Required)

```markdown
## Key Insight

> [!tip]- What's the trick?
> Water trapped at position depends on minimum of max heights to its left and right. Use two pointers moving inward, tracking max heights from both ends.
```

- Section header: `## Key Insight`
- Key insight must be in an Obsidian callout: `> [!tip]- What's the trick?`
- Content after the callout header is extracted
- Supports markdown formatting and LaTeX math

### 3. Derivation (Optional)

```markdown
## Derivation

1. Water trapped at index $i$ equals: $\min(\text{maxLeft}[i], \text{maxRight}[i]) - \text{height}[i]$
2. We can avoid precomputing all max values by using two pointers
    - Track running maximum from left side
    - Track running maximum from right side
3. Move pointer with smaller max height inward
    - The side with smaller max determines water level
    - Safe to calculate water at that position
```

- Section header: `## Derivation`
- **Optional section** - only include if problem requires detailed derivation
- Supports ordered/unordered lists with nested items
- Supports markdown formatting and LaTeX math
- Extracted until next `##` heading

### 4. Algorithm

```markdown
## Algorithm

1. Initialize LEFT and RIGHT pointers at both ends
2. Initialize MAXLEFT and MAXRIGHT to track maximum heights
3. Initialize RESULT to accumulate trapped water
4. WHILE LEFT < RIGHT:
    1. IF height[LEFT] < height[RIGHT]:
        - Update MAXLEFT with current height
        - Add trapped water: MAXLEFT - height[LEFT]
        - Move LEFT pointer inward
    2. ELSE:
        - Update MAXRIGHT with current height
        - Add trapped water: MAXRIGHT - height[RIGHT]
        - Move RIGHT pointer inward
5. RETURN total water trapped
```

- Section header: `## Algorithm`
- Supports ordered/unordered lists with nested items
- Supports markdown formatting
- Extracted until next `##` heading or code block (```)

### 5. Complexity

```markdown
## Complexity

- **Time:** $O(n)$ - single pass through array
- **Space:** $O(1)$ - only use constant extra space
```

- Section header: `## Complexity`
- Supports LaTeX math notation
- Can be single line or multiple bullet points

---

## Complete Example

File: `42. Trapping Rain Water.md`

```markdown
---
tags:
  - algorithm/two-pointer
  - data-structure/array
---

# 42. Trapping Rain Water

🔗 [LeetCode](https://leetcode.com/problems/trapping-rain-water/description)

---

## Key Insight

> [!tip]- What's the trick?
> Water trapped at position depends on minimum of max heights to its left and right. Use two pointers moving inward, tracking max heights from both ends.

---

## Derivation

1. Water trapped at index $i$ equals: $\min(\text{maxLeft}[i], \text{maxRight}[i]) - \text{height}[i]$
2. We can avoid precomputing all max values by using two pointers
    - Track running maximum from left side
    - Track running maximum from right side
3. Move pointer with smaller max height inward
    - The side with smaller max determines water level
    - Safe to calculate water at that position

## Algorithm

1. Initialize LEFT and RIGHT pointers at both ends
2. Initialize MAXLEFT and MAXRIGHT to track maximum heights
3. Initialize RESULT to accumulate trapped water
4. WHILE LEFT < RIGHT:
    1. IF height[LEFT] < height[RIGHT]:
        - Update MAXLEFT with current height
        - Add trapped water: MAXLEFT - height[LEFT]
        - Move LEFT pointer inward
    2. ELSE:
        - Update MAXRIGHT with current height
        - Add trapped water: MAXRIGHT - height[RIGHT]
        - Move RIGHT pointer inward
5. RETURN total water trapped

## Complexity

- **Time:** $O(n)$ - single pass through array
- **Space:** $O(1)$ - only use constant extra space

## Implementation

\`\`\`python
# Implementation code here (NOT synced to Anki)
\`\`\`
```

---

## What Gets Synced to Anki

**Automatically fetched from LeetCode API:**
- Problem description
- Examples (Input/Output/Explanation)
- Constraints

**From your Obsidian note:**
- Problem number (from filename)
- Problem title (from filename)
- Key Insight (required - from callout)
- Derivation (optional - if `## Derivation` section exists)
- Algorithm (required - from `## Algorithm` section)
- Complexity (required - from `## Complexity` section)
- Pattern tags (from frontmatter tags matching configured prefixes)

**NOT synced:**
- Implementation code (focus is on understanding approach, not memorizing code)
