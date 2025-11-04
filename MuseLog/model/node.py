from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import List


# 定义 NodeType 枚举
class NodeType(enum.Enum):
    FOLDER = "folder"
    LEAF = "leaf"


@dataclass(slots=True)
class FavoriteNode:
    node_id: int
    name: str
    path: str
    created_at: float
    node_type: NodeType
    children: List["FavoriteNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.node_id,
            "name": self.name,
            "path": self.path,
            "created_at": self.created_at,
            "node_type": self.node_type.value,
            "children": [child.to_dict() for child in self.children],
        }

    def max_node_id(self) -> int:
        current_max = self.node_id
        for child in self.children:
            current_max = max(current_max, child.max_node_id())
        return current_max

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FavoriteNode":
        node_id = int(data.get("id", 0))
        name = str(data.get("name", ""))
        path = str(data.get("path", ""))
        created_at = float(data.get("created_at", time.time()))
        node_type_str = str(data.get("node_type", "folder"))
        try:
            node_type = NodeType(node_type_str)
        except ValueError:
            node_type = NodeType.FOLDER
        children_data = data.get("children", [])
        children: List[FavoriteNode] = []
        if isinstance(children_data, list):
            for child in children_data:
                if isinstance(child, dict):
                    children.append(cls.from_dict(child))
        return cls(node_id=node_id, name=name, path=path, created_at=created_at, node_type=node_type, children=children)
