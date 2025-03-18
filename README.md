# Kropki Sudok Solver using Backtracking and Forward Checking

Implement the Backtracking Algorithm to solve the Kropki Sudoku puzzle.
The rules of the game are:
- The game board consists of 9 × 9 cells divided into 3 × 3 non-overlapping blocks as shown below. Some of the cells already have digits (1 to 9) assigned to them initially.
- The goal is to find assignments (1 to 9) for the empty cells so that every row, every column, and every 3x3 block contains the digits from 1 to 9 exactly once.
- A white dot between two adjacent cells requires that the value in one cell is exactly 1 greater than the value of the other cell. This could be satisfied in either direction; e.g., “3 & 4” or “4 & 3” will both satisfy the requirement. A black dot between two adjacent cells
requires that the value in one cell is exactly double the value of the other cell. This also could be satisfied in either direction; e.g., “3 & 6” or “6 & 3.” If there is no dot between two adjacent cells, then neither condition needs to be fulfilled between the two cells.

![img](/img/puzzle-solution.png)
