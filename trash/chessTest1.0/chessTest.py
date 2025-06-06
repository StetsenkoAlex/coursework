from itertools import combinations_with_replacement
from typing import List, Tuple, Optional, Set
from abc import ABC, abstractmethod
# from grafics import *
from typing import List, Tuple, Optional, Set
from abc import ABC, abstractmethod
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QPushButton,
    QSpinBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QGraphicsRectItem,
    QGraphicsScene, 
    QGraphicsView, 
    QGraphicsRectItem, 
    QGraphicsSimpleTextItem

)
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QBrush, QPen, QColor, QFont, QPainter
from PySide6.QtUiTools import QUiLoader
# import sys
from re import fullmatch

class InputCoordinatesDialog(QDialog):
    def __init__(self, num_figures, parent=None):
        super().__init__(parent)
        self.num_figures = num_figures
        self.coordinate_inputs = []  # список QLineEdit
        self.figure_selectors = []   # список QComboBox
        self.resFig = []
        self.load_ui()
        self.create_input_fields()
        self.setWindowTitle("Шахматы :: Ввод координат")  # Устанавливаем заголовок
    @staticmethod
    def is_valid_format(s: str) -> bool:
        return bool(fullmatch(r"\d+\s\d+", s.strip()))
    def load_ui(self):
        loader = QUiLoader()
        file = QFile("input_coordinates.ui")
        if not file.open(QFile.ReadOnly):
            QMessageBox.critical(None, "Ошибка", "Не удалось открыть файл UI!")
            return

        self.ui = loader.load(file, self)
        file.close()

        self.okButton = self.ui.findChild(QPushButton, "okButton")
        self.cancelButton = self.ui.findChild(QPushButton, "cancelButton")
        self.mainLayout = self.ui.findChild(QVBoxLayout, "verticalLayout")
        self.coordinatesLayout = self.ui.findChild(QVBoxLayout, "coordinatesLayout")


        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        for input in self.coordinate_inputs:
            input.textChanged.connect(self.color)
        self.setLayout(self.mainLayout)
    def accept(self):
        """
        Возвращает список кортежей вида: (тип фигуры, (x, y))
        Например: [("Конь", (2, 3)), ("Визирь", (1, 4))]
        """
        for line_edit, combo in zip(self.coordinate_inputs, self.figure_selectors):
            x_str, y_str = line_edit.text().strip().split()
            self.resFig.append((combo.currentText(), (int(x_str), int(y_str))))
        super().accept()
    def create_input_fields(self):
        for i in range(self.num_figures):
            label = QLabel(f"Фигура {i+1}:")
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("Например: 1 1")
            line_edit.setStyleSheet("background-color: lightcoral;")
            line_edit.textChanged.connect(self.validate_all_inputs)

            combo = QComboBox()
            combo.addItems(["Horse", "Vizir"])

            self.coordinatesLayout.addWidget(label)
            self.coordinatesLayout.addWidget(line_edit)
            self.coordinatesLayout.addWidget(combo)
            
            self.coordinate_inputs.append(line_edit)
            self.figure_selectors.append(combo)
    def validate_all_inputs(self):
            all_valid = True
            for line_edit in self.coordinate_inputs:
                text = line_edit.text()
                if self.is_valid_format(text):
                    line_edit.setStyleSheet("background-color: lightgreen;")
                else:
                    line_edit.setStyleSheet("background-color: lightcoral;")
                    all_valid = False
            self.okButton.setEnabled(all_valid)
    def get_coordinates(self):
        """Возвращает список введенных координат"""
        return self.resFig
    

