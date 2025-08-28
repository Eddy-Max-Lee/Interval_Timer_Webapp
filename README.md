# 間歇時鐘網頁版
一款可在桌機與手機瀏覽器流暢使用的「間歇時鐘」Web App，協助所有貢獻者和使用者維持健康
支援三大分頁：

1. **社群 Community**：瀏覽並複製他人「公開」的時鐘到個人庫。
2. **團隊 Your Team**：本期顯示「開發中」，預留團隊協作介面與權限架構。
3. **個人 Your Timer**：建立/編輯/播放自己的最多 10 個時鐘（每個時鐘由多個「計時段/Stage」組成）。

同時滿足：中文語音播報（段落名稱、倒數、報秒頻率）、上傳與混音背景音樂（BGM）、離線可用（PWA）。

---

## 一、技術選型（Python優先）

### 推薦主架構（Django 方案）

- **Django 5 + Django REST Framework (DRF)**：快速搭建權限、Admin、API；資料一致性強。
- **資料庫**：PostgreSQL（推薦）或 MySQL；開發期可 SQLite。
- **即時/推播**：Django Channels + Redis（預留給日後多人同步/直播倒數；單人計時以前端為主）。
- **前端**：
    - **HTMX + Alpine.js + Tailwind CSS**（Python 開發者友善、輕量）、或
    - **React + Vite + Tailwind**（若團隊偏好SPA）。
- **檔案儲存**：本機或 S3（`django-storages`）。
- **PWA**：Service Worker + Web App Manifest，支援離線與安裝。
- **部署**：Docker（gunicorn+uvicorn worker / nginx 反向代理）。

> 若更偏 API 驅動與微服務：FastAPI + SQLAlchemy/SQLModel + Uvicorn + Alembic + （前端同上）。
> 

### 主要 Python 套件

- Web 與 API：`Django`, `djangorestframework`, `django-allauth`（社群登入可選）, `django-cors-headers`
- 儲存/雲端：`django-storages`, `boto3`
- 即時：`channels`, `channels-redis`
- 媒體處理：`pydub`（伺服器端音檔處理，非必須）, `Pillow`（封面圖）
- 驗證/Schema：`pydantic`（若 FastAPI）
- 文字轉語音（伺服器備援，可選）：`edge-tts` 或各雲端 SDK（Azure/Google），但**預設以瀏覽器 Web Speech API 為主**

### 前端 Web API 與瀏覽器能力

- **Web Speech API（speechSynthesis）**：中文（含繁中/國語）語音播報；
- **Web Audio API**：
    - BGM 播放與音量控制；
    - 「蜂鳴/提示音」與 **精準排程**（以 `AudioContext.currentTime` 排程事件，避免 `setTimeout` 漂移）。
- **Screen Wake Lock API**（可選）：防止螢幕睡眠（行動端需使用者手勢觸發）。
- **Service Worker / Cache Storage**：離線支援、安裝捷徑。

---

## 二、系統架構總覽

**客戶端（PWA）**

- UI（HTMX/React）
- Timer Engine（以 Web Audio API 為心臟，負責準確排程/倒數/播報）
- Speech 層（優先瀏覽器 TTS；若不可用→呼叫後端 TTS 取得音檔）
- 本地資料：IndexedDB（離線快取使用者的時鐘配置與最近使用音檔索引）

**伺服器**

- REST API（CRUD、分享/複製、搜尋、上傳）
- Auth（Email/社群登入）
- 檔案服務（BGM 上傳、轉碼/驗證）
- 後備 TTS（選用）
- Admin 後台（審核、內容管理、黑名單）

---

## 三、資訊模型（資料庫設計）

### 1) User 與團隊

- `users_user`: id, email, name, avatar, created_at, updated_at
- `teams_team`（預留）：id, name, owner_id, created_at
- `teams_membership`（預留）：id, team_id, user_id, role (owner|editor|viewer)

### 2) 時鐘（Clock）與階段（Stage）

- `timers_clock`
    - id, user_id (擁有者)
    - name（時鐘名稱）
    - repeat_count（整組重複次數）
    - is_public（公開/私人；預設 false）
    - cover_image_url（可選）
    - bgm_asset_id（BGM 關聯，可空）
    - tags（陣列/多對多）
    - forked_from_clock_id（來源 clock，支援「加入到我的」）
    - usage_stats（收藏/播放次數等）
    - created_at, updated_at
