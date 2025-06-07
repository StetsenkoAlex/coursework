from itertools import combinations_with_replacement
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
    QGraphicsRectItem,
    QGraphicsScene, 
    QGraphicsView, 
    QGraphicsRectItem, 


)
from PySide6.QtCore import QFile, QThread, Signal, QRegularExpression
from PySide6.QtGui import QPen, QColor, QPainter
from PySide6.QtUiTools import QUiLoader

class InputCoordinatesDialog(QDialog):
    """
    Диалоговое окно для ручного ввода координат фигур на шахматной доске.
    """
    def __init__(self, num_figures: int, parent: Optional[QDialog] = None):
        """
        Конструктор диалога координат.

        :param num_figures (int): Количество фигур для размещения
        :param parent (Optional[QDialog]): Родительское окно
        """
        super().__init__(parent)
        self.Parent = parent
        self.num_figures = num_figures
        self.coordinate_inputs = []  # список QLineEdit
        self.figure_selectors = []   # список QComboBox
        self.resFig = []
        self.load_ui()
        self.create_input_fields()
        self.setWindowTitle("Шахматы :: Ввод координат")
    @staticmethod
    def is_valid_format(s: str) -> bool:
        """
        Проверяет, соответствует ли строка формату "X Y" (два целых числа через пробел).
        
        :param s: строка для проверки

        :return: True, если формат корректный
        """
        regex = QRegularExpression(r"^\d+\s\d+$")
        return regex.match(s.strip()).hasMatch()
    def load_ui(self):
        """
        Загружает интерфейс из .ui-файла и подключает кнопки.
        """
        loader = QUiLoader()
        file = QFile(r"ui/input_coordinates.ui")
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
    def __check_safe_position(self, pieces) -> bool:
        """
        Проверяет, не угрожают ли фигуры друг другу.

        :param pieces: Итерация по парам (QLineEdit, QComboBox)

        :return: True, если позиции безопасны
        """
        tempBoard = ChessBoard(self.Parent.boardSizeSpinBox.value())
        for line_edit, combo in pieces:
            x, y = map(int,line_edit.text().strip().split())
            type = combo.currentText()
            piece = Knight(x, y) if type == "Horse" else Vizir(x, y)
            if not tempBoard.add_piece(piece):
                return False
        return True

    def accept(self) -> None:
        """
        Проверяет валидность позиций и сохраняет их.
        Если все позиции безопасны — принимает диалог и сохраняет данные в self.resFig.
        """
        if self.__check_safe_position(zip(self.coordinate_inputs, self.figure_selectors)):
            
            for line_edit, combo in zip(self.coordinate_inputs, self.figure_selectors):
                x_str, y_str = line_edit.text().strip().split()
                self.resFig.append((combo.currentText(), (int(x_str), int(y_str))))
            super().accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Фигуры находтся под боем")
    def create_input_fields(self) -> None:
        """
        Создаёт поля ввода координат и выпадающие списки для выбора типа фигуры.
        """
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
    """
    Диалоговое окно, отображающее одно из решений размещения фигур на шахматной доске.
    """
    def __init__(self, table: "ChessBoard", solution: List[Tuple[int, int, str]], Parent=None):
        """
        Инициализация диалога, загрузка интерфейса и визуализация переданного решения.

        :param table: Объект доски (ChessBoard)
        :param solution: Список кортежей с координатами и типами фигур
        :param Parent: Родительское окно (обычно MainWindow)
        """
        super().__init__(Parent)
        self.table = table
        self.solution = solution  # список кортежей: (x, y, 'k' или 'v')
        self.Parent = Parent
        self.load_ui()
        self.setWindowTitle("Шахматы :: Одно из решений")
        self.vizualize_solution()


    def load_ui(self):
        """
        Загружает интерфейс из файла .ui и находит нужные элементы.
        """
        loader = QUiLoader()
        file = QFile(r"ui/board_window.ui")
        if not file.open(QFile.ReadOnly):
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть файл UI!")
            return
        self.ui = loader.load(file, self)
        file.close()

        # Основной layout
        self.mainLayout = self.ui.findChild(QVBoxLayout, "verticalLayout")
        # Виджет для доски
        self.boardWidget = self.ui.findChild(QWidget, "boardWidget")

        # Layout для кнопок
        self.button_layout = self.ui.findChild(QHBoxLayout, "buttonLayout")

        self.saveButton = self.ui.findChild(QPushButton, "saveButton")
        self.exitButton = self.ui.findChild(QPushButton, "exitButton")

        self.saveButton.clicked.connect(self.save_to_file)
        self.exitButton.clicked.connect(self.close)



        self.setLayout(self.mainLayout)

    def vizualize_solution(self):
        """
        Визуализирует текущее решение на графической сцене с использованием QGraphicsView.
        """
        size = len(self.table.grid)
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
        # Визуализация всех ячеек доски
        for x in range(size):
            for y in range(size):
                if not self.table.grid[y][x].is_empty() and self.table.grid[y][x].piece._initiatedByUser:
                    cell = Cell(x,y,2) # Пользовательская фигура
                elif self.table.grid[y][x].threatened:
                    cell = Cell(x,y,3) # Под угрозой
                elif self.table.grid[y][x].is_empty():
                    cell = Cell(x,y,0) # Пустая клетка
                else:
                    cell = Cell(x,y,1) # Размещенная программой фигура
                scene.addItem(cell)

        view.setFixedSize(view.sizeHint())
    def save_to_file(self):
        """
        Сохраняет решения в файл через отдельный поток SaveThread.
        """
        try:
            self.save_thread = SaveThread(self.Parent.solver, self.Parent.solver.solutions, "output.txt")
            self.save_thread.finished.connect(self.on_save_finished)
            self.save_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
    # Slot
    def on_save_finished(self, filename: str):
        """
        Обработчик завершения сохранения файла. Показывает сообщение пользователю.

        :param filename: Имя файла, в который были сохранены данные
        """
        print(len(self.Parent.solver.solutions))
        QMessageBox.information(
                self, 
                "Успех", 
                f"Решения сохранены в {filename}"
            )
        
