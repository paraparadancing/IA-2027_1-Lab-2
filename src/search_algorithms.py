"""
Algoritmos de búsqueda para el cubo de Rubik: A*, GBF y Bidireccional.

Optimizaciones principales
--------------------------
1. Los 27 movimientos se precalculan UNA vez como permutaciones de los
   54 stickers; aplicar un movimiento es un solo itemgetter (~0.5 us)
   en lugar de construir un RubikCube completo (~70 us).
2. Los estados son `bytes` de 54 posiciones (no tuplas de enteros):
   ~5x menos memoria y hashing más rápido.
3. No se guarda el padre de cada estado: solo el último movimiento
   (un entero chico). El padre se recupera aplicando el movimiento
   inverso, así que cada estado guardado cuesta mucho menos RAM.
4. Poda de movimientos redundantes: no se mueve el mismo eje dos veces
   seguidas y los ejes paralelos (A,B,C / D,E,F / G,H,I) conmutan, así
   que solo se permite el orden creciente dentro de cada grupo.
5. Límites duros de estados guardados (RAM), tiempo y cancelación, para
   que la búsqueda termine con un mensaje en vez de trabarse.
"""

import heapq
import time
from itertools import count
from operator import itemgetter, ne

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
        message="",
        stored_states=0
    ):
        self.moves = moves if moves is not None else []
        self.explored_nodes = explored_nodes      # nodos expandidos
        self.stored_states = stored_states        # estados en memoria
        self.execution_time = execution_time
        self.algorithm = algorithm
        self.success = success
        self.message = message


# ==============================================================
# TABLAS PRECALCULADAS (se construyen una sola vez al importar)
# ==============================================================

START = 27            # marca "sin movimiento previo" (raíz del árbol)