- `timers_stage`
    - id, clock_id, order_index（序）
    - name（段落名稱，播報用）
    - duration_ms（毫秒，或秒 int）
    - tts_enabled（是否開啟語音）
    - tts_voice_preset（可選："auto-zh-TW" 等）
    - speak_every_sec（報秒頻率；0=不報秒，n=每 n 秒報一次）
    - countdown_speak_from_sec（開始倒數讀出的時間點；如 10 表示最後 10 秒開始每秒倒數）
    - cue_beep_last_n_sec（尾段蜂鳴提示秒數；例如最後 3 秒每秒嗶一聲）
    - bgm_volume（此段相對 BGM 音量 0~100，可覆寫全局）
    - voice_volume（TTS 音量 0~100）
    - voice_rate（語速 0.5~2.0）
    - voice_pitch（音高 0.5~2.0）

### 3) 媒體/社群

- `media_asset`
    - id, user_id, kind ("bgm"|"cover"|"tts_cache")
    - url, mime_type, duration_ms, size_bytes, created_at
- `social_like`：id, user_id, clock_id, created_at
- `social_comment`（可選）
- `social_report`（檢舉，含原因）
- `taxonomy_tag` 與 `clock_tags`（多對多關聯）

> 規則：每位使用者最多 10 個 Clock（DB constraint + 服務端驗證 + 前端提醒）。
> 

---

## 四、API 介面（範例）

- `POST /api/auth/*`：登入/註冊/社群登入（allauth）
- `GET /api/clocks?public=true&search=...&tag=...&sort=popular`（社群列表）
- `POST /api/clocks`（建立 clock；若>10 拒絕）
- `GET /api/clocks/:id`（讀取，權限控管：公開或本人/團隊可讀）
- `PUT /api/clocks/:id`（更新基本屬性：名稱、repeat_count、is_public、bgm 等）
- `DELETE /api/clocks/:id`（刪除）
- `POST /api/clocks/:id/fork`（加入到我的）
- `GET /api/clocks/:id/stages` / `POST` / `PUT` / `DELETE`（維護段落）
- `POST /api/upload/bgm`（上傳 BGM，回傳 `asset_id`）
- `GET /api/search/suggest`（標籤/熱門搜尋詞）
- `GET /api/limits`（回傳當前使用者時鐘數、限制等等）

> 前端播報與計時在客戶端執行（精準排程），API 僅負責配置與分享。
> 

---

## 五、前端資訊架構與頁面流程

### 全站導覽

- 頁首：Logo｜**Community**｜**Your Team（開發中）**｜**Your Timer**｜搜尋（社群）｜個人頭像（登入/設定）
- 快速行動：右下角**＋建立時鐘**（Your Timer 頁亦提供）

### A. 社群（Community）

**目的**：瀏覽所有公開時鐘、預覽、收藏、加入到我的。

- **上方工具列**：篩選（標籤、多選：HIIT、瑜珈、番茄鐘等）、排序（熱門/最新/播放多）、搜尋框。
- **卡片**（每個公開時鐘）
    - 封面/波形縮圖（可選）、名稱、作者、標籤、收藏數/被加入數
    - 按鈕：**預覽**、**加入到我的**（fork）、**詳情**
- **預覽對話框**
    - 簡表：總時長、重複次數、段落清單
    - **試播**（僅播放 1~2 段，避免自動播放規範問題，需要使用者點擊）
    - 加入到我的（成功→導向 Your Timer 清單）

### B. 團隊（Your Team）

- 首版：**「開發中」** Badge、功能預告（成員管理、共編、版本鎖等），引導追蹤更新。

### C. 個人（Your Timer）

- **清單**：最多十張卡片（已建立的時鐘）；空位顯示「＋ 新增」。
    - 卡片資訊：名稱、總時長、段數、重複次數、是否公開、BGM 標記
    - 行為：**播放**、**編輯**、**公開切換**、**刪除**、**匯出 JSON**、**複製**
- **建立流程**：
    1. 點「＋ 新增」→ 輸入名稱（必填），可先設 `repeat_count`
    2. 進入**編輯頁**（如下）

### 編輯頁（Stage Editor）

- **左側**：時鐘基本屬性（即時保存開關）
    - 名稱、重複次數（1~999）
    - 是否公開（預設私人）
    - 背景音樂：上傳/移除、全局 BGM 音量
    - 測試：**播放/暫停**、音量、蜂鳴測試、**語音測試**（選擇中文女聲/男聲、語速、音高）
