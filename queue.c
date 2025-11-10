#include <stdio.h>
#include <stdlib.h>
#define SIZE 100

typedef int element;
typedef struct {
    element data[SIZE];
    int front;
    int rear;
} QueueType;

void init(QueueType *q) {
    q -> rear = -1;
    q -> front = -1;
}

int is_empty(QueueType *q) {
    return q -> rear == q -> front;
}

int is_full(QueueType *q) {
    return q -> rear == SIZE;
}

void enqueue(QueueType *q, element item) {
    if(is_full(q)) {
        perror("큐의 메모리 포화 상태");
    }
    else {
        q -> rear++;
        q -> data[q -> rear] = item;
    }
}

element dequeue(QueueType *q) {
    if(is_empty(q)) {
        perror("큐의 메모리 공백 상태");
        return 0;
    }
    else {
        q -> front++;
        return q -> data[q -> front];
    }
}

void println(QueueType *q) {
    int i;
    printf("front: %d  ||  rear: %d\n", q -> front, q -> rear);
    for(i = q -> front + 1; i <= q -> rear; i++) {
        printf("[%d] ", q -> data[i]);
    }
    printf("\n");
}

int main(void) {
    QueueType q;
    init(&q);
    enqueue(&q, 1215);
    enqueue(&q, 2000);
    enqueue(&q, 2019);
    println(&q);
    printf("[%d]\n", dequeue(&q));
    return 0;
}
