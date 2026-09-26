from enum import Enum, auto

class Axis(Enum):
    A = auto()
    B = auto()
    C = auto()

    D = auto()
    E = auto()
    F = auto()

    G = auto()
    H = auto()
    I = auto()

class Direction(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()

    @classmethod
    def invert(cls, direction: Direction) -> Direction:
        if direction == Direction.POSITIVE:
            return Direction.NEGATIVE
        else:
            return Direction.POSITIVE

class FaceSide(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

class RubikCube():
    ABC = (Axis.A, Axis.B, Axis.C)
    CBA = (Axis.C, Axis.B, Axis.A)
    DEF = (Axis.D, Axis.E, Axis.F)
    GHI = (Axis.G, Axis.H, Axis.I)
    IHG = (Axis.I, Axis.H, Axis.G)

    def __init__(self) -> None:
        self.faces = tuple(CubeFace(i) for i in range(6))
        self.history: list[Move] = []

        RubikCube.set_sides(self.faces[0], (
            self.faces[4],
            self.faces[1],
            self.faces[5],
            self.faces[3]), 
            (RubikCube.ABC, RubikCube.DEF)
        )

        RubikCube.set_sides(self.faces[1], (
            self.faces[4],
            self.faces[2],
            self.faces[5],
            self.faces[0]),
            (RubikCube.GHI, RubikCube.DEF)
        )

        RubikCube.set_sides(self.faces[2], (
            self.faces[5],
            self.faces[3],
            self.faces[4],
            self.faces[1]),
            (RubikCube.CBA, RubikCube.DEF)
        )

        RubikCube.set_sides(self.faces[3], (
            self.faces[5],
            self.faces[0],
            self.faces[4],
            self.faces[2]),
            (RubikCube.IHG, RubikCube.DEF)
        )

        RubikCube.set_sides(self.faces[4], (
            self.faces[2],
            self.faces[3],
            self.faces[0],
            self.faces[1]),
            (RubikCube.ABC, RubikCube.IHG)
        )

        RubikCube.set_sides(self.faces[5], (
            self.faces[1],
            self.faces[0],
            self.faces[3],
            self.faces[2]),
            (RubikCube.GHI, RubikCube.CBA)
        )

    def is_solved(self) -> bool:
        return all(face.is_solved() for face in self.faces)

    def get_starting_face(self, axis: Axis) -> CubeFace:
        if axis in RubikCube.ABC or axis in RubikCube.DEF:
            return self.faces[0]
        elif axis in RubikCube.GHI:
            return self.faces[1]

    def turn(
        self,
        axis: Axis,
        direction: Direction,
        times: int,
        save_move:bool = True
    ) -> None:
        match times % 4:
            case 1:
                self.shift_one_time(axis, direction)
            case 2:
                self.cross_swap(axis)
            case 3:
                self.shift_one_time(axis, Direction.invert(direction))

        if save_move:
            self.history.append(Move(axis, direction, times))

    def revert_last_move(self) -> None:
        last_move = self.history.pop()
        self.turn(
            last_move.axis,
            Direction.invert(last_move.direction),
            last_move.times,
            False
        )
        return last_move

    def shift_one_time(self, axis: Axis, direction: Direction) -> None:
        current_face = self.get_starting_face(axis)
        for _ in range(3):
            next_face = current_face.get_neighbor_face(axis,direction)
            current_face.swap_values(axis, next_face)
            current_face = next_face

    def cross_swap(self, axis: Axis) -> None:
        current_face = self.get_starting_face(axis)
        swapping_faces: list[CubeFace] = []
        for _ in range(4):
            swapping_faces.append(current_face)
            current_face = current_face.get_neighbor_face(
                axis, Direction.POSITIVE
            )

        swapping_faces[0].swap_values(axis, swapping_faces[2])
        swapping_faces[1].swap_values(axis, swapping_faces[3])

    @classmethod
    def set_sides(
        cls,
        base_face: CubeFace,
        neighbor_faces: tuple[CubeFace],
        axes: tuple[tuple[Axis]]
    ) -> None:
        for i, nf in enumerate(neighbor_faces):
            base_face.set_neighbor_face(nf, FaceSide(i + 1))
        base_face.set_axes(axes[0], axes[1])

class CubeFace():
    def __init__(self, value: int) -> None:
        self.values = [[value for c in range(3)] for r in range(3)]
        self.neighbor_faces = {
            FaceSide.NORTH: None,
            FaceSide.SOUTH: None,
            FaceSide.EAST: None,
            FaceSide.WEST: None
        }

    def get_neighbor_face(self, axis: Axis, direction: Direction) -> CubeFace:
        if axis in self.h_axes and direction == Direction.POSITIVE:
            return self.neighbor_faces[FaceSide.NORTH]
        elif axis in self.h_axes and direction == Direction.NEGATIVE:
            return self.neighbor_faces[FaceSide.SOUTH]
        elif axis in self.v_axes and direction == Direction.POSITIVE:
            return self.neighbor_faces[FaceSide.EAST]
        elif axis in self.v_axes and direction == Direction.NEGATIVE:
            return self.neighbor_faces[FaceSide.WEST]

    def swap_values(self, axis: Axis, other_face: CubeFace) -> None:
        buffer = other_face.get_values(axis)
        other_face.set_values(axis, self.get_values(axis))
        self.set_values(axis, buffer)

    def get_values(self, axis: Axis) -> tuple[int]:
        if axis in self.h_axes:
            index = self.h_axes.index(axis)
            return tuple(self.values[v][index] for v in range(3))
        elif axis in self.v_axes:
            index = self.v_axes.index(axis)
            return tuple(self.values[index][v] for v in range(3))

    def set_values(self, axis: Axis, values: tuple[int]) -> None:
        if axis in self.h_axes:
            index = self.h_axes.index(axis)
            for v in range(3):
                self.values[v][index] = values[v]
        elif axis in self.v_axes:
            index = self.v_axes.index(axis)
            for v in range(3):
                self.values[index][v] = values[v]

    def set_neighbor_face(self, other: CubeFace, side: FaceSide) -> None:
        self.neighbor_faces[side] = other
    
    def set_axes(self, h_axes: tuple[Axis], v_axes: tuple[Axis]) -> None:
        self.h_axes = h_axes
        self.v_axes = v_axes

    def is_solved(self) -> bool:
        return all(self.values[0] == v for v in self.values)

class Move():
    def __init__(self, axis: Axis, direction: Direction, times: int) -> None:
        self.axis = axis
        self.direction = direction
        self.times = times
