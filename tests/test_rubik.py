from rubik import RubikCube
import pytest

def test_rubik_class():
    my_cube = RubikCube()

    assert my_cube.is_solved()