class SaveThread(QThread):
    """
    Поток для асинхронного сохранения решений в файл.

    Сигналы:
        finished (str, str): Сигнал, испускаемый после завершения работы.
            Первый параметр — имя файла.
            Второй параметр — сообщение об ошибке (пустая строка, если ошибок не было).
    """

    finished = Signal(str, str)
    
    def __init__(self, solver, solutions: Set[frozenset], filename: str):
        """
        Инициализирует поток сохранения.

        :param solver: Объект Solver, содержащий метод записи в файл.
        :param solutions: Множество решений для сохранения.
        :param filename: Имя файла, в который нужно сохранить данные.
        """
        super().__init__()
        self.solver = solver
        self.solutions = solutions
        self.filename = filename
    
    def run(self):
        """
        Выполняет сохранение решений в файл.
        При успешном завершении отправляет сигнал без ошибки.
        В случае исключения — сигнал с сообщением об ошибке.
        """
        try:
            self.solver.write_output(self.filename, self.solutions)
            self.finished.emit(self.filename, "")
        except Exception as e:
            self.finished.emit(self.filename, str(e))

class Cell(QGraphicsRectItem):
    """
    Класс для отображения одной ячейки шахматного поля в QGraphicsScene.
    
    Наследуется от QGraphicsRectItem и отвечает за визуализацию ячейки на сцене.
    Цвет зависит от значения, переданного при создании.
    """
    CELL_SIZE = 32 # Размер одной клетки в пикселях

    # Назначим цвет в зависимости от значения в матрице
    COLOR_MAP = {
            0: QColor("white"),
            1: QColor("green"),
            2: QColor("blue"),
            3: QColor("red")
        }
    def __init__(self, x: int, y: int, value: int):
        """
        Инициализирует ячейку на заданных координатах и с заданным значением цвета.

        :param x (int): Координата по горизонтали (в клетках).
        :param y (int): Координата по вертикали (в клетках).
        :param value (int): Значение клетки, определяющее цвет заливки (0–3).
        """
        super().__init__(0, 0, self.CELL_SIZE, self.CELL_SIZE)
        self.setPos(x * self.CELL_SIZE, y * self.CELL_SIZE)
        self.setPen(QPen(QColor("black")))

        
        self.setBrush(self.COLOR_MAP.get(value, QColor("white")))


