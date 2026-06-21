import time
from database.db import DB

class Result:
    def __init__(self, wid, term, typed, correct):
        self.wid = wid
        self.term = term   # 실제 정답
        self.typed = typed
        self.correct = correct

class Typer:
    def __init__(self, uid, cid, mode='en'):
        # mode: 'en' = 한글뜻→영어 / 'ko' = 영어→한글 / 'en_pos' = 영어→영어 / 'ko_pos' = 한글→한글
        self.mode = mode
        self.db = DB()
        self.sid = self.db.add_session(uid, cid)
        self.words = [dict(w) for w in self.db.get_words(cid)]
        self.total = len(self.words)
        self.idx = 0
        self.results = []
        self.session_start = time.time()
        self.word_start_time = None
        print(f"Typer 초기화 완료 - 단어 {self.total}개 로드됨 / 모드: {mode}")

    def get_word(self):
        if self.idx >= self.total:
            return None
        return self.words[self.idx]

    def is_done(self):
        return self.idx >= self.total

    def word_start(self):
        self.word_start_time = time.time()

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
        tpying_time = time.time() - self.session_start
        if tpying_time < 1:
            return 0
        total_chars = sum(len(r.typed) for r in self.results)
        return int(total_chars / tpying_time * 60)

    def get_sec(self):
        return int(time.time() - self.session_start)

    def finish(self):
        sec = self.get_sec()
        total = len(self.results)
        correct = sum(1 for r in self.results if r.correct)
        acc = int(correct / total * 100) if total else 0
        cpm = self.get_cpm()
        self.db.end_session(self.sid, total, correct, cpm, acc, sec)
        return {
            "sid": self.sid,
            "total": total,
            "correct": correct,
            "acc": acc,
            "cpm": cpm,
            "sec": sec,
            "results": self.results,
        }