def _build_tables():
    # Índice de movimiento: 3*eje + {0: +1, 1: -1, 2: doble}
    moves = []
    for axis in Axis:
        moves.append(Move(axis, Direction.POSITIVE, 1))
        moves.append(Move(axis, Direction.NEGATIVE, 1))
        moves.append(Move(axis, Direction.POSITIVE, 2))

    # Permutación de cada movimiento: se etiquetan los 54 stickers con
    # ids distintos, se aplica el movimiento real del cubo y se lee
    # qué id quedó en cada posición.
    getters = []
    for mv in moves:
        cube = RubikCube()
        label = 0
        for face in cube.faces:
            face.values = [
                [label + 3 * r + c for c in range(3)] for r in range(3)
            ]
            label += 9
        cube.turn(mv.axis, mv.direction, mv.times, False)
        perm = tuple(
            v for face in cube.faces for row in face.values for v in row
        )
        getters.append(itemgetter(*perm))

    # Movimiento inverso de cada índice.
    inverse = []
    for i in range(27):
        r = i % 3
        inverse.append(i + 1 if r == 0 else i - 1 if r == 1 else i)

    # Movimientos permitidos después de cada movimiento previo.
    allowed = []
    for last in range(27):
        last_axis = last // 3
        last_group = last_axis // 3
        allowed.append([
            i for i in range(27)
            if i // 3 != last_axis
            and not (i // 9 == last_group and i // 3 < last_axis)
        ])
    allowed.append(list(range(27)))   # índice START: todo permitido

    goal_cube = RubikCube()
    goal = bytes(
        v for face in goal_cube.faces for row in face.values for v in row
    )

    return moves, getters, inverse, allowed, goal


_MOVES, _GET, _INV, _ALLOWED, _GOAL = _build_tables()


def _climb(info, state):
    """Movimientos desde la raíz hasta `state` (árbol hacia adelante)."""
    out = []
    while True:
        i = info[state] & 31
        if i == START:
            break
        out.append(i)
        state = bytes(_GET[_INV[i]](state))
    out.reverse()
    return out


def _descend(info, state):
    """Movimientos desde `state` hasta la raíz (árbol del objetivo)."""
    out = []
    while True:
        i = info[state] & 31
        if i == START:
            break
        j = _INV[i]
        out.append(j)
        state = bytes(_GET[j](state))
    return out


_TABLE = {}              # estado -> distancia exacta al cubo resuelto
_TABLE_DEPTH = 0


def _ensure_table(depth):
    """BFS desde el objetivo hasta `depth` (tabla de patrones truncada).

    Un estado dentro de la tabla tiene distancia exacta; uno fuera tiene
    distancia >= depth + 1. Con depth=4 son ~234 mil estados (~45 MB) y
    tarda ~1 s; depth=5 ya serían 4.5 millones (~800 MB)."""
    global _TABLE_DEPTH
    if _TABLE_DEPTH >= depth:
        return
    table = {_GOAL: 0}
    frontier = [(_GOAL, START)]
    for d in range(1, depth + 1):
        nxt = []
        for state, last in frontier:
            for i in _ALLOWED[last]:
                n = bytes(_GET[i](state))
                if n not in table:
                    table[n] = d
                    nxt.append((n, i))
        frontier = nxt
    _TABLE.clear()
    _TABLE.update(table)
    _TABLE_DEPTH = depth


def _misplaced(state):
    """Stickers que no coinciden con el cubo resuelto."""
    return sum(map(ne, state, _GOAL))


# ==============================================================
# ALGORITMOS DE BÚSQUEDA
# ==============================================================

class SearchAlgorithms:

    def __init__(
        self,
        max_nodes=None,
        max_states=1_500_000,
        max_time=60.0,
        astar_weight=1.0,
        use_table=True,
        table_depth=4
    ):
        """
        max_nodes    : tope de nodos expandidos (None = sin tope).
        max_states   : tope de estados guardados en memoria. Con ~150 B
                       por estado, 1.5 M son unos 250-400 MB.
        max_time     : segundos máximos por búsqueda.
        astar_weight : 1.0 = A* óptimo; >1 = A* ponderado (más rápido,
                       solución no necesariamente óptima).
        use_table    : usa la tabla de distancias exactas hasta
                       `table_depth` movimientos del objetivo como
                       heurística (A* y GBF).
        """
        self.max_nodes = max_nodes
        self.max_states = max_states
        self.max_time = max_time
        self.astar_weight = astar_weight
        self.use_table = use_table
        self.table_depth = table_depth
        self.cancel_requested = False

        self.possible_moves = list(_MOVES)
        self.goal_state = _GOAL

    # ----------------------------------------------------------
    # Utilidades
    # ----------------------------------------------------------

    def cancel(self):
        self.cancel_requested = True

    def cube_to_state(self, cube):
        return bytes(
            v for face in cube.faces for row in face.values for v in row
        )

    def state_to_cube(self, state):
        cube = RubikCube()
        index = 0
        for face in cube.faces:
            face.values = [
                list(state[index + 3 * r: index + 3 * r + 3])
                for r in range(3)
            ]
            index += 9
        cube.history = []
        return cube

    def verify_solution(self, cube, moves):
        """Aplica `moves` con el cubo real y revisa que quede resuelto."""
        copy = self.state_to_cube(self.cube_to_state(cube))
        for m in moves:
            copy.turn(m.axis, m.direction, m.times, False)
        return self.cube_to_state(copy) == _GOAL

    def _table(self):
        """(tabla, piso): `piso` es la cota para estados fuera de ella."""
        if not self.use_table:
            return {}, 0
        _ensure_table(self.table_depth)
        return _TABLE, _TABLE_DEPTH + 1

    def _limit_reason(self, expanded, stored, t0):
        if self.cancel_requested:
            return "Búsqueda cancelada."
        if self.max_nodes is not None and expanded >= self.max_nodes:
            return "Límite de nodos expandidos alcanzado."
        if stored >= self.max_states:
            return "Límite de memoria (estados guardados) alcanzado."
        if time.perf_counter() - t0 >= self.max_time:
            return "Límite de tiempo alcanzado."
        return None

    def _ok(self, name, t0, indices, expanded, stored, message):
        return SearchResult(
            moves=[_MOVES[i] for i in indices],
            explored_nodes=expanded,
            execution_time=time.perf_counter() - t0,
            algorithm=name,
            success=True,
            message=message,
            stored_states=stored
        )

    def _fail(self, name, t0, expanded, stored, reason):
        return SearchResult(
            moves=[],
            explored_nodes=expanded,
            execution_time=time.perf_counter() - t0,
            algorithm=name,
            success=False,
            message=f"No se encontró solución. {reason}",
            stored_states=stored
        )

    # ==========================================================
    # A*
    #
    # h(n) = max(ceil(stickers_mal_colocados / 12), distancia en la tabla
    # truncada). Un movimiento cambia 12 stickers como máximo y la tabla
    # es exacta (o una cota inferior), así que h es admisible y
    # consistente.
    # ==========================================================

    def astar(self, cube):
        name = "A*"
        t0 = time.perf_counter()
        start = self.cube_to_state(cube)

        if start == _GOAL:
            return self._ok(name, t0, [], 0, 1, "El cubo ya está resuelto.")

        w = self.astar_weight
        tie = count()
        tab, floor = self._table()
        tget = tab.get

        def h_of(state):
            h = (_misplaced(state) + 11) // 12
            t = tget(state, floor)
            return t if t > h else h

        # info[estado] = (g << 5) | último_movimiento
        info = {start: START}
        h0 = h_of(start)
        heap = [(w * h0, h0, next(tie), 0, start)]
        expanded = 0

        heappush = heapq.heappush
        heappop = heapq.heappop

        while heap:
            _, _, _, g, state = heappop(heap)
            v = info[state]

            if (v >> 5) != g:          # entrada obsoleta (hubo mejor g)
                continue

            if state == _GOAL:
                return self._ok(
                    name, t0, _climb(info, state), expanded, len(info),
                    "Solución encontrada."
                )

            expanded += 1
            if not expanded & 1023:
                reason = self._limit_reason(expanded, len(info), t0)
                if reason:
                    return self._fail(name, t0, expanded, len(info), reason)

            ng = g + 1
            for i in _ALLOWED[v & 31]:
                n = bytes(_GET[i](state))
                old = info.get(n)
                if old is not None and (old >> 5) <= ng:
                    continue
                info[n] = (ng << 5) | i
                hn = h_of(n)
                heappush(heap, (ng + w * hn, hn, next(tie), ng, n))

        return self._fail(name, t0, expanded, len(info), "Espacio agotado.")

    # ==========================================================
    # GREEDY BEST-FIRST SEARCH
    #
    # h(n) = distancia exacta si el estado está en la tabla truncada;
    # si no, piso + stickers mal colocados. No es óptimo.
    # ==========================================================

    def gbf(self, cube):
        name = "GBF"
        t0 = time.perf_counter()
        start = self.cube_to_state(cube)

        if start == _GOAL:
            return self._ok(name, t0, [], 0, 1, "El cubo ya está resuelto.")

        tie = count()
        tab, floor = self._table()
        tget = tab.get

        def h_of(state):
            t = tget(state)
            return t if t is not None else floor + _misplaced(state)

        info = {start: START}
        heap = [(h_of(start), 0, next(tie), start)]
        expanded = 0

        heappush = heapq.heappush
        heappop = heapq.heappop

        while heap:
            _, depth, _, state = heappop(heap)

            expanded += 1
            if not expanded & 1023:
                reason = self._limit_reason(expanded, len(info), t0)
                if reason:
                    return self._fail(name, t0, expanded, len(info), reason)

            nd = depth + 1
            for i in _ALLOWED[info[state] & 31]:
                n = bytes(_GET[i](state))
                if n in info:
                    continue
                info[n] = i

                if n == _GOAL:
                    return self._ok(
                        name, t0, _climb(info, n), expanded, len(info),
                        "Solución encontrada."
                    )

                heappush(heap, (h_of(n), nd, next(tie), n))

        return self._fail(name, t0, expanded, len(info), "Espacio agotado.")

    # ==========================================================
    # BIDIRECCIONAL (BFS desde el inicio y desde el objetivo)
    #
    # En cada ronda se expande por completo la frontera más chica.
    # La solución puede ser 1 movimiento más larga que la óptima.
    # ==========================================================

    def bidirectional(self, cube):
        name = "Bidirectional"
        t0 = time.perf_counter()
        start = self.cube_to_state(cube)

        if start == _GOAL:
            return self._ok(name, t0, [], 0, 1, "El cubo ya está resuelto.")

        tree_a = {start: START}
        tree_b = {_GOAL: START}
        front_a = [start]
        front_b = [_GOAL]
        expanded = 0

        while front_a and front_b:
            forward = len(front_a) <= len(front_b)
            if forward:
                frontier, mine, other = front_a, tree_a, tree_b
            else:
                frontier, mine, other = front_b, tree_b, tree_a

            nxt = []
            for state in frontier:
                expanded += 1
                if not expanded & 1023:
                    stored = len(tree_a) + len(tree_b)
                    reason = self._limit_reason(expanded, stored, t0)
                    if reason:
                        return self._fail(name, t0, expanded, stored, reason)

                for i in _ALLOWED[mine[state] & 31]:
                    n = bytes(_GET[i](state))
                    if n in mine:
                        continue
                    mine[n] = i

                    if n in other:
                        path = _climb(tree_a, n) + _descend(tree_b, n)
                        return self._ok(
                            name, t0, path, expanded,
                            len(tree_a) + len(tree_b),
                            "Solución encontrada."
                        )
                    nxt.append(n)

            if forward:
                front_a = nxt
            else:
                front_b = nxt

        return self._fail(
            name, t0, expanded, len(tree_a) + len(tree_b),
            "Espacio agotado."
        )