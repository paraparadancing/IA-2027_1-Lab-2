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
    Move
)

from search_algorithms import (
    SearchAlgorithms,
    SearchResult
)


# ==============================================================
# COLORES DE LAS CARAS
# ==============================================================

COLORS = {
    0: "#ff8c00",   # naranja
    1: "#00a651",   # verde
    2: "#ed1c24",   # rojo
    3: "#0066cc",   # azul
    4: "#ffffff",   # blanco
    5: "#ffd500",   # amarillo
}


# ==============================================================
# GUI
# ==============================================================

class RubiksCubeGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Lab 2 IA - Cubo Rubik"
        )

        self.setMinimumSize(
            1300,
            900
        )

        # ----------------------------------------------------------
        # MODELO DEL CUBO
        # ----------------------------------------------------------

        self.cube = RubikCube()

        # ----------------------------------------------------------
        # CLASE DE ALGORITMOS
        # ----------------------------------------------------------

        self.search_algorithms = (
            SearchAlgorithms(
                max_nodes=100000
            )
        )

        # ----------------------------------------------------------
        # ÚLTIMA SOLUCIÓN ENCONTRADA
        # ----------------------------------------------------------

        self.last_solution = []

        # ----------------------------------------------------------
        # STICKERS DE LA GUI
        # ----------------------------------------------------------

        self.stickers = {}

        # ----------------------------------------------------------
        # MAPA DE ALGORITMOS
        # ----------------------------------------------------------

        self.algorithm_map = {}

        self.setup_ui()

        self.load_algorithms()

        self.update_cube_view()

    # ==============================================================
    # CREAR INTERFAZ
    # ==============================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        # ==========================================================
        # TÍTULO
        # ==========================================================

        title = QLabel(
            "SIMULADOR DE CUBO RUBIK"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)

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
            "Estado:"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        status_font = QFont()
        status_font.setPointSize(12)
        status_font.setBold(True)

        self.status_label.setFont(
            status_font
        )

        main_layout.addWidget(
            self.status_label
        )

        # ==========================================================
        # DESARROLLO DEL CUBO
        #
        #             [4]
        #
        #     [0] [1] [2] [3]
        #
        #             [5]
        #
        # ==========================================================

        cube_container = QFrame()

        cube_layout = QGridLayout(
            cube_container
        )

        cube_layout.setSpacing(
            8
        )

        self.faces = {}

        for face_index in range(6):

            self.faces[
                face_index
            ] = self.create_face(
                face_index
            )

        cube_layout.addWidget(
            self.faces[4],
            0,
            1
        )

        cube_layout.addWidget(
            self.faces[0],
            1,
            0
        )

        cube_layout.addWidget(
            self.faces[1],
            1,
            1
        )

        cube_layout.addWidget(
            self.faces[2],
            1,
            2
        )

        cube_layout.addWidget(
            self.faces[3],
            1,
            3
        )

        cube_layout.addWidget(
            self.faces[5],
            2,
            1
        )

        main_layout.addWidget(
            cube_container,
            stretch=1
        )

        # ==========================================================
        # ZONA INFERIOR
        # ==========================================================

        content_layout = QHBoxLayout()

        # ==========================================================
        # MOVIMIENTOS MANUALES
        # ==========================================================

        controls_group = QGroupBox(
            "Movimientos por eje - ABC / DEF / GHI"
        )

        controls_layout = QGridLayout(
            controls_group
        )

        for index, axis in enumerate(
            list(Axis)
        ):

            # ------------------------------------------------------
            # NOMBRE
            # ------------------------------------------------------

            axis_label = QLabel(
                axis.name
            )

            axis_label.setAlignment(
                Qt.AlignCenter
            )

            axis_font = QFont()
            axis_font.setBold(True)

            axis_label.setFont(
                axis_font
            )

            controls_layout.addWidget(
                axis_label,
                index,
                0
            )

            # ------------------------------------------------------
            # POSITIVO
            # ------------------------------------------------------

            positive_button = QPushButton(
                f"{axis.name}+"
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
            # NEGATIVO
            # ------------------------------------------------------

            negative_button = QPushButton(
                f"{axis.name}-"
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
            # DOBLE
            # ------------------------------------------------------

            double_button = QPushButton(
                f"{axis.name}2"
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

        content_layout.addWidget(
            controls_group,
            stretch=2
        )

        # ==========================================================
        # PANEL DERECHO
        # ==========================================================

        right_layout = QVBoxLayout()

        # ==========================================================
        # ALGORITMOS
        # ==========================================================

        algorithm_group = QGroupBox(
            "Algoritmos de búsqueda"
        )

        algorithm_group.setMinimumWidth(430)
        algorithm_group.setMinimumHeight(330)

        algorithm_layout = QVBoxLayout(
            algorithm_group
        )

        algorithm_layout.setSpacing(8)

        algorithm_layout.setContentsMargins(
            12,
            18,
            12,
            12
        )

        # ----------------------------------------------------------
        # SELECTOR
        # ----------------------------------------------------------

        algorithm_label = QLabel(
            "Selecciona un algoritmo:"
        )

        algorithm_layout.addWidget(
            algorithm_label
        )

        self.algorithm_combo = QComboBox()

        self.algorithm_combo.setMinimumHeight(
            32
        )

        algorithm_layout.addWidget(
            self.algorithm_combo
        )

        # ----------------------------------------------------------
        # EJECUTAR
        # ----------------------------------------------------------

        self.run_algorithm_button = QPushButton(
            "Buscar solución"
        )

        self.run_algorithm_button.setMinimumHeight(
            38
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
            "Aplicar solución"
        )

        self.apply_solution_button.setMinimumHeight(
            38
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

        # ----------------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------------

        self.algorithm_result_label = QLabel(
            "Resultado: pendiente"
        )

        self.algorithm_result_label.setWordWrap(
            True
        )

        self.algorithm_result_label.setMinimumHeight(
            75
        )

        self.algorithm_result_label.setAlignment(
            Qt.AlignTop
        )

        algorithm_layout.addWidget(
            self.algorithm_result_label
        )

        # ----------------------------------------------------------
        # SOLUCIÓN
        # ----------------------------------------------------------

        solution_label = QLabel(
            "Movimientos de la solución:"
        )

        algorithm_layout.addWidget(
            solution_label
        )

        self.solution_text = QTextEdit()

        self.solution_text.setReadOnly(
            True
        )

        self.solution_text.setMinimumHeight(
            110
        )

        self.solution_text.setMaximumHeight(
            150
        )

        self.solution_text.setPlaceholderText(
            "Aquí aparecerá la solución encontrada."
        )

        algorithm_layout.addWidget(
            self.solution_text
        )

        right_layout.addWidget(
            algorithm_group
        )

        # ==========================================================
        # HISTORIAL
        # ==========================================================

        history_group = QGroupBox(
            "Historial de movimientos"
        )

        history_group.setMinimumWidth(
            430
        )

        history_group.setMinimumHeight(
            250
        )

        history_layout = QVBoxLayout(
            history_group
        )

        self.history_text = QTextEdit()

        self.history_text.setReadOnly(
            True
        )

        self.history_text.setMinimumHeight(
            200
        )

        history_layout.addWidget(
            self.history_text
        )

        right_layout.addWidget(
            history_group
        )

        # ==========================================================
        # PROPORCIÓN DEL PANEL DERECHO
        # ==========================================================

        right_layout.setStretch(
            0,
            0
        )

        right_layout.setStretch(
            1,
            1
        )

        # ==========================================================
        # AGREGAR PANEL DERECHO AL CONTENEDOR PRINCIPAL
        # ==========================================================

        content_layout.addLayout(
            right_layout,
            stretch=2
        )

        main_layout.addLayout(
            content_layout
        )
        # ==========================================================
        # MEZCLA
        # ==========================================================

        scramble_settings = QHBoxLayout()

        scramble_label = QLabel(
            "Movimientos para mezclar:"
        )

        self.scramble_count = (
            QSpinBox()
        )

        # ----------------------------------------------------------
        # IMPORTANTE:
        #
        # Para probar algoritmos de búsqueda,
        # es mejor comenzar con pocas mezclas.
        # ----------------------------------------------------------

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

        self.scramble_button = QPushButton(
            "Mezclar"
        )

        self.undo_button = QPushButton(
            "Deshacer"
        )

        self.reset_button = QPushButton(
            "Reiniciar"
        )

        self.scramble_button.setMinimumHeight(
            42
        )

        self.undo_button.setMinimumHeight(
            42
        )

        self.reset_button.setMinimumHeight(
            42
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
    # CREAR CARA
    # ==============================================================

    def create_face(
        self,
        face_index
    ):

        frame = QGroupBox(
            f"Cara {face_index}"
        )

        layout = QGridLayout(
            frame
        )

        layout.setSpacing(
            2
        )

        layout.setContentsMargins(
            5,
            5,
            5,
            5
        )

        self.stickers[
            face_index
        ] = []

        for row in range(3):

            sticker_row = []

            for col in range(3):

                sticker = QLabel()

                sticker.setFixedSize(
                    55,
                    55
                )

                sticker.setStyleSheet(
                    """
                    QLabel {
                        background-color: gray;
                        border: 2px solid #222;
                        border-radius: 3px;
                    }
                    """
                )

                layout.addWidget(
                    sticker,
                    row,
                    col
                )

                sticker_row.append(
                    sticker
                )

            self.stickers[
                face_index
            ].append(
                sticker_row
            )

        return frame

    # ==============================================================
    # CARGAR ALGORITMOS
    # ==============================================================

    def load_algorithms(self):

        self.algorithm_combo.clear()

        self.algorithm_map = {
            "A*": (
                self.search_algorithms.astar
            ),

            "GBF": (
                self.search_algorithms.gbf
            ),

            "Bidirectional": (
                self.search_algorithms.bidirectional
            ),
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

        # Una nueva modificación invalida
        # cualquier solución anterior.

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
                "Deshacer",
                "No hay movimientos para deshacer."
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
    # ACTUALIZAR VISTA
    # ==============================================================

    def update_cube_view(self):

        for face_index in range(6):

            face = self.cube.faces[
                face_index
            ]

            for row in range(3):

                for col in range(3):

                    value = (
                        face.values[
                            row
                        ][
                            col
                        ]
                    )

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
                            border: 2px solid #222;
                            border-radius: 3px;
                        }}
                        """
                    )

        # ----------------------------------------------------------
        # ESTADO
        # ----------------------------------------------------------

        if self.cube.is_solved():

            self.status_label.setText(
                "Estado: RESUELTO"
            )

        else:

            self.status_label.setText(
                "Estado: MEZCLADO"
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

        if times == 0:

            return (
                f"{move.axis.name}0"
            )

        if times == 2:

            return (
                f"{move.axis.name}2"
            )

        # ----------------------------------------------------------
        # 1 GIRO
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
        # 3 GIROS
        #
        # Equivale a uno en dirección contraria.
        # ----------------------------------------------------------

        if times == 3:

            inverted = (
                Direction.invert(
                    move.direction
                )
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
    # HISTORIAL
    # ==============================================================

    def update_history_view(self):

        if not self.cube.history:

            self.history_text.setPlainText(
                "Sin movimientos."
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

    # ==============================================================
    # COPIAR CUBO
    # ==============================================================

    def get_cube_copy(self):

        cube_copy = RubikCube()

        # ----------------------------------------------------------
        # Copiamos directamente los valores actuales.
        # ----------------------------------------------------------

        for face_index in range(6):

            cube_copy.faces[
                face_index
            ].values = [

                row[:]

                for row in (
                    self.cube.faces[
                        face_index
                    ].values
                )
            ]

        cube_copy.history = []

        return cube_copy

    # ==============================================================
    # EJECUTAR ALGORITMO SELECCIONADO
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
                "Algoritmo",
                "No se encontró el algoritmo seleccionado."
            )

            return

        # ----------------------------------------------------------
        # DESACTIVAR BOTÓN TEMPORALMENTE
        # ----------------------------------------------------------

        self.run_algorithm_button.setEnabled(
            False
        )

        self.run_algorithm_button.setText(
            "Buscando..."
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
                "Buscar solución"
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
                "Resultado inválido",
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
            f"Movimientos solución: {len(result.moves)}\n"
            f"Resultado: {result.message}"
        )

        self.algorithm_result_label.setText(
            stats
        )

        # ----------------------------------------------------------
        # SI NO HUBO SOLUCIÓN
        # ----------------------------------------------------------

        if not result.success:

            self.solution_text.setPlainText(
                "No se encontró una solución."
            )

            self.last_solution = []

            self.apply_solution_button.setEnabled(
                False
            )

            return

        # ----------------------------------------------------------
        # GUARDAR SOLUCIÓN
        # ----------------------------------------------------------

        self.last_solution = (
            result.moves
        )

        # ----------------------------------------------------------
        # SI YA ESTABA RESUELTO
        # ----------------------------------------------------------

        if not result.moves:

            self.solution_text.setPlainText(
                "El cubo ya está resuelto."
            )

            self.apply_solution_button.setEnabled(
                False
            )

            return

        # ----------------------------------------------------------
        # MOSTRAR PASOS
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

        self.apply_solution_button.setEnabled(
            True
        )

    # ==============================================================
    # APLICAR ÚLTIMA SOLUCIÓN
    # ==============================================================

    def apply_last_solution(self):

        if not self.last_solution:

            return

        # Hacemos una copia para evitar
        # que clear_last_solution borre
        # la lista mientras la aplicamos.

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
    # BORRAR SOLUCIÓN GUARDADA
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
            "algorithm_result_label"
        ):

            self.algorithm_result_label.setText(
                "Resultado: pendiente"
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