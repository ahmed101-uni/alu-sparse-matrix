#!/usr/bin/python3

import sys

# Load a sparse matrix from a file
def load_matrix(path):
    try:
        with open(path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 2:
            raise ValueError("File missing shape info (rows and cols).")

        rows = int(lines[0].split('=')[1].strip())
        cols = int(lines[1].split('=')[1].strip())

        data = {}
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue
            try:
                row, col, val = eval(line)  # not super safe but assuming trusted input
                data[(row, col)] = val
            except:
                raise ValueError(f"Bad line: {line}")

        return data, (rows, cols)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except Exception as e:
        raise RuntimeError(f"Problem reading {path}: {e}")


# Save the matrix back to file in the same format
def save_matrix(matrix, shape, path):
    rows, cols = shape
    try:
        with open(path, 'w') as f:
            f.write(f"rows={rows}\n")
            f.write(f"cols={cols}\n")
            for (r, c), v in sorted(matrix.items()):
                if v != 0:
                    f.write(f"({r}, {c}, {v})\n")
    except Exception as e:
        raise RuntimeError(f"Couldn't write to {path}: {e}")


# Matrix multiplication (for sparse matrices)
def multiply(A, A_shape, B, B_shape):
    a_rows, a_cols = A_shape
    b_rows, b_cols = B_shape

    if a_cols != b_rows:
        raise ValueError("Shapes don't match for multiplication.")

    # Group B values by row to avoid looping too much later
    B_rows = {}
    for (r, c), val in B.items():
        B_rows.setdefault(r, []).append((c, val))

    result = {}
    for (ar, ac), a_val in A.items():
        if ac in B_rows:
            for bc, b_val in B_rows[ac]:
                key = (ar, bc)
                result[key] = result.get(key, 0) + a_val * b_val

    return result, (a_rows, b_cols)


# Handles addition and subtraction
def add_or_subtract(A, A_shape, B, B_shape, op):
    if A_shape != B_shape:
        raise ValueError("Shapes must be the same for add/subtract.")

    result = {}
    keys = set(A.keys()) | set(B.keys())

    for k in keys:
        val_a = A.get(k, 0)
        val_b = B.get(k, 0)

        if op == 'add':
            result[k] = val_a + val_b
        elif op == 'subtract':
            result[k] = val_a - val_b

        if result[k] == 0:
            del result[k]  # keep it sparse

    return result, A_shape


# Main driver
def main():
    if len(sys.argv) != 5:
        print("Usage: sparse_matrix_calc <file1> <file2> <operation> <result_file>")
        print("operation: add | subtract | multiply")
        sys.exit(1)

    file1, file2, op, out_path = sys.argv[1:]

    try:
        A, shape_A = load_matrix(file1)
        B, shape_B = load_matrix(file2)

        if op == 'multiply':
            result, result_shape = multiply(A, shape_A, B, shape_B)
        elif op == 'add':
            result, result_shape = add_or_subtract(A, shape_A, B, shape_B, op='add')
        elif op == 'subtract':
            result, result_shape = add_or_subtract(A, shape_A, B, shape_B, op='subtract')
        else:
            raise ValueError("Operation must be add, subtract, or multiply.")

        save_matrix(result, result_shape, out_path)
        print(f"Done! Output saved to: {out_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
