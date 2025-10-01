import time
import unittest

class Sudoku:
    def __init__(self, rank, state, domains=None):
        self.rank = rank
        self.size = self.rank**2
        self.state = state
        if domains is None:
            self.domains = [[[i for i in range(1, self.size+1)] for _ in range(self.size)] for _ in range(self.size)]
            for r in range(self.size):
                for c in range(self.size):
                    if self.state[r][c] == 0:
                        self.domains[r][c] = [v for v in self.domains[r][c] if self.is_value_consistent((r,c), v)]
                    else:
                        self.domains[r][c] = [self.state[r][c]] # uni constraint
        else:
            self.domains = domains
    
    def deep_copy(self):
        return Sudoku(
            self.rank,
            [row[:] for row in self.state], # create new state list
            [[d[:] for d in row] for row in self.domains], # create new domains list
        )
    
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
        self.domains[row][col] = [value]

    def get_cell_legal_values(self, cell):
        r,c = cell
        return [v for v in self.domains[r][c] if self.is_value_consistent(cell, v)]
    
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

    def is_value_consistent(self, cell, value):
        r_idx, c_idx = cell

        # check if value is in cell's row
        for v in self.state[r_idx]:
            if v == value:
                return False
            
        # check if value is in cell's column
        for row in self.state:
            if row[c_idx] == value:
                return False

        # check value is in region
        r_start = r_idx - r_idx % self.rank
        c_start = c_idx - c_idx % self.rank
        for r in range(r_start, r_start + self.rank):
            for c in range(c_start, c_start + self.rank):
                if self.state[r][c] == value:
                    return False

        
        return True

    def get_neighbours(self, cell):
        r_idx,c_idx = cell
        neighbours = set()
        for i in range(self.size):
            if i != r_idx: # get same column neighours
                neighbours.add((i, c_idx)) 
            if i != c_idx:
                neighbours.add((r_idx,i))
        r_start = r_idx - r_idx % self.rank
        c_start = c_idx - c_idx % self.rank
        for r in range(r_start, r_start + self.rank):
            for c in range(c_start, c_start + self.rank):
                neighbours.add((r,c))
        neighbours.remove(cell)
        return list(neighbours)
    
class CSP:
    def __init__(self, assignment, ordering_func, filtering_func):
        self.initial_assignment = assignment
        self.ordering_func = ordering_func
        self.filtering_func = filtering_func

    def get_successors(self, assignment, cell, cell_values):
        successors = []
        for value in cell_values:
            copied_assgn = assignment.deep_copy()
            copied_assgn.assign_cell(cell, value)
            if self.filtering_func(copied_assgn, cell, value): # filtering Forward checking or AC-3
                successors.append(copied_assgn)
        return successors

    def select_unassigned_cell(self, assignment):
        return self.ordering_func(assignment)

def arc_consistency_3(assignment, cell, value):
    """
    ac-3 arc consistency: constraint propagation assigned to unassigned and propagates usassigned to unassigned
    """
    def remove_inconsistent_values(assignment, head, tail):
        """
        Removes inconsistent values from the tail that do not agree with values in the head.
        """
        removed = False

        hr, hc = head
        tr, tc = tail

        possible_tail_values = assignment.domains[tr][tc]
        possible_head_values = assignment.domains[hr][hc]

        if len(possible_head_values) == 1 and (possible_head_values[0] in possible_tail_values):
            possible_tail_values.remove(possible_head_values[0])
            removed = True
        return removed

    row, col = cell
    assignment.domains[row][col] = [value] 
    neighbours = assignment.get_neighbours(cell)
    arc_queue = []
    for neighbour in neighbours:
        arc_queue.append((cell, neighbour))

    while len(arc_queue) > 0:
        head, tail = arc_queue.pop(0)
        tr, tc = tail
        if remove_inconsistent_values(assignment, head, tail):
            if len(assignment.domains[tr][tc]) == 0:
                return False
            for neighbour in assignment.get_neighbours((tr,tc)):
                if assignment.state[neighbour[0]][neighbour[1]] != 0:
                    arc_queue.append((tail, neighbour))
    return True

def forward_checking(assignment, cell, value):
    """
    Forward checking: constraint propagation from assigned to unassigned variables
    """
    for (r, c) in assignment.get_neighbours(cell):
        if assignment.state[r][c] != 0:
            continue
        d = assignment.domains[r][c]
        # If removing `value` would empty the domain, fail fast
        if len(d) == 1 and d[0] == value:
            return False
        # In-place remove avoids allocating a new list
        if value in d:
            d.remove(value)
            if not d:  # just in case
                return False
    return True

def minium_remaining_values(assignment):
    """
    MRV: choose an empty cell with the smallest number of legal values.
    """
    best = None
    best_len = float("inf")
    best_lv = []
    size = assignment.size
    for row in range(size):
        for col in range(size):
            if assignment.state[row][col] == 0:
                # lv = assignment.get_cell_legal_values((row, col))
                lv = assignment.domains[row][col] # foward checking filter already for inconsistent values
                if len(lv) < best_len:
                    best = (row, col)
                    best_lv = lv
                    best_len = len(lv)
                    if best_len == 1:  # quick exit if only one choice
                        return best, best_lv
    return best, best_lv

def recursive_backtracking(csp, assignment):
    if assignment.is_complete():
        return assignment

    cell, cell_legal_values = csp.select_unassigned_cell(assignment) # cell is tuple (row_idx, col_idx)
    for new_assignment in csp.get_successors(assignment, cell, cell_legal_values):
        result = recursive_backtracking(csp, new_assignment)
        if result:
            return result
    # return Failure
    return False

