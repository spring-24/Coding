import numpy as np

def echelon_form(matrix_list):
    A = np.array(matrix_list, dtype = float)
    rows, cols = A.shape
    
    if(rows == 0 or cols == 0):
        return "Not Echelon Form (Empty Matrix)"

    leading_entry_col_indices = []
    is_ref = True
    is_rref = True
    prev_leading_col = -1 
    
    for r in range(rows):
        current_leading_col = -1
        
        for c in range(cols):
            if(abs(A[r, c]) > 1e-9): 
                current_leading_col = c
                break
        
        if(current_leading_col != -1):
            
            if(current_leading_col <= prev_leading_col):
                is_ref = False
                is_rref = False
                break

            if(abs(A[r, current_leading_col] - 1.0) > 1e-9):
                is_ref = False
                is_rref = False
                break
            
            for other_r in range(rows):
                if(other_r != r and abs(A[other_r, current_leading_col]) > 1e-9):
                    is_rref = False
            
            prev_leading_col = current_leading_col
            leading_entry_col_indices.append(current_leading_col)

        else:
            for subsequent_r in range(r + 1, rows):
                if(not np.all(abs(A[subsequent_r, :]) < 1e-9)):
                    is_ref = False
                    is_rref = False
                    break
            if(not is_ref):
                break

    if(is_rref):
        return "Reduced Row-Echelon Form (RREF)"
    elif(is_ref):
        return "Row-Echelon Form (REF)"
    else:
        return "Not Echelon Form"

matrix_rref = [
    [1, 0, 3, 0],
    [0, 1, 2, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0]
]
print(echelon_form(matrix_rref))

matrix_ref = [
    [1, 2, 3, 4],
    [0, 1, 5, 6],
    [0, 0, 1, 7],
    [0, 0, 0, 0]
]
print(echelon_form(matrix_ref))

matrix_not_echelon = [
    [1, 2, 3],
    [0, 0, 1],
    [0, 1, 0]
]

print(echelon_form(matrix_not_echelon))