class MainWindow(QMainWindow):
    """
    Главное окно приложения, управляющее взаимодействием пользователя с UI и логикой решения задачи.
    """
    def __init__(self):
        """
        Инициализация главного окна: загрузка UI, настройка кнопок, установка начального состояния.
        """
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

        # self.thread_pool = QThreadPool()
    
    
    def load_ui(self):
        """
        Загружает интерфейс из .ui-файла и инициализирует элементы управления.
        """
        loader = QUiLoader()
        file = QFile(r"ui/chess_ui.ui")
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
        
        # Установка центрального виджета
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def get_n_l_k_pieces(self) -> Tuple[int, int, int, List[Tuple[str, Tuple[int, int]]]]:
        """
        Возвращает значения с элементов управления: размер доски, число фигур для размещения,
        количество уже размещенных фигур и их координаты.

        :return: Кортеж из (n, l, k, координаты фигур)
        """
        return self.boardSizeSpinBox.value(), self.requiredFiguresSpinBox.value(), self.placedFiguresSpinBox.value(), self.coords
    def create_board(self):
        """
        Создает доску и запрашивает координаты уже размещенных фигур,
        если они есть. Делает кнопку рисования доступной.
        """
        try:
            k = self.placedFiguresSpinBox.value()

            if k > 0:
                coords_menu = InputCoordinatesDialog(k, self)
                if coords_menu.exec() == QDialog.Accepted:
                    self.coords = coords_menu.get_coordinates()
            # Если доска успешно создана
            self.board_created = True
            self.drawBoardButton.setEnabled(True)

            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать доску: {str(e)}")
            self.drawBoardButton.setEnabled(False)
    
    def draw_board(self):
        """
        Отрисовывает доску и запускает поток для поиска решений, если доска уже создана.
        """
        if self.board_created:
            board, combinations = self.solver.generateBoard(*self.get_n_l_k_pieces())
            
            self.solver_thread = SolverThread(self.solver, board, combinations)
            self.solver_thread.finished.connect(self.on_solver_finished)
            self.solver_thread.start()
            
            # self.solver.solve(board, combinations)
            # ModalTable(board, next(iter(self.solver.solutions)), Parent = self).exec()
            # QMessageBox.information(self, "Информация", "Доска отрисована")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте доску")
    # Slot
    def on_solver_finished(self, board, solutions):
        """
        Обрабатывает завершение потока решения и отображает найденное решение.

        :param board: Объект доски.
        :param solutions: Найденные решения в виде множества.
        """
        if solutions:
            ModalTable(board, next(iter(solutions)), self).exec()
    def closeEvent(self, event):
        """
        Перехватывает закрытие окна и завершает все работающие потоки корректно.

        :param event: Событие закрытия окна.
        """
        threads = [
            getattr(self, attr) for attr in dir(self) 
            if attr.endswith('_thread') and isinstance(getattr(self, attr), QThread)
        ]
        
        for thread in threads:
            if thread.isRunning():
                thread.quit()
                thread.wait(500)  # Даем 500мс на завершение
        
        event.accept()








class Piece(ABC):
    """
    Базовый класс шахматной фигуры.

    """
    def __init__(self, x: int, y: int, initiated = False):
        """
        Инициализация фигуры на позиции (x, y).

        :param x: Координата X на доске.
        :param y: Координата Y на доске.
        """
        self.x = x
        self.y = y
        self._initiatedByUser = initiated
    
    @abstractmethod
    def get_moves(self) -> List[Tuple[int, int]]:
        """
        Метод, который должен быть реализован в подклассах.
        Возвращает множество клеток, находящихся под ударом фигуры.

        :return: Список координат клеток, находящихся под угрозой.
        """
        pass
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        """:return: Символьное обозначение фигуры"""
        pass

