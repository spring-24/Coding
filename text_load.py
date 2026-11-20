import re
import unicodedata
from pathlib import Path

class TextLoader: # txt / pdf 파일을 읽어 짧은 글 / 긴 글 연습 예제로 변환하는 클래스
    SUPPORTED_EXTS = {".txt", ".pdf"}  # 이 클래스가 처리하는 파일 확장자
    SHORT_MIN, SHORT_MAX = 10, 100  # 짧은 글로 사용할 문장 길이 범위 (글자 수)
    LONG_LINE_MAX = 80  # 긴 글 한 줄의 최대 글자 수
    LONG_LINES = 5  # 긴 글 예제 하나에 들어가는 줄 수

    # 특수문자를 키보드로 입력 가능한 문자로 치환하는 코드
    CHAR_MAP = str.maketrans({
        "‘": "'", "’": "'", "‚": "'", "′": "'",
        "“": '"', "”": '"', "„": '"', "″": '"',
        "–": "-", "—": "-", "―": "-", "−": "-", "‐": "-", "‑": "-",
        " ": " ", "​": "", "﻿": "",
        "•": "", "▪": "", "●": "", "◦": "", "■": "", "□": "", "▶": "", "►": "",
    })

    # 예제 목록 'short' 또는 'long'
    @classmethod
    def load(cls, path):
        p = Path(path)
        ext = p.suffix.lower()
        if ext == ".pdf":
            raw = cls.read_pdf(p)
        elif ext == ".txt":
            raw = cls.read_txt(p)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {p.suffix}")
        sentences = cls.split_sentences(cls.clean_text(raw))
        return sentences, cls.build_passages(sentences)

    @staticmethod
    def read_txt(path): # 텍스트(.txt) 파일을 읽는 함수
        data = Path(path).read_bytes()
        for enc in ("utf-8-sig", "cp949", "utf-16"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="ignore")

    @staticmethod
    def read_pdf(path): # PDF(.pdf) 파일을 읽는 함수
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("ERROR")
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(pages)

    @classmethod
    def clean_text(cls, text): # 유니코드, 특수문자, PDF 하이픈 줄바꿈 등을 정리하는 함수
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.translate(cls.CHAR_MAP)
        text = text.replace("…", "...")
        text = re.sub(r"(\w)-\n(?=[a-z])", r"\1", text)  # 작동 예시: infor-\nmation -> information
        # 줄바꿈/탭 이외의 제어문자를 제거함.
        text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
        return text

    @staticmethod
    def split_sentences(text): # 텍스트를 문단 단위로 나눈 뒤, 문단 안의 줄바꿈을 합치고 문장 단위로 분리함.
        sentences = []  # 분리한 문장을 모아 둘 리스트
        for para in re.split(r"\n\s*\n", text):
            para = " ".join(para.split())
            if not para:
                continue
            for s in re.split(r"(?<=[.!?。])\s+", para):
                s = s.strip()
                if len(s) < 5:
                    continue
                if not re.search(r"[A-Za-z가-힣]", s):  # 페이지 번호, 기호만 있는 줄 제외
                    continue
                sentences.append(s)
        return sentences

    @classmethod
    def wrap_line(cls, sentence): # 긴 문장을 일정 길이 이하의 줄로 나누는 함수.
        lines, cur = [], ""
        for word in sentence.split():
            if cur and len(cur) + 1 + len(word) > cls.LONG_LINE_MAX:
                lines.append(cur)
                cur = word
            else:
                cur = f"{cur} {word}" if cur else word
        if cur:
            lines.append(cur)
        return lines

    @classmethod
    def build_passages(cls, sentences): # 문장을 짧은 글 / 긴 글 예제로 변환하는 함수
        rows = []
        # 짧은 글: 적당한 길이의 문장 하나 = 예제 하나
        for s in sentences:
            if cls.SHORT_MIN <= len(s) <= cls.SHORT_MAX:
                rows.append(("short", s))
        # 긴 글: 문장마다 한 줄(길면 여러 줄로 나눔), 연속된 LONG_LINES줄을 예제 하나로 묶음
        lines = []
        for s in sentences:
            lines.extend(cls.wrap_line(s))
        for i in range(0, len(lines), cls.LONG_LINES):
            chunk = lines[i:i + cls.LONG_LINES]
            if len(chunk) >= 2:
                rows.append(("long", "\n".join(chunk)))
        return rows
