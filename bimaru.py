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


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    board = []

    rows = [] #? Este atributo diz respeito à contagem de partes de barcos por preencher por linha
    cols = [] #? Este atributo diz respeito à contagem de partes de barcos por preencher por coluna

    row_completed = [] #? Atributo que é reduzido quando se coloca um barco completo
    col_completed = [] #? Atributo que é reduzido quando se coloca um barco completo

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
        self.board = [[None] * len(cols)] * len(rows)

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
            if (val == 'T'):
                self.insert_hint(row+1, col, '?')
            elif(val == 'B'):
                self.insert_hint(row-1, col, '?')
            elif(val == 'R'):
                self.insert_hint(row, col+1, '?')
            elif(val == 'L'):
                self.insert_hint(row, col-1, '?')
            elif(val == 'C'):
                self.row_completed[row] = self.row_completed[row] - 1
                self.col_completed[col] = self.col_completed[col] - 1
        

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
            rows = input().split()
            if rows[0] != "ROW":
                raise ValueError()
            return rows[1:]

        def read_cols():
            cols = input().split()
            if cols[0] != "COLUMN":
                raise ValueError("Invalid input")
            return cols[1:]

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
            hint = hint[1:]
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

        for i in range(self.cols):
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

        for i in range(10):
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
        if ('A' <= self.board[row][col] <= 'Z'):
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
            and any(self.board[row][col].upper() == x for x in ['T', 'M', 'C', 'B', 'L', 'R', '?'])
    
    def is_cell_water(self, row: int, col: int):
        #* For optimization purposes, we can say that any cell out of bounds is water
        return (not 0 <= row < len(self.rows) or not 0 <= col < len(self.cols)) \
            or (self.board[row][col] is not None and self.board[row][col] == '.')
    
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

            self.set_cell(row+rel_pos[0], col+rel_pos[1])
            

    def prepare_board(self):
        #* Função que prepara o tabuleiro para ser jogado, preenchendo os espaços vazios com água
        self.fill_rows()
        self.fill_cols()

    def to_string(self):
        #! Esta função apenas funciona quando o board está preenchido!
        rows_as_strings = []
        for i in range(len(self.rows)):
            rows_as_strings.append("".join(self.rows))
        
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
        # TODO
        pass

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
    pass