- **主區：段落時間軸**（垂直列表或水平時間軸）
    - 每段（Stage）卡片包含：
        - **時間（秒/分:秒）**（必填）
        - **名稱**（播報詞；可空→以「第N段」）
        - 語音：開關、語音預設（自動 zh-TW）、語速/音高/音量
        - **報秒頻率**（0=不報；或 5/10/15/30…）
        - **倒數播報啟始秒數**（如 10 表示最後 10 秒：10、9、8…）
        - **尾段蜂鳴**（最後 N 秒每秒嗶）
        - **此段 BGM 音量覆寫**（可不設）
        - 操作：上/下移、複製、刪除
    - 頂端工具：**＋ 新增段落**、**批次新增**（貼上 CSV/多行「名稱,秒」）
- **右下固定工具列**：**儲存**、**試播整組**、**匯出 JSON**、**回個人清單**

### 播放頁（Player）

- 大型圓形倒數（顯示目前段落剩餘時間）+ 進度環（全程進度）
- 當前段資訊：名稱、此段時長、當前循環（例如 2/4）
- 控制列：**播放/暫停/停止**、上一段/下一段、靜音（TTS/BGM 分離）
- 功能：
    - 語音播報：開始唸「名稱」→按設定的報秒頻率與倒數規則播報
    - 蜂鳴：最後 N 秒每秒短嗶；段落切換短聲提示
    - BGM：全局或逐段音量
    - 重複：整組完成自動依 `repeat_count` 次數重跑

---

## 六、體驗細節與規則

1. **最大 10 個時鐘限制**：
    - 建立前先查詢/快取使用者數量；到 10 時灰化「＋ 新增」，並在社群頁的「加入到我的」動作時提示先刪除/匯出。
2. **語音策略**：
    - 預設優先 **瀏覽器 Web Speech API**（Chrome/Edge 良好，Safari 需測試）。
    - 若偵測不到可用語音（或使用者指定雲端高品質），後端提供 TTS 轉檔（快取）回傳音檔，由前端播放與排程。
3. **時間準確性**：
    - 使用 **Web Audio API 的精準排程**（`AudioContext` 定時器 + `setInterval` 作 UI 更新），避免 `setTimeout` 漂移。
    - 倒數播報與蜂鳴嚴格對齊 `AudioContext.currentTime`。
4. **行動端限制**：
    - 需使用者手勢啟動音訊（首次播放需點擊）。
    - 提供「螢幕常亮」提示（可選擇使用 Wake Lock）。
5. **離線**：
    - PWA 快取核心頁面與最近編輯的 JSON；BGM 不做離線預設（可選擇「離線保存此 BGM」）。
6. **可存取性（a11y）**：
    - 鍵盤操作、ARIA 標記；色彩對比；聽障模式（語音→文字提示、震動 API）。

---

## 七、Timer Engine（前端）設計

**核心目標**：在瀏覽器中以高準度與低抖動管理「多段落 + 語音/蜂鳴/BGM + 倒數/報秒」的排程。

- **排程器**：
    - 每段開始時：
        - 若 `tts_enabled`：先播報段名（語音或 TTS 音檔）
        - 設置報秒節點：`speak_every_sec > 0` → 安排 t= n, 2n, 3n… 的播報
        - 設置倒數節點：最後 `countdown_speak_from_sec` 開始每秒播報
        - 設置蜂鳴節點：最後 `cue_beep_last_n_sec` 每秒嗶
    - 時間源：Web Audio `currentTime`，以短期 lookahead（例如 0.2s）+ `setInterval(50ms)` 填入即將到期的事件到 Audio graph/隊列
- **音量 Ducking**：播報時暫時降低 BGM 音量（ducking），讓語音更清晰（比例與時長可調）
- **錯誤容忍**：若語音未能即時開始（瀏覽器限制），改用蜂鳴+視覺提示，並提示使用者允許音訊。

---

## 八、屬性與UI欄位（匯總）

### Clock（時鐘）層

- 名稱、重複次數（整組重複）、公開/私人、封面（可選）、BGM（檔案/URL）、全局 BGM 音量
- 匯出/匯入 JSON（便於分享/備份）

### Stage（段落）層

