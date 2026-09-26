from rubik import FaceSide
from rubik import RubikCube, CubeFace, Axis, Direction
import pytest

def test_rubik_class():
    my_cube = RubikCube()

    assert my_cube.is_solved()

    assert axis_are_set(
        my_cube.faces[0], RubikCube.ABC, RubikCube.DEF
    )
    assert axis_are_set(
        my_cube.faces[1], RubikCube.GHI, RubikCube.DEF
    )
    assert axis_are_set(
        my_cube.faces[2], RubikCube.CBA, RubikCube.DEF
    )
    assert axis_are_set(
        my_cube.faces[3], RubikCube.IHG, RubikCube.DEF
    )
    assert axis_are_set(
        my_cube.faces[4], RubikCube.ABC, RubikCube.IHG
    )
    assert axis_are_set(
        my_cube.faces[5], RubikCube.GHI, RubikCube.CBA
    )

    assert faces_connect(my_cube.faces[0], my_cube, (4, 1, 5, 3))
    assert faces_connect(my_cube.faces[1], my_cube, (4, 2, 5, 0))
    assert faces_connect(my_cube.faces[2], my_cube, (5, 3, 4, 1))
    assert faces_connect(my_cube.faces[3], my_cube, (5, 0, 4, 2))
    assert faces_connect(my_cube.faces[4], my_cube, (2, 3, 0, 1))
    assert faces_connect(my_cube.faces[5], my_cube, (1, 0, 3, 2))

def test_rubik_turning():
    my_cube = RubikCube()
    for ax in RubikCube.ABC:
        turns_one_by_one(my_cube, ax, Direction.POSITIVE)
    for ax in RubikCube.DEF:
        turns_one_by_one(my_cube, ax, Direction.POSITIVE)
    for ax in RubikCube.GHI:
        turns_one_by_one(my_cube, ax, Direction.POSITIVE)

    for ax in RubikCube.ABC:
        turns_one_by_one(my_cube, ax, Direction.NEGATIVE)
    for ax in RubikCube.DEF:
        turns_one_by_one(my_cube, ax, Direction.NEGATIVE)
    for ax in RubikCube.GHI:
        turns_one_by_one(my_cube, ax, Direction.NEGATIVE)

    for ax in RubikCube.ABC:
        turns_twice(my_cube, ax, Direction.POSITIVE)
    for ax in RubikCube.DEF:
        turns_twice(my_cube, ax, Direction.POSITIVE)
    for ax in RubikCube.GHI:
        turns_twice(my_cube, ax, Direction.POSITIVE)

def turns_one_by_one(cube: RubikCube, axis: Axis, direction: Direction) -> None:
    cube.turn(axis, direction, 1)
    assert not cube.is_solved()

    cube.turn(axis, direction, 1)
    assert not cube.is_solved()

    cube.turn(axis, direction, 1)
    assert not cube.is_solved()

    cube.turn(axis, direction, 1)
    assert cube.is_solved()

def turns_twice(cube: RubikCube, axis: Axis, direction: Direction) -> None:
    cube.turn(axis, direction, 2)
    assert not cube.is_solved()

    cube.turn(axis, direction, 2)
    assert cube.is_solved()

def axis_are_set(
    face: CubeFace, h_axes: tuple[Axis], v_axes: tuple[Axis]
) -> bool:
    ha_result = face.h_axes == h_axes 
    va_result = face.v_axes == v_axes

    return ha_result and va_result

def faces_connect(
    face: CubeFace, cube: RubikCube, face_numbers: tuple[int]
) -> bool:
    if face.neighbor_faces[FaceSide.NORTH] != cube.faces[face_numbers[0]]:
        return False
    if face.neighbor_faces[FaceSide.EAST] != cube.faces[face_numbers[1]]:
        return False
    if face.neighbor_faces[FaceSide.SOUTH] != cube.faces[face_numbers[2]]:
        return False
    if face.neighbor_faces[FaceSide.WEST] != cube.faces[face_numbers[3]]:
        return False

    return True
