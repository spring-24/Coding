PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS chapter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    word_count INTEGER NOT NULL DEFAULT 0,
    imported_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE(title, file_path)
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS word (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cid INTEGER NOT NULL,
    term TEXT NOT NULL,
    mean TEXT NOT NULL,
    UNIQUE(cid, term),
    FOREIGN KEY (cid) REFERENCES chapter(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    cid INTEGER NOT NULL,
    mode TEXT NOT NULL DEFAULT 'word',
    total INTEGER NOT NULL DEFAULT 0,
    correct INTEGER NOT NULL DEFAULT 0,
    cpm REAL NOT NULL DEFAULT 0,
    acc REAL NOT NULL DEFAULT 0,
    sec REAL NOT NULL DEFAULT 0,
    started TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    ended TEXT,
    FOREIGN KEY (uid) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (cid) REFERENCES chapter(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sid INTEGER NOT NULL,
    wid INTEGER NOT NULL,
    typed TEXT NOT NULL,
    correct INTEGER NOT NULL CHECK(correct IN (0,1)),
    cpm REAL NOT NULL DEFAULT 0,
    sec REAL NOT NULL DEFAULT 0,
    logged TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (sid) REFERENCES session(id) ON DELETE CASCADE,
    FOREIGN KEY (wid) REFERENCES word(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS passage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('short', 'long')),
    text TEXT NOT NULL UNIQUE,
    source TEXT,   -- 문장을 가져온 파일 경로 (txt/pdf 우선 출제용)
    topic TEXT,    -- 주제 (긴 글 목록을 주제별로 묶어 보여주기 위함)
    title TEXT,    -- 예제 제목
    imported_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS passage_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    ptype TEXT NOT NULL CHECK(ptype IN ('short', 'long')),
    count INTEGER NOT NULL DEFAULT 0,
    cpm REAL NOT NULL DEFAULT 0,
    acc REAL NOT NULL DEFAULT 0,
    sec REAL NOT NULL DEFAULT 0,
    started TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    ended TEXT,
    FOREIGN KEY (uid) REFERENCES user(id) ON DELETE CASCADE
);

-- 타자 검정(단어 검정 / 문장 검정) 결과
CREATE TABLE IF NOT EXISTS test_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL,
    mode TEXT NOT NULL CHECK(mode IN ('word', 'sentence')),
    total INTEGER NOT NULL DEFAULT 0,   -- 전체 문제 수 (단어 수 / 줄 수)
    correct INTEGER NOT NULL DEFAULT 0,   -- 맞힌 문제 수
    score INTEGER NOT NULL DEFAULT 0,   -- 최종 점수 (100점 만점)
    cpm REAL NOT NULL DEFAULT 0,
    acc REAL NOT NULL DEFAULT 0,
    sec REAL NOT NULL DEFAULT 0,
    timeout INTEGER NOT NULL DEFAULT 0,   -- 시간 초과로 종료되었으면 1
    started TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (uid) REFERENCES user(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_chapter_uniq ON chapter(title, file_path);
CREATE INDEX IF NOT EXISTS idx_word ON word(cid);
CREATE INDEX IF NOT EXISTS idx_log ON log(sid);
CREATE INDEX IF NOT EXISTS idx_session ON session(uid);
CREATE INDEX IF NOT EXISTS idx_passage ON passage(type);
CREATE INDEX IF NOT EXISTS idx_passage_session ON passage_session(uid);
CREATE INDEX IF NOT EXISTS idx_test_session ON test_session(uid);
