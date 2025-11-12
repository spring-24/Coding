#include <stdio.h>
#define ROW 3
#define COL 3

void matrix_T(int A[ROW][COL], int A_T[ROW][COL]) {
    int r, c;
    for(r = 0; r < ROW; r++) {
        for(c = 0; c < COL; c++) {
            A_T[c][r] = A[r][c];
        }
    }
}

void matrix_PF(int C[ROW][COL]) {
    int r, c;
    printf("============\n");
    printf("A = \n");
    for(r = 0; r < ROW; r++) {
        for(c = 0; c < COL; c++) {
            printf("%d ", C[r][c]);
        }
        printf("\n");
    }
    printf("============\n");
}

int main(void) {
    int A[ROW][COL] = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    int A_T[ROW][COL] = {0};
    matrix_T(A, A_T);
    matrix_PF(A);
    matrix_PF(A_T);
    return 0;
}
