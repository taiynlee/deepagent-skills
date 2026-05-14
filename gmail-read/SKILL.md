---
name: gmail-read
description: "讀取 Gmail 信箱的最新郵件。需要 GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 存在於 .env 檔案中。觸發時機：用戶要求查看郵件、查看 email、讀取 Gmail。"
license: MIT
compatibility: designed for deepagents-cli
---

# Gmail 讀取技能

## 使用條件

- `.env` 檔案需包含以下變數：
  - `GOOGLE_REFRESH_TOKEN`
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`

## 執行方式

使用 Python 搭配 google-api-python-client 庫：

```python
import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 讀取 .env
with open('.env') as f:
    for line in f:
        if line.startswith('GOOGLE_REFRESH_TOKEN='):
            refresh_token = line.split('=')[1].strip()
        elif line.startswith('GOOGLE_CLIENT_ID='):
            client_id = line.split('=')[1].strip()
        elif line.startswith('GOOGLE_CLIENT_SECRET='):
            client_secret = line.split('=')[1].strip()

creds = Credentials(
    None,
    refresh_token=refresh_token,
    token_uri='https://oauth2.googleapis.com/token',
    client_id=client_id,
    client_secret=client_secret,
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

service = build('gmail', 'v1', credentials=creds)

# 取得最新郵件
results = service.users().messages().list(userId='me', maxResults=1).execute()
messages = results.get('messages', [])

if messages:
    msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(無主旨)')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), '(無寄件人)')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), '(無日期)')
    
    # 取得內文
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
        else:
            body = '(無純文字內文)'
    else:
        body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
    
    print(f'日期: {date}')
    print(f'寄件人: {sender}')
    print(f'主旨: {subject}')
    print(f'內文: {body[:500]}...' if len(body) > 500 else f'內文: {body}')
```

## 參數說明

- `maxResults`: 取得郵件數量，預設 1
- `format`: 可選 `full` (完整資訊), `metadata` (僅標頭), `minimal` (僅 ID)