- 時長（秒/分:秒）、名稱、語音開關、語音預設/音量/語速/音高
- 報秒頻率（0/5/10/15/30…）
- 倒數播報啟始秒（例如 10）
- 尾段蜂鳴（最後 N 秒）
- 段落 BGM 音量覆寫（可空）

> 皆提供 即時測試 與 重置 按鈕。
> 

---

## 九、社群工作流（Public → Mine）

1. 使用者在 **Community** 找到喜歡的公開時鐘 → 點「預覽」。
2. 若滿意 → **加入到我的**：
    - 伺服器建立一份 fork（擁有者=當前使用者，`forked_from_clock_id` 記錄來源）。
    - 若已達 10 份 → 提示需刪除或匯出備份。
3. 到 **Your Timer** 編輯或直接播放。

> 來源作者的統計「被加入次數」增加；若有標籤/關鍵字也一併帶入。
> 

---

## 十、權限與安全

- 私人與公開隔離；私人連結不可直接存取（檢查 owner）。
- 上傳檔案型別白名單（mp3, m4a, wav），限制大小（例如 20MB）。
- 內容政策與檢舉機制（社群面）。
- Rate limiting（API）與 CSRF/同源策略（Django 既有機制）。

---

## 十一、PWA 與離線

- **manifest.json**：名稱、圖標、display: standalone。
- **Service Worker**：
    - Cache：核心 HTML/CSS/JS、字型、圖示
    - 後台更新：新版本提示
    - （可選）離線 BGM 的 IndexedDB 儲存與版本管理

---

## 十二、測試與品質

- 單元測試（Django / pytest）
- E2E（Playwright）：建立/編輯/播放/倒數/報秒/蜂鳴 行為
- Lighthouse：PWA、可存取性、效能
- 行動裝置真機測試：iOS/Safari、Android/Chrome

---

## 十三、部署建議

- Docker Compose：web（Django）、db（Postgres）、redis（Channels）
- 反向代理：Nginx，提供 HTTPS 與 gzip/brotli
- 媒體：S3/CloudFront 或本機 NFS
- CI/CD：GitHub Actions（lint、test、build、deploy）

---

## 十四、擴充藍圖（團隊頁未來）

- 團隊資料夾、權限（擁有者/編輯/檢視）
- 時鐘共編（stage 鎖/版本）
- 同步播放（教室/健身房廣播，同步開始）
- 直播房：主持人控制、成員跟播

---

## 十五、匯出/匯入 JSON（範例）

{

"name": "Tabata 8輪",

"repeat_count": 2,

"is_public": false,

"bgm_asset_id": null,

"stages": [

{"order":1, "name":"Warm-up", "duration_sec":60, "tts_enabled":true, "speak_every_sec":0, "countdown_speak_from_sec":10, "cue_beep_last_n_sec":3},

{"order":2, "name":"Work", "duration_sec":20, "tts_enabled":true, "speak_every_sec":10, "countdown_speak_from_sec":10, "cue_beep_last_n_sec":3},

{"order":3, "name":"Rest", "duration_sec":10, "tts_enabled":true, "speak_every_sec":0, "countdown_speak_from_sec":5,  "cue_beep_last_n_sec":3}

]

}

---

## 十六、UI 元件清單（Tailwind/HTMX/Alpine）

- 分頁導覽(Tab)
- 卡片（Clock/Community）
- 時間輸入（mm:ss 轉秒）
- Toggles/Sliders（音量、語速、音高）
- 可排序列表（Drag & Drop，可用 `SortableJS` 或 `@dnd-kit` 若 React）
- 模態窗（預覽、刪除確認）
- Toaster（操作回饋）

---

## 十七、最小可行版本（MVP）里程碑

**M1**（2 週）

- Your Timer：建立/編輯/播放；段落語音（Web Speech）、蜂鳴、BGM；PWA 基本

**M2**（+2 週）

- Community：公開/私有、列表、搜尋/標籤、加入到我的

**M3**（+2 週）

- 匯出/匯入 JSON、封面圖、Like/收藏統計、後台管理

> 之後迭代 Team 協作、同步播報。
> 

---

### 備註：中文語音品質

- 瀏覽器 Web Speech 在 Chrome/Edge 表現佳（`Microsoft HanHan (zh-TW)` 等）；Safari 需實測。
- 若教學/健身場景要求高品質穩定性，建議提供「雲端 TTS」切換選項並快取音檔（避免延遲）。


