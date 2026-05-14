---
name: public-apis
description: public-apis 是一個開源的免費 API 列表專案，收錄了各類免費公開的 API。當用戶需要：(1) 查詢某類 API、(2) 找免費 API 資源、(3) 了解某個 API 的資訊、(4) 查詢 public-apis 的相關問題。
---

# Public APIs Skill

## 簡介

[public-apis/public-apis](https://github.com/public-apis/public-apis) 是一個社群維護的開源專案，收錄免費公開的 API。

## 使用方式

### 查詢 API

```bash
# 查詢 README 內容（包含完整分類清單）
curl -s "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
```

### 常用分類關鍵字

| 分類 | 關鍵字 |
|------|--------|
| 股票/金融 | `stock`, `finance`, `market` |
| 鐵路/交通 | `train`, `railway`, `transport` |
| 天氣 | `weather` |
| 加密貨幣 | `crypto`, `coin` |
| 匯率 | `forex`, `currency` |

### 搜尋範例

```bash
# 查金融相關 API
curl -s "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md" | grep -i -B1 -A1 "finance"

# 查火車相關 API
curl -s "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md" | grep -i -B1 -A1 "train\|railway"
```

## 自動更新

### 更新 API 清單

```bash
# 更新本地快取
~/.deepagents/agent/skills/public-apis/scripts/update.sh
```

### 設定自動更新 (Cron)

```bash
# 每天凌晨 3 點自動更新
(crontab -l 2>/dev/null; echo "0 3 * * * ~/.deepagents/agent/skills/public-apis/scripts/update.sh >> ~/.deepagents/agent/skills/public-apis/update.log 2>&1") | crontab -
```

## 資料位置

- API 清單快取：`references/apis.md`
- 更新腳本：`scripts/update.sh`

## 注意事項

- 此清單為社群維護，可能有不完整或過時的資訊
- 使用前建議確認 API 是否仍可正常運作
- 某些 API 需要付費或 API Key