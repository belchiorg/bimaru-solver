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
            self.board[hint[0]][hint[1]] = hint[2]

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
        hints = []
        hint_count = input()
        for i in range(int(hint_count)):
            hint = input().split()
            if hint[0] != "HINT":
                raise ValueError("Invalid input")
            hint = hint[1:]
            hints.append(hint)
            
            if(hint[2] != "W"):
                rows[hint[0]] = rows[hint[0]] - 1
                cols[hint[1]] = cols[hint[1]] - 1
        return Board(rows, cols, hints)

    # TODO: outros metodos da classe

    """
    ================================================================================================================
    
    Funções daqui para baixo são auxiliares para filtrar os casos gerados e ajudar a completar o jogo
    
    ================================================================================================================
    """ 

    def fill_rows(self, row: int):
        #* Função que preenche uma linha com água

        for row in self.rows:
            if row == 0:
                for i in range(10):
                    if self.board[row][i] is None:
                        self.board[row][i] = "W"

    def fill_cols(self, col: int):
        #* Função que preenche uma coluna com água

        for col in self.cols:
            if col == 0:
                for i in range(10):
                    if self.board[i][col] is None:
                        self.board[i][col] = "W"

    def prepare_board(self):
        #* Função que prepara o tabuleiro para ser jogado, preenchendo os espaços vazios com água

        self.fill_rows()
        self.fill_cols()

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
        # TODO
        pass

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
