#!/bin/bash
# Find-Skills 更新腳本
# 用於同步已安裝的 skills 清單到本地

SKILL_DIR="$HOME/.deepagents/agent/skills/find-skills"
SKILLS_FILE="$SKILL_DIR/references/skills.md"

echo "$(date): 開始更新 find-skills 清單..."

# 更新本地 skills 清單
skills list > "$SKILLS_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): 更新成功！檔案大小: $(wc -c < "$SKILLS_FILE") bytes"
else
    echo "$(date): 更新失敗！" >&2
    exit 1
fi