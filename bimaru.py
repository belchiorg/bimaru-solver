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
        print(new_state.board.to_string_debug())
        return new_state


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    board = []

    rows = []  # ? Este atributo diz respeito à contagem de partes de barcos por preencher por linha
    cols = []  # ? Este atributo diz respeito à contagem de partes de barcos por preencher por coluna

    init_rows = []
    init_cols = []

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

    def __init__(self, rows: list, cols: list, hints: list, boats: dict, init_rows: list, init_cols: list):

        # * Initializes a blank board
        self.board = [[None] * len(cols) for i in range(len(rows))]

        # * Adds the rows and cols to the board
        self.rows = rows
        self.cols = cols

        self.init_rows = init_rows
        self.init_cols = init_cols

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

        init_rows = rows.copy()
        init_cols = cols.copy()

        hints = []
        hint_count = input()
        for i in range(int(hint_count)):
            hint = input().split()
            if hint[0] != "HINT":
                raise ValueError("Invalid input")
            hint = [eval(hint[1]), eval(hint[2]), hint[3]]
            hints.append(hint)

        return Board(rows, cols, hints, {4: 1, 3: 2, 2: 3, 1: 4}, init_rows, init_cols)

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

        #* Belchior, suponho que não seja necessário usar o convert_cell para converter 
        #* a parte do barco noutra, dependendo dos blocos em redor.
        #* No entanto, coloquei esta função abaixo para preencher as células à volta com água 
        #* (as que fazem sentido colocar). É isto que se pretende?   - Gonçalo
        #* Sim, é isso mesmo. - Belchior
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
            # Caso do barco em cima e àgua em baixo
            elif self.is_cell_water(row+1, col):
                self.board[row][col] = 'b'
                self.surround_cell(row, col)

        elif self.is_cell_ship(row, col-1):
            if self.is_cell_ship(row, col+1):  # Caso do barco à esq e à direita
                self.board[row][col] = 'm'
                self.surround_cell(row, col)
            # Caso do barco à esq e àgua à direita
            elif self.is_cell_water(row, col+1):
                self.board[row][col] = 'r'
                self.surround_cell(row, col)

        elif self.is_cell_water(row-1, col):
            if self.is_cell_water(row+1, col) and self.is_cell_water(row, col-1) \
                    and self.is_cell_water(row, col+1):  # Caso de haver àgua à volta
                self.board[row][col] = 'c'
                self.surround_cell(row, col)
            # Caso de àgua em cima e barco em baixo
            elif self.is_cell_ship(row+1, col):
                self.board[row][col] = 't'
                self.surround_cell(row, col)

        # Caso de àgua à esq. e barco à dir
        elif self.is_cell_water(row, col-1) and self.is_cell_ship(row, col+1):
            self.board[row][col] = 'l'
            self.surround_cell(row, col)

        else:  # Impossível de saber a posição relativa
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
        self.num_empty_cells = count


    def get_possible_actions_for_size(self, size: int, init_rows: list, init_cols:list):
        actions = []
        for row in range(len(init_rows)):
            if init_rows[row] >= size:
                actions.extend(self.attempt_boat_row(row, size))
        if size > 1:
            for col in range(len(init_cols)):
                if init_cols[col] >= size:
                    actions.extend(self.attempt_boat_col(col, size))
        return actions

    def attempt_boat_row(self, row, size):
        possibilities = []
        for col in range(len(self.cols)-size+1):
            if self.is_cell_water(row, col):
                continue
            #Checks if there are ships in the col before the boat
            if self.check_if_boat_exists(row, col, False):
                continue
            if not self.is_cell_ship(row-1, col-1) and not self.is_cell_ship(row+1, col-1) and not self.is_cell_ship(row, col-1):
                #It's going to check all cols of the boat, both above and below
                add = True
                for i in range(size):
                    if not self.is_cell_ship(row+1, col+i) and not self.is_cell_ship(row-1, col+i):
                        count = 0
                        value = self.get_value(row, col+i)
                        if value is None:
                            if self.cols[col+i] == 0 or self.rows[row]-count == 0:
                                add = False
                                break
                            count += 1
                        elif value.upper() in ['W', '.']:
                            add = False
                            break
                        elif self.is_cell_ship(row, col+i):
                            if i == 0:
                                if value.upper() not in ['L', '?']:
                                    add = False
                                    break
                            elif i == size-1:
                                if value.upper() not in ['R', '?']:
                                    add = False
                                    break
                            else:
                                if value.upper() not in ['M', '?']:
                                    add = False
                                    break
                            
                        #Checks the cols after the boat
                    
            if add:
                if self.is_cell_ship(row-1, col+size) or self.is_cell_ship(row+1, col+size) or self.is_cell_ship(row, col+size):
                    possibilities.append({'row': row, 'col': col, 'size': size, 'orientation': 'h'})
        return possibilities
    
    def attempt_boat_col(self, col, size):
        possibilities = []
        for row in range(len(self.rows)-size+1):
            if self.is_cell_water(row, col):
                continue
            if self.check_if_boat_exists(row, col, False):
                continue
            #Checks if there are ships in the row before the boat
            if not self.is_cell_ship(row-1, col-1) and not self.is_cell_ship(row-1, col+1) and not self.is_cell_ship(row-1, col):
                #It's going to check all rows of the boat, both left and right
                add = True
                for i in range(size):
                    if not self.is_cell_ship(row+i, col+1) and not self.is_cell_ship(row+i, col-1):
                        value = self.get_value(row+i, col)
                        count = 0
                        if value is None:
                            if self.rows[row+i] == 0 or self.cols[col]-count == 0:
                                add = False
                                break
                            count += 1
                        elif value.upper() in ['W', '.']:
                            add = False
                            break
                        elif self.is_cell_ship(row+i, col):
                            if i == 0:
                                if value.upper() not in ['T', '?']:
                                    add = False
                                    break
                            elif i == size-1:
                                if value.upper() not in ['B', '?']:
                                    add = False
                                    break
                            else:
                                if value.upper() not in ['M', '?']:
                                    add = False
                                    break
                if add:
                    if not self.is_cell_ship(row+size, col-1) and not self.is_cell_ship(row+size, col+1) and not self.is_cell_ship(row+size, col):
                        possibilities.append({'row': row, 'col': col, 'size': size, 'orientation': 'v'})
        return possibilities
            

    def attempt_boat_horizontally(self, row: int, col: int):
        """
        This function takes two coordinates for a cell and checks if it is possible to place a boat horizontally
        on that cell. If it is, it returns a list of all the possible sizes for the boat.
        """

        possibilities = []

        if self.is_cell_ship(row, col):
            if self.check_if_boat_exists(row, col, False) != []:
                return possibilities

        # Check if we can place the first part of the ship
        if (not self.is_cell_ship(row-1, col-1) and not self.is_cell_ship(row, col-1) and not self.is_cell_ship(row+1, col-1)):
            # Checks the column right before the boat
            if (not self.is_cell_ship(row-1, col) and not self.is_cell_ship(row+1, col) and (self.board[row][col] is None or any(x == self.board[row][col].upper() for x in ['L', '?']))):
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

        if self.is_cell_ship(row, col):
            if self.check_if_boat_exists(row, col, True) != []:
                return possibilities

        # Check if we can place the first part of the ship
        if (not self.is_cell_ship(row-1, col-1) and not self.is_cell_ship(row-1, col) and not self.is_cell_ship(row-1, col+1)):

            # Checks the column right before the boat
            if (not self.is_cell_ship(row, col-1) and not self.is_cell_ship(row, col+1) and (self.board[row][col] is None or any(x == self.board[row][col].upper() for x in ['T', '?']))):
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
        if self.get_value(row, col) is None:
            return []
        boat_pos = []
        if self.get_value(row, col) == 'C':
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

        for i in range(4, 0, -1):
            if self.boats_to_place[i]>0:
                return self.get_possible_actions_for_size(i, self.init_rows, self.init_cols)
        
        return []
    
    def update_boats_to_place(self):
        '''Updates the boats_to_place variable to reflect on the already placed boats.'''
        to_place = { 4: 1, 3: 2, 2: 3, 1: 4 }
        for i in range(len(self.rows)):
            size = 0
            for j in range(len(self.cols)):
                if (self.board[i][j] is None):
                    size = 0
                    continue

                if (self.board[i][j].upper() == 'L' and size == 0) \
                or (self.board[i][j].upper() == 'M' and size > 0):
                    size = size + 1
                elif self.board[i][j].upper() == 'R' and size > 0:
                    to_place[size + 1] = to_place[size + 1] - 1
                    size = 0
                elif self.board[i][j].upper() == 'C' and size == 0:
                    to_place[1] = to_place[1] - 1
                else:
                    size = 0

        for i in range(len(self.cols)):
            size = 0
            for j in range(len(self.rows)):
                if (self.board[j][i] is None):
                    size = 0
                    continue
                
                if (self.board[j][i].upper() == 'T' and size == 0) \
                or (self.board[j][i].upper() == 'M' and size > 0):
                    size = size + 1
                elif self.board[j][i].upper() == 'B' and size > 0:
                    to_place[size + 1] = to_place[size + 1] - 1
                    size = 0
                else:
                    size = 0

        self.boats_to_place = to_place
        
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

            # * Assume-se que todas as hints já foram circundada com água
            rows_to_fill = [i for i, x in enumerate(self.rows) if x == 0]
            for i in rows_to_fill:
                self.fill_rows(i)

            cols_to_fill = [i for i, x in enumerate(self.cols) if x == 0]
            for i in cols_to_fill:
                self.fill_cols(i)

            if rows_to_fill == last_rows_to_fill and cols_to_fill == last_cols_to_fill:
                break
            else:
                last_rows_to_fill = rows_to_fill.copy()
                last_cols_to_fill = cols_to_fill.copy()

        # As hints deixam de ser necessárias, por isso liberta-se espaço
        self.hints = []

        self.update_num_empty_cells()
        #self.update_boats_to_place()


    def insert_boat(self, action):
        """
        Function that inserts a boat in the board, given an action \n
        example_action = {"row": 4, "col": 3, "size": 2, "orientation": "v"}
        """
        row = action["row"]
        col = action["col"]
        size = action["size"]
        orientation = action["orientation"]

        if size == 1:
            self.set_cell_type(row, col, 'c')
            self.boats_to_place[1] -= 1
            return
    
        for i in range(1,size-1):
            if orientation == 'h':
                self.set_cell_type(row, col+i, 'm')
            elif orientation == 'v':
                self.set_cell_type(row+i, col, 'm')
        
        if orientation == 'h':
            self.set_cell_type(row, col, 'l')
            self.set_cell_type(row, col+size-1, 'r')

        elif orientation == 'v':
            self.set_cell_type(row, col, 't')
            self.set_cell_type(row+size-1, col, 'b')

        self.boats_to_place[size] -= 1

        

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

        return ("\n".join(rows_as_strings) + "\n")
    
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
        pass

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

    print(board.to_string_debug())

    print(depth_first_tree_search(problem).state.board.to_string())