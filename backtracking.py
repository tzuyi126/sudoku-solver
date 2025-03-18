import sys
import time

class CSP:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def solve(self, input_file, output_file):
        board = self.read_file(input_file)
        self.set_variables(board)
        self.set_constraints()
        self.set_domain(board)

        # Start a timer
        start = time.time()

        solution = self.backtrack(board, {})

        # Stop the timer
        end = time.time()
        print("It took", end - start, "seconds!")
        
        if solution == None:
            print("Could not find a solution to this Kropki Sudoku!")
            sys.exit(1)
        
        self.print_solution(solution, output_file)

    def read_file(self, input_path):
        try:
            with open(input_path, "r") as file:
                # Read the first 9 rows of the initial game board state
                board = [[int(val) for val in next(file).strip().split()] for _ in range(self.rows)]
                next(file)

                # Read the next 9 rows for the dots between horizontal-adjacent cells
                self.horizontal = [[int(val) for val in next(file).strip().split()] for _ in range(self.rows)]
                next(file)

                # Read the next 8 rows for the dots between vertically-adjacent cells
                self.vertical = [[int(val) for val in next(file).strip().split()] for _ in range(self.rows - 1)]

            return board
        except Exception as e:
            print(f"Failed to read the file: {e}")
            sys.exit(1)

    # ----------------- Initialization -----------------

    def set_variables(self, board):
        # Store unassigned cells into a list
        self.variables = [(i, j) for i in range(self.rows) for j in range(self.cols) if board[i][j] == 0]
    
    def set_domain(self, board):
        self.domains = dict()

        # Iterate through each unassigned cell position
        for var in self.variables:
            self.domains[var] = []

            # Try each possible value (1-9) for this cell
            for value in range(1, 10):
                # Check if this value satisfies all constraints
                if self.is_consistent(var, value, board):
                    self.domains[var].append(value)
    
    def set_constraints(self):
        self.constraints = dict()

        for cur_row, cur_col in self.variables:
            var = (cur_row, cur_col)
            self.constraints[var] = dict()
        
            # Constraints:
            # 1 = white dot (difference of 1)
            # 2 = black dot (double value)
            # 3 = must be different

            # Add left neighbor constraints
            if cur_col - 1 >= 0 and self.horizontal[cur_row][cur_col - 1] != 0:
                self.constraints[var][(cur_row, cur_col - 1)] = self.horizontal[cur_row][cur_col - 1]

            # Add right neighbor constraints
            if cur_col < self.cols - 1 and self.horizontal[cur_row][cur_col] != 0:
                self.constraints[var][(cur_row, cur_col + 1)] = self.horizontal[cur_row][cur_col]

            # Add upper neighbor constraints
            if cur_row - 1 >= 0 and self.vertical[cur_row - 1][cur_col] != 0:
                self.constraints[var][(cur_row - 1, cur_col)] = self.vertical[cur_row - 1][cur_col]

            # Add lower neighbor constraints
            if cur_row < self.rows - 1 and self.vertical[cur_row][cur_col] != 0:
                self.constraints[var][(cur_row + 1, cur_col)] = self.vertical[cur_row][cur_col]

            # Add column constraints (skip if neighbor exist)
            for iterate_col in range(self.cols):
                if iterate_col != cur_col and (cur_row, iterate_col) not in self.constraints[var]:
                    self.constraints[var][(cur_row, iterate_col)] = 3

            # Add row constraints (skip if neighbor exist)
            for iterate_row in range(self.rows):
                if iterate_row != cur_row and (iterate_row, cur_col) not in self.constraints[var]:
                    self.constraints[var][(iterate_row, cur_col)] = 3

            # Add 3x3 subgrid constraints (skip if neighbor exist)
            for i in range(3):
                for j in range(3):
                    # Calculate the actual row/col positions within the subgrid
                    # cur_row // 3 * 3 finds the top-left corner row of the current subgrid
                    # cur_col // 3 * 3 finds the top-left corner column of the current subgrid
                    # Adding i/j iterates through all cells in the subgrid
                    iterate_row, iterate_col = (cur_row // 3) * 3 + i, (cur_col // 3) * 3 + j

                    if (iterate_row != cur_row and iterate_col != cur_col and 
                        (iterate_row, iterate_col) not in self.constraints[var]):
                        self.constraints[var][(iterate_row, iterate_col)] = 3

    # -----------------------------------------------

    # ----------------- Consistency -----------------

    def is_consistent(self, var, value, board):
        # Check if the value satisfies all constraints with its neighbors
        for neighbor, constraint in self.constraints[var].items():
            neighbor_row, neighbor_col = neighbor
            neighbor_value = board[neighbor_row][neighbor_col]
            
            # Return False if the current value assignment violates the constraint
            if not self.satisfy_constraint(value, neighbor_value, constraint):
                return False

        return True
    
    def satisfy_constraint(self, value, neighbor_value, constraint):
        # Skip constraint check if neighbor cell is not yet assigned
        if neighbor_value == 0:
            return True

        match constraint:
            case 1:
                # White dot: difference must be 1
                if abs(neighbor_value - value) != 1:
                    return False
            case 2:
                # Black dot: one value must be double the other
                if max(neighbor_value, value) / min(neighbor_value, value) != 2:
                    return False
            case 3:
                # One value must be different from the other (same row/column/subgrid)
                if neighbor_value == value:
                    return False
        return True
    
    # -----------------------------------------------
    
    def select_unassigned_variable(self, assignment):
        unassigned = [var for var in self.variables if var not in assignment]

        # Use Minimum Remaining Value
        mrv_value = min(len(self.domains[var]) for var in unassigned)
        mrv_vars = [var for var in unassigned if len(self.domains[var]) == mrv_value]

        # If there's only one unassigned variables with minimum remaining value, return it
        if len(mrv_vars) == 1:
            return mrv_vars[0]

        # Use Degree Heuristics
        return max(mrv_vars, key=lambda var: sum(1 for neighbor in self.constraints[var] if neighbor not in assignment))
    
    def order_domain_values(self, var):
        return self.domains[var]
    
    # ----------------- Inference -----------------
    
    def prepare_inference(self, var):
        # Create a backup of domain values before inference
        var_domains = dict()

        for neighbor in self.constraints[var]:
            # Skip if neighbor is already assigned
            if neighbor not in self.domains:
                continue

            # Create a copy of each neighbor's domain
            # This allows us to restore domains if backtracking is needed
            var_domains[neighbor] = []
            for neighbor_value in self.domains[neighbor]:
                var_domains[neighbor].append(neighbor_value)

        return var_domains

    def inference(self, var, value):
        # Use Forward Checking
        # Iterate through all neighbors and their constraints with the current variable
        for neighbor, constraint in self.constraints[var].items():
            # Skip if neighbor is already assigned
            if neighbor not in self.domains:
                continue

            domains_to_remove = []

            # Check each possible value in the neighbor's domain
            for neighbor_value in self.domains[neighbor]:
                # If this value violates the constraint with our current assignment,
                # it should be removed
                if not self.satisfy_constraint(value, neighbor_value, constraint):
                    domains_to_remove.append(neighbor_value)

            # Remove all inconsistent values from neighbor's domain
            for domain in domains_to_remove:
                self.domains[neighbor].remove(domain)

            # If any variable's domain becomes empty, forward checking has failed
            if len(self.domains[neighbor]) == 0:
                return False
            
        # Forward checking succeeded
        return True
    
    def backtrack_inference(self, var, var_domains):
        for neighbor in self.constraints[var]:
            # Skip if neighbor is already assigned
            if neighbor not in self.domains:
                continue

            for neighbor_value in var_domains[neighbor]:
                # If this value was removed during forward checking, add it back
                if neighbor_value not in self.domains[neighbor]:
                    self.domains[neighbor].append(neighbor_value)
            
            # Sort the restored domain to maintain consistent ordering
            self.domains[neighbor].sort()

    # ------------------------------------------------
    
    # ----------------- Backtracking -----------------

    def backtrack(self, board, assignment):
        # If assignment is complete, then return assignment
        if len(self.variables) == len(assignment):
            return board
        
        # Select the next unassigned variable
        var = self.select_unassigned_variable(assignment)
        cur_row, cur_col = var

        # Try each value in the domain of the selected variable
        for value in self.order_domain_values(var):
            # Check if assigning this value violates any constraints
            if self.is_consistent(var, value, board):
                # If consistent, make the assignment
                assignment[var] = value
                board[cur_row][cur_col] = value
                
                # Save a backup of neighbor domains before inference
                var_domains = self.prepare_inference(var)

                if self.inference(var, value):
                    # Recursively try to complete the assignment
                    solution = self.backtrack(board, assignment)
                    if solution is not None:
                        return solution
                
                # If we reach here, this path didn't work out
                # Undo the inference and assignment (backtrack), and try next value
                self.backtrack_inference(var, var_domains)

                board[cur_row][cur_col] = 0
                del assignment[var]

        # If no value works, return None to trigger backtracking
        return None
    
    # ------------------------------------------------
    
    def print_solution(self, solution, output_file):
        with open(output_file, "w") as file:
            for lines in solution:
                file.write(" ".join(str(value) for value in lines))
                file.write("\n")

        print(f"Solution has been write to \"{output_file}\"")

def main():
    try:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    except Exception:
        print(f"Please provide the input and output filenames (Use space to separate the arguments)")
        sys.exit(1)

    csp = CSP(9, 9)
    csp.solve(input_file, output_file)

if __name__ == "__main__":
    main()