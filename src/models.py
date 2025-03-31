from helper import calculate_distance, direction_to

from typing import Literal
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
import numpy as np


class Map:
    def __init__(self, width: int = 2000, height: int = 1200, grid_resolution_px: int = 2):
        self.width = width // grid_resolution_px
        self.height = height // grid_resolution_px
        self.grid_resolution_px = grid_resolution_px

        # Initialize 2D grid for discovered paths
        self.data = np.zeros((self.height, self.width), dtype=np.uint8)


class EntityClass(Enum):
    """All detection classes available"""
    pacman = "pacman"
    ghost_red = "ghost-red"
    ghost_orange = "ghost-orange"
    ghost_green = "ghost-green"
    ghost_yellow = "ghost-yellow"
    vulnerable_ghost = "vulnerable-ghost"
    buff = "buff"
    berry = "berry"
    unknown = "unknown"  # fallback, not an actual class


class Prediction(BaseModel):
    """Model for each prediction coming from Roboflow."""
    width: float
    height: float
    x: float
    y: float
    confidence: float
    class_id: int
    class_name: str = Field(alias="class")  # need to use alias because "class" is reserved keyword
    detection_id: UUID
    parent_id: str


class Entity(BaseModel):
    """Model for entity used by the code"""
    entity_id: str
    class_name: EntityClass
    x: int
    y: int
    size: int

    @property
    def xy(self):
        return (self.x, self.y)

    def scaled_xy(self, resolution: int) -> tuple[int]:
        """Helper method to return scaled xy coordinates (used almost everywhere)"""
        return int(self.x // resolution), int(self.y // resolution)

    def entity_bbox(self, max_size_px: int, resolution: int) -> tuple[int]:
        """Returns entity bounding box"""
        hs = int(max_size_px // resolution // 2) - 10
        rx, ry = self.scaled_xy(resolution)

        return (rx - hs, rx + hs), (ry - hs, ry + hs)

    @property
    def is_pacman(self) -> bool:
        """Returns True if the entity is the pacman."""
        return self.class_name == EntityClass.pacman

    @property
    def is_ghost(self) -> bool:
        """Returns True if the entity is a ghost."""
        return self.class_name == EntityClass.vulnerable_ghost \
            or self.class_name.value.startswith("ghost-")

    @property
    def is_alive(self) -> bool:
        """Returns True if the entity is Pacman or a ghost."""
        return self.class_name == EntityClass.pacman or self.is_ghost

    @staticmethod
    def from_prediction(ent_id: str, pred: Prediction):
        """Constructor that creates Entity model from Prediction model"""
        data_mapping = {
            "entity_id": ent_id,
            "class_name": pred.class_name,
            "x": int(pred.x),
            "y": int(pred.y),
            "size": int(max(pred.width, pred.height)),
        }
        return __class__.model_validate(data_mapping)

    def distance_to(self, target_entity) -> float:
        return calculate_distance(self.xy, target_entity.xy)

    def direction_to(self, target) -> tuple[str]:
        return direction_to(self.xy, target.xy)

    def direction_away_from(self, target) -> tuple[str]:
        return direction_to(target.xy, self.xy)


class Memory():
    power_ups = {}
    ghosts = {}

    # @property
    # def ghosts(self):
    #     ghosts = [self.ghost_red, self.ghost_yellow, self.ghost_green, self.ghost_orange]
    #     return [g for g in ghosts if g is not None]


class BotActionType(Enum):
    RUN_AWAY = "run-away"
    EAT_GHOST = "eat-ghost"
    EAT_POWERUP = "eat-powerup"
    EAT_BERRY = "eat-berry"
    WANDER = "wander"


class BotAction(BaseModel):
    action_type: BotActionType
    action_key: tuple  # Literal["up", "down", "left", "right"]
    target: Entity|None = None  # entity that we go to


class NavigationStep(BaseModel):
    x: int
    y: int
    direction: Literal["up", "down", "left", "right"]

    @property
    def xy(self):
        return self.x, self.y

    def __str__(self):
        """Print easier to read string"""
        return f"{self.direction} until ({self.xy})"
