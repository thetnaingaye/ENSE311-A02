import time
class Sudoku:
    def __init__(self, size, values):
        rank_map = {
            "4x4" : 2,
            "9x9" : 3,
            "16x16" : 4
        }
        self.rank = rank_map[size]
        self.values = values
        self.board = self.make_board(self.rank,self.values)
        
    def reset(self):
        self.board = self.make_board(self.rank, self.values)

    def make_board(self,rank, values):
        values = values.split(" ")
        board = []
        idx = 0
        for _ in range(rank**2):
            row = []
            for _ in range(self.rank**2):
                row.append(int(values[idx]))
                idx +=1
            board.append(row)
        return board

    def is_complete(self):
        return not self.has_unassinged_cell()

    def has_unassinged_cell(self):
        for row in range(self.rank**2):
            for col in range(self.rank**2):
                if self.board[row][col] == 0:
                    return True
        return False
    
    def assign_cell(self, cell, value):
        row, col = cell
        self.board[row][col] = value

    def unassign_cell(self, cell):
        row, col = cell
        self.board[row][col] = 0

    # --- MRV additions (minimal) ---
    def legal_values(self, pos):
        """Return only values consistent with current board at pos."""
        return [v for v in self.get_domain_values_by_pos(pos) if self.is_consistent(pos, v)]
    
    def select_unassigned_cell(self):
        """
        MRV: choose an empty cell with the smallest number of legal values.
        Ties are left as-is to keep changes minimal.
        """
        best = None
        best_len = float("inf")
        for row in range(self.rank**2):
            for col in range(self.rank**2):
                if self.board[row][col] == 0:
                    lv = self.legal_values((row, col))
                    if len(lv) < best_len:
                        best = (row, col)
                        best_len = len(lv)
                        if best_len == 1:  # quick exit if only one choice
                            return best
        return best
    # --- end MRV additions ---
    
    def print(self):
        for row in range(self.rank**2):
            for col in range(self.rank**2):
                print(self.board[row][col], end=" ")
            print()

    def pprint(self):
        print(f"-----" * self.rank**2)
        for i in range(self.rank**2):
            print("|", end="")
            for j in range(self.rank**2):
                value_str = f"{self.board[i][j] or ' '}".rjust(2).center(4)
                print(f"{value_str}",end="|")
            print()
            print(f"-----" * self.rank**2)

    def get_value(self, pos):
        row, col = pos
        return self.board[row][col]

    def get_row_values_by_pos(self,pos):
        r_idx, c_idx = pos
        return [ x for x in self.board[r_idx]]
    
    def get_col_values_by_pos(self, pos):
        r_idx, c_idx = pos
        values = []
        for row in self.board:
            values.append(row[c_idx])
        return values
    
    def get_region_values_by_pos(self, pos):
        r_idx, c_idx = pos
        values = []
        r_start = r_idx - r_idx % self.rank
        c_start = c_idx - c_idx % self.rank
        for r in range(r_start, r_start + self.rank):
            for c in range(c_start, c_start + self.rank):
                values.append(self.board[r][c])
        return values
    
    def get_domain_values_by_pos(self, pos):
        return [ x+1 for x in range(self.rank**2) ]

    def is_consistent(self, pos, value):
        for v in self.get_row_values_by_pos(pos):
            if v == value:
                return False
            
        for v in self.get_col_values_by_pos(pos):
            if v == value:
                return False
            
        for v in self.get_region_values_by_pos(pos):
            if v == value:
                return False
        
        return True

def recursive_backtracking(board):
    if board.is_complete():
        return True

    cell = board.select_unassigned_cell() # cell is tuple (row_idx, col_idx)
    
    for value in board.legal_values(cell):
        board.assign_cell(cell, value)
        if recursive_backtracking(board):
            return True # return Success

        # remove var from assignment
        board.unassign_cell(cell)
    
    # return Failure
    return False

def backtracking(board):
    is_solved = recursive_backtracking(board)
    if is_solved:
        board.print()
    else:
        print("No solution found!!!") 
            
def run():
    """
    Welcome to the Sudoku Solver!
    Enter a size (4x4, 9x9, 16x16):
    4x4
    Enter the values (a blank is represented by a 0):
    2 0 0 0 3 1 4 0 0 0 0 1 0 2 0 0
    The solution is
    2 4 1 3 
    3 1 4 2 
    4 3 2 1 
    1 2 3 4 

    9x9
    1 0 6 9 0 0 2 0 0 0 0 9 0 0 1 0 0 0 7 0 8 6 0 5 3 0 0 0 6 0 0 0 0 0 0 3 0 0 0 0 5 0 0 0 0 4 0 0 0 0 0 0 5 0 0 0 1 3 0 9 7 0 2 0 0 0 7 0 0 5 0 0 0 0 7 0 0 2 9 0 1

    16x16
    0 0 15 0 0 10 0 0 0 5 3 13 1 0 0 4 2 0 0 0 8 7 13 4 10 0 0 6 9 0 14 15 0 0 4 0 5 0 14 0 16 0 1 9 0 0 0 2 8 9 13 0 16 6 0 1 2 14 0 15 0 7 11 0 0 12 0 1 0 5 0 16 0 13 0 11 2 0 0 3 0 0 9 15 0 1 4 6 0 0 0 12 0 13 0 11 16 0 3 0 0 9 0 14 0 0 0 4 0 0 15 0 4 7 8 0 3 12 0 2 0 15 0 0 0 0 6 0 0 5 0 0 0 0 16 0 9 0 15 10 0 2 3 6 0 15 0 0 10 0 0 0 13 0 11 0 0 14 0 1 13 0 12 0 1 0 0 0 3 6 2 0 16 9 0 0 3 0 0 14 6 0 9 0 8 0 5 0 10 0 7 0 0 8 14 0 12 0 1 15 4 0 6 2 0 11 10 16 12 0 0 0 4 16 0 5 0 7 0 8 0 3 0 0 15 13 0 6 11 0 0 10 12 1 16 3 0 0 0 9 11 0 0 4 2 8 3 0 0 0 14 0 0 6 0 0
    """
    print("Welcome to the Sudoku Solver!")
    size = input("Enter a size (4x4, 9x9, 16x16):\n")
    values = input("Enter the values (a blank is represented by a 0):\n")
    board = Sudoku(size, values)
    # board.pprint()
    
    print("The solution is")
    start = time.perf_counter()
    backtracking(board)
    end = time.perf_counter()
    print(f"Total time {end - start}")

if __name__ == "__main__":
    run()