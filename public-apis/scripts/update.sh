#!/bin/bash
# Public APIs 更新腳本
# 用於同步最新的 API 清單到本地

SKILL_DIR="$HOME/.deepagents/agent/skills/public-apis"
API_FILE="$SKILL_DIR/references/apis.md"

echo "$(date): 開始更新 public-apis 清單..."

# 下載最新 README
curl -s "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md" -o "$API_FILE"

if [ $? -eq 0 ]; then
    echo "$(date): 更新成功！檔案大小: $(wc -c < "$API_FILE") bytes"
else
    echo "$(date): 更新失敗！" >&2
    exit 1
fi