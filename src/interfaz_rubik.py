import sys

import random



from PySide6.QtWidgets import (

    QApplication,

    QWidget,

    QGridLayout,

    QVBoxLayout,

    QHBoxLayout,

    QLabel,

    QPushButton,

    QGroupBox,

    QFrame,

    QComboBox,

    QTextEdit,

    QMessageBox,

    QSpinBox,

)



from PySide6.QtCore import Qt

from PySide6.QtGui import QFont



from rubik import (

    RubikCube,

    Axis,

    Direction,

)



from search_algorithms import (

    SearchAlgorithms,

    SearchResult,

)





# ==============================================================

# COLORES DEL CUBO

# ==============================================================



COLORS = {

    0: "#ff8c00",  # naranja

    1: "#00a651",  # verde

    2: "#ed1c24",  # rojo

    3: "#0066cc",  # azul

    4: "#ffffff",  # blanco

    5: "#ffd500",  # amarillo

}





# ==============================================================

# INTERFAZ GRÁFICA

# ==============================================================



class RubiksCubeGUI(QWidget):



    def __init__(self):

        super().__init__()



        # ----------------------------------------------------------

        # VENTANA

        # ----------------------------------------------------------



        self.setWindowTitle(

            "AI Lab 2 - Rubik's Cube"

        )



        self.setMinimumSize(

            1250,

            900

        )



        self.resize(

            1450,

            980

        )



        # ----------------------------------------------------------

        # MODELO DEL CUBO

        # ----------------------------------------------------------



        self.cube = RubikCube()



        # ----------------------------------------------------------

        # ALGORITMOS

        # ----------------------------------------------------------



        self.search_algorithms = SearchAlgorithms(

            max_nodes=100000

        )



        # ----------------------------------------------------------

        # ÚLTIMA SOLUCIÓN

        # ----------------------------------------------------------



        self.last_solution = []



        # ----------------------------------------------------------

        # STICKERS

        # ----------------------------------------------------------



        self.stickers = {}



        # ----------------------------------------------------------

        # MAPA DE ALGORITMOS

        # ----------------------------------------------------------



        self.algorithm_map = {}



        # ----------------------------------------------------------

        # CREAR GUI

        # ----------------------------------------------------------



        self.setup_ui()



        self.load_algorithms()



        self.update_cube_view()



    # ==============================================================

    # CONFIGURAR INTERFAZ

    # ==============================================================



    def setup_ui(self):



        main_layout = QVBoxLayout(self)



        main_layout.setContentsMargins(

            18,

            12,

            18,

            12

        )



        main_layout.setSpacing(

            8

        )



        # ==========================================================

        # TÍTULO

        # ==========================================================



        title = QLabel(

            "RUBIK'S CUBE SIMULATOR"

        )



        title.setAlignment(

            Qt.AlignCenter

        )



        title_font = QFont()



        title_font.setPointSize(

            20

        )



        title_font.setBold(

            True

        )



        title.setFont(

            title_font

        )



        main_layout.addWidget(

            title

        )



        # ==========================================================

        # ESTADO DEL CUBO

        # ==========================================================



        self.status_label = QLabel(

            "Status:"

        )



        self.status_label.setAlignment(

            Qt.AlignCenter

        )



        status_font = QFont()



        status_font.setPointSize(

            12

        )



        status_font.setBold(

            True

        )



        self.status_label.setFont(

            status_font

        )



        main_layout.addWidget(

            self.status_label

        )



        # ==========================================================

        # DESARROLLO DEL CUBO

        #

        #                  [4]

        #

        #          [0] [1] [2] [3]

        #

        #                  [5]

        #

        # ==========================================================



        cube_container = QFrame()



        cube_container.setObjectName(

            "cubeContainer"

        )



        cube_container.setStyleSheet("""

            QFrame#cubeContainer {

                border: none;

                background: transparent;

            }

        """)



        cube_main_layout = QVBoxLayout(

            cube_container

        )



        cube_main_layout.setContentsMargins(

            10,

            4,

            10,

            8

        )



        cube_main_layout.setSpacing(

            12

        )



        # ----------------------------------------------------------

        # CREAR CARAS

        # ----------------------------------------------------------



        self.faces = {}



        for face_index in range(6):



            self.faces[

                face_index

            ] = self.create_face(

                face_index

            )



        # ==========================================================

        # FILA SUPERIOR

        # ==========================================================



        top_row = QHBoxLayout()



        top_row.setContentsMargins(

            0,

            0,

            0,

            0

        )



        top_row.addStretch()



        top_row.addWidget(

            self.faces[4]

        )



        top_row.addStretch()



        cube_main_layout.addLayout(

            top_row

        )



        # ==========================================================

        # FILA CENTRAL

        # ==========================================================



        middle_row = QHBoxLayout()



        middle_row.setContentsMargins(

            0,

            0,

            0,

            0

        )



        middle_row.setSpacing(

            24

        )



        middle_row.addStretch()



        middle_row.addWidget(

            self.faces[0]

        )



        middle_row.addWidget(

            self.faces[1]

        )



        middle_row.addWidget(

            self.faces[2]

        )



        middle_row.addWidget(

            self.faces[3]

        )



        middle_row.addStretch()



        cube_main_layout.addLayout(

            middle_row

        )



        # ==========================================================

        # FILA INFERIOR

        # ==========================================================



        bottom_cube_row = QHBoxLayout()



        bottom_cube_row.setContentsMargins(

            0,

            0,

            0,

            0

        )



        bottom_cube_row.addStretch()



        bottom_cube_row.addWidget(

            self.faces[5]

        )



        bottom_cube_row.addStretch()



        cube_main_layout.addLayout(

            bottom_cube_row

        )



        # Espacio entre el cubo y los controles.

        cube_main_layout.addSpacing(

            8

        )



        main_layout.addWidget(

            cube_container

        )



        # ==========================================================

        # ZONA INFERIOR

        #

        # MOVIMIENTOS | ALGORITMOS | HISTORIAL

        #

        # ==========================================================



        lower_layout = QHBoxLayout()



        lower_layout.setSpacing(

            14

        )



        # ==========================================================

        # MOVIMIENTOS MANUALES

        # ==========================================================



        controls_group = QGroupBox(

            "Moves by axis - ABC / DEF / GHI"

        )



        controls_layout = QGridLayout(

            controls_group

        )



        controls_layout.setContentsMargins(

            10,

            18,

            10,

            10

        )



        controls_layout.setHorizontalSpacing(

            7

        )



        controls_layout.setVerticalSpacing(

            4

        )



        for index, axis in enumerate(

            list(Axis)

        ):



            # ------------------------------------------------------

            # NOMBRE DEL EJE

            # ------------------------------------------------------



            axis_label = QLabel(

                axis.name

            )



            axis_label.setAlignment(

                Qt.AlignCenter

            )



            axis_font = QFont()



            axis_font.setBold(

                True

            )



            axis_label.setFont(

                axis_font

            )



            controls_layout.addWidget(

                axis_label,

                index,

                0

            )



            # ------------------------------------------------------

            # MOVIMIENTO POSITIVO

            # ------------------------------------------------------



            positive_button = QPushButton(

                f"{axis.name}+"

            )



            positive_button.setMinimumHeight(

                27

            )



            positive_button.clicked.connect(

                lambda checked=False, a=axis:

                self.make_move(

                    a,

                    Direction.POSITIVE,

                    1

                )

            )



            controls_layout.addWidget(

                positive_button,

                index,

                1

            )



            # ------------------------------------------------------

            # MOVIMIENTO NEGATIVO

            # ------------------------------------------------------



            negative_button = QPushButton(

                f"{axis.name}-"

            )



            negative_button.setMinimumHeight(

                27

            )



            negative_button.clicked.connect(

                lambda checked=False, a=axis:

                self.make_move(

                    a,

                    Direction.NEGATIVE,

                    1

                )

            )



            controls_layout.addWidget(

                negative_button,

                index,

                2

            )



            # ------------------------------------------------------

            # MOVIMIENTO DOBLE

            # ------------------------------------------------------



            double_button = QPushButton(

                f"{axis.name}2"

            )



            double_button.setMinimumHeight(

                27

            )



            double_button.clicked.connect(

                lambda checked=False, a=axis:

                self.make_move(

                    a,

                    Direction.POSITIVE,

                    2

                )

            )



            controls_layout.addWidget(

                double_button,

                index,

                3

            )



        lower_layout.addWidget(

            controls_group,

            3

        )



        # ==========================================================

        # ALGORITMOS DE BÚSQUEDA

        # ==========================================================



        algorithm_group = QGroupBox(

            "Search Algorithms"

        )



        algorithm_layout = QVBoxLayout(

            algorithm_group

        )



        algorithm_layout.setContentsMargins(

            12,

            18,

            12,

            10

        )



        algorithm_layout.setSpacing(

            6

        )



        # ----------------------------------------------------------

        # SELECTOR

        # ----------------------------------------------------------



        algorithm_label = QLabel(

            "Select an algorithm:"

        )



        algorithm_layout.addWidget(

            algorithm_label

        )



        self.algorithm_combo = QComboBox()



        self.algorithm_combo.setMinimumHeight(

            31

        )



        algorithm_layout.addWidget(

            self.algorithm_combo

        )



        # ----------------------------------------------------------

        # BUSCAR SOLUCIÓN

        # ----------------------------------------------------------



        self.run_algorithm_button = QPushButton(

            "Find Solution"

        )



        self.run_algorithm_button.setMinimumHeight(

            35

        )



        self.run_algorithm_button.clicked.connect(

            self.run_selected_algorithm

        )



        algorithm_layout.addWidget(

            self.run_algorithm_button

        )



        # ----------------------------------------------------------

        # APLICAR SOLUCIÓN

        # ----------------------------------------------------------



        self.apply_solution_button = QPushButton(

            "Apply Solution"

        )



        self.apply_solution_button.setMinimumHeight(

            35

        )



        self.apply_solution_button.setEnabled(

            False

        )



        self.apply_solution_button.clicked.connect(

            self.apply_last_solution

        )



        algorithm_layout.addWidget(

            self.apply_solution_button

        )



        # ==========================================================

        # RESULTADO DE LA BÚSQUEDA

        # ==========================================================



        result_label = QLabel(

            "Search Result:"

        )



        algorithm_layout.addWidget(

            result_label

        )



        self.algorithm_result_text = QTextEdit()



        self.algorithm_result_text.setReadOnly(

            True

        )



        # Tamaño estable.

        # Si hay más texto, se usa scrollbar.

        self.algorithm_result_text.setFixedHeight(

            82

        )



        self.algorithm_result_text.setVerticalScrollBarPolicy(

            Qt.ScrollBarAsNeeded

        )



        self.algorithm_result_text.setHorizontalScrollBarPolicy(

            Qt.ScrollBarAlwaysOff

        )



        self.algorithm_result_text.setLineWrapMode(

            QTextEdit.LineWrapMode.WidgetWidth

        )



        self.algorithm_result_text.setPlainText(

            "Result: pending"

        )



        algorithm_layout.addWidget(

            self.algorithm_result_text

        )



        # ==========================================================

        # MOVIMIENTOS DE LA SOLUCIÓN

        # ==========================================================



        solution_label = QLabel(

        )



        algorithm_layout.addWidget(

            solution_label

        )



        self.solution_text = QTextEdit()



        self.solution_text.setReadOnly(

            True

        )



        # Mismo principio:

        # altura fija + scroll.

        self.solution_text.setFixedHeight(

            82

        )



        self.solution_text.setVerticalScrollBarPolicy(

            Qt.ScrollBarAsNeeded

        )



        self.solution_text.setHorizontalScrollBarPolicy(

            Qt.ScrollBarAlwaysOff

        )



        self.solution_text.setLineWrapMode(

            QTextEdit.LineWrapMode.WidgetWidth

        )



        self.solution_text.setPlaceholderText(

            "The solution will appear here."

        )



        algorithm_layout.addWidget(

            self.solution_text

        )



        lower_layout.addWidget(

            algorithm_group,

            2

        )



        # ==========================================================

        # HISTORIAL DE MOVIMIENTOS

        # ==========================================================



        history_group = QGroupBox(

            "Move History"

        )



        history_layout = QVBoxLayout(

            history_group

        )



        history_layout.setContentsMargins(

            10,

            18,

            10,

            10

        )



        self.history_text = QTextEdit()



        self.history_text.setReadOnly(

            True

        )



        self.history_text.setVerticalScrollBarPolicy(

            Qt.ScrollBarAsNeeded

        )



        self.history_text.setHorizontalScrollBarPolicy(

            Qt.ScrollBarAlwaysOff

        )



        self.history_text.setLineWrapMode(

            QTextEdit.LineWrapMode.WidgetWidth

        )



        self.history_text.setPlaceholderText(

            "Performed moves will appear here."

        )



        history_layout.addWidget(

            self.history_text

        )



        lower_layout.addWidget(

            history_group,

            2

        )



        main_layout.addLayout(

            lower_layout,

            1

        )



        # ==========================================================

        # CONFIGURACIÓN DE MEZCLA

        # ==========================================================



        scramble_settings = QHBoxLayout()



        scramble_settings.setSpacing(

            8

        )



        scramble_label = QLabel(

            "Scramble moves:"

        )



        self.scramble_count = QSpinBox()



        self.scramble_count.setMinimum(

            1

        )



        self.scramble_count.setMaximum(

            20

        )



        self.scramble_count.setValue(

            3

        )



        scramble_settings.addWidget(

            scramble_label

        )



        scramble_settings.addWidget(

            self.scramble_count

        )



        scramble_settings.addStretch()



        main_layout.addLayout(

            scramble_settings

        )



        # ==========================================================

        # BOTONES GENERALES

        # ==========================================================



        bottom_layout = QHBoxLayout()



        bottom_layout.setSpacing(

            12

        )



        self.scramble_button = QPushButton(

            "Scramble"

        )



        self.undo_button = QPushButton(

            "Undo"

        )



        self.reset_button = QPushButton(

            "Reset"

        )



        self.scramble_button.setMinimumHeight(

            40

        )



        self.undo_button.setMinimumHeight(

            40

        )



        self.reset_button.setMinimumHeight(

            40

        )



        self.scramble_button.clicked.connect(

            self.scramble_cube

        )



        self.undo_button.clicked.connect(

            self.undo_move

        )



        self.reset_button.clicked.connect(

            self.reset_cube

        )



        bottom_layout.addWidget(

            self.scramble_button

        )



        bottom_layout.addWidget(

            self.undo_button

        )



        bottom_layout.addWidget(

            self.reset_button

        )



        main_layout.addLayout(

            bottom_layout

        )



    # ==============================================================

    # CREAR CARA DEL CUBO

    # ==============================================================



    def create_face(

        self,

        face_index

    ):



        frame = QFrame()



        frame.setObjectName(

            "cubeFace"

        )



        frame.setStyleSheet("""

            QFrame#cubeFace {

                background-color: #202020;

                border: 2px solid #555555;

                border-radius: 7px;

            }

        """)



        frame.setFixedSize(

            110,

            120

        )



        face_layout = QVBoxLayout(

            frame

        )



        face_layout.setContentsMargins(

            6,

            5,

            6,

            6

        )



        face_layout.setSpacing(

            3

        )



        # ----------------------------------------------------------

        # NOMBRE DE LA CARA

        # ----------------------------------------------------------



        face_title = QLabel(

            f"Cara {face_index}"

        )



        face_title.setAlignment(

            Qt.AlignCenter

        )



        face_title.setFixedHeight(

            17

        )



        face_title.setStyleSheet("""

            QLabel {

                font-weight: bold;

                font-size: 12px;

                border: none;

            }

        """)



        face_layout.addWidget(

            face_title

        )



        # ----------------------------------------------------------

        # CUADRÍCULA 3 x 3

        # ----------------------------------------------------------



        grid_container = QWidget()



        grid = QGridLayout(

            grid_container

        )



        grid.setContentsMargins(

            0,

            0,

            0,

            0

        )



        grid.setHorizontalSpacing(

            3

        )



        grid.setVerticalSpacing(

            3

        )



        grid.setAlignment(

            Qt.AlignCenter

        )



        self.stickers[

            face_index

        ] = []



        STICKER_SIZE = 28



        for row in range(3):



            sticker_row = []



            for col in range(3):



                sticker = QLabel()



                # Sticker cuadrado.

                sticker.setFixedSize(

                    STICKER_SIZE,

                    STICKER_SIZE

                )



                sticker.setAlignment(

                    Qt.AlignCenter

                )



                sticker.setStyleSheet("""

                    QLabel {

                        background-color: gray;

                        border: 2px solid #111111;

                        border-radius: 2px;

                    }

                """)



                grid.addWidget(

                    sticker,

                    row,

                    col,

                    alignment=Qt.AlignCenter

                )



                sticker_row.append(

                    sticker

                )



            self.stickers[

                face_index

            ].append(

                sticker_row

            )



        face_layout.addWidget(

            grid_container,

            alignment=Qt.AlignCenter

        )



        return frame



    # ==============================================================

    # CARGAR ALGORITMOS

    # ==============================================================



    def load_algorithms(self):



        self.algorithm_combo.clear()



        self.algorithm_map = {

            "A*":

                self.search_algorithms.astar,



            "GBF":

                self.search_algorithms.gbf,



            "Bidirectional":

                self.search_algorithms.bidirectional,

        }



        for name in self.algorithm_map:



            self.algorithm_combo.addItem(

                name

            )



    # ==============================================================

    # MOVIMIENTO MANUAL

    # ==============================================================



    def make_move(

        self,

        axis,

        direction,

        times=1

    ):



        self.cube.turn(

            axis,

            direction,

            times

        )



        # Una modificación invalida

        # una solución calculada anteriormente.

        self.clear_last_solution()



        self.update_cube_view()



    # ==============================================================

    # MEZCLAR

    # ==============================================================



    def scramble_cube(self):



        amount = (

            self.scramble_count.value()

        )



        axes = list(

            Axis

        )



        directions = list(

            Direction

        )



        for _ in range(amount):



            axis = random.choice(

                axes

            )



            direction = random.choice(

                directions

            )



            times = random.choice(

                [1, 2]

            )



            self.cube.turn(

                axis,

                direction,

                times

            )



        self.clear_last_solution()



        self.update_cube_view()



    # ==============================================================

    # DESHACER

    # ==============================================================



    def undo_move(self):



        if not self.cube.history:



            QMessageBox.information(

                self,

                "Undo",

                "There are no moves to undo."

            )



            return



        self.cube.revert_last_move()



        self.clear_last_solution()



        self.update_cube_view()



    # ==============================================================

    # REINICIAR

    # ==============================================================



    def reset_cube(self):



        self.cube = RubikCube()



        self.clear_last_solution()



        self.update_cube_view()



    # ==============================================================

    # ACTUALIZAR REPRESENTACIÓN DEL CUBO

    # ==============================================================



    def update_cube_view(self):



        for face_index in range(6):



            face = self.cube.faces[

                face_index

            ]



            for row in range(3):



                for col in range(3):



                    value = face.values[

                        row

                    ][

                        col

                    ]



                    color = COLORS.get(

                        value,

                        "#808080"

                    )



                    self.stickers[

                        face_index

                    ][

                        row

                    ][

                        col

                    ].setStyleSheet(

                        f"""

                        QLabel {{

                            background-color: {color};

                            border: 2px solid #111111;

                            border-radius: 2px;

                        }}

                        """

                    )



        # ----------------------------------------------------------

        # ESTADO DEL CUBO

        # ----------------------------------------------------------



        if self.cube.is_solved():



            self.status_label.setText(

                "Status: SOLVED"

            )



        else:



            self.status_label.setText(

                "Status: SCRAMBLED"

            )



        self.update_history_view()



    # ==============================================================

    # MOVIMIENTO -> TEXTO

    # ==============================================================



    def move_to_text(

        self,

        move

    ):



        times = (

            move.times % 4

        )



        # ----------------------------------------------------------

        # CUATRO GIROS

        # ----------------------------------------------------------



        if times == 0:



            return (

                f"{move.axis.name}0"

            )



        # ----------------------------------------------------------

        # DOS GIROS

        # ----------------------------------------------------------



        if times == 2:



            return (

                f"{move.axis.name}2"

            )



        # ----------------------------------------------------------

        # UN GIRO

        # ----------------------------------------------------------



        if times == 1:



            if (

                move.direction

                == Direction.POSITIVE

            ):



                sign = "+"



            else:



                sign = "-"



            return (

                f"{move.axis.name}{sign}"

            )



        # ----------------------------------------------------------

        # TRES GIROS

        # ----------------------------------------------------------



        if times == 3:



            inverted = Direction.invert(

                move.direction

            )



            if (

                inverted

                == Direction.POSITIVE

            ):



                sign = "+"



            else:



                sign = "-"



            return (

                f"{move.axis.name}{sign}"

            )



        return (

            move.axis.name

        )



    # ==============================================================

    # ACTUALIZAR HISTORIAL

    # ==============================================================



    def update_history_view(self):



        if not self.cube.history:



            self.history_text.setPlainText(

                "No moves."

            )



            return



        lines = []



        for index, move in enumerate(

            self.cube.history,

            start=1

        ):



            lines.append(

                f"{index:02d}. "

                f"{self.move_to_text(move)}"

            )



        self.history_text.setPlainText(

            "\n".join(lines)

        )



        # Llevar automáticamente el historial

        # al último movimiento.

        scroll_bar = (

            self.history_text.verticalScrollBar()

        )



        scroll_bar.setValue(

            scroll_bar.maximum()

        )



    # ==============================================================

    # COPIA DEL CUBO

    # ==============================================================



    def get_cube_copy(self):



        cube_copy = RubikCube()



        for face_index in range(6):



            cube_copy.faces[

                face_index

            ].values = [

                row[:]

                for row in self.cube.faces[

                    face_index

                ].values

            ]



        cube_copy.history = []



        return cube_copy



    # ==============================================================

    # EJECUTAR ALGORITMO

    # ==============================================================



    def run_selected_algorithm(self):



        algorithm_name = (

            self.algorithm_combo.currentText()

        )



        algorithm_function = (

            self.algorithm_map.get(

                algorithm_name

            )

        )



        if algorithm_function is None:



            QMessageBox.warning(

                self,

                "Algorithm",

                "The selected algorithm was not found."

            )



            return



        # ----------------------------------------------------------

        # DESACTIVAR BOTÓN DURANTE LA BÚSQUEDA

        # ----------------------------------------------------------



        self.run_algorithm_button.setEnabled(

            False

        )



        self.run_algorithm_button.setText(

            "Searching..."

        )



        QApplication.processEvents()



        try:



            cube_copy = (

                self.get_cube_copy()

            )



            result = algorithm_function(

                cube_copy

            )



            self.show_search_result(

                result

            )



        except Exception as error:



            QMessageBox.critical(

                self,

                "Error",

                (

                    "Ocurrió un error durante "

                    "la búsqueda:\n\n"

                    f"{error}"

                )

            )



        finally:



            self.run_algorithm_button.setEnabled(

                True

            )



            self.run_algorithm_button.setText(

                "Find Solution"

            )



    # ==============================================================

    # MOSTRAR RESULTADO

    # ==============================================================



    def show_search_result(

        self,

        result

    ):



        if not isinstance(

            result,

            SearchResult

        ):



            QMessageBox.warning(

                self,

                "Invalid result",

                (

                    "El algoritmo debe regresar "

                    "un objeto SearchResult."

                )

            )



            return



        # ----------------------------------------------------------

        # ESTADÍSTICAS

        # ----------------------------------------------------------



        stats = (

            f"Algoritmo: {result.algorithm}\n"

            f"Nodos explorados: {result.explored_nodes}\n"

            f"Tiempo: {result.execution_time:.6f} s\n"

            f"Movimientos de solución: {len(result.moves)}\n"

            f"Resultado: {result.message}"

        )



        self.algorithm_result_text.setPlainText(

            stats

        )



        # Regresar el scroll del resultado

        # a la parte superior.

        self.algorithm_result_text.verticalScrollBar().setValue(

            0

        )



        # ----------------------------------------------------------

        # NO SE ENCONTRÓ SOLUCIÓN

        # ----------------------------------------------------------



        if not result.success:



            self.solution_text.setPlainText(

                "No solution was found."

            )



            self.last_solution = []



            self.apply_solution_button.setEnabled(

                False

            )



            return



        # ----------------------------------------------------------

        # GUARDAR SOLUCIÓN

        # ----------------------------------------------------------



        self.last_solution = list(

            result.moves

        )



        # ----------------------------------------------------------

        # YA ESTABA RESUELTO

        # ----------------------------------------------------------



        if not result.moves:



            self.solution_text.setPlainText(

                "The cube is already solved."

            )



            self.apply_solution_button.setEnabled(

                False

            )



            return



        # ----------------------------------------------------------

        # MOSTRAR PASOS DE LA SOLUCIÓN

        # ----------------------------------------------------------



        lines = []



        for index, move in enumerate(

            result.moves,

            start=1

        ):



            lines.append(

                f"{index:02d}. "

                f"{self.move_to_text(move)}"

            )



        self.solution_text.setPlainText(

            "\n".join(lines)

        )



        # Mostrar la solución desde el primer paso.

        self.solution_text.verticalScrollBar().setValue(

            0

        )



        self.apply_solution_button.setEnabled(

            True

        )



    # ==============================================================

    # APLICAR SOLUCIÓN

    # ==============================================================



    def apply_last_solution(self):



        if not self.last_solution:



            return



        solution = list(

            self.last_solution

        )



        for move in solution:



            self.cube.turn(

                move.axis,

                move.direction,

                move.times

            )



        self.last_solution = []



        self.apply_solution_button.setEnabled(

            False

        )



        self.update_cube_view()



    # ==============================================================

    # LIMPIAR SOLUCIÓN

    # ==============================================================



    def clear_last_solution(self):



        self.last_solution = []



        if hasattr(

            self,

            "solution_text"

        ):



            self.solution_text.clear()



        if hasattr(

            self,

            "algorithm_result_text"

        ):



            self.algorithm_result_text.setPlainText(

                "Result: pending"

            )



        if hasattr(

            self,

            "apply_solution_button"

        ):



            self.apply_solution_button.setEnabled(

                False

            )





# ==============================================================

# MAIN

# ==============================================================



if __name__ == "__main__":



    app = QApplication(

        sys.argv

    )



    window = RubiksCubeGUI()



    window.show()



    sys.exit(

        app.exec()

    )