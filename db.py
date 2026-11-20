import re
import sqlite3
import openpyxl
from pathlib import Path
from datetime import datetime
from database.text_load import TextLoader

IMPORT_EXTS = {".xlsx"} | TextLoader.SUPPORTED_EXTS  # 가져오기 폴더에서 불러올 파일 확장자

class DB:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
            path = Path(__file__).parent / "vocab.db"
            conn = sqlite3.connect(str(path), check_same_thread = False)
            conn.row_factory = sqlite3.Row
            cls._inst._conn = conn
            cls._inst.init()
        return cls._inst

    def init(self):
        sql = (Path(__file__).parent / "db.sql").read_text(encoding = "utf-8")
        self._conn.executescript(sql)
        cols = [r["name"] for r in self._conn.execute("PRAGMA table_info(passage)")]
        for col in ("source", "topic", "title"):  # 예전 버전 DB에 없는 열은 추가함
            if col not in cols:
                self._conn.execute(f"ALTER TABLE passage ADD COLUMN {col} TEXT")
        self._conn.commit()

    def one(self, q, p = ()):
        return self._conn.execute(q, p).fetchone()

    def all(self, q, p = ()):
        return self._conn.execute(q, p).fetchall()

    def run(self, q, p = ()):
        cur = self._conn.execute(q, p)
        self._conn.commit()
        return cur.lastrowid

    def many(self, q, rows):
        self._conn.executemany(q, rows)
        self._conn.commit()

    # uid = 유저 관련 DB 코드임.
    def get_users(self):
        return self.all("SELECT * FROM user ORDER BY name")

    def add_user(self, name):
        try:
            return self.run("INSERT INTO user (name) VALUES (?)", (name,))
        except sqlite3.IntegrityError:
            return self.one("SELECT id FROM user WHERE name=?", (name,))["id"]

    def reset(self):
        self._conn.executescript("""
            PRAGMA foreign_keys = OFF;
            DELETE FROM log;
            DELETE FROM session;
            DELETE FROM passage_session;
            DELETE FROM test_session;
            DELETE FROM passage;
            DELETE FROM word;
            DELETE FROM chapter;
            DELETE FROM settings WHERE key = 'priority_text_files';
            PRAGMA foreign_keys = ON;
        """)
        self._conn.commit()

    # 설정(설정 메뉴) 관련 코드임 - 키/값 저장.
    def get_setting(self, key, default = None):
        row = self.one("SELECT value FROM settings WHERE key=?", (key,))
        return row["value"] if row else default

    def set_setting(self, key, value):
        self.run(
            "INSERT INTO settings (key, value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value)
        )

    # 단어장/예제 코드를 자동으로 읽어들일 폴더 경로를 설정하고, 해당 폴더 안의 모든 .xlsx 파일을 찾아 자동으로 불러옴.
    def get_import_dir(self):
        val = self.get_setting("import_dir")
        if val:
            return val
        default = str((Path(__file__).resolve().parent.parent / "data"))
        self.set_setting("import_dir", default)
        return default

    def set_import_dir(self, path):
        self.set_setting("import_dir", str(path))

    # cid = 챕터 관련한 코드임.
    def get_chapters(self):
        return self.all("SELECT * FROM chapter ORDER BY imported_at DESC")

    # 단어장으로 불러온 엑셀 파일 목록을 파일별로 집계해서 반환함 (파일 선택 메뉴용).
    def get_vocab_files(self):
        return self.all(
            "SELECT file_path, COUNT(*) as chapters, COALESCE(SUM(word_count),0) as words "
            "FROM chapter GROUP BY file_path ORDER BY MAX(imported_at) DESC"
        )

    def get_or_create_chapter(self, title, path):
        self.run("INSERT OR IGNORE INTO chapter (title, file_path) VALUES (?,?)", (title, str(path)))
        return self.one("SELECT id FROM chapter WHERE title=? AND file_path=?", (title, str(path)))["id"]

    def set_word_count(self, cid, count):
        self.run("UPDATE chapter SET word_count=? WHERE id=?", (count, cid))

    def del_chapter(self, cid):
        self.run("DELETE FROM chapter WHERE id=?", (cid,))

    # 단어 관련한 코드임.
    def get_words(self, cid):
        return self.all("SELECT * FROM word WHERE cid =? ORDER BY RANDOM()", (cid,))

    # 타자 검정(단어 검정) 코드 - 챕터 구분 없이 전체 단어장에서 무작위로 추출
    def get_random_words(self, limit):
        return self.all("SELECT * FROM word ORDER BY RANDOM() LIMIT ?", (limit,))

    def add_words(self, rows): # DB로 임시 저장한 단어를 전송하여 최종 저장함.
        """rows: [(cid, term, mean), ...]"""
        self.many(
            "INSERT OR IGNORE INTO word (cid, term, mean) "
            "VALUES (?,?,?)",
            rows
        )
        
    # 세션에 관련한 코드임.
    def add_session(self, uid, cid):
        return self.run("INSERT INTO session (uid, cid) VALUES (?,?)", (uid, cid))

    def end_session(self, sid, total, correct, cpm, acc, sec):
        self.run(
            "UPDATE session "
            "SET total = ?, correct = ?, cpm = ?, acc = ?, sec = ?, ended = ? "
            "WHERE id = ?",
            (total, correct, cpm, acc, sec,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sid)
        )

    def get_sessions(self, uid):
        return self.all(
            "SELECT s.*, c.title FROM session s "
            "JOIN chapter c ON c.id = s.cid "
            "WHERE s.uid = ? ORDER BY s.started DESC",
            (uid,)
        )

    # 타자 로그 기록에 대한 코드임.
    def add_log(self, sid, wid, typed, correct, cpm, sec):
        self.run(
            "INSERT INTO log (sid, wid, typed, correct, cpm, sec) "
            "VALUES (?,?,?,?,?,?)",
            (sid, wid, typed, int(correct), cpm, sec)
        )

    def get_wrong(self, uid):
        return self.all(
            "SELECT w.term, w.mean, COUNT(l.id) as cnt "
            "FROM log l "
            "JOIN word    w ON w.id = l.wid "
            "JOIN session s ON s.id = l.sid "
            "WHERE s.uid = ? AND l.correct = 0 "
            "GROUP BY w.id ORDER BY cnt DESC",
            (uid,)
        )

    # 글 연습 세션 관련 코드임.
    def add_passage_session(self, uid, ptype):
        return self.run("INSERT INTO passage_session (uid, ptype) VALUES (?,?)", (uid, ptype))

    def end_passage_session(self, psid, count, cpm, acc, sec):
        self.run(
            "UPDATE passage_session SET count = ?, cpm = ?, acc = ?, sec = ?, ended = ? WHERE id = ?",
            (count, cpm, acc, sec, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), psid)
        )

    def get_passage_sessions(self, uid):
        return self.all(
            "SELECT * FROM passage_session WHERE uid=? ORDER BY started DESC",
            (uid,)
        )

    # 타자 검정 결과 관련 코드임. started는 검정 시작 시각으로 저장함.
    def add_test_session(self, uid, mode, total, correct, score, cpm, acc, sec, timeout, started):
        return self.run(
            "INSERT INTO test_session (uid, mode, total, correct, score, cpm, acc, sec, timeout, started) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (uid, mode, total, correct, score, cpm, acc, sec, int(timeout), started)
        )

    def get_test_sessions(self, uid):
        return self.all(
            "SELECT * FROM test_session WHERE uid=? ORDER BY started DESC",
            (uid,)
        )

    # 예제(짧은 글/긴 글) 관련 코드임.
    def get_passages(self, ptype):
        return self.all("SELECT * FROM passage WHERE type=?", (ptype,))

    # 출제 우선순위: 0 = 사용자가 직접 선택한 txt/pdf, 1 = 엑셀 예제 코드, 2 = 그 밖의 txt/pdf
    def passage_rank(self, p, priority_files):
        if p["source"] and p["source"] in priority_files:
            return 0
        return 1 if p["source"] is None else 2

    # 짧은 글/긴 글 연습 실행 시, 주제별로 그룹화하는 코드임. (소원호 교수님 피드백 반영)
    # 우선순위가 높은 예제의 주제가 먼저 오고, 같은 순위 안에서는 등록된 순서대로 정렬함.
    def get_passages_by_topic(self, ptype):
        priority_files = set(self.get_priority_files())
        rows = self.all("SELECT * FROM passage WHERE type=? ORDER BY id", (ptype,))
        rows.sort(key = lambda p: self.passage_rank(p, priority_files))
        groups = {}
        for p in rows:
            groups.setdefault(p["topic"] or "기타", []).append(p)
        return list(groups.items())

    # 제목이 없는 예제 코드에서 함수/클래스 이름을 찾아 제목으로 사용함.
    @staticmethod
    def guess_title(text):
        for pat in (r"^\s*class\s+(\w+)", r"^\s*def\s+(\w+)"):  # Python 클래스/함수
            m = re.search(pat, text, re.M)
            if m:
                return m.group(1)
        # C 함수 정의 (예: int factorial(int n) {) - main은 제외
        for m in re.finditer(r"^\s*[A-Za-z_][\w \t\*]*?(\w+)\s*\([^;{]*\)\s*\{", text, re.M):
            if m.group(1) not in ("main", "if", "for", "while", "switch"):
                return m.group(1)
        lines = [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#include")]
        first = (lines[0] if lines else text).strip()
        return first if len(first) <= 30 else first[:30] + "…"

    # 지정한 파일에서 가져온 예제만 사용함 (우선 출제용)
    def get_passages_from(self, ptype, sources):
        if not sources:
            return []
        marks = ",".join("?" * len(sources))
        return self.all(
            f"SELECT * FROM passage WHERE type=? AND source IN ({marks})",
            (ptype, *sources)
        )

    # 사용자가 직접 불러온 txt/pdf 파일 목록 (짧은 글/긴 글 연습에서 우선 출제)
    def get_priority_files(self):
        val = self.get_setting("priority_text_files", "")
        return [p for p in val.split("\n") if p]

    def set_priority_files(self, paths):
        self.set_setting("priority_text_files", "\n".join(str(p) for p in paths))

    # 엑셀 파일 하나를 시트별로 검사하여, 예제 코드 시트는 passage 테이블에, 단어장 시트는 chapter/word 테이블에 각각 저장함.
    def import_excel(self, path):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"파일 없음: {path}")

        wb = openpyxl.load_workbook(path, data_only = True)
        imported = 0
        skipped = 0
        counts = {'short': 0, 'long': 0}

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            hdrs = {}
            for i, cell in enumerate(next(ws.iter_rows(min_row = 1, max_row = 1))):
                if cell.value:
                    hdrs[str(cell.value).strip()] = i
            hdrs_lower = {k.lower(): v for k, v in hdrs.items()}

            if '예제 코드' in hdrs:
                name = sheet_name.strip()
                if '짧은 글' in name:
                    ptype = 'short'
                elif '긴 글' in name:
                    ptype = 'long'
                else:
                    print(f"'{sheet_name}' 건너뜀 - 시트 이름에 짧은 글/긴 글 구분 없음")
                    continue
                ti = hdrs['예제 코드']
                topic_i = hdrs.get('주제', hdrs.get('언어'))  # 주제 열이 없으면 언어 열로 묶음
                title_i = hdrs.get('제목')
                def cell(row, i):
                    if i is None or i >= len(row) or row[i].value is None:
                        return None
                    return str(row[i].value).strip() or None
                rows = []  # 예제 코드를 임시로 여기에 저장하여 추후에 DB로 전송
                for row in ws.iter_rows(min_row = 2):
                    val = row[ti].value
                    if val is None:
                        continue
                    if ptype == 'long':
                        # 긴 글은 줄 단위로 타이핑. 줄바꿈은 유지하고 줄 내부 공백만 정규화함.
                        lines = [' '.join(line.split()) for line in str(val).splitlines()]
                        text = '\n'.join(line for line in lines if line)
                    else:
                        text = ' '.join(str(val).split())  # 줄바꿈이랑 공백을 한 줄로 정규화 시키기
                    if text:
                        topic = cell(row, topic_i) or "기타"
                        title = cell(row, title_i) or self.guess_title(text)
                        rows.append((ptype, text, topic, title))
                if rows:
                    # 엑셀에서 주제/제목이 바뀐 경우, 기존 DB의 주제/제목도 새 값으로 업데이트하는 코드. (소원호 교수님 피드백 반영)
                    self.many(
                        "INSERT INTO passage (type, text, topic, title) VALUES (?,?,?,?) "
                        "ON CONFLICT(text) DO UPDATE SET topic = excluded.topic, title = excluded.title",
                        rows
                    )
                    counts[ptype] += len(rows)
                    print(f"'{sheet_name}' - {len(rows)}개 저장")

            elif 'term' in hdrs_lower and 'mean' in hdrs_lower:
                cid = self.get_or_create_chapter(sheet_name, path)
                ti, mi = hdrs_lower['term'], hdrs_lower['mean']

                def get(row, i):
                    v = row[i].value
                    if v is None:
                        return ""
                    s = str(v).strip()
                    return "" if s.lower() == "nan" else s

                rows = []  # Excel에서 불러온 단어, 뜻 정보를 튜플 형태로 묶어서, 리스트 rows에 임시 저장 후, DB로 연결.
                skip = 0
                for row in ws.iter_rows(min_row = 2):
                    term = get(row, ti)
                    mean = get(row, mi)
                    if not term or not mean:
                        skip += 1
                        continue
                    rows.append((cid, term, mean))

                self.add_words(rows)  # DB에 단어, 뜻 정보 전달
                self.set_word_count(cid, len(rows))
                imported += len(rows)
                skipped += skip
                print(f"'{sheet_name}' - {len(rows)}개 저장, {skip}개 스킵")
            else:
                print(f"'{sheet_name}' 건너뜀 - 알 수 없는 형식 (term/mean 또는 예제 코드 열 없음)")

        return {
            "imported": imported,
            "skipped": skipped,
            "short": counts['short'],
            "long": counts['long'],
        }

    # txt / pdf 파일에서 문장을 읽어 짧은 글/긴 글 예제(passage 테이블)로 저장
    # 사용자가 직접 불러온 경우. 이미 저장된 같은 문장도 출처를 이 파일로 바꿈.
    def import_text_file(self, path, claim = False):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"파일 없음: {path}")
        sentences, rows = TextLoader.load(p)  # 파일 읽기/문장 분리는 TextLoader가 담당
        if rows:
            src = str(p.resolve())
            topic = p.stem  # txt/pdf는 파일 이름을 주제로 사용
            if claim:
                q = ("INSERT INTO passage (type, text, source, topic, title) VALUES (?,?,?,?,?) "
                     "ON CONFLICT(text) DO UPDATE SET source = excluded.source, "
                     "topic = excluded.topic, title = excluded.title")
            else:
                q = ("INSERT INTO passage (type, text, source, topic, title) VALUES (?,?,?,?,?) "
                     "ON CONFLICT(text) DO UPDATE SET topic = COALESCE(passage.topic, excluded.topic), "
                     "title = COALESCE(passage.title, excluded.title)")
            data = []
            for t, text in rows:
                first = text.splitlines()[0]  # 글의 첫 부분을 제목으로 사용
                title = first if len(first) <= 30 else first[:30].rstrip() + "…"
                data.append((t, text, src, topic, title))
            self.many(q, data)
        short = sum(1 for t, _ in rows if t == "short")
        long_ = len(rows) - short
        print(f"'{p.name}' - 문장 {len(sentences)}개 / 짧은 글 {short}개, 긴 글 {long_}개 저장")
        return {"imported": 0, "skipped": 0, "short": short, "long": long_}

    # 확장자에 따라 엑셀 / 텍스트(txt, pdf) 불러오기로 분기
    def import_file(self, path, claim = False):
        ext = Path(path).suffix.lower()
        if ext == ".xlsx":
            return self.import_excel(path)
        if ext in TextLoader.SUPPORTED_EXTS:
            return self.import_text_file(path, claim)
        raise ValueError(f"지원하지 않는 파일 형식: {Path(path).suffix}")

    # 설정된 폴더 안의 모든 .xlsx / .txt / .pdf 파일을 찾아 자동으로 불러옴 (앱 시작 시 호출).
    def scan_import_dir(self):
        folder = self.get_import_dir()
        p = Path(folder)
        result = {"files": 0, "imported": 0, "skipped": 0, "short": 0, "long": 0}
        if not p.is_dir():
            return result
        files = sorted(f for f in p.iterdir() if f.is_file() and f.suffix.lower() in IMPORT_EXTS)
        for f in files:
            if f.name.startswith("~$"):  # 엑셀이 열려 있을 때 생기는 임시 파일 제외
                continue
            try:
                r = self.import_file(f)
                result["files"] += 1
                result["imported"] += r["imported"]
                result["skipped"] += r["skipped"]
                result["short"] += r["short"]
                result["long"] += r["long"]
            except Exception as e:
                print(f"'{f.name}' 자동 불러오기 실패: {e}")
        return result
