# Artificial Intelligence 2022

# Project: Bimaru

### May 2, 2023

## 1 Introduction

The project of the Artificial Intelligence (AI) curriculum aims to develop a Python program that solves the Bimaru problem using AI techniques. The Bimaru problem, also known as Battleship Puzzle, Yubotu, or Solitaire Battleship, is a puzzle inspired by the well-known game of Battleship between two players. The game was created in Argentina by Jaime Poniachik and first appeared in 1982 in the Argentine magazine "Humor & Juegos." The game gained international recognition when it was first integrated into the World Puzzle Championship in 1992.

## 2 Problem Description

According to the description provided by [CSPlib](https://www.csplib.org/Problems/prob014/references/), the Bimaru game takes place on a square grid, representing an area of the ocean. Published games usually use a 10×10 grid, so we will assume this dimension in the context of the project. The ocean area contains a hidden fleet that the player must find. This fleet consists of a battleship (four squares in length), two cruisers (each with three squares in length), three destroyers (each with two squares in length), and four submarines (one square each). Ships can be oriented horizontally or vertically, and two ships do not occupy adjacent grid squares, not even diagonally. The player also receives row and column counts, i.e., the number of occupied squares in each row and column, and various hints. Each hint specifies the state of an individual square on the grid: water (the square is empty); circle (the square is occupied by a submarine); middle (this is a square in the middle of a battleship or cruiser); top, bottom, left, or right (this square is the end of a ship that occupies at least two squares). Figure 1 shows an example of the initial arrangement of a grid. Figure 2 shows a solution to that same grid. We can assume that a Bimaru instance has a unique solution.

(INSERT FIGURE 1 HERE)

Figure 1: Example of a Bimaru instance

(INSERT FIGURE 2 HERE)

Figure 2: Example of a solution for a Bimaru instance

The images in the statement were obtained from the Sea Battle application developed by AculApps for [IOS](https://apps.apple.com/pt/app/sea-battle-unlimited/id6444275561?l=en) and [Android](https://play.google.com/store/apps/details?id=ch.aculapps.seabattleunlimited&hl=en).

## 3 Objective

The objective of this project is to develop a program in Python 3.8 that, given a Bimaru instance, returns a solution, i.e., a fully filled grid. The program must be developed in a file [bimaru.py](./bimaru.py), which reads a Bimaru instance from the standard input in the format described in section 4.1. The program must solve the problem using a technique of your choice and print the solution to the standard output in the format described in section 4.2.

Usage:

```bash
python3 bimaru.py < <instance_file>
```

## 4 Input and Output Format

The following format is based on the document "File Format Description for Unsolvable Boards for CSPLib" written by Moshe Rubin (Mountain Vista Software) in December 2005.

### 4.1 Input Format

Bimaru problem instances consist of 3 parts:

1. The first line starts with the word ROW and contains information about the count of occupied positions in each row of the grid.
2. The second line starts with the word COLUMN and contains information about the count of occupied positions in each column of the grid.
3. The third line contains an integer corresponding to the number of hints.
4. The following lines start with the word `HINT` and contain hints corresponding to pre-filled positions.

Formally, each of the 4 parts described above has the following format:

1. `ROW <count-0> ... <count-9>`
2. `COLUMN <count-0> ... <count-9>`
3. `<hint total>`
4. `HINT <row> <column> <hint value>`

Possible values for `<row>` and `<column>` are integers between 0 and 9. The top-left corner of the grid corresponds to the coordinates (0,0). Possible values for `<hint value>` are: W (water), C (circle), T (top), M (middle), B (bottom), L (left), and R (right).

**Example**

The input file describing the instance in Figure 1 is as follows:

```
ROW 2 3 2 2 3 0 1 3 2 2
COLUMN 6 0 1 0 2 1 3 1 2 4
6
HINT 0 0 T
HINT 1 6 M
HINT 3 2 C
HINT 6 0 W
HINT 8 8 B
HINT 9 5 C
```

```
ROW\t2\t3\t2\t2\t3\t0\t1\t3\t2\t2\n
COLUMN\t6\t0\t1\t0\t2\t1\t3\t1\t2\t4\n
6\n
HINT\t0\t0\tT\n
HINT\t1\t6\tM\n
HINT\t3\t2\tC\n
HINT\t6\t0\tW\n
HINT\t8\t8\tB\n
HINT\t9\t5\tC\n
```

### 4.2 Output Format

The program's output should describe a solution to the Bimaru problem described in the input file, i.e., a fully filled grid that respects the rules outlined earlier. The output should follow the format below:

- 10 lines, where each line indicates the content of the respective row of the grid.
- In pre-filled positions (corresponding to hints), the respective uppercase letter is placed.
- In other positions, the respective lowercase letters are placed, except for water positions, which, for readability, are represented by a dot.
- All lines, including the last one, end with a newline character, i.e., `\n`.

Example:

The output describing the solution in Figure 2 is:

```
T.....t...
b.....M..t
......b..m
..C......m
c......c.b
..........
W...t.....
t...b...t.
m.......B.
b....C....
```

```
T.....t...\n
b.....M..t\n
......b..m\n
..C......m\n
c......c.b\n


..........\n
W...t.....\n
t...b...t.\n
m.......B.\n
b....C....\n
```

Certainly! Continuing from where we left off:

### 4.3 Example

Here is an example illustrating the input and output formats:

#### 4.3.1 Input Example

Input file (`instance.txt`):

```plaintext
ROW 2 3 2 2 3 0 1 3 2 2
COLUMN 6 0 1 0 2 1 3 1 2 4
6
HINT 0 0 T
HINT 1 6 M
HINT 3 2 C
HINT 6 0 W
HINT 8 8 B
HINT 9 5 C
```

#### 4.3.2 Output Example

Output file (`solution.txt`):

```plaintext
T.....t...
b.....M..t
......b..m
..C......m
c......c.b
..........
W...t.....
t...b...t.
m.......B.
b....C....
```
