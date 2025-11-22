class CirQueue:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
    
    def is_full(self) -> bool:
        return (self.rear + 1) % self.capacity == self.front

    def is_empty(self) -> bool:
        return self.front == self.rear

    def enqueue(self, item) -> bool:
        if self.is_full():
            print("큐가 포화상태")
            return False
        self.queue[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        print(f"{item} 삽입 완료")
        return True

    def dequeue(self):
        if self.is_empty():
            print("큐가 비어있음")
            return None
        item = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        print(f"✅ {item} 삭제 완료")
        return item

def peek(self):
        if self.is_empty():
            print("확인할 요소가 없음")
            return None
        return self.queue[self.front]

    def display(self):
        print("--- 큐 상태 ---")
        if self.is_empty():
            print("현재 큐는 비어 있음")
            return
        items = []
        i = self.front
        while i != self.rear:
            items.append(str(self.queue[i]))
            i = (i + 1) % self.capacity
        print(f"[ {', '.join(items)} ] (front={self.front}, rear={self.rear}, size={self.capacity})")
        print(f"내부 배열: {self.queue}")
        print("-------------")
