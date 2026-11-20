import time
from database.db import DB

# 한글 타수를 자모(키 입력) 기준으로 세기 위한 표
# 겹모음은 키 2번, 겹받침은 키 2번
_JUNG_DOUBLE = {9, 10, 11, 14, 15, 16, 19}
_JONG_DOUBLE = {3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 18}

def count_strokes(text):
    # 완성형 한글 한 글자 = 초성 1 + 중성 1~2 + 종성 0~2, 그 밖의 문자(영어, 숫자, 공백 등) = 1
    strokes = 0
    for ch in text:
        code = ord(ch) - 0xAC00
        if 0 <= code < 11172:
            jung = (code % 588) // 28
            jong = code % 28
            strokes += 1 + (2 if jung in _JUNG_DOUBLE else 1)
            if jong:
                strokes += 2 if jong in _JONG_DOUBLE else 1
        else:
            strokes += 1
    return strokes

class Result:
    def __init__(self, wid, term, typed, correct):
        self.wid = wid
        self.term = term  # 실제 정답
        self.typed = typed
        self.correct = correct

class Typer:
    def __init__(self, uid, cid, mode='en'):
        # mode: 'en' = 한글뜻 > 영어 / 'ko' = 영어 > 한글 / 'en_pos' = 영어 > 영어 / 'ko_pos' = 한글 > 한글
        self.mode = mode
        self.db = DB()
        self.sid = self.db.add_session(uid, cid)
        self.words = [dict(w) for w in self.db.get_words(cid)]
        self.total = len(self.words)
        self.idx = 0
        self.results = []
        self.session_start = time.time()
        self.word_start_time = None
        self.paused_time = 0.0
        self.result = None   # finish() 결과 (중복 저장 방지용)
        print(f"Typer 초기화 완료 - 단어 {self.total}개 로드됨 / 모드: {mode}")

    def get_word(self):
        if self.idx >= self.total:
            return None
        return self.words[self.idx]

    def is_done(self):
        return self.idx >= self.total

    def word_start(self):
        self.word_start_time = time.time()

    def add_pause(self, seconds):
        self.paused_time += seconds

    def submit(self, typed):
        w = self.words[self.idx]
        answer = w["term"] if self.mode in ('en', 'en_pos') else w["mean"]
        correct = (typed.strip() == answer.strip())
        r = Result(w["id"], answer, typed, correct)
        self.results.append(r)
        self.idx += 1
        print(f"submit - 입력:{typed} / 정답:{answer} / {'O' if correct else 'X'}")
        return r

    def get_cpm(self):
        tpying_time = time.time() - self.session_start - self.paused_time
        if tpying_time < 1:
            return 0
        total_strokes = sum(count_strokes(r.typed) for r in self.results)  # 한글은 자모 기준 타수
        return int(total_strokes / tpying_time * 60)

    def get_sec(self):
        return int(time.time() - self.session_start)

    def finish(self):
        # 이미 종료 처리된 세션이면 DB를 다시 덮어쓰지 않고 기존 결과를 반환함
        if self.result is not None:
            return self.result
        sec = self.get_sec()
        total = len(self.results)
        correct = sum(1 for r in self.results if r.correct)
        acc = int(correct / total * 100) if total else 0
        cpm = self.get_cpm()
        self.db.end_session(self.sid, total, correct, cpm, acc, sec)
        self.result = {
            "sid": self.sid,
            "total": total,
            "correct": correct,
            "acc": acc,
            "cpm": cpm,
            "sec": sec,
            "results": self.results,
        }
        return self.result
