def total_n_queens(n):
    cols, diag, anti = set(), set(), set()

    def place(row):
        if row == n:
            return 1
        count = 0
        for col in range(n):
            if col in cols or row - col in diag or row + col in anti:
                continue
            cols.add(col); diag.add(row - col); anti.add(row + col)
            count += place(row + 1)
            cols.remove(col); diag.remove(row - col); anti.remove(row + col)   # backtrack
        return count

    return place(0)
