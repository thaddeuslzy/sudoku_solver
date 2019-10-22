import sys
import copy
import itertools

board_range = range(9)

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.initVariables()        # create self.variables, self.domains, self.pruned
        self.createConstraints()    # create self.constraints
        self.createNeighbours()     # create self.neighbours

    def solve(self):
        if self.ac3():
            if self.isSolved():
                print('solved')
            else:
                assignment = {}
                
                assignment = self.initAssignment(assignment)
                assignment = self.backtrack(assignment)

                if assignment:
                    self.setAnswers(assignment)
                    #print("ans found")
                #else:
                    #print("No Soln")

        # self.ans is a list of lists
        return self.ans
        
    def initVariables(self):
        variables = self.combine(board_range, board_range)
        pruned = [[0 for i in board_range] for j in board_range]
        domains = [[0 for i in board_range] for j in board_range]

        # Populate domain and pruned
        for i in board_range:
            for j in board_range:
                # If variable is 0, then domain is all values from 0-9, pruned is empty
                if self.puzzle[i][j] == 0:
                    domains[i][j] = range(1, 10)
                    pruned[i][j] = []

                # Else domain and pruned contains that value only as its fixed
                else:
                    domains[i][j] = [ self.puzzle[i][j] ]
                    pruned[i][j] = [ self.puzzle[i][j] ]
        
        self.variables = variables
        self.domains = domains
        self.pruned = pruned
        
    # Creates the necessary binary constraints from each of the rows, columns,
    # and block constraints
    # build_constraints
    def createConstraints(self):
        constraints = []
        
        rows = [self.combine(board_range, y) for y in board_range]
        columns = [self.combine(x, board_range) for x in board_range]
        blocks_3x3 = [self.combine(x, y) for x in ([0, 1, 2], [3, 4, 5], [6, 7, 8]) for y in ([0, 1, 2], [3, 4, 5], [6, 7, 8])]
            
        blocks = (rows + columns + blocks_3x3)

        # For every block, permutate all the constraints, and add them into constraints
        for block in blocks:
            permutations = self.permutate(block)
            for p in permutations:
                if [p[0], p[1]] not in constraints:
                    constraints.append([p[0], p[1]])
        
        self.constraints = constraints
    
    def createNeighbours(self):
        neighbours = [[ [] for i in board_range] for j in board_range]

        # For every variable, look through constraints, and add all 'neighbours' linked to variable by constraints.
        for var in self.variables:
            for constraint in self.constraints:
                coordinate = constraint[0]
                if coordinate[0] == var[0] and coordinate[1] == var[1]:
                    neighbours[var[0]][var[1]].append(constraint[1])
            '''print (var[0], ", ", var[1], ":")
            print (neighbours[var[0]][var[1]])
            print ("\n")'''
        self.neighbours = neighbours
    
    # complete
    def isComplete(self, assignment):
        for x in board_range:
            for y in board_range:
                # if domain contains more than 1 valie, and (x,y) is not in assignment
                if len(self.domains[x][y]) > 1 and (x, y) not in assignment:
                    return False
                    
        return True
    
    # Check for consistency
    def isConsistent(self, assignment, var, value):
        consistent = True
        
        # For every existing assignment, if there is a value equal to the current assignment and is a 'neighbour' of current box, then fail
        for key, val in assignment.iteritems():
            x = var[0]
            y = var[1]
            # If the value is 
            if val == value and key in self.neighbours[x][y]:
                consistent = False 
        return consistent
    
    # Check if puzzle is solved
    # Returns false if there is a single domain with more than 1 element
    def isSolved(self):
        for x in board_range:
            for y in board_range:
                if len(self.domains[x][y]) > 1:
                    return False
        return True
     
    def combine(self, alpha, beta):
        if isinstance(alpha, int):
            return [(alpha, b) for b in beta]
        if isinstance(beta, int):
            return [(a, beta) for a in alpha]
        return [(a, b) for a in alpha for b in beta]

    def permutate(self, iterable):
        result = list()

        for L in range(0, len(iterable) + 1):
            if L == 2:
                for subset in itertools.permutations(iterable, L):
                    result.append(subset)
        
        return result
    
    def initAssignment(self, assignment):
        # Iterate through all variables
        for var in self.variables:
            x = var[0]
            y = var[1]
            if len(self.domains[x][y]) == 1:
                # Trivial case where 1 value left
                assignment[var] = self.domains[x][y]
        return assignment

    def setAnswers(self, assignment):
        for x in board_range:
            for y in board_range:
                if len(self.domains[x][y]) > 1:
                    self.ans[x][y] = assignment[(x, y)]
                else:
                    self.ans[x][y] = self.domains[x][y].pop(0)
    
    # Checks if two values are different
    def checkConstraint(self, val1, val2):
        return val1 != val2
        
    def assign(self, var, value, assignment):
        assignment[var] = value
        self.doForwardChecking(var, value, assignment)
        
    def unassign(self, var, assignment):
        if var in assignment:
            x = var[0]
            y = var[1]
            for tuple in self.pruned[x][y]:
                neighbour = tuple[0]
                value = tuple[1]
                n_x = neighbour[0]
                n_y = neighbour[1]
                self.domains[n_x][n_y].append(value)
            
            self.pruned[x][y] = []
            
            del assignment[var]
        
    # var is a tuple with x and y
    def doForwardChecking(self, var, value, assignment):
        for neighbour in self.neighbours[var[0]][var[1]]:
            x = neighbour[0]
            y = neighbour[1]
            if neighbour not in assignment:
                if value in self.domains[x][y]:
                    self.domains[x][y].remove(value)
                    self.pruned[var[0]][var[1]].append((neighbour, value))
                    
    def numConflicts(self, var, value):
        conflicts = 0
        var_x = var[0]
        var_y = var[1]
        for neighbour in self.neighbours[var_x][var_y]:
            n_x = neighbour[0]
            n_y = neighbour[1]
            if len(self.domains[n_x][n_y]) > 1 and value in self.domains[n_x][n_y]:
                conflicts += 1
        return conflicts

    # AC-3 Algorithm
    def ac3(self):
        constraints = list(self.constraints)
        while constraints:
            # Obtain constraint/arc
            x, y = constraints.pop(0)
            # Revise constraints for x between x and y
            if self.revise_constraints(x, y):
                # If no valid assignments exists, return false
                if len(self.domains[x[0]][x[1]]) == 0:
                    return False

                # Add constraints from current box to neighbour
                for neighbour in self.neighbours[x[0]][x[1]]:
                    if neighbour != x:
                        constraints.append([neighbour, x])
        return True


    def revise_constraints(self, x, y):
        revised = False

        # For each value in domain x
        for value in self.domains[x[0]][x[1]]:
            if not any(self.checkConstraint(value,y) for y in self.domains[y[0]][y[1]]):
                self.domains[x[0]][x[1]].remove(value)
                revised = True

        return revised

    # Backtracking algorithm
    # Assigns values to variables based on MCV and, returns False if no consistent assignment found.
    def backtrack(self, assignment):
        # If all variables are assigned, return assignment
        if len(assignment) == len(self.variables):
            return assignment

        # Select most constrained variable
        var = self.select_most_con_var(assignment)

        # For every value in the sorted domain of variable
        for value in self.sort_domain(var):
            # If the assignment is consistent, assign
            if self.isConsistent(assignment, var, value):
                self.assign(var, value, assignment)
                
                # Backtrack further, return result if true
                result = self.backtrack(assignment)
                if result:
                    return result
                self.unassign(var, assignment)
        return False

    # Most Constrained Variable
    # Pick variable with fewest valid assignments
    # Heuristic to improve time-efficiency
    def select_most_con_var(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key = lambda var: len(self.domains[var[0]][var[1]]))

    # Least Constraining Value
    # Preference for values that rules out fewest choices for neighbouring variables
    def sort_domain(self, var):
        if len(self.domains[var[0]][var[1]]) == 1:
            return self.domains[var[0]][var[1]]

        return sorted(self.domains[var[0]][var[1]], key= lambda val: self.numConflicts(var, val))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print ("\nUsage: python sudoku.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python sudoku.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")

