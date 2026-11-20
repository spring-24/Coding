CREATE TABLE STUDENT (
  ch INTEGER PRIMARY KEY,
  major TEXT,
  id INTEGER,
  name TEXT
);

INSERT INTO STUDENT (ch, major, id, name) VALUES
(1, '컴퓨터교육과', 20270001, '홍길동'),
(2, '컴퓨터교육과', 20270002, '홍길순'),
(3, '컴퓨터교육과', 20270003, '김국방'),
(4, '컴퓨터교육과', 20270004, '정윤슬');

ALTER TABLE STUDENT ADD COLUMN mail TEXT;
SELECT *FROM STUDENT;

UPDATE STUDENT SET mail = 'ce20270001@s.s.scnu.ac.kr' WHERE ch = 1;
UPDATE STUDENT SET mail = 'ce20270002@s.s.scnu.ac.kr' WHERE ch = 2;
