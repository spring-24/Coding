#include <stdio.h>
#include <stdlib.h>
#define SIZE 10
int top = -1;

int is_empty(int e[]) {
    if(top == -1) {
        printf("스택이 공백 사태입니다.\n");
        return top;
    }
    else {
        return (SIZE - 1) - top;
    }
}

int main(void) {
    int s[SIZE];
    int i;
    for(i = 0; i < SIZE; i++) {
        s[i] = i * 10;
        top++;
    }
    top = is_empty(s);
    printf("현재 여유 현황: %d", top);

    return 0;
}
