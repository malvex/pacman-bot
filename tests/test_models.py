from models import Prediction, Entity, EntityClass

import pytest


@pytest.fixture
def pred():
    return Prediction(
        width=11.1,
        height=12.5,
        x=22.3,
        y=44.8,
        confidence=55.231245534323,
        class_id=4,
        detection_id="00000000-0000-0000-0000-000000000000",
        parent_id="parent",
        **{"class": "ghost-green"}  # can't use "class" directly, so I need to use kwargs to pass the value
    )


@pytest.mark.parametrize("prediction, expected", [
    ({
        "width": 45,
        "height": 46,
        "x": 597.5,
        "y": 278,
        "confidence": 0.983401358127594,
        "class_id": 4,
        "class": "ghost-red",
        "detection_id": "5bbae579-b45a-44b2-8e0d-837d6edbdfb9",
        "parent_id": "image"
    }, [597.5, 278, "ghost-red"])
])
def test_validate_prediction(prediction, expected):
    pred = Prediction.model_validate(prediction)

    assert pred.x == expected[0]
    assert pred.y == expected[1]
    assert pred.class_name == expected[2]


def test_entity_from_prediction(pred: Prediction):
    entity = Entity.from_prediction("test", pred)

    assert entity.entity_id == "test"
    assert entity.size == 12
    assert entity.x == 22
    assert entity.y == 44
    assert entity.class_name == EntityClass.ghost_green
