class Problem:
    def __init__(self, board):
        self.board = board
        
    def is_goal(self):
        return self.board.is_complete()
    

class SudoKuBoard:
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

    def has_unassinged_cell(self):
        for row in range(self.rank**2):
            for col in range(self.rank**2):
                if self.board[row][col] == 0:
                    return True
        return False
    
    def assign_cell(self, cell, value):
        row, col = cell
        self.board[row][col] = value
    
    def next_unassigned_cell(self):
        for row in range(self.rank**2):
            for col in range(self.rank**2):
                if self.board[row][col] == 0:
                    return (row,col)
        return None
    
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
    # def is_valid(self):
    #     for row in range(self.rank**2):
    #         for col in range(self.rank**2):
    #             if not self.is_valid_cell((row,col)):
    #                 return False
                
    #     return True

    def is_valid_cell(self, pos):
        cell_row, cell_col = pos
        cell_value = self.board[cell_row][cell_col]

        if cell_value == 0:
            return False

        for col_idx in range(self.rank**2):
            if cell_col == col_idx:
                continue
            if self.board[cell_row][col_idx] == cell_value:
                return False
            
        for row_idx in range(self.rank**2):
            if row_idx == cell_row:
                continue
            if self.board[row_idx][cell_col] == cell_value:
                return False
        
        r_start = cell_row - cell_row % self.rank
        c_start = cell_col - cell_col % self.rank
        for row_idx in range(r_start, r_start + self.rank):
            for col_idx in range(c_start, c_start + self.rank):
                if (row_idx, col_idx) == pos:
                    continue
                if self.board[row_idx][col_idx] == cell_value:
                    return False
        return True


        # for row in range(self.rank**2):
        #     seen = set()
        #     for col in range(self.rank**2):
        #         value = self.board[row][col]
        #         if not value:
        #             continue
        #         if value in seen:
        #             return False
        #         seen.add(value)

        # for col in range(self.rank**2):
        #     seen = set()
        #     for row in range(self.rank**2):
        #         value = self.board[row][col]
        #         if not value:
        #             continue
        #         if value in seen:
        #             return False
        #         seen.add(value)

        # for quarter in range(self.rank):
        #     seen = set()
        #     for row in range(quarter, quarter+self.rank):
        #         for col in range(quarter+self.rank):
        #             value = self.board[row][col]
        #             if not value:
        #                 continue
        #             if value in seen:
        #                 return False
        #             seen.add(value)
        # return True

def recursive_backtracking(board):
    next_cell = board.next_unassigned_cell()

    if not next_cell:
        return True
    
    for i in range(board.rank**2):
        domain_value = i+1
        board.assign_cell(next_cell, domain_value)
        if board.is_valid_cell(next_cell):
            if recursive_backtracking(board):
                return True
 
        board.assign_cell(next_cell, 0)
    return False


def backtracking(board):
    return recursive_backtracking(board)
            
def run():
    """
    Welcome to the Sudoku Solver!
    Enter a size (4x4, 9x9, 16x16):
    4x4
    Enter the values (a blank is represented by a 0):
    2 0 0 0 3 1 4 0 0 0 0 1 0 2 0 0

    9x9
    1 0 6 9 0 0 2 0 0 0 0 9 0 0 1 0 0 0 7 0 8 6 0 5 3 0 0 0 6 0 0 0 0 0 0 3 0 0 0 0 5 0 0 0 0 4 0 0 0 0 0 0 5 0 0 0 1 3 0 9 7 0 2 0 0 0 7 0 0 5 0 0 0 0 7 0 0 2 9 0 1


    16x16
    0 0 15 0 0 10 0 0 0 5 3 13 1 0 0 4 2 0 0 0 8 7 13 4 10 0 0 6 9 0 14 15 0 0 4 0 5 0 14 0 16 0 1 9 0 0 0 2 8 9 13 0 16 6 0 1 2 14 0 15 0 7 11 0 0 12 0 1 0 5 0 16 0 13 0 11 2 0 0 3 0 0 9 15 0 1 4 6 0 0 0 12 0 13 0 11 16 0 3 0 0 9 0 14 0 0 0 4 0 0 15 0 4 7 8 0 3 12 0 2 0 15 0 0 0 0 6 0 0 5 0 0 0 0 16 0 9 0 15 10 0 2 3 6 0 15 0 0 10 0 0 0 13 0 11 0 0 14 0 1 13 0 12 0 1 0 0 0 3 6 2 0 16 9 0 0 3 0 0 14 6 0 9 0 8 0 5 0 10 0 7 0 0 8 14 0 12 0 1 15 4 0 6 2 0 11 10 16 12 0 0 0 4 16 0 5 0 7 0 8 0 3 0 0 15 13 0 6 11 0 0 10 12 1 16 3 0 0 0 9 11 0 0 4 2 8 3 0 0 0 14 0 0 6 0 0
    """
    print("Welcome to the Sudoku Solver!")

    size = input("Enter a size (4x4, 9x9, 16x16):\n")
    values = input("Enter the values (a blank is represented by a 0):\n")
    board = SudoKuBoard(size, values)

 
    board.pprint()
    
    print("The solution is")
    if backtracking(board):
        board.pprint()
    else:
        print("no solution")
        board.pprint()
    

if __name__ == "__main__":
    run()