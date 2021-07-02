import itertools

class Sudoku:    #define a class to obtain a new version of the sudoku puzzle of each cell containing all posible values
    def __init__(self, sudoku="""""", diagonal=False):
        sudoku = [[int(e) for e in row.split()] for row in sudoku.split('\n')]
        self._n = len(sudoku)
        for row in sudoku:
            if len(row) != self._n:
                raise ValueError("Puzzel is missing some values")
        self._line = range(self._n)
        self._matrix = [[i // self._n, i % self._n] for i in range(self._n ** 2)]
        self._link_map = self.mapValuestoarray(diagonal)
        self._depth_matrix = [[[float(len(self._link_map[i][j])), i, j] for j in self._line] for i in self._line]
        self._depth_line = list(itertools.chain.from_iterable(self._depth_matrix))
        k = max(e[0] for e in self._depth_line) + 2              # Analyze depth to assign the probable values for each cell
        for e in self._depth_line:
            e[0] = self._n - e[0] / k                                     #All probable values are saved into a matrix

        self._x = [[list(range(-self._n, 0)) for j in self._line] for i in self._line]
        # Apply the initial values.
        for i, j in self._matrix:
            value = sudoku[i][j]
            if value:
                self.Assign(value, i, j)        #checking the given values of the original matrix to the probable value matrix

    def mapValuestoarray(self, diagonal=False):  #creating the matrix which can contain multiple probable values
        n_region = int(self._n ** .5)
        # Check for the correct input.
        if n_region ** 2 != self._n:
            raise ValueError("Sudoku puzzel size is weird. Please check file again")
        region = [[i // n_region, i % n_region] for i in self._line]
        m = []
        for i in self._line:
            column = []
            for j in self._line:
                ceil = []
                # Add row.
                ceil.extend([[e, j] for e in self._line if e != i])
                # Add column.
                ceil.extend([[i, e] for e in self._line if e != j])
                # Add region.
                for a, b in region:
                    x = a + i // n_region * n_region
                    y = b + j // n_region * n_region
                    if x != i and y != j:
                        ceil.append([x, y])
                if diagonal:
                    if i == j:
                        ceil.extend([[e, e] for e in self._line if e != i])
                    if i == self._n - j - 1:
                        ceil.extend([[e, self._n - e - 1] for e in self._line if e != j])
                column.append(ceil)
            m.append(column)
        return m

    def Assign(self, value, x, y):  #assigning of values to an specific cell in the matrix
        if 0 < value <= self._n and -value in self._x[x][y]:
            self._Assign(-value, x, y)
            self._depth_line.remove(self._depth_matrix[x][y])
        else:
            raise ValueError('Failed to Assign %d to [%d;%d]!' % (value, y + 1, x + 1))  #assign fail if the value is out of range
        self._depth_line.sort(key=lambda e: e[0])

    def solve(self):#call the solution function
        solution = self.Start_Solve()
        self._x = solution
        return bool(solution)

    def Start_Solve(self):
        #check is depth matrix is empty
        if not self._depth_line:
            return self._x

        clue = self._depth_line[0] #next best probable values
        if not clue[0]:
            # possible values.
            return None
        i, j = clue[1], clue[2]
        del self._depth_line[0]

        x_value = self._x[i][j] #check all posibilities
        for value in x_value:
            log = []
            self._Assign(value, i, j, log)
            self._depth_line.sort(key=lambda e: e[0])

            if self.Start_Solve() is not None: #check for solution
                return self._x

            for k in log:  #if not solved depth matrix restored
                a, b = k >> 16, k & (1 << 16) - 1
                self._x[a][b].append(value)
                self._depth_matrix[a][b][0] += 1
        self._x[i][j] = x_value
        self._depth_line.insert(0, clue)
        self._depth_line.sort(key=lambda e: e[0])
        return None

    def _Assign(self, value, i, j, fallback=None):
        self._x[i][j] = [-value]

        for a, b in self._link_map[i][j]:
            try:
                self._x[a][b].remove(value)
                self._depth_matrix[a][b][0] -= 1
                if fallback is not None:
                    fallback.append(a << 16 | b)
            except ValueError:
                pass

    @property
    def solution(self):
        return self._x

    @staticmethod
    def format(x):
        return '\n'.join([' '.join([str(e[0]) for e in row]) for row in x]) #returns the self._x solved matrix


def solve(text):
    sudoku = Sudoku(text)  #call class constructor
    solved = sudoku.solve() #solution
    if solved:
        sol=Sudoku.format(sudoku.solution)
        return sol
    else:
        print('Failed to solve!') #if no solutions found
        return -1
def solver_algo(grid):
    sudoku=""
    for i in range(9):
        for j in range(9):
            sudoku=sudoku+""+str(grid[i][j])+" "
        sudoku=sudoku+"\n"
    sudoku = sudoku[:-1]
    sol =solve(sudoku)

    solution=[]
    row=[]
    for stri in sol.splitlines():
        for i  in range(len(stri)):
            if stri[i].isdigit():
                row.append(int(stri[i]))
        solution.append(row[:])
        row.clear()
    return solution    #return the solution list
