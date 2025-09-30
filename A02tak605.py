import time
class Sudoku:
    def __init__(self, rank, state, domains=None):
        self.rank = rank
        self.size = self.rank**2
        self.state = state
        if domains is None:
            self.domains = [[[i for i in range(1, self.size+1)] for _ in range(self.size)] for _ in range(self.size)]
        else:
            self.domains = domains

    def get_state(self):
        copy_state = []
        for row in self.state:
            copy_state.append(list(row))
        return copy_state
    
    def get_domains(self):
        values = []
        for row in self.domains:
            value_row=[]
            for col in row:
                value_row.append(list(col))
            values.append(value_row)
        return values
    
    def deep_copy(self):
        return Sudoku(self.rank, self.get_state(), self.get_domains())
    
    def is_complete(self):
        return not self.has_unassinged_cell()

    def has_unassinged_cell(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.state[row][col] == 0:
                    return True
        return False
    
    def assign_cell(self, cell, value):
        row, col = cell
        self.state[row][col] = value

    def unassign_cell(self, cell):
        row, col = cell
        self.state[row][col] = 0

    def legal_values(self, pos):
        r,c = pos
        return [v for v in self.domains[r][c] if self.is_consistent(pos, v)]
    
    def select_unassigned_cell(self):
        """
        MRV: choose an empty cell with the smallest number of legal values.
        """
        best = None
        best_len = float("inf")
        best_lv = []
        for row in range(self.size):
            for col in range(self.size):
                if self.state[row][col] == 0:
                    lv = self.legal_values((row, col))
                    if len(lv) < best_len:
                        best = (row, col)
                        best_lv = lv
                        best_len = len(lv)
                        if best_len == 1:  # quick exit if only one choice
                            return best, best_lv
        return best, best_lv
    
    def print(self):
        for row in range(self.size):
            for col in range(self.size):
                print(self.state[row][col], end=" ")
            print()

    def pprint(self):
        print(f"-----" * self.size)
        for i in range(self.size):
            print("|", end="")
            for j in range(self.size):
                value_str = f"{self.state[i][j] or ' '}".rjust(2).center(4)
                print(f"{value_str}",end="|")
            print()
            print(f"-----" * self.size)

    def get_value(self, pos):
        row, col = pos
        return self.state[row][col]

    def get_row_values_by_pos(self,pos):
        r_idx, c_idx = pos
        return [ x for x in self.state[r_idx]]
    
    def get_col_values_by_pos(self, pos):
        r_idx, c_idx = pos
        values = []
        for row in self.state:
            values.append(row[c_idx])
        return values
    
    def get_region_values_by_pos(self, pos):
        r_idx, c_idx = pos
        values = []
        r_start = r_idx - r_idx % self.rank
        c_start = c_idx - c_idx % self.rank
        for r in range(r_start, r_start + self.rank):
            for c in range(c_start, c_start + self.rank):
                values.append(self.state[r][c])
        return values

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

    def get_neighours(self, pos):
        r_idx,c_idx = pos

        neighbours = []
        for i in range(self.size):
            if i != r_idx: # get same column neighours
                neighbours.append((i, c_idx)) 
            if i != c_idx:
                neighbours.append((r_idx,i))
        r_start = r_idx - r_idx % self.rank
        c_start = c_idx - c_idx % self.rank
        for r in range(r_start, r_start + self.rank):
            for c in range(c_start, c_start + self.rank):
                pos = (r,c)
                if pos not in neighbours:
                    neighbours.append((r,c))
        return neighbours
    
def recursive_backtracking(board):
    if board.is_complete():
        return board

    cell, legal_values = board.select_unassigned_cell() # cell is tuple (row_idx, col_idx)
    
    for value in legal_values:
        board.assign_cell(cell, value)
        result =  recursive_backtracking(board.deep_copy())
        if result:
            return result # return Success

        # remove var from assignment
        board.unassign_cell(cell)
    
    # return Failure
    return False

def backtracking(board):
    solved_board = recursive_backtracking(board)
    if solved_board:
        print("The solution is")
        solved_board.print()
        # board.pprint()
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
    input_size = input("Enter a size (4x4, 9x9, 16x16):\n")
    input_values = input("Enter the values (a blank is represented by a 0):\n")


    rank_map = {
        "4x4" : 2,
        "9x9" : 3,
        "16x16" : 4
    }
    values = input_values.split(" ")
    state = []
    rank = rank_map[input_size]
    idx = 0
    
    for _ in range(rank**2):
        row = []
        for _ in range(rank**2):
            row.append(int(values[idx]))
            idx +=1
        state.append(row)
    board = Sudoku(rank, state, domains=None)
    # board.pprint()
   
    start = time.perf_counter()
    backtracking(board)
    end = time.perf_counter()


    print(f"Total time {end - start}")

if __name__ == "__main__":
    run()