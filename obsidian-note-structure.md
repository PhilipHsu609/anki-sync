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
date: 2025-12-06T23:16
description:
tags:
  - algorithm/dynamic-programming
  - algorithm/prefix-sum
  - data-structure/queue
reviewed:
---
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tags` | list | ✓ | Tags with configured prefixes (e.g., `algorithm/`, `data-structure/`) |
| `date` | datetime | Optional | Note creation date |
| `description` | string | Optional | Brief description |
| `reviewed` | datetime | Optional | Last review date |

**Note:** Tags with configured prefixes (from `config.yaml`) will be displayed on the Anki card as pattern tags.

---

## Markdown Content Structure

The sync tool extracts specific sections from your markdown content:

### 1. LeetCode Link (Required)

```markdown
🔗 [LeetCode](https://leetcode.com/problems/sliding-window-maximum/description)
```

- Must contain a link with text "LeetCode" pointing to the problem URL
- This URL is used to fetch problem description, examples, and constraints from LeetCode API

### 2. Key Insight (Required)

```markdown
## Key Insight

> [!tip]- What's the trick?
> The core insight is to maintain a monotonic decreasing queue...
```

- Section header: `## Key Insight`
- Key insight must be in an Obsidian callout: `> [!tip]- What's the trick?`
- Content after the callout header is extracted
- Supports markdown formatting and LaTeX math

### 3. Derivation (Optional)

```markdown
## Derivation

1. Define $dp[i + 1]$ as the number of valid partition for $nums[0,i]$.
2. Identify the DP recurrence relation: $dp[i + 1] = dp[j] + \dots + dp[i]$
    - Use prefix sum.
3. If $nums[j,i]$ is a valid segment, then for each $j < L <= i$...
    - Use sliding window to keep track the $L$.
```

- Section header: `## Derivation`
- **Optional section** - only include if problem requires detailed derivation
- Supports ordered/unordered lists with nested items
- Supports markdown formatting and LaTeX math
- Extracted until next `##` heading

### 4. Algorithm

```markdown
## Algorithm

1. Initialize a list 'DP' to store partition counts
2. Set base case: DP[0] = 1 (1 way to partition nothing)
3. FOR each number 'X' in Sequence:
    1. UPDATE WINDOW
        - Include 'X' in the current window.
    2. SHRINK WINDOW (Constraint Check)
        - WHILE (Window.Max - Window.Min > K):
            - Remove elements from the start
```

- Section header: `## Algorithm`
- Supports ordered/unordered lists with nested items
- Supports markdown formatting
- Extracted until next `##` heading or code block (```)

### 5. Complexity

```markdown
## Complexity

- **Time:** $O(n)$
- **Space:** $O(n)$
```

- Section header: `## Complexity`
- Supports LaTeX math notation
- Can be single line or multiple bullet points

---

## Complete Example

File: `42. Trapping Rain Water.md`

```markdown
---
date: 2024-01-15T10:30
description: Calculate trapped rainwater using two-pointer approach
tags:
  - algorithm/two-pointer
  - data-structure/array
reviewed: 2024-02-01T14:20
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
