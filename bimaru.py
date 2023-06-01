# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 05:
# 102447 Guilherme Belchior
# 103540 Gonçalo Alves

import sys
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

import copy


class BimaruState:
    state_id = 0
    board: "Board"

    def __init__(self, board):
        self.board = board
        self.board.prepare_board()
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

    # * Aqui já é viagem da minha cabeça
    def get_actions(self):
        return self.board.get_actions()

    def get_result(self, action) -> "BimaruState":
        new_state = BimaruState(copy.deepcopy(self.board))
        new_state.board.place_boat(action)
        new_state.board.prepare_board()
        return new_state


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    board = []

    rows = []  # ? Este atributo diz respeito à contagem de partes de barcos por preencher por linha
    cols = []  # ? Este atributo diz respeito à contagem de partes de barcos por preencher por coluna

    hints = [] #* Esta veriável é só usada no início. Quando o algoritmo chega à parte das actions
               #* e do result, o atributo é apagado (para não ocupar espaço).
    num_empty_cells = 100
    
    boats_to_place = {}

    def __init__(self):
        for i in range(10):
            self.filled_rows.append(0)
            self.filled_cols.append(0)

            row = []
            for j in range(10):
                row.append(None)
            self.board.append(row)

    def __init__(self, rows: list, cols: list, hints: list, boats: dict):

        # * Initializes a blank board
        self.board = [[None] * len(cols) for i in range(len(rows))]

        # * Adds the rows and cols to the board
        self.rows = rows
        self.cols = cols

        # * Adds the hints (to be used temporarily)
        self.hints = hints

        self.boats_to_place = boats

        # * Adds the hints to the board
        for hint in hints:
            # hint template: [row, col, val]
            self.insert_hint(hint[0], hint[1], hint[2])

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""

        if row == 0:
            top = None
            bottom = self.board[row + 1][col]
        elif row == 9:
            bottom = None
            top = self.board[row - 1][col]
        else:
            top = self.board[row - 1][col]
            bottom = self.board[row + 1][col]

        return (top, bottom)

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""

        if col == 0:
            left = None
            right = self.board[row][col + 1]
        elif col == 9:
            right = None
            left = self.board[row][col - 1]
        else:
            left = self.board[row][col - 1]
            right = self.board[row][col + 1]

        return (left, right)

    def insert_hint(self, row: int, col: int, val: str):
        """Insere uma dica no tabuleiro."""
        if (val != 'W'):
            self.rows[row] = self.rows[row] - 1
            self.cols[col] = self.cols[col] - 1
        if (val == 'C'):
            self.boats_to_place[1] = self.boats_to_place[1] - 1

        self.board[row][col] = val

        self.surround_cell(row, col)  # ? Colocar esta função ao inicializar?
        a = self.check_if_boat_exists(row, col, False) + self.check_if_boat_exists(row, col, True)
        if a != [] and val != 'C':
            self.boats_to_place[len(a)] -= 1

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """
        def read_rows():
            rowText = input().split()
            if rowText[0] != "ROW":
                raise ValueError()
            rows = [eval(i) for i in rowText[1:]]
            return rows

        def read_cols():
            colsText = input().split()
            if colsText[0] != "COLUMN":
                raise ValueError("Invalid input")
            cols = [eval(i) for i in colsText[1:]]
            return cols
        
        rows = read_rows()
        cols = read_cols()

        hints = []
        hint_count = input()
        for i in range(int(hint_count)):
            hint = input().split()
            if hint[0] != "HINT":
                raise ValueError("Invalid input")
            hint = [eval(hint[1]), eval(hint[2]), hint[3]]
            hints.append(hint)

        return Board(rows, cols, hints, {4: 1, 3: 2, 2: 3, 1: 4})

    # TODO: Outros métodos da classe

    """
    ================================================================================================================
    
    Funções daqui para baixo são auxiliares para filtrar os casos gerados e ajudar a completar o jogo
    
    ================================================================================================================
    """

    def fill_rows(self, row: int):
        # * Função que preenche uma linha com água
        not_filled = []

        for i in range(len(self.cols)):
            if self.board[row][i] is None:
                self.board[row][i] = '.'
            else:
                not_filled.append(i)

        # Verifica se cada célula não preenchida é parte de um barco
        # e troca pela posição relativa correspondente caso tenha informação
        # suficiente (esta operação deve ser feita APÓS preencher o resto com água)
        skip_verif = []
        for i in not_filled:
            r = self.convert_cell(row, i)
            if r == True and (row, i) not in skip_verif:
                a = self.check_if_boat_exists(row, i, False) + self.check_if_boat_exists(row, i, True)
                if a != []:
                    skip_verif.extend(a)
                    if self.board[row][i].upper() == 'C':
                        self.boats_to_place[1] -= 1
                    else:
                        self.boats_to_place[len(a)] -= 1

    def fill_cols(self, col: int):
        # * Função que preenche uma coluna com água
        not_filled = []

        for i in range(len(self.rows)):
            if self.board[i][col] is None:
                self.board[i][col] = '.'
            else:
                not_filled.append(i)

        # Verifica se cada célula não preenchida é parte de um barco
        # e troca pela posição relativa correspondente caso tenha informação
        # suficiente (esta operação deve ser feita APÓS preencher o resto com água)
        skip_verif = []
        for i in not_filled:
            r = self.convert_cell(i, col)
            if r == True and (i, col) not in skip_verif:
                a = self.check_if_boat_exists(i, col, True) + self.check_if_boat_exists(i, col, False)
                if a != []:
                    skip_verif.extend(a)
                    if self.board[i][col].upper() == 'C':
                        self.boats_to_place[1] -= 1
                    else:
                        self.boats_to_place[len(a)] -= 1

    def fill_rows_with_boats(self, row: int):
        to_fill = [i for i in range(len(self.cols)) if self.board[row][i] is None]
        if len(to_fill) != self.rows[row] or to_fill == []:
            return
        
        to_check = []
        # Add boat parts for all empty cells in row
        for i in to_fill:
            self.set_cell(row, i, True)
            if self.board[row][i] != '?':
                to_check.append(i)
            else:
                # Cells that changed are automattically surrounded, the others aren't
                self.surround_cell(row, i)
        
        # For every boat part that was converted from '?', check if it's on a newly
        # completed boat and decrement the number of boats to place if positive
        for i in to_check:
            a = self.check_if_boat_exists(row, i, True) + self.check_if_boat_exists(row, i, False)
            if a != []:
                if self.board[row][i].upper() == 'C':
                    self.boats_to_place[1] -= 1
                else:
                    self.boats_to_place[len(a)] -= 1

    def fill_cols_with_boats(self, col: int):
        to_fill = [i for i in range(len(self.rows)) if self.board[i][col] is None]
        if len(to_fill) != self.cols[col] or to_fill == []:
            return
        
        to_check = []
        # Add boat parts for all empty cells in row
        for i in to_fill:
            self.set_cell(i, col, True)
            if self.board[i][col] != '?':
                to_check.append(i)
            else:
                # Cells that changed are automattically surrounded, the others aren't
                self.surround_cell(i, col)
        
        # For every boat part that was converted from '?', check if it's on a newly
        # completed boat and decrement the number of boats to place if positive
        for i in to_check:
            a = self.check_if_boat_exists(i, col, True) + self.check_if_boat_exists(i, col, False)
            if a != []:
                if self.board[i][col].upper() == 'C':
                    self.boats_to_place[1] -= 1
                else:
                    self.boats_to_place[len(a)] -= 1

    def set_cell(self, row: int, col: int, is_ship: bool):
        if (self.board[row][col] is not None and 'A' <= self.board[row][col] <= 'Z'):
            # ? Lançar erro aqui, por não se poder mudar a célula?
            return False

        if (is_ship == False):
            self.board[row][col] = '.'
        else:
            # Colocar uma parte do barco, cuja posição relativa é desconhecida
            self.board[row][col] = '?'
            self.convert_cell(row, col)
            self.rows[row] = self.rows[row] - 1
            self.cols[col] = self.cols[col] - 1
        
        return True

    def set_cell_type(self, row: int, col: int, cell_type: str):
        if (self.board[row][col] is not None and 'A' <= self.board[row][col] <= 'Z'):
            # ? Lançar erro aqui, por não se poder mudar a célula?
            return

        # Check if cell_type is a part of a ship, if so, decrements the row and col values
        if (any(cell_type.upper() == x for x in ['T', 'M', 'C', 'B', 'L', 'R', '?']) and not self.is_cell_ship(row, col)):
            self.rows[row] = self.rows[row] - 1
            self.cols[col] = self.cols[col] - 1

        self.board[row][col] = cell_type

        self.surround_cell(row, col)



    def erase_cell(self, row: int, col: int):
        #! Atenção: Esta função não reverte as células à volta que são preenchidas com água, 
        #! caso tenha sido colocada uma parte de um navio!
        if (self.board[row][col] is not None and 'A' <= self.board[row][col] <= 'Z'):
            # ? Lançar erro aqui, por não se poder mudar a célula?
            return

        self.board[row][col] = None

    def is_cell_ship(self, row: int, col: int):
        return (0 <= row < len(self.rows) and 0 <= col < len(self.cols) and (self.board[row][col] is not None and any(self.board[row][col].upper() == x for x in ['T', 'M', 'C', 'B', 'L', 'R', '?'])))

    def is_cell_water(self, row: int, col: int) -> bool:
        # * For optimization purposes, we can say that any cell out of bounds is water
        return (not 0 <= row < len(self.rows) or not 0 <= col < len(self.cols)) \
            or (self.board[row][col] is not None and any(self.board[row][col] == x for x in ['.', 'W']))

    def convert_cell(self, row: int, col: int):
        '''Converts a cell to another one depending on the adjacent cells, and returns True
        if the state of the cell has changed'''
        if (self.board[row][col] is None or self.board[row][col] == "."
                or 'A' <= self.board[row][col] <= 'Z'):
            # Não alterar posições que não tenham barcos colocados pelo agente
            return False
        
        before_conversion = self.board[row][col]

        # Os 8 possíveis casos para partes do barco, consoante as células adjacentes
        if self.is_cell_ship(row-1, col):
            if self.is_cell_ship(row+1, col):  # Caso do barco em cima e em baixo
                self.board[row][col] = 'm'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
            # Caso do barco em cima e àgua em baixo
            if self.is_cell_water(row+1, col):
                self.board[row][col] = 'b'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]

        if self.is_cell_ship(row, col-1):
            if self.is_cell_ship(row, col+1):  # Caso do barco à esq e à direita
                self.board[row][col] = 'm'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
            # Caso do barco à esq e àgua à direita
            elif self.is_cell_water(row, col+1):
                self.board[row][col] = 'r'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]

        if self.is_cell_water(row-1, col):
            if self.is_cell_water(row+1, col) and self.is_cell_water(row, col-1) \
                    and self.is_cell_water(row, col+1):  # Caso de haver àgua à volta
                self.board[row][col] = 'c'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
            # Caso de àgua em cima e barco em baixo
            elif self.is_cell_ship(row+1, col):
                self.board[row][col] = 't'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]

        # Caso de àgua à esq. e barco à dir
        if self.is_cell_water(row, col-1) and self.is_cell_ship(row, col+1):
            self.board[row][col] = 'l'
            self.surround_cell(row, col)
            return before_conversion != self.board[row][col]

        elif self.get_incomplete_boat_length(row, col, (0, 0)) == 4:  # Impossível de saber a posição relativa
            if self.is_cell_ship(self.board[row-1][col]):
                self.board[row][col] = 'b'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
            elif self.is_cell_ship(self.board[row+1][col]):
                self.board[row][col] = 't'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
            elif self.is_cell_ship(self.board[row][col-1]):
                self.board[row][col] = 'r'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
            elif self.is_cell_ship(self.board[row][col+1]):
                self.board[row][col] = 'l'
                self.surround_cell(row, col)
                return before_conversion != self.board[row][col]
        else:
            self.board[row][col] = '?'

        # Return whether the state has changed or not
        return before_conversion != self.board[row][col]

    def surround_cell_list(self, row: int, col: int):
        '''This function takes two coordinates for a cell with a part of a ship on it
        and returns a list of all coordinates waiting to be filled'''
        if (self.board[row][col].upper() == 'C'):
            return [(-1, 0), (-1, 1), (0, 1), (1, 1),
                      (1, 0), (1, -1), (0, -1), (-1, -1)]
        elif (self.board[row][col].upper() == 'T'):
            return [(2, -1), (1, -1), (0, -1), (-1, -1),
                      (-1, 0), (-1, 1), (0, 1), (1, 1), (2, 1)]
        elif (self.board[row][col].upper() == 'L'):
            return [(-1, 2), (-1, 1), (-1, 0), (-1, -1),
                      (0, -1), (1, -1), (1, 0), (1, 1), (1, 2)]
        elif (self.board[row][col].upper() == 'R'):
            return [(-1, -2), (-1, -1), (-1, 0), (-1, 1),
                      (0, 1), (1, 1), (1, 0), (1, -1), (1, -2)]
        elif (self.board[row][col].upper() == 'B'):
            return [(-2, -1), (-1, -1), (0, -1), (1, -1),
                      (1, 0), (1, 1), (0, 1), (-1, 1), (-2, 1)]
        elif (self.board[row][col].upper() == 'M' or self.board[row][col] == '?'):
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            return []

    def surround_cell(self, row: int, col: int):
        """This function takes two coordinates for a cell with a part of a ship on it
        and fills some of the cells around it with water, depending on the relative
        position of such part"""
        if (self.board[row][col] is None or self.is_cell_water(row, col)):
            # Do nothing if the specified cell is not a ship part
            return

        # Relative positions of squares to put water
        toFill = self.surround_cell_list(row, col)
        
        for rel_pos in toFill:
            if not (0 <= row+rel_pos[0] < len(self.rows) and 0 <= col+rel_pos[1] < len(self.cols)):
                continue

            if (self.is_cell_ship(row+rel_pos[0], col+rel_pos[1])):
                # ? Raise exception to affirm there is a mistake, or just return an error value?
                raise AssertionError(
                    'Ship part is on a cell that should supposedly be water')

            self.set_cell(row+rel_pos[0], col+rel_pos[1], False)

    def update_num_empty_cells(self):
        count = 0
        for i in range(len(self.rows)):
            for j in range(len(self.cols)):
                if self.board[i][j] is None:
                    count += 1
                elif self.board[i][j] == '?':
                    count += self.get_incomplete_boat_length(i, j, (0, 0))

        self.num_empty_cells = count

    def get_incomplete_boat_length(self, row: int, col: int, exclusion: tuple):
        if not 0 <= row < len(self.rows) or not 0 <= col < len(self.cols) or self.board[row][col] is None or self.is_cell_water(row, col):
            return 0

        recursion_list = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        try:
            recursion_list.remove(exclusion)
        except ValueError:
            pass
        return 1 + sum(self.get_incomplete_boat_length(row+i[0], col+i[1], (0-i[0], 0-i[1])) for i in recursion_list)

    def attempt_boat_horizontally(self, row: int, col: int):
        possibilities = []

        # Check if we can place the first part of the ship
        if (self.is_cell_ship(row-1, col-1) or self.is_cell_ship(row, col-1) or self.is_cell_ship(row+1, col-1)):
            return possibilities
        # Checks the column right before the boat
        if (self.is_cell_ship(row-1, col) or self.is_cell_ship(row+1, col) or not (self.board[row][col] is None or any(x == self.board[row][col].upper() for x in ['L', '?']))):
            return possibilities
        
        # Checks the boat column
        rows = self.rows.copy()
        cols = self.cols.copy()
        for i in range(1, 5):
            if self.boats_to_place[i] == 0:
                continue
            if col + i > 10:
                return possibilities
            # Checks the next columns
            if (not self.is_cell_ship(row-1, col+i) and not self.is_cell_ship(row+1, col+i)):
                if (self.is_cell_water(row, col+i-1)):
                    return possibilities
                if (self.is_cell_ship(row, col+i)):
                    if (self.board[row][col+i-1] is None):
                        if rows[row] == 0 or cols[col+i-1] == 0:
                            return possibilities
                    continue
                elif (self.board[row][col+i-1] is None):
                    if rows[row] == 0 or cols[col+i-1] == 0:
                        return possibilities
                    rows[row] -= 1
                    cols[col+i-1] -= 1
                    possibilities.append(
                        {"row": row, "col": col, "size": i, "orientation": "h"})
                elif (self.board[row][col+i-1].upper() == '?'):
                    possibilities.append(
                        {"row": row, "col": col, "size": i, "orientation": "h"})
                elif (self.board[row][col+i-1].upper() == 'R'):
                    possibilities.append(
                        {"row": row, "col": col, "size": i, "orientation": "h"})
                    return possibilities
            else:
                return possibilities
        return possibilities

    def attempt_boat_vertically(self, row: int, col: int):

        possibilities = []
        # Check if we can place the first part of the ship
        if (self.is_cell_ship(row-1, col-1) or self.is_cell_ship(row-1, col) or self.is_cell_ship(row-1, col+1)):
            return possibilities

        # Checks the column right before the boat
        if (self.is_cell_ship(row, col-1) or self.is_cell_ship(row, col+1) or not (self.board[row][col] is None or any(x == self.board[row][col].upper() for x in ['T', '?']))):
            return possibilities
            
        # Checks the boat column
        rows_val = self.rows.copy()
        cols_val = self.cols.copy()
        for i in range(1, 5):
            if self.boats_to_place[i] == 0:
                continue
            if row + i > 10:
                return possibilities
            # Checks the next columns
            if (not self.is_cell_ship(row+i, col-1) and not self.is_cell_ship(row+i, col+1)):
                if (self.is_cell_water(row+i-1, col)):
                    return possibilities
                elif (self.is_cell_ship(row+i, col)):
                    if (self.board[row+i-1][col] is None):
                        if rows_val[row+i-1] == 0 or cols_val[col] == 0:
                            return possibilities
                    continue
                elif (self.board[row+i-1][col] is None):
                    if rows_val[row+i-1] == 0 or cols_val[col] == 0:
                        return possibilities
                    rows_val[row+i-1] -= 1
                    cols_val[col] -= 1
                    if i > 1:
                        possibilities.append(
                            {"row": row, "col": col, "size": i, "orientation": "v"})
                elif (self.board[row+i-1][col].upper() == '?'):
                    possibilities.append(
                        {"row": row, "col": col, "size": i, "orientation": "v"})
                elif (self.board[row+i-1][col] == 'B'):
                    if i > 1:
                        possibilities.append(
                            {"row": row, "col": col, "size": i, "orientation": "v"})
                    return possibilities
            else:
                return possibilities

        return possibilities

    def check_if_boat_exists(self, row: int, col: int, vertical: bool):
        boat_pos = []
        if self.get_value(row, col).upper() == 'C':
            return [(row, col)]
        
        boat_pos.append((row, col))
        if vertical:
            if self.get_value(row, col).upper() == 'T':
                for i in range(1, 4):
                    boat_pos.append((row+i,col))
                    if not self.is_cell_ship(row+i, col) or self.board[row+i][col] == '?':
                        return []
                    if self.get_value(row+i, col).upper() == 'B':
                        return boat_pos
            elif self.get_value(row, col).upper() == 'B':
                for i in range(1, 4):
                    boat_pos.append((row-i,col))
                    if not self.is_cell_ship(row-i, col) or self.board[row-i][col] == '?':
                        return []
                    if self.get_value(row-i, col).upper() == 'T':
                        return boat_pos
            elif self.get_value(row, col).upper() == 'M':
                for a in range(1, 3):
                    boat_pos.append((row-a,col))
                    if not self.is_cell_ship(row-a, col) or self.board[row-a][col] == '?':
                        return []
                    if self.get_value(row-a, col).upper() == 'T':
                        break
                    elif a == 2:
                        return []
                for b in range(1, 3):
                    boat_pos.append((row+b,col))
                    if not self.is_cell_ship(row+b, col) or self.board[row+b][col] == '?':
                        return []
                    if self.get_value(row+b, col).upper() == 'B':
                        break
                    elif a == 2:
                        return []
                return boat_pos
        else:
            if self.get_value(row, col).upper() == 'L':
                for i in range(1, 4):
                    boat_pos.append((row,col+i))
                    if not self.is_cell_ship(row, col+i) or self.board[row][col+i] == '?':
                        return []
                    if self.get_value(row, col+i).upper() == 'R':
                        return boat_pos
            elif self.get_value(row, col).upper() == 'R':
                for i in range(1, 4):
                    boat_pos.append((row,col-i))
                    if not self.is_cell_ship(row, col-i) or self.board[row][col-i] == '?':
                        return []
                    if self.get_value(row, col-i).upper() == 'L':
                        return boat_pos
            elif self.get_value(row, col).upper() == 'M':
                for a in range(1, 3):
                    boat_pos.append((row,col-a))
                    if not self.is_cell_ship(row, col-a) or self.board[row][col-a] == '?':
                        return []
                    if self.get_value(row, col-a).upper() == 'L':
                        break
                    elif a == 2:
                        return []
                for b in range(1, 3):
                    boat_pos.append((row,col+b))
                    if not self.is_cell_ship(row, col+b) or self.board[row][col+b] == '?':
                        return []
                    if self.get_value(row, col+b).upper() == 'R':
                        break
                    elif a == 2:
                        return []
                return boat_pos
        return []

    def attempt_complete_boat_hint(self, row: int, col: int):
        # ? Lógica inicial: vai usar uma hint para colocar outra parte do barco que seja óbvio que irá
        # ? usar. Caso a parte do barco seja a outra extremidade, reduz o número de barcos do tipo gerado
        # ? Retorna True quando consegue colocar uma célula adjacente e False caso contrário
        if not self.is_cell_ship(row, col):
            return True # Para efeitos de otimização
        
        if self.board[row][col].upper() == 'C':
            return True

        # * Caso da hint ser o meio do barco (deve-se ver em que orientação se deve colocar o barco)
        if self.board[row][col].upper() == 'M':
            vertical = self.adjacent_vertical_values(row, col)
            horizontal = self.adjacent_horizontal_values(row, col)

            # * Caso vertical
            if vertical == (None, None) and (self.is_cell_water(row, col-1) or self.is_cell_water(row, col+1)):
                self.set_cell(row-1, col, True)
                self.set_cell(row+1, col, True)

                # * Depois de set_cell, a peça do barco pode transformar numa extremidade do barco
                if self.board[row-1][col].upper() == 'T' and self.board[row+1][col].upper() == 'B':
                    self.boats_to_place[3] -= 1
            
                return True                

            # * Caso horizontal
            elif horizontal == (None, None) and (self.is_cell_water(row-1, col) or self.is_cell_water(row+1, col)):
                self.set_cell(row, col-1, True)
                self.set_cell(row, col+1, True)

                # * Depois de set_cell, a peça do barco pode transformar numa extremidade do barco
                if self.board[row][col-1].upper() == 'L' and self.board[row][col+1].upper() == 'R':
                    self.boats_to_place[3] -= 1
                
                return True

        # * Caso de ser uma extremidade do barco
        elif not any(self.board[row][col].upper() == x for x in ['C', '?']):
            # * Verifica onde deve estar o adjacente e qual o outcome esperado
            adjacent_cases = {
                'T': ((1, 0), 'B'),
                'B': ((-1, 0), 'T'),
                'L': ((0, 1), 'R'),
                'R': ((0, -1), 'L')
            }

            adjacent = adjacent_cases[self.board[row][col].upper()]

            # ? Talvez colocar um erro para o caso de estar out of bounds?

            a = self.set_cell(row+adjacent[0][0], col+adjacent[0][1], True)

            # * Depois de set_cell, a peça do barco pode transformar numa extremidade do barco
            if a == True and self.board[row+adjacent[0][0]][col+adjacent[0][1]].upper() == adjacent[1]:
                self.boats_to_place[2] -= 1

            # ? Talvez adicionar uma função para quando a peça colocada fica no meio de duas peças?
            return True

        return False

    def get_actions(self) -> list:
        actions = []
        if self.num_empty_cells < sum(i * self.boats_to_place[i] for i in range(1, 5)):
            return []
        
        if any([i < 0 for i in self.rows + self.cols]):
            return []

        # for row in range(len(self.board)):
        #     for col in range (len(self.board[row])):
        #         if not self.is_cell_water(row, col):
        #             if self.rows[row] > 0:
        #                 actions.extend(self.attempt_boat_horizontally(row, col))
        #             if self.cols[col] > 0:
        #                 actions.extend(self.attempt_boat_vertically(row, col))

        size = 0
        for i in range(4, 0, -1):
            if self.boats_to_place[i] > 0:
                size = i
                break

        for row in range(len(self.board)):
            skip = 0
            for col in range (len(self.board[row])):
                if col + size > len(self.board):
                    break
                if skip > 0:
                    skip -= 1
                    continue
                if self.rows[row] > 0:
                    if self.is_cell_ship(row, col):
                        already_boat = len(self.check_if_boat_exists(row, col, False))
                        if already_boat > 0:
                            skip = already_boat-1
                            continue
                        elif self.get_value(row, col).upper() in ['M', 'T', 'C', 'B' ]:
                            skip = 1
                            continue
                    else:
                        if self.cols[col] <= 0:
                            continue
                    actions.extend(self.attempt_boat_horizontally(row, col))
                else:
                    break
    
        for col in range(len(self.board)):
            skip = 0
            for row in range (len(self.board[row])):
                if row + size > len(self.board):
                    break
                if skip > 0:
                    skip -= 1
                    continue
                if self.cols[col] > 0:
                    if self.is_cell_ship(row, col):
                        already_boat = len(self.check_if_boat_exists(row, col, True))
                        if already_boat > 0:
                            skip = already_boat-1
                            continue
                        elif self.get_value(row, col).upper() in ['M', 'L', 'C', 'R' ]:
                            skip = 1
                            continue
                    else:
                        if self.rows[row] <= 0:
                            continue
                    actions.extend(self.attempt_boat_vertically(row, col))
                else:
                    break

        for boat_size in range(4,0, -1):
            if self.boats_to_place[boat_size] > 0:
                filtered_actions = list(filter(lambda x: x['size'] == boat_size, actions))
                if len(filtered_actions) < self.boats_to_place[boat_size]:
                    return []
                return self.sort_actions(filtered_actions)
        return []
    
    def sort_actions(self, actions: list) -> list:

        def sorting_aux(row, col):
            value = 0
            if self.rows[row] == 0 and self.cols[col] == 0:
                value += 100
            return self.rows[row] + self.cols[col] + value

        actions.sort(key=lambda x: sorting_aux(x['row'], x['col']))

        return actions

    def corre_linhas(self):
        max_size = 0
        for i in range(4,0 , -1):
            if self.boats_to_place[i] > 0:
                max_size = i
                break

        for row in range(len(self.board)):
            cont = 0
            for col in range(len(self.board[row])):
                if self.is_cell_ship(row, col):
                    cont += 1
                elif self.is_cell_water(row, col):
                    cont = 0                
                else:
                    if cont >= max_size:
                        self.set_cell_type(row, col, 'W')
            
            cont = 0
            for col in range(len(self.board[row])-1 , -1, -1):
                if self.is_cell_ship(row, col):
                    cont += 1
                elif self.is_cell_water(row, col):
                    cont = 0
                else:
                    if cont >= max_size:
                        self.set_cell_type(row, col, 'W')
            
        for col in range(len(self.board)):
            cont = 0
            for row in range(len(self.board[row])):
                if self.is_cell_ship(row, col):
                    cont += 1
                elif self.is_cell_water(row, col):
                    cont = 0
                else:
                    if cont >= max_size:
                        self.set_cell_type(row, col, 'W')
            
            cont = 0
            for row in range(len(self.board[row])-1 , -1, -1):
                if self.is_cell_ship(row, col):
                    cont += 1
                elif self.is_cell_water(row, col):
                    cont = 0
                else:
                    if cont >= max_size:
                        self.set_cell_type(row, col, 'W')
        
    def prepare_board(self):
        # * Função que prepara o tabuleiro para ser jogado, preenchendo os espaços vazios com água

        last_rows_to_fill = []
        last_cols_to_fill = []
        # Estas funções têm de ser executadas várias vezes para garantir que o board fica preparado
        while True:
            # * Coloca partes de barco que podem ser inferidas pelas hints
            i = 0
            while i < len(self.hints):
                hint = self.hints[i]
                ret_val = self.attempt_complete_boat_hint(hint[0], hint[1])
                if ret_val == True:
                    del self.hints[i]
                else:
                    i = i + 1

            #self.corre_linhas()

            # * Assume-se que todas as hints já foram circundada com água
            rows_to_fill = [i for i, x in enumerate(self.rows) if x == 0 and i not in last_rows_to_fill]
            for i in rows_to_fill:
                self.fill_rows(i)

            cols_to_fill = [i for i, x in enumerate(self.cols) if x == 0 and i not in last_cols_to_fill]
            for i in cols_to_fill:
                self.fill_cols(i)

            rows_left = set(range(len(self.rows))).symmetric_difference(set(rows_to_fill + last_rows_to_fill))
            for i in rows_left:
                self.fill_rows_with_boats(i)

            cols_left = set(range(len(self.cols))).symmetric_difference(set(cols_to_fill + last_cols_to_fill))
            for i in cols_left:
                self.fill_cols_with_boats(i)

            if len(rows_to_fill) == 0 and len(cols_to_fill) == 0:
                break
            else:
                last_rows_to_fill.extend(rows_to_fill)
                last_cols_to_fill.extend(cols_to_fill)

        # As hints deixam de ser necessárias, por isso liberta-se espaço
        self.hints = []

        self.update_num_empty_cells()

    def to_string(self):
        #! Esta função apenas funciona quando o board está preenchido!
        #! Mudar para a submissão final
        board_to_str = [self.board[i].copy() for i in range(len(self.rows))]
        rows_as_strings = []

        for i in range(len(self.rows)):
            for j in range(len(self.cols)):
                if board_to_str[i][j] is None:
                    board_to_str[i][j] = '_'

            rows_as_strings.append("".join(board_to_str[i]))

        return ("\n".join(rows_as_strings))
    
    def to_string_debug(self):
        #! Esta função apenas funciona quando o board está preenchido!
        #! Mudar para a submissão final
        board_to_str = [self.board[i].copy() for i in range(len(self.rows))]
        rows_as_strings = []

        for i in range(len(self.rows)):
            for j in range(len(self.cols)):
                if board_to_str[i][j] is None:
                    board_to_str[i][j] = '_'

            rows_as_strings.append("".join(board_to_str[i] + [" ", str(self.rows[i])]))
        
        rows_as_strings.append("".join(str(self.cols[j]) for j in range(len(self.cols))))
        rows_as_strings.append(str(self.boats_to_place))

        return ("\n".join(rows_as_strings) + "\n")

    # TODO: outros metodos da classe

    def place_boat(self, action):
        """
        Places a boat according to the action passed as argument
        """
        row = action["row"]
        col = action["col"]
        size = action["size"]
        orientation = action["orientation"]

        if size == 1:
            self.set_cell_type(row, col, 'c')
            self.boats_to_place[1] -= 1
            return
        
        
        if orientation == 'h':
            if not self.get_value(row, col) == 'L':
                self.set_cell_type(row, col, 'l')
            for i in range(1, size-1):
                if not self.get_value(row, col+i) == 'M':
                    self.set_cell_type(row, col+i, 'm')
            if not self.get_value(row, col+size-1) == 'R':
                self.set_cell_type(row, col+size-1, 'r')

        else:
            if not self.get_value(row, col) == 'T':
                self.set_cell_type(row, col, 't')
            for i in range(1, size-1):
                if not self.get_value(row+i, col) == 'M':
                    self.set_cell_type(row+i, col, 'm')
            if not self.get_value(row+size-1, col) == 'B':
                self.set_cell_type(row+size-1, col, 'b')
        
        self.boats_to_place[size] -= 1
        return

        
        


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        self.initial = BimaruState(board)
        return

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        return state.get_actions()

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        return state.get_result(action)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        for i in range(len(state.board.rows)):
            if state.board.rows[i] != 0:
                return False

        for i in range(len(state.board.cols)):
            if state.board.cols[i] != 0:
                return False
            
        for i in range(1,5):
            if state.board.boats_to_place[i] != 0:
                return False

        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        som = 0
        for i in range(4, 0, -1):
            som += (i * node.state.board.boats_to_place[i])**2
        som += sum(node.state.board.rows + node.state.board.cols)
        return som

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    # TODO: Initializar o Problem, Iniciar o primeiro estado e o board
    # TODO: Usar a técnica de procura para resolver a instância

    board = Board.parse_instance()
    
    problem = Bimaru(board)

    if problem.goal_test(problem.initial) == True:
        print(board.to_string())
    else:
        print(depth_first_tree_search(problem).state.board.to_string())