def backtracking(csp, assignment):
    solved_board = recursive_backtracking(csp, assignment)
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

    if input_size not in rank_map:
        raise Exception("Invalid size, enter a size (4x4, 9x9, 16x16) ")
    
    rank = rank_map[input_size]
    size = rank**2
    
    splitted = str(input_values).strip().split(" ")
    if len(splitted) != size * size:
        raise Exception("Invalid input values")
    
    state = []
    idx = 0
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(int(splitted[idx]))
            idx +=1
        state.append(row)
    assignment = Sudoku(rank, state, domains=None)
    csp = CSP(assignment, ordering_func=minium_remaining_values, filtering_func=forward_checking)
    # assignment.pprint()
    
    start = time.perf_counter()
    backtracking(csp, assignment)
    end = time.perf_counter()


    # print(f"Total run time =  {end - start}")


class TestSudokuSolver(unittest.TestCase):
    def setUp(self):
        self.puzzle4 = "2 0 0 0 3 1 4 0 0 0 0 1 0 2 0 0"
        self.puzzle9 = "1 0 6 9 0 0 2 0 0 0 0 9 0 0 1 0 0 0 7 0 8 6 0 5 3 0 0 0 6 0 0 0 0 0 0 3 0 0 0 0 5 0 0 0 0 4 0 0 0 0 0 0 5 0 0 0 1 3 0 9 7 0 2 0 0 0 7 0 0 5 0 0 0 0 7 0 0 2 9 0 1"
        self.puzzle16 = "0 0 15 0 0 10 0 0 0 5 3 13 1 0 0 4 2 0 0 0 8 7 13 4 10 0 0 6 9 0 14 15 0 0 4 0 5 0 14 0 16 0 1 9 0 0 0 2 8 9 13 0 16 6 0 1 2 14 0 15 0 7 11 0 0 12 0 1 0 5 0 16 0 13 0 11 2 0 0 3 0 0 9 15 0 1 4 6 0 0 0 12 0 13 0 11 16 0 3 0 0 9 0 14 0 0 0 4 0 0 15 0 4 7 8 0 3 12 0 2 0 15 0 0 0 0 6 0 0 5 0 0 0 0 16 0 9 0 15 10 0 2 3 6 0 15 0 0 10 0 0 0 13 0 11 0 0 14 0 1 13 0 12 0 1 0 0 0 3 6 2 0 16 9 0 0 3 0 0 14 6 0 9 0 8 0 5 0 10 0 7 0 0 8 14 0 12 0 1 15 4 0 6 2 0 11 10 16 12 0 0 0 4 16 0 5 0 7 0 8 0 3 0 0 15 13 0 6 11 0 0 10 12 1 16 3 0 0 0 9 11 0 0 4 2 8 3 0 0 0 14 0 0 6 0 0"

    def _parse_state(self, rank, values):
        size = rank**2
        splitted = str(values).strip().split(" ")
        if len(splitted) != size * size:
            raise Exception("Invalid input values")
        
        state = []
        idx = 0
        for _ in range(size):
            row = []
            for _ in range(size):
                row.append(int(splitted[idx]))
                idx +=1
            state.append(row)
        return state

    def _solve(self, rank, values, timeout=2.0):
        state = self._parse_state(rank, values)
        assignment = Sudoku(rank, state, domains=None)
        csp = CSP(assignment, ordering_func=minium_remaining_values, filtering_func=forward_checking)

        t0 = time.perf_counter()
        solved = recursive_backtracking(csp, assignment)
        dt = time.perf_counter() - t0
        print(f"test {rank**2}x{rank**2} runtime", dt)
        self.assertIsNotNone(solved, "Solver returned None")
        self.assertLessEqual(dt, timeout, f"Solver took too long: {dt:.2f}s")
        return solved.state

    def _verify(self, initial, solved, rank):
        n = rank * rank
        allvals = list(range(1, n+1))
        # check filled
        for r in range(n):
            for c in range(n):
                self.assertNotEqual(solved[r][c], 0, f"Cell ({r},{c}) empty")
                if initial[r][c] != 0:
                    self.assertEqual(solved[r][c], initial[r][c], f"Clue changed at ({r},{c})")
        # check rows
        for r in range(n):
            self.assertEqual(sorted(solved[r]), allvals)
        # check cols
        for c in range(n):
            col = [solved[r][c] for r in range(n)]
            self.assertEqual(sorted(col), allvals)
        # check regions
        for br in range(0, n, rank):
            for bc in range(0, n, rank):
                box = []
                for r in range(br, br+rank):
                    box.extend(solved[r][bc:bc+rank])
                self.assertEqual(sorted(box), allvals)

    def test_4x4(self):
        rank = 2
        init = self._parse_state(rank, self.puzzle4)
        solved = self._solve(rank, self.puzzle4, timeout=5.0)
        self._verify(init, solved, rank)

    def test_9x9(self):
        rank = 3
        init = self._parse_state(rank, self.puzzle9)
        solved = self._solve(rank, self.puzzle9, timeout=5.0)
        self._verify(init, solved, rank)

    def test_16x16(self):
        rank = 4
        init = self._parse_state(rank, self.puzzle16)
        solved = self._solve(rank, self.puzzle16, timeout=5.0)
        self._verify(init, solved, rank)



if __name__ == "__main__":
    run()