class ModalTable(QDialog):
    def __init__(self, table,solution, Parent=None):
        super().__init__(Parent)
        self.table = table
        self.solution = solution  # список кортежей: (x, y, 'k' или 'v')
        self.Parent = Parent
        self.load_ui()
        self.setWindowTitle("Одно из решений")
        self.vizualize_solution()


    # def init_ui(self):
    #     # Основной layout
    #     main_layout = QVBoxLayout(self)
        
    #     # Виджет для доски
    #     self.boardWidget = QWidget()
    #     main_layout.addWidget(self.boardWidget)
        
    #     # Layout для кнопок
    #     button_layout = QHBoxLayout()
        
    #     # Кнопка сохранения
    #     self.saveButton = QPushButton("Сохранить")
    #     self.saveButton.clicked.connect(self.save_to_file)
    #     button_layout.addWidget(self.saveButton)
        
    #     # Кнопка выхода
    #     self.exitButton = QPushButton("Закрыть")
    #     self.exitButton.clicked.connect(self.close)
    #     button_layout.addWidget(self.exitButton)
        
    #     main_layout.addLayout(button_layout)
    
    # def vizualize_solution(self):
    #     # Очистка предыдущего содержимого
    #     if self.boardWidget.layout():
    #         QWidget().setLayout(self.boardWidget.layout())
        
    #     size = self.Parent.boardSizeSpinBox.value()
    #     table = QTableWidget(size, size)
        
    #     # Настройка таблицы
    #     table.setEditTriggers(QTableWidget.NoEditTriggers)
    #     table.setSelectionMode(QTableWidget.NoSelection)
    #     table.horizontalHeader().setVisible(False)
    #     table.verticalHeader().setVisible(False)
        
    #     # Заполнение данными
    #     for x, y, piece in self.table:
    #         item = QTableWidgetItem("♘" if piece == "k" else "♖")
    #         item.setTextAlignment(Qt.AlignCenter)
    #         item.setBackground(QColor("lightblue") if piece == "k" else QColor("lightgreen"))
    #         table.setItem(y, x, item)
        
    #     # Установка layout
    #     layout = QVBoxLayout(self.boardWidget)
    #     layout.addWidget(table)
    #     self.boardWidget.setLayout(layout)

    def load_ui(self):
        loader = QUiLoader()
        file = QFile("board_window.ui")
        if not file.open(QFile.ReadOnly):
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть файл UI!")
            return
        self.ui = loader.load(file, self)
        file.close()

        # Основной layout
        self.mainLayout = self.ui.findChild(QVBoxLayout, "verticalLayout")
        # Виджет для доски
        self.boardWidget = self.ui.findChild(QWidget, "boardWidget")
        # self.mainLayout.addWidget(self.boardWidget)
        # Layout для кнопок
        self.button_layout = self.ui.findChild(QHBoxLayout, "buttonLayout")

        self.saveButton = self.ui.findChild(QPushButton, "saveButton")
        self.exitButton = self.ui.findChild(QPushButton, "exitButton")

        self.saveButton.clicked.connect(self.save_to_file)
        self.exitButton.clicked.connect(self.close)



        self.setLayout(self.mainLayout)

    def vizualize_solution(self):
        size = len(self.table.grid)
        print(self.table.grid)
        scene = QGraphicsScene()
        view = QGraphicsView()
        view.setScene(scene)
        view.setRenderHint(QPainter.Antialiasing)
        layout = QVBoxLayout(self.boardWidget)
        layout.addWidget(view)

        view.setSceneRect(-1,-1, size * Cell.CELL_SIZE+2, size * Cell.CELL_SIZE+2 )
        scene.setSceneRect(view.sceneRect())
        # Добавляем фигуры, которые проинициализированы пользователем
        for x,y,type in self.solution:
            if self.table.grid[y][x].is_empty():
                piece = Knight(x,y) if type == "k" else Vizir(x,y)
                self.table.add_piece(piece)
        for x in range(size):
            for y in range(size):
                if self.table.grid[y][x].threatened:
                    cell = Cell(x,y,3)
                elif self.table.grid[y][x].is_empty():
                    cell = Cell(x,y,0)
                else:
                    cell = Cell(x,y,1)
                scene.addItem(cell)
        # Добавляем фигуры, которые проинициализированы 
        # for x, y, piece in self.table:
        #     item = QTableWidgetItem("♘" if piece == "k" else "♖")
        #     item.setTextAlignment(Qt.AlignCenter)
        #     item.setBackground(QColor("lightblue") if piece == "k" else QColor("lightgreen"))
        #     # table.setItem(y, x, item)
        view.setFixedSize(view.sizeHint())
    def save_to_file(self):
        try:
            self.Parent.solver.write_output("output.txt", self.Parent.solver.solutions)
            QMessageBox.information(self, "Успех", "Решение сохранено в output.txt.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

class Cell(QGraphicsRectItem):
    CELL_SIZE = 32
    # Назначим цвет в зависимости от значения в матрице
    COLOR_MAP = {
            0: QColor("white"),
            1: QColor("green"),
            2: QColor("blue"),
            3: QColor("red")
        }
    def __init__(self, x, y, value):
        super().__init__(0, 0, self.CELL_SIZE, self.CELL_SIZE)
        self.setPos(x * self.CELL_SIZE, y * self.CELL_SIZE)
        self.setPen(QPen(QColor("black")))

        
        self.setBrush(self.COLOR_MAP.get(value, QColor("white")))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.board_created = False
        self.coords = []
        # Инициализация кнопок
        self.createBoardButton.clicked.connect(self.create_board)
        self.drawBoardButton.clicked.connect(self.draw_board)
        self.exitButton.clicked.connect(self.close)
        
        # Изначально кнопка "Нарисовать доску" неактивна
        self.drawBoardButton.setEnabled(False)

        self.solver = Solver()
    
    
    def load_ui(self):
        loader = QUiLoader()
        file = QFile("chess_ui.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        
        # Получаем доступ к элементам UI
        self.createBoardButton = self.ui.findChild(QPushButton, "createBoardButton")
        self.drawBoardButton = self.ui.findChild(QPushButton, "drawBoardButton")
        self.exitButton = self.ui.findChild(QPushButton, "exitButton")
        self.boardSizeSpinBox = self.ui.findChild(QSpinBox, "boardSizeSpinBox")
        self.requiredFiguresSpinBox = self.ui.findChild(QSpinBox, "requiredFiguresSpinBox")
        self.placedFiguresSpinBox = self.ui.findChild(QSpinBox, "placedFiguresSpinBox")
        # self.figureComboBox = self.ui.findChild(QComboBox, "figureComboBox")
        
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    def get_n_l_k_pieces(self):
        return self.boardSizeSpinBox.value(), self.requiredFiguresSpinBox.value(), self.placedFiguresSpinBox.value(), self.coords
    def create_board(self):
        """Создает доску и активирует кнопку рисования"""
        try:
            n = self.boardSizeSpinBox.value()
            l = self.requiredFiguresSpinBox.value()
            k = self.placedFiguresSpinBox.value()

            if k > 0:
                coords_menu = InputCoordinatesDialog(k, self)
                if coords_menu.exec() == QDialog.Accepted:
                    self.coords = coords_menu.get_coordinates()
            else:
                pass
            # Если доска успешно создана
            self.board_created = True
            self.drawBoardButton.setEnabled(True)

            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать доску: {str(e)}")
            self.drawBoardButton.setEnabled(False)
    
    def draw_board(self):
        """Отрисовывает доску"""
        if self.board_created:
            board, combinations = self.solver.generateBoard(*self.get_n_l_k_pieces())
            self.solver.solve(board, combinations)
            print(combinations)
           
            print(len(self.solver.solutions))
            ModalTable(board, next(iter(self.solver.solutions)), Parent = self).exec()
            # QMessageBox.information(self, "Информация", "Доска отрисована")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте доску")









class Piece(ABC):
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    @abstractmethod
    def get_moves(self) -> List[Tuple[int, int]]:
        """Возвращает возможные ходы фигуры"""
        pass
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Символьное обозначение фигуры"""
        pass

class Knight(Piece):
    moves = [(-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (-1, 2), (1, -2), (1, 2)]
    def get_moves(self):
        return [(-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (-1, 2), (1, -2), (1, 2)]
    
    @property
    def symbol(self):
        return 'k'

class Vizir(Piece):
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]
    def get_moves(self):
        return [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]
    
    @property
    def symbol(self):
        return 'v'

class BoardCell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.piece: Optional[Piece] = None
        self.threatened = False
    
    def place_piece(self, piece: Piece):
        self.piece = piece
    
    def remove_piece(self):
        self.piece = None
    
    def is_empty(self) -> bool:
        return self.piece is None
    
    def __str__(self):
        return self.piece.symbol if self.piece else '*' if self.threatened else '0'

class ChessBoard:
    def __init__(self, size: int):
        self.size = size
        self.grid = [[BoardCell(x, y) for x in range(size)] for y in range(size)]
        self.pieces: List[Piece] = []
    
    def add_piece(self, piece: Piece) -> bool:
        """Добавляет фигуру на доску с проверкой безопасности"""
        cell = self.grid[piece.y][piece.x]
        
        if not cell.is_empty() or not self.is_position_safe(piece):
            return False
        
        cell.place_piece(piece)
        self.pieces.append(piece)
        self.update_threats()
        return True
    
    def remove_piece(self, piece: Piece):
        """Удаляет фигуру с доски"""
        cell = self.grid[piece.y][piece.x]
        if cell.piece == piece:
            cell.remove_piece()
            self.pieces.remove(piece)
            self.update_threats()
    
    def is_position_safe(self, piece: Piece) -> bool:
        """Проверяет безопасность позиции для фигуры"""
        # Проверка выхода за границы
        if not (0 <= piece.x < self.size and 0 <= piece.y < self.size):
            return False
        
        # Проверка занятости клетки
        if not self.grid[piece.y][piece.x].is_empty():
            return False
        # Проверка атак от фигуры
        for dx, dy in piece.get_moves():
            nx, ny = piece.x + dx, piece.y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if not self.grid[ny][nx].is_empty() and self.grid[ny][nx].piece.symbol in ('k', 'v'):
                    return False

        # Проверка атак от других фигур
        for other in self.pieces:
            for dx, dy in other.get_moves():
                if other.x + dx == piece.x and other.y + dy == piece.y:
                    return False
        
        return True
    
    def update_threats(self):
        """Обновляет состояние угроз на доске"""
        # Сброс всех угроз
        for row in self.grid:
            for cell in row:
                cell.threatened = False
        
        # Обновление угроз
        for piece in self.pieces:
            for dx, dy in piece.get_moves():
                nx, ny = piece.x + dx, piece.y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    self.grid[ny][nx].threatened = True
    
    def get_solution(self) -> List[Tuple[int, int, str]]:
        """Возвращает текущее решение"""
        return sorted([(p.x, p.y, p.symbol) for p in self.pieces], 
                    key=lambda item: (item[1], item[0]))
    
    def visualize(self):
        """Визуализирует доску"""
        for row in self.grid:
            print(' '.join(str(cell) for cell in row))
        print()

class Solver:
    def __init__(self):
        self.solutions: Set[frozenset] = set()
    def __transform_solution_to_board(self): pass
    def solve(self, board: ChessBoard, combinations: List[str]):
        """Находит все решения с помощью backtracking"""
        def backtrack(remaining_pieces: List[str]):
            if not remaining_pieces:
                self.solutions.add(frozenset(board.get_solution()))
                return
            
            piece_type = remaining_pieces[0]
            for y in range(board.size):
                for x in range(board.size):
                    piece = Knight(x, y) if piece_type == 'k' else Vizir(x, y)
                    if board.add_piece(piece):
                        backtrack(remaining_pieces[1:])
                        board.remove_piece(piece)
        
        for combination in combinations:
            backtrack(combination)
    
    # @staticmethod
    # def read_input(file_path: str) -> Tuple[int, int, int, int, ChessBoard, List[str]]:
    #     """Чтение входных данных"""
    #     with open(file_path, 'r') as file:
    #         lines = file.readlines()
    #     n, l, k, v = map(int, lines[0].strip().split())
    #     board = ChessBoard(n)
    #     existing_piece = [list(map(int, line.strip().split())) for line in lines[1:] if line.strip().split()]
    #     # Чтение существующих фигур
    #     for i in range(k + v):
    #         x, y = existing_piece[i]
    #         piece = Knight(x, y) if i < k else Vizir(x, y)
    #         board.add_piece(piece)
        
    #     # Генерация комбинаций фигур для размещения
    #     combinations = set(combinations_with_replacement('kv', l))
        
    #     return n, l, k, v, board, combinations

    @staticmethod
    def generateBoard(n, l, k, pieces) -> Tuple[int, int, int, int, ChessBoard, List[str]]:
        """Чтение входных данных"""
        # with open(file_path, 'r') as file:
        #     lines = file.readlines()
        # n, l, k, v = map(int, lines[0].strip().split())
        board = ChessBoard(n)
        # existing_piece = [list(map(int, line.strip().split())) for line in lines[1:] if line.strip().split()]
        # Чтение существующих фигур
        for i in range(k):
            type, coords = pieces[i]
            piece = Knight(*coords) if type == "Horse" else Vizir(*coords)
            board.add_piece(piece)
        
        # Генерация комбинаций фигур для размещения
        combinations = set(combinations_with_replacement('kv', l))
        print(board.grid, combinations)
        return board, combinations
    
    @staticmethod
    def write_output(file_path: str, solutions: Set[frozenset]):
        """Запись результатов в файл"""
        with open(file_path, 'w') as file:
            if solutions:
                for solution in solutions:
                    solution_str = " ".join(f"({x}, {y}, {f})" for x, y, f in solution)
                    file.write(solution_str + "\n")
            else:
                file.write("no solutions\n")
    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
