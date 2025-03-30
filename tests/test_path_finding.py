import pytest

from pathfinding import find_path

from models import Map

@pytest.fixture
def small_map():
    m = Map(width=20, height=20, grid_resolution_px=1)

    m.data[2,2:8] = 1
    m.data[8,2:8] = 1
    m.data[2:9,2] = 1
    m.data[2:9,8] = 1

    return m

def test_pathfinding(small_map: Map):
    pacman_loc = (8, 8)
    target_loc = (2, 2)

    found_path = find_path(small_map.data, pacman_loc, target_loc)

    assert found_path == [(8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (8, 3),
                          (8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (3, 2),
                          (2, 2)]

    target_loc = (8, 5)
    found_path = find_path(small_map.data, pacman_loc, target_loc)
    assert found_path == [(8, 8), (8, 7), (8, 6), (8, 5)]

    target_loc = (10, 10)
    found_path = find_path(small_map.data, pacman_loc, target_loc)
    assert found_path is None
