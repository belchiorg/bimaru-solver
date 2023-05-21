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


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

    #* Aqui já é viagem da minha cabeça
    def get_actions(self):
        self.board.get_actions() 


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    board = []

    rows = [] #? Este atributo diz respeito à contagem de partes de barcos por preencher por linha
    cols = [] #? Este atributo diz respeito à contagem de partes de barcos por preencher por coluna

    row_completed = [] #? Atributo que é reduzido quando se coloca um barco completo
    col_completed = [] #? Atributo que é reduzido quando se coloca um barco completo

    boats_to_place = { 4: 1, 3: 2, 2: 3, 1: 4 } #? Este atributo diz respeito ao número de barcos por colocar em cada tipo

    def __init__(self):
        for i in range(10):
            self.filled_rows.append(0)
            self.filled_cols.append(0)

            row = []
            for j in range(10):
                row.append(None)
            self.board.append(row)

    def __init__(self,rows:list, cols:list , hints: list):

        #* Initializes a blank board
        self.board = [[None] * len(cols)] * len(rows)

        #* Adds the rows and cols to the board
        self.rows = rows
        self.cols = cols

        #* Adds the hints to the board
        for hint in hints:
            # hint template: [row, col, val]
            self.insert_hint(hint[0], hint[1], hint[2])

    def __init__(self,rows:list, cols:list , row_completed: list, col_completed: list, hints: list):

        #* Initializes a blank board
        self.board = [[None] * len(cols) for i in range(len(rows))]
        self.board[0][0] = 'W'

        #* Adds the rows and cols to the board
        self.rows = rows
        self.cols = cols

        self.row_completed = row_completed
        self.col_completed = col_completed

        #* Adds the hints to the board
        for hint in hints:
            # hint template: [row, col, val]
            self.insert_hint(hint[0], hint[1], hint[2])
        

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""

        return (self.board[row-1][col], self.board[row+1][col]  )

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""

        return (self.board[row][col-1], self.board[row][col+1])
    

    def insert_hint(self, row: int, col: int, val: str):
        """Insere uma dica no tabuleiro."""
        if(val != 'W'):
            self.rows[row] = self.rows[row] - 1
            self.cols[col] = self.cols[col] - 1
        if(val == 'C'):
            self.row_completed[row] = self.row_completed[row] - 1
            self.col_completed[col] = self.col_completed[col] - 1
            self.boats_to_place[1] = self.boats_to_place[1] - 1
            
        self.board[row][col] = val

        self.surround_cell(row, col) #? Colocar esta função ao inicializar?
        

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
        
        #? Adiciona a lista de valores sem os barcos preenchidos
        rows_completed = rows
        cols_completed = cols

        hints = []
        hint_count = input()
        for i in range(int(hint_count)):
            hint = input().split()
            if hint[0] != "HINT":
                raise ValueError("Invalid input")
            hint = [eval(hint[1]), eval(hint[2]), hint[3]]
            hints.append(hint)

        return Board(rows, cols, rows_completed, cols_completed, hints)

    # TODO: Outros métodos da classe

    """
    ================================================================================================================
    
    Funções daqui para baixo são auxiliares para filtrar os casos gerados e ajudar a completar o jogo
    
    ================================================================================================================
    """ 

    def fill_rows(self, row: int):
        #* Função que preenche uma linha com água
        not_filled = []

        for i in range(len(self.cols)):
            if self.board[row][i] is None:
                self.board[row][i] = '.'
            else:
                not_filled.append(i)
        
        # Verifica se cada célula não preenchida é parte de um barco
        # e troca pela posição relativa correspondente caso tenha informação
        # suficiente (esta operação deve ser feita APÓS preencher o resto com água)
        for i in not_filled:
            self.convert_cell(row, i)

    def fill_cols(self, col: int):
        #* Função que preenche uma coluna com água
        not_filled = []

        for i in range(len(self.rows)):
            if self.board[i][col] is None:
                self.board[i][col] = '.'
            else:
                not_filled.append(i)
        
        # Verifica se cada célula não preenchida é parte de um barco
        # e troca pela posição relativa correspondente caso tenha informação
        # suficiente (esta operação deve ser feita APÓS preencher o resto com água)
        for i in not_filled:
            self.convert_cell(i, col)


    def set_cell(self, row: int, col: int, is_ship: bool):
        if (self.board[row][col] is not None and 'A' <= self.board[row][col] <= 'Z'):
            #? Lançar erro aqui, por não se poder mudar a célula?
            return
        
        if (is_ship == False):
            self.board[row][col] = '.'
        else:
            self.board[row][col] = '?' # Colocar uma parte do barco, cuja posição relativa é desconhecida
            self.convert_cell(row, col)

    def erase_cell(self, row: int, col: int):
        if (self.board[row][col] is not None and 'A' <= self.board[row][col] <= 'Z'):
            #? Lançar erro aqui, por não se poder mudar a célula?
            return
        
        self.board[row][col] = None

    def is_cell_ship(self, row: int, col: int):
        return 0 <= row < len(self.rows) and 0 <= col < len(self.cols) \
            and (self.board[row][col] is not None and any(self.board[row][col].upper() == x) for x in ['T', 'M', 'C', 'B', 'L', 'R', '?'])
    
    def is_cell_water(self, row: int, col: int):
        #* For optimization purposes, we can say that any cell out of bounds is water
        return (not 0 <= row < len(self.rows) or not 0 <= col < len(self.cols)) \
            or (self.board[row][col] is not None and any(self.board[row][col] == x) for x in ['.', '?'])
    
    def convert_cell(self, row: int, col: int):
        if (self.board[row][col] is None or self.board[row][col] == "." \
            or 'A' <= self.board[row][col] <= 'Z'):
            # Não alterar posições que não tenham barcos colocados pelo agente
            return
        
        # Os 8 possíveis casos para partes do barco, consoante as células adjacentes
        if self.is_cell_ship(row-1, col):
            if self.is_cell_ship(row+1, col): # Caso do barco em cima e em baixo
                self.board[row][col] = 'm'
            elif self.is_cell_water(row+1, col): # Caso do barco em cima e àgua em baixo
                self.board[row][col] = 'b'
        
        elif self.is_cell_ship(row, col-1):
            if self.is_cell_ship(row, col+1): # Caso do barco à esq e à direita
                self.board[row][col] = 'm'
            elif self.is_cell_water(row, col+1): # Caso do barco à esq e àgua à direita
                self.board[row][col] = 'r'

        elif self.is_cell_water(row-1, col):
            if self.is_cell_water(row+1, col) and self.is_cell_water(row, col-1) \
            and self.is_cell_water(row, col+1): # Caso de haver àgua à volta
                self.board[row][col] = 'c'
            elif self.is_cell_ship(row+1, col): # Caso de àgua em cima e barco em baixo
                self.board[row][col] = 't'
        
        # Caso de àgua à esq. e barco à dir
        elif self.is_cell_water(row, col-1) and self.is_cell_ship(row, col+1):
            self.board[row][col] = 'l'

        else: # Impossível de saber a posição relativa
            self.board[row][col] = '?'

    def surround_cell(self, row: int, col: int):
        """This function takes two coordinates for a cell with a part of a ship on it
        and fills some of the cells around it with water, depending on the relative
        position of such part"""
        if(self.board[row][col] is None or self.is_cell_water(row, col)):
            # Do nothing if the specified cell is not a ship part
            return
        
        # Relative positions of squares to put water
        toFill = []
        if(self.board[row][col].upper() == 'C'):
            toFill = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        elif(self.board[row][col].upper() == 'T'):
            toFill = [(2, -1), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (2, 1)]
        elif(self.board[row][col].upper() == 'L'):
            toFill = [(-1, 2), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (1, 2)]
        elif(self.board[row][col].upper() == 'R'):
            toFill = [(-1, -2), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (1, -2)]
        elif(self.board[row][col].upper() == 'B'):
            toFill = [(-2, -1), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-2, 1)]
        elif(self.board[row][col].upper() == 'M' or self.board[row][col] == '?'):
            toFill = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for rel_pos in toFill:
            if not(0 <= row+rel_pos[0] < len(self.rows) and 0 <= col+rel_pos[1] < len(self.cols)):
                continue

            if(self.is_cell_ship(row+rel_pos[0], col+rel_pos[1])):
                #? Raise exception to affirm there is a mistake, or just return an error value?
                raise AssertionError('Ship part is on a cell that should supposedly be water')

            self.set_cell(row+rel_pos[0], col+rel_pos[1], False)
            
    def attempt_boat_horizontally(self, row: int, col:int):

        possibilities = []

        #Check if we can place the first part of the ship

        for i in range(4):
            if (not is_cell_ship(row-1, col-1) and not is_cell_ship(row, col-1) and not is_cell_ship(row+1, col-1)):
                #Checks the column right before the boat
                if (not is_cell_ship(row-1, col) and not is_cell_ship(row, col) and not is_cell_ship(row+1, col)):
                    #Checks the boat column
                    if (not is_cell_ship(row-1, col+1) and is_cell_ship(row+1, col+1)):
                        #Checks the next column





        #* Some more complexity to identify cases where hints were given
        if (not self.is_cell_water(row, col) or self.board[row][col].lower() == 'l'):
            possibilities.append({"row": row, "col": col, "size":1, "orientation": "h"})
        else:
            return possibilities

        for i in range(1,4):
            if (not self.is_cell_water(row, col)):    
                #! É importante garantir que há volta de todos os outros barcos, temos sempre agua
                possibilities.append({"row": row, "col": col, "size":i+1, "orientation": "h"})
            else:
                return possibilities
        return possibilities
    
    def attempt_boat_vertically(self, row: int, col:int):
        #? Logica inicial: Vai testar se dá para colocar barcos verticalmente na pos (x,y), se conseguir, junta a uma list. 
        #? Talvez o melhor fosse dar return a um tuple, mas em objeto ficou mais facil para "representar" e talvez perceberes o que eu tinha pensado

        possibilities = []

        for i in range(4):
            if (not self.is_cell_water()):    
                #! É importante garantir que há volta de todos os outros barcos, temos sempre agua
                possibilities.append({"row": row, "col": col, "size": i+1, "orientation": "v"})
            else:
                return possibilities
        return possibilities
    
    def attempt_complete_boat_hint(self, row: int, col: int):
        #? Lógica inicial: vai usar uma hint para colocar outra parte do barco que seja óbvio que irá
        #? usar. Caso a parte do barco seja a outra extremidade, reduz o número de barcos do tipo gerado
        if not self.is_cell_ship(row, col):
            return
        
        #* Caso da hint ser o meio do barco (deve-se ver em que orientação se deve colocar o barco)
        if self.board[row][col].upper() == 'M':
            vertical = self.adjacent_horizontal_values(row, col)
            horizontal = self.adjacent_vertical_values(row, col)

            #* Caso vertical
            if vertical == (None, None) and (self.is_cell_water(horizontal[0]) or self.is_cell_water(horizontal[1])):
                self.set_cell(row-1, col, True)
                self.set_cell(row+1, col, True)

                #* Depois de set_cell, a peça do barco pode transformar numa extremidade do barco
                if self.board[row-1][col].upper() == 'T' and self.board[row+1][col].upper() == 'B':
                    self.boats_to_place[3] = self.boats_to_place[3] - 1

            #* Caso horizontal
            elif horizontal == (None, None) and (self.is_cell_water(vertical[0]) or self.is_cell_water(vertical[1])):
                self.set_cell(row, col-1, True)
                self.set_cell(row, col+1, True)

                #* Depois de set_cell, a peça do barco pode transformar numa extremidade do barco
                if self.board[row][col-1].upper() == 'L' and self.board[row][col+1].upper() == 'R':
                    self.boats_to_place[3] = self.boats_to_place[3] - 1
        
        #* Caso de ser uma extremidade do barco
        elif not any(self.board[row][col].upper() == x for x in ['C', '?']):
            #* Verifica onde deve estar o adjacente e qual o outcome esperado 
            adjacent_cases = {
                'T': ((1, 0), 'B'),
                'B': ((-1, 0), 'T'),
                'L': ((0, 1), 'R'),
                'R': ((0, -1), 'L')
            }
            
            adjacent = adjacent_cases[self.board[row][col].upper()]

            #? Talvez colocar um erro para o caso de estar out of bounds?

            self.set_cell(row+adjacent[0][0], col+adjacent[0][1], True)

            #* Depois de set_cell, a peça do barco pode transformar numa extremidade do barco
            if self.board[row+adjacent[0][0]][col+adjacent[0][1]].upper() == adjacent[1]:
                self.boats_to_place[2] = self.boats_to_place[2] - 1

            #? Talvez adicionar uma função para quando a peça colocada fica no meio de duas peças?
    
    def get_actions(self):
        actions = []
        for row in self.board:
            for col in self.board[row]:
                if self.board[row][col] == None:
                    #! Falta verificar os espaços com barcos
                    actions.append(self.attempt_boat_horizontally)
                    actions.append(self.attempt_boat_vertically)
        return actions;

    def prepare_board(self):
        #* Função que prepara o tabuleiro para ser jogado, preenchendo os espaços vazios com água

        #* Assume-se que todas as hints já foram circundada com água
        rows_to_fill = [i for i, x in enumerate(self.rows) if x == 0]
        for i in rows_to_fill:
            self.fill_rows(i)

        cols_to_fill = [i for i, x in enumerate(self.cols) if x == 0]
        for i in cols_to_fill:
            self.fill_rows(i)
        self.fill_cols()

    def to_string(self):
        #! Esta função apenas funciona quando o board está preenchido!
        board_to_str = self.board.copy()
        rows_as_strings = []

        for i in range(len(self.rows)):
            for j in range(len(self.cols)):
                if board_to_str[i][j] is None:
                    board_to_str[i][j] = '_'

            rows_as_strings.append("".join(board_to_str[i]))
        
        return ("\n".join(rows_as_strings))

    # TODO: outros metodos da classe

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        return state.get_actions()

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

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

    # This needs to be done automatically
    board.surround_cell(0, 0)
    board.surround_cell(1, 6)
    board.surround_cell(3, 2)
    board.surround_cell(6, 0)
    board.surround_cell(8, 8)
    board.surround_cell(9, 5)
    
    print(board.to_string())


