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
            self.faces[4],
            self.faces[3],
            self.faces[5],
            self.faces[1]),
            (RubikCube.CBA, RubikCube.DEF)
        )

        RubikCube.set_sides(self.faces[3], (
            self.faces[4],
            self.faces[0],
            self.faces[5],
            self.faces[2]),
            (RubikCube.IHG, RubikCube.DEF)
        )

        RubikCube.set_sides(self.faces[4], (
            self.faces[2],
            self.faces[1],
            self.faces[0],
            self.faces[3]),
            (RubikCube.ABC, RubikCube.IHG)
        )

        RubikCube.set_sides(self.faces[5], (
            self.faces[1],
            self.faces[2],
            self.faces[4],
            self.faces[0]),
            (RubikCube.GHI, RubikCube.CBA)
        )

    def is_solved(self) -> bool:
        return all(face.is_solved() for face in self.faces)

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

    def set_neighbor_face(self, other: CubeFace, side: FaceSide) -> None:
        self.neighbor_faces[side] = other
    
    def set_axes(self, h_axes: tuple[Axis], v_axes: tuple[Axis]) -> None:
        self.h_axes = h_axes
        self.v_axes = v_axes

    def is_solved(self) -> bool:
        return all(self.values[0] == v for v in self.values)
