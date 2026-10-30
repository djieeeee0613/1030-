-- 活動報名平台(基本款) 資料庫（PostgreSQL）
--
-- 【步驟 1】先建立資料庫（只需做一次）。在 Adminer 登入 postgres 後，開「SQL command」執行：
--     CREATE DATABASE ruins_events ENCODING 'UTF8' TEMPLATE template0;
--   （或用 psql：psql -U postgres -c "CREATE DATABASE ruins_events ENCODING 'UTF8' TEMPLATE template0;"）
--
-- 【步驟 2】進入 ruins_events 資料庫，匯入本檔（Adminer 的 Import，或 SQL command 貼上執行）：
--     psql -U postgres -d ruins_events -f database.sql
--   可重複匯入，會先刪除舊的兩張表再重建。

SET client_encoding = 'UTF8';

-- 先刪子表再刪父表，方便重複匯入
DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS events;

-- 活動表: 對應「新增新的活動」「列出可報名的活動清單」
CREATE TABLE events (
  event_id    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title       VARCHAR(100) NOT NULL,                 -- 活動名稱
  description TEXT,                                  -- 活動說明
  location    VARCHAR(150),                          -- 活動地點
  event_date  TIMESTAMP NOT NULL,                    -- 活動日期時間
  status      VARCHAR(10) NOT NULL DEFAULT 'open'    -- open=可報名, closed=截止
              CHECK (status IN ('open', 'closed')),
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 報名表: 對應「填寫報名表(姓名、連絡電話)」「查看活動的報名清單」
CREATE TABLE registrations (
  registration_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id        INT NOT NULL                       -- 報名的活動
                  REFERENCES events(event_id) ON DELETE CASCADE ON UPDATE CASCADE,
  name            VARCHAR(50) NOT NULL,              -- 姓名
  phone           VARCHAR(20) NOT NULL,              -- 連絡電話
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reg_event ON registrations (event_id);

-- 測試資料（3 個可報名的 demo 活動）
INSERT INTO events (title, description, location, event_date, status) VALUES
  ('程式設計入門工作坊', '從零開始學 Python，請自備筆電。',           '資訊大樓 301 教室', '2026-11-15 19:00:00', 'open'),
  ('校園攝影散步',       '跟著攝影社走訪校園，手機或相機皆可。',     '校門口集合',        '2026-11-22 09:00:00', 'open'),
  ('職涯分享講座',       '邀請業界學長姐分享求職與實習經驗。',       '圖書館國際會議廳',  '2026-12-06 14:00:00', 'open');

INSERT INTO registrations (event_id, name, phone) VALUES
  (1, '王小明', '0912345678'),
  (1, '李小華', '0923456789'),
  (2, '陳大文', '0934567890');

-- 常用查詢範例
-- 1) 列出可報名的活動清單
--    SELECT * FROM events WHERE status = 'open' ORDER BY event_date;
-- 2) 新增報名
--    INSERT INTO registrations (event_id, name, phone) VALUES (1, '姓名', '電話');
-- 3) 查看某活動的報名清單
--    SELECT name, phone, created_at FROM registrations WHERE event_id = 1 ORDER BY created_at;
