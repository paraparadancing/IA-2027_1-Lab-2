import heapq
import math
import time
from itertools import count

from rubik import RubikCube, Axis, Direction, Move


# ==============================================================
# RESULTADO DE UNA BÚSQUEDA
# ==============================================================

class SearchResult:

    def __init__(
        self,
        moves=None,
        explored_nodes=0,
        execution_time=0.0,
        algorithm="",
        success=False,
        message=""
    ):
        self.moves = moves if moves is not None else []
        self.explored_nodes = explored_nodes
        self.execution_time = execution_time
        self.algorithm = algorithm
        self.success = success
        self.message = message


# ==============================================================
# ALGORITMOS DE BÚSQUEDA
# ==============================================================

class SearchAlgorithms:

    def __init__(self, max_nodes=100000):
        self.max_nodes = max_nodes

        # ----------------------------------------------------------
        # Movimientos posibles
        #
        # Por cada eje:
        # A+
        # A-
        # A2
        #
        # ... hasta I
        # ----------------------------------------------------------

        self.possible_moves = []

        for axis in Axis:

            self.possible_moves.append(
                Move(
                    axis,
                    Direction.POSITIVE,
                    1
                )
            )

            self.possible_moves.append(
                Move(
                    axis,
                    Direction.NEGATIVE,
                    1
                )
            )

            self.possible_moves.append(
                Move(
                    axis,
                    Direction.POSITIVE,
                    2
                )
            )

        # Estado objetivo
        solved_cube = RubikCube()
        self.goal_state = self.cube_to_state(
            solved_cube
        )

    # ==========================================================
    # CONVERSIÓN CUBO -> ESTADO
    # ==========================================================

    def cube_to_state(self, cube):

        state = []

        for face in cube.faces:

            for row in face.values:

                for value in row:

                    state.append(value)

        return tuple(state)

    # ==========================================================
    # CONVERSIÓN ESTADO -> CUBO
    # ==========================================================

    def state_to_cube(self, state):

        cube = RubikCube()

        index = 0

        for face in cube.faces:

            new_values = []

            for row in range(3):

                new_row = []

                for col in range(3):

                    new_row.append(
                        state[index]
                    )

                    index += 1

                new_values.append(
                    new_row
                )

            face.values = new_values

        cube.history = []

        return cube

    # ==========================================================
    # APLICAR MOVIMIENTO SOBRE UN ESTADO
    # ==========================================================

    def apply_move(self, state, move):

        cube = self.state_to_cube(
            state
        )

        cube.turn(
            move.axis,
            move.direction,
            move.times,
            False
        )

        return self.cube_to_state(
            cube
        )

    # ==========================================================
    # MOVIMIENTO INVERSO
    # ==========================================================

    def inverse_move(self, move):

        # Un movimiento doble es su propio inverso.

        if move.times % 4 == 2:

            return Move(
                move.axis,
                Direction.POSITIVE,
                2
            )

        return Move(
            move.axis,
            Direction.invert(
                move.direction
            ),
            move.times
        )

    # ==========================================================
    # HEURÍSTICA
    # ==========================================================

    def heuristic(self, state):
        """
        Cuenta cuántas casillas están fuera
        de su cara objetivo.

        Cada cara resuelta contiene únicamente
        su propio número:

            cara 0 -> 0
            cara 1 -> 1
            ...
            cara 5 -> 5

        Dividimos entre 12 porque un giro puede
        afectar varias casillas simultáneamente.
        """

        misplaced = 0

        index = 0

        for face_index in range(6):

            for _ in range(9):

                if state[index] != face_index:

                    misplaced += 1

                index += 1

        return math.ceil(
            misplaced / 12
        )

    # ==========================================================
    # RECONSTRUIR CAMINO
    # ==========================================================

    def reconstruct_path(
        self,
        parents,
        final_state
    ):

        path = []

        current_state = final_state

        while parents[current_state] is not None:

            previous_state, move = (
                parents[current_state]
            )

            path.append(
                move
            )

            current_state = (
                previous_state
            )

        path.reverse()

        return path

    # ==========================================================
    # A*
    # ==========================================================

    def astar(self, cube):

        algorithm_name = "A*"

        start_time = time.perf_counter()

        start_state = self.cube_to_state(
            cube
        )

        # Ya está resuelto.

        if start_state == self.goal_state:

            return SearchResult(
                moves=[],
                explored_nodes=0,
                execution_time=(
                    time.perf_counter()
                    - start_time
                ),
                algorithm=algorithm_name,
                success=True,
                message="El cubo ya está resuelto."
            )

        # ------------------------------------------------------
        # Cola de prioridad
        #
        # (f, contador, g, estado)
        # ------------------------------------------------------

        queue = []

        unique_counter = count()

        start_h = self.heuristic(
            start_state
        )

        heapq.heappush(
            queue,
            (
                start_h,
                next(unique_counter),
                0,
                start_state
            )
        )

        g_score = {
            start_state: 0
        }

        parents = {
            start_state: None
        }

        explored_nodes = 0

        closed = set()

        # ------------------------------------------------------
        # BÚSQUEDA
        # ------------------------------------------------------

        while queue:

            f_score, _, current_g, current_state = (
                heapq.heappop(queue)
            )

            if current_state in closed:
                continue

            closed.add(
                current_state
            )

            explored_nodes += 1

            # --------------------------------------------------
            # OBJETIVO
            # --------------------------------------------------

            if current_state == self.goal_state:

                path = self.reconstruct_path(
                    parents,
                    current_state
                )

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                return SearchResult(
                    moves=path,
                    explored_nodes=explored_nodes,
                    execution_time=elapsed,
                    algorithm=algorithm_name,
                    success=True,
                    message="Solución encontrada."
                )

            # --------------------------------------------------
            # LÍMITE
            # --------------------------------------------------

            if explored_nodes >= self.max_nodes:

                break

            # --------------------------------------------------
            # SUCESORES
            # --------------------------------------------------

            for move in self.possible_moves:

                new_state = self.apply_move(
                    current_state,
                    move
                )

                tentative_g = (
                    current_g + 1
                )

                if tentative_g < g_score.get(
                    new_state,
                    float("inf")
                ):

                    g_score[new_state] = (
                        tentative_g
                    )

                    parents[new_state] = (
                        current_state,
                        move
                    )

                    h = self.heuristic(
                        new_state
                    )

                    f = tentative_g + h

                    heapq.heappush(
                        queue,
                        (
                            f,
                            next(unique_counter),
                            tentative_g,
                            new_state
                        )
                    )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        return SearchResult(
            moves=[],
            explored_nodes=explored_nodes,
            execution_time=elapsed,
            algorithm=algorithm_name,
            success=False,
            message=(
                "No se encontró solución dentro "
                "del límite de nodos."
            )
        )

    # ==========================================================
    # GREEDY BEST-FIRST SEARCH
    # ==========================================================

    def gbf(self, cube):

        algorithm_name = "GBF"

        start_time = time.perf_counter()

        start_state = self.cube_to_state(
            cube
        )

        if start_state == self.goal_state:

            return SearchResult(
                moves=[],
                explored_nodes=0,
                execution_time=(
                    time.perf_counter()
                    - start_time
                ),
                algorithm=algorithm_name,
                success=True,
                message="El cubo ya está resuelto."
            )

        queue = []

        unique_counter = count()

        start_h = self.heuristic(
            start_state
        )

        heapq.heappush(
            queue,
            (
                start_h,
                next(unique_counter),
                start_state
            )
        )

        parents = {
            start_state: None
        }

        visited = set()

        explored_nodes = 0

        while queue:

            _, _, current_state = (
                heapq.heappop(queue)
            )

            if current_state in visited:
                continue

            visited.add(
                current_state
            )

            explored_nodes += 1

            # --------------------------------------------------
            # OBJETIVO
            # --------------------------------------------------

            if current_state == self.goal_state:

                path = self.reconstruct_path(
                    parents,
                    current_state
                )

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                return SearchResult(
                    moves=path,
                    explored_nodes=explored_nodes,
                    execution_time=elapsed,
                    algorithm=algorithm_name,
                    success=True,
                    message="Solución encontrada."
                )

            if explored_nodes >= self.max_nodes:
                break

            # --------------------------------------------------
            # SUCESORES
            # --------------------------------------------------

            for move in self.possible_moves:

                new_state = self.apply_move(
                    current_state,
                    move
                )

                if (
                    new_state in visited
                    or new_state in parents
                ):
                    continue

                parents[new_state] = (
                    current_state,
                    move
                )

                h = self.heuristic(
                    new_state
                )

                heapq.heappush(
                    queue,
                    (
                        h,
                        next(unique_counter),
                        new_state
                    )
                )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        return SearchResult(
            moves=[],
            explored_nodes=explored_nodes,
            execution_time=elapsed,
            algorithm=algorithm_name,
            success=False,
            message=(
                "No se encontró solución dentro "
                "del límite de nodos."
            )
        )

    # ==========================================================
    # BIDIRECCIONAL
    # ==========================================================

    def bidirectional(self, cube):

        algorithm_name = "Bidirectional"

        start_time = time.perf_counter()

        start_state = self.cube_to_state(
            cube
        )

        goal_state = self.goal_state

        if start_state == goal_state:

            return SearchResult(
                moves=[],
                explored_nodes=0,
                execution_time=(
                    time.perf_counter()
                    - start_time
                ),
                algorithm=algorithm_name,
                success=True,
                message="El cubo ya está resuelto."
            )

        # ------------------------------------------------------
        # FRONTERAS
        # ------------------------------------------------------

        frontier_start = {
            start_state
        }

        frontier_goal = {
            goal_state
        }

        # ------------------------------------------------------
        # PADRES
        # ------------------------------------------------------

        parents_start = {
            start_state: None
        }

        parents_goal = {
            goal_state: None
        }

        explored_nodes = 0

        while (
            frontier_start
            and frontier_goal
        ):

            # ==================================================
            # EXPANDIR DESDE EL ESTADO INICIAL
            # ==================================================

            next_frontier_start = set()

            for current_state in frontier_start:

                explored_nodes += 1

                if explored_nodes >= self.max_nodes:
                    break

                for move in self.possible_moves:

                    new_state = self.apply_move(
                        current_state,
                        move
                    )

                    if new_state in parents_start:
                        continue

                    parents_start[new_state] = (
                        current_state,
                        move
                    )

                    # ------------------------------------------
                    # INTERSECCIÓN
                    # ------------------------------------------

                    if new_state in parents_goal:

                        elapsed = (
                            time.perf_counter()
                            - start_time
                        )

                        path = (
                            self.build_bidirectional_path(
                                parents_start,
                                parents_goal,
                                new_state
                            )
                        )

                        return SearchResult(
                            moves=path,
                            explored_nodes=explored_nodes,
                            execution_time=elapsed,
                            x=algorithm_name,
                            success=True,
                            message="Solución encontrada."
                        )

                    next_frontier_start.add(
                        new_state
                    )

            if explored_nodes >= self.max_nodes:
                break

            frontier_start = (
                next_frontier_start
            )

            # ==================================================
            # EXPANDIR DESDE EL OBJETIVO
            # ==================================================

            next_frontier_goal = set()

            for current_state in frontier_goal:

                explored_nodes += 1

                if explored_nodes >= self.max_nodes:
                    break

                for move in self.possible_moves:

                    new_state = self.apply_move(
                        current_state,
                        move
                    )

                    if new_state in parents_goal:
                        continue

                    parents_goal[new_state] = (
                        current_state,
                        move
                    )

                    # ------------------------------------------
                    # INTERSECCIÓN
                    # ------------------------------------------

                    if new_state in parents_start:

                        elapsed = (
                            time.perf_counter()
                            - start_time
                        )

                        path = (
                            self.build_bidirectional_path(
                                parents_start,
                                parents_goal,
                                new_state
                            )
                        )

                        return SearchResult(
                            moves=path,
                            explored_nodes=explored_nodes,
                            execution_time=elapsed,
                            algorithm=algorithm_name,
                            success=True,
                            message="Solución encontrada."
                        )

                    next_frontier_goal.add(
                        new_state
                    )

            if explored_nodes >= self.max_nodes:
                break

            frontier_goal = (
                next_frontier_goal
            )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        return SearchResult(
            moves=[],
            explored_nodes=explored_nodes,
            execution_time=elapsed,
            algorithm=algorithm_name,
            success=False,
            message=(
                "No se encontró solución dentro "
                "del límite de nodos."
            )
        )

    # ==========================================================
    # CONSTRUIR SOLUCIÓN BIDIRECCIONAL
    # ==========================================================

    def build_bidirectional_path(
        self,
        parents_start,
        parents_goal,
        meeting_state
    ):

        # ------------------------------------------------------
        # INICIO -> INTERSECCIÓN
        # ------------------------------------------------------

        first_half = []

        current_state = meeting_state

        while (
            parents_start[current_state]
            is not None
        ):

            previous_state, move = (
                parents_start[current_state]
            )

            first_half.append(
                move
            )

            current_state = (
                previous_state
            )

        first_half.reverse()

        # ------------------------------------------------------
        # INTERSECCIÓN -> OBJETIVO
        # ------------------------------------------------------

        second_half = []

        current_state = meeting_state

        while (
            parents_goal[current_state]
            is not None
        ):

            previous_state, move = (
                parents_goal[current_state]
            )

            # El árbol del objetivo se construyó
            # desde el objetivo hacia afuera.
            #
            # Por eso debemos invertir cada
            # movimiento para regresar al objetivo.

            inverse = self.inverse_move(
                move
            )

            second_half.append(
                inverse
            )

            current_state = (
                previous_state
            )

        return (
            first_half
            + second_half
        )