class Knight(Piece):
    """
    Класс шахматной фигуры — Конь.
    """
    moves = [(-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (-1, 2), (1, -2), (1, 2)]
    def get_moves(self):
        return [(-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (-1, 2), (1, -2), (1, 2)]
    
    @property
    def symbol(self):
        return 'k'

class Vizir(Piece):
    """
    Класс шахматной фигуры — Визирь.
    """
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]
    def get_moves(self):
        return [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]
    
    @property
    def symbol(self):
        return 'v'

class BoardCell:
    """
    Класс, представляющий одну ячейку шахматной доски.

    Атрибуты:
        :param x (int): Координата X (столбец).
        :param y (int): Координата Y (строка).
        :param piece (Optional[Piece]): Фигура, размещённая в ячейке, если есть.
        :param threatened (bool): Флаг, указывающий, находится ли ячейка под угрозой.
    """
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
    """
    Класс, представляющий шахматную доску и методы размещения фигур.
    """
    def __init__(self, size: int):
        """
        Инициализация пустой доски.

        :param size: Размер доски.
        """
        self.size = size
        self.grid = [[BoardCell(x, y) for x in range(size)] for y in range(size)]
        self.pieces: List[Piece] = []
    
    def add_piece(self, piece: Piece) -> bool:
        """
        Размещает фигуру на доске и обновляет угрозы.

        :param piece: Экземпляр фигуры.
        """
        cell = self.grid[piece.y][piece.x]
        
        if not cell.is_empty() or not self.is_position_safe(piece):
            return False
        
        cell.place_piece(piece)
        self.pieces.append(piece)
        self.update_threats()
        return True
    
    def remove_piece(self, piece: Piece):
        """
        Удаляет фигуру с доски и пересчитывает угрозы.

        :param piece: Экземпляр фигуры, которую нужно убрать.
        """
        cell = self.grid[piece.y][piece.x]
        if cell.piece == piece:
            cell.remove_piece()
            self.pieces.remove(piece)
            self.update_threats()
    
    def is_position_safe(self, piece: Piece) -> bool:
        """
        Проверяет безопасность позиции для фигуры.

        :param piece: Экземпляр фигуры.
        """
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
    """
    Класс, реализующий решение задачи размещения фигур на шахматной доске
    с использованием метода полного перебора (backtracking).
    """
    def __init__(self):
        """
        Инициализация хранилища решений.
        """
        self.solutions: Set[frozenset] = set()

    def solve(self, board: ChessBoard, combinations: List[List[str]]) -> None:
        """
        Находит все допустимые расстановки фигур, не угрожающих друг другу.

        :param board: Объект шахматной доски с уже размещёнными фигурами.
        :param combinations: Список всех перестановок фигур для размещения, например ['k', 'v', 'v'].
        """
        def backtrack(remaining_pieces: List[str]):
            """
            Рекурсивный алгоритм поиска с возвратом.

            :param remaining_pieces: Список оставшихся фигур для размещения.
            """
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

    @staticmethod
    def generateBoard(n, l, k, pieces) -> Tuple[int, int, int, int, ChessBoard, List[str]]:
        """
        Генерирует шахматную доску и комбинации фигур для размещения.

        :param n: Размер доски (n x n).
        :param l: Количество новых фигур, которые нужно разместить.
        :param k: Количество уже размещённых фигур.
        :param pieces: Список уже размещённых фигур в формате (тип, (x, y)),
                       где тип — 'Horse' или 'Vizir'.
        :return: Кортеж, содержащий:
            - объект доски (ChessBoard) с размещёнными фигурами,
            - множество всех возможных комбинаций из L фигур ('k' и 'v') для размещения.
        """

        board = ChessBoard(n)

        if k > 0:
            for i in range(k):
                type, coords = pieces[i]
                piece = Knight(*coords, initiated = True) if type == "Horse" else Vizir(*coords, initiated = True)
                board.add_piece(piece)

        # Генерация комбинаций фигур для размещения
        combinations = set(combinations_with_replacement('kv', l))

        return board, combinations
    
    @staticmethod
    def write_output(file_path: str, solutions: Set[frozenset]):
        """
        Записывает все найденные решения в выходной файл.

        :param file_path: Путь к выходному файлу.
        :param solutions: Множество решений, каждое из которых представлено как frozenset
                          кортежей вида (x, y, тип).
        """
        with open(file_path, 'w') as file:
            if solutions:
                for solution in solutions:
                    solution_str = " ".join(f"({x}, {y}, {f})" for x, y, f in solution)
                    file.write(solution_str + "\n")
            else:
                file.write("no solutions\n")

class SolverThread(QThread):
    """
    Поток для выполнения поиска решений в фоновом режиме, не блокируя GUI.
    По завершении испускает сигнал с результатами.
    """

    finished = Signal(object,object)
    # Сигнал, испускаемый по завершении работы потока.
    # Передаёт: доску и найденные решения.

    def __init__(self, solver: Solver, board: ChessBoard, combinations:List[List[str]]) -> None:
        """
        Инициализация потока с нужными параметрами.

        :param solver: Объект класса Solver, реализующий логику поиска решений.
        :param board: Объект шахматной доски (ChessBoard).
        :param combinations: Список комбинаций фигур для размещения (например: [['k', 'v'], ['v', 'v']] и т.д.).
        """
        super().__init__()
        self.solver = solver
        self.board = board
        self.combinations = combinations
    
    def run(self) -> None:
        """
        Запускает алгоритм поиска решений в отдельном потоке.
        По завершении испускает сигнал с доской и найденными решениями.
        """
        self.solver.solve(self.board, self.combinations)
        self.finished.emit(self.board, self.solver.solutions)



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
