from __future__ import annotations

import json
import os
import time
from copy import deepcopy
from dataclasses import dataclass, field
from threading import Lock
from typing import ClassVar, List, Optional, Sequence

from MuseLog.config_paths import get_config_file
import enum

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


class FavoritesStore:
    filename = "tab_favorites.json"

    _instance: ClassVar["FavoritesStore"] | None = None
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.file_path = get_config_file(self.filename)
        self._root: FavoriteNode = FavoriteNode(0, "收藏夹", "", time.time(), NodeType.FOLDER)
        self._next_id: int = 1
        self._load_data()
        self._initialized = True

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _load_data(self) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except FileNotFoundError:
            self._save_data()
            return
        except Exception:
            # 如果配置无法读取，则重置为默认结构
            self._save_data()
            return

        if isinstance(raw, dict) and "root" in raw:
            root_data = raw.get("root")
            if isinstance(root_data, dict):
                self._root = FavoriteNode.from_dict(root_data)
            self._next_id = int(raw.get("next_id", self._root.max_node_id() + 1))
            if self._next_id <= self._root.max_node_id():
                self._next_id = self._root.max_node_id() + 1
            return

        if isinstance(raw, dict) and "folders" in raw:
            # 兼容旧版本的平铺结构
            folders = raw.get("folders")
            if isinstance(folders, Sequence):
                self._root = FavoriteNode(0, "收藏夹", "", time.time())
                for entry in folders:
                    if not isinstance(entry, dict):
                        continue
                    path = entry.get("path")
                    alias = entry.get("alias")
                    if not path or not isinstance(path, str):
                        continue
                    if not alias or not isinstance(alias, str):
                        alias = self._derive_alias(path)
                    node = FavoriteNode(
                        node_id=self._next_id,
                        name=alias,
                        path=path,
                        created_at=time.time(),
                        children=[],
                    )
                    self._root.children.append(node)
                    self._next_id += 1
                self._save_data()
            return

        # 未知结构，重置
        self._root = FavoriteNode(0, "收藏夹", "", time.time())
        self._next_id = 1
        self._save_data()

    def _save_data(self) -> None:
        payload = {
            "next_id": self._next_id,
            "root": self._root.to_dict(),
        }
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_root(self, *, clone: bool = True) -> FavoriteNode:
        with self._lock:
            return deepcopy(self._root) if clone else self._root

    def add_child_node(self, node_name: str, parent_id: Optional[int] = None) -> FavoriteNode:
        parent_id = self._root.node_id if parent_id is None else parent_id

        with self._lock:
            parent = self._find_node(parent_id)
            if parent is None:
                raise KeyError(f"Parent node {parent_id} does not exist")

            name = node_name.strip()
            name = self._ensure_unique_alias(name, parent.children)

            node = FavoriteNode(
                node_id=self._next_id,
                name=name,
                path="",
                node_type=NodeType.FOLDER,
                created_at=time.time(),
            )
            self._next_id += 1
            parent.children.append(node)
            self._save_data()
            return deepcopy(node)


    def get_node_by_path(self, tree_path: str) -> Optional[FavoriteNode]:
        """根据路径查找收藏节点。
        Args:
            tree_path (str): 收藏节点的路径。例如； /A/B
        Returns:
            Optional[FavoriteNode]: 如果找到收藏节点，则返回该节点，否则返回 None。
        """
        with self._lock:
            parts = tree_path.strip().split('/')
            current = self._root
            for part in parts:
                found = None
                for child in current.children:
                    if child.name == part:
                        found = child
                        break
                if found is None:
                    return None
                current = found
            return deepcopy(current)
        
    def get_node_path(self, node_id: int) -> str:
        """获取收藏节点的路径, 通过深度优先搜索。
        Args:
            node_id (int): 收藏节点的 ID。
        Returns:
            str: 收藏节点的路径。例如； /A/B。如果节点不存在，则返回空字符串。
        """
        with self._lock:
            path_parts = []
            def dfs(current: FavoriteNode, target_id: int) -> bool:
                if current.node_id == target_id:
                    return True
                for child in current.children:
                    if dfs(child, target_id):
                        path_parts.append(child.name)
                        return True
                return False

            if dfs(self._root, node_id):
                path_parts.reverse()
                return '/' + '/'.join(path_parts)
            return ""
        
    def add_leaf_node(
        self,
        path: str,
        alias: str | None = None,
        parent_id: Optional[int] = None,
    ) -> FavoriteNode:
        parent_id = self._root.node_id if parent_id is None else parent_id
        if not os.path.isdir(path):
            raise FileNotFoundError(path)

        with self._lock:
            parent = self._find_node(parent_id)
            if parent is None:
                raise KeyError(f"Parent node {parent_id} does not exist")

            normalized_path = self._normalize(path)
            for child in parent.children:
                if self._normalize(child.path) == normalized_path:
                    return deepcopy(child)

            name = alias.strip() if isinstance(alias, str) else None
            if not name:
                name = self._derive_alias(path)
            name = self._ensure_unique_alias(name, parent.children)

            node = FavoriteNode(
                node_id=self._next_id,
                name=name,
                path=path,
                node_type=NodeType.LEAF,
                created_at=time.time(),
            )
            self._next_id += 1
            parent.children.append(node)
            self._save_data()
            return deepcopy(node)

    def remove_node(self, node_id: int) -> bool:
        if node_id == self._root.node_id:
            return False

        with self._lock:
            parent = self._find_parent(self._root, node_id)
            if parent is None:
                return False
            before = len(parent.children)
            parent.children = [child for child in parent.children if child.node_id != node_id]
            if before == len(parent.children):
                return False
            self._save_data()
            return True

    def remove_folder(self, path: str) -> bool:
        # 保留旧接口：按路径移除第一个匹配项
        normalized = self._normalize(path)
        with self._lock:
            node = self._find_node_by_path(normalized)
            if node is None or node.node_id == self._root.node_id:
                return False
            parent = self._find_parent(self._root, node.node_id)
            if parent is None:
                return False
            parent.children = [child for child in parent.children if child.node_id != node.node_id]
            self._save_data()
            return True

    def find_node(self, node_id: int) -> Optional[FavoriteNode]:
        with self._lock:
            node = self._find_node(node_id)
            return deepcopy(node) if node else None

    def list_children(self, parent_id: int) -> List[FavoriteNode]:
        with self._lock:
            parent = self._find_node(parent_id)
            if parent is None:
                return []
            return deepcopy(parent.children)

    def rename_node(self, node_id: int, new_name: str) -> FavoriteNode:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("收藏名称不能为空")

        with self._lock:
            node = self._find_node(node_id)
            if node is None:
                raise KeyError(f"Node {node_id} does not exist")

            parent = self._find_parent(self._root, node_id)
            siblings: Sequence[FavoriteNode]
            if parent is None:
                siblings = [self._root]
            else:
                siblings = parent.children

            lowered = new_name.lower()
            for sibling in siblings:
                if sibling.node_id != node_id and sibling.name.lower() == lowered:
                    raise ValueError("同级已存在同名收藏")

            node.name = new_name
            self._save_data()
            return deepcopy(node)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _find_node(self, node_id: int, current: Optional[FavoriteNode] = None) -> Optional[FavoriteNode]:
        if current is None:
            current = self._root
        if current.node_id == node_id:
            return current
        for child in current.children:
            found = self._find_node(node_id, child)
            if found is not None:
                return found
        return None

    def _find_parent(self, current: FavoriteNode, node_id: int) -> Optional[FavoriteNode]:
        for child in current.children:
            if child.node_id == node_id:
                return current
            found = self._find_parent(child, node_id)
            if found is not None:
                return found
        return None

    def _find_node_by_path(self, normalized_path: str) -> Optional[FavoriteNode]:
        stack: List[FavoriteNode] = [self._root]
        while stack:
            node = stack.pop()
            if node.path and self._normalize(node.path) == normalized_path:
                return node
            stack.extend(node.children)
        return None

    @staticmethod
    def _derive_alias(path: str) -> str:
        cleaned = os.path.normpath(path)
        name = os.path.basename(cleaned)
        return name or cleaned

    @staticmethod
    def _normalize(path: str) -> str:
        return os.path.normcase(os.path.normpath(path))

    @staticmethod
    def _ensure_unique_alias(alias: str, siblings: Sequence[FavoriteNode]) -> str:
        existing = {node.name.lower() for node in siblings}
        candidate = alias
        counter = 2
        while candidate.lower() in existing:
            candidate = f"{alias} ({counter})"
            counter += 1
        return candidate


def get_favorites_store() -> FavoritesStore:
    """Return the shared FavoritesStore instance."""
    return FavoritesStore()


def get_favorites_root() -> FavoriteNode:
    """Return a copy of the root favorite node."""
    return get_favorites_store().get_root()


def list_favorites(parent_id: int | None = None) -> List[FavoriteNode]:
    """List children of the given node (defaults to root)."""
    store = get_favorites_store()
    node_id = store.get_root(clone=False).node_id if parent_id is None else parent_id
    return store.list_children(node_id)


def add_favorite_folder(path: str, alias: str | None = None, parent_id: int | None = None) -> FavoriteNode:
    """Add a folder to favorites via the shared store."""
    return get_favorites_store().add_leaf_node(path=path, alias=alias, parent_id=parent_id)


def remove_favorite_folder(node_id: int) -> bool:
    """Remove a folder (and its descendants) via the shared store."""
    return get_favorites_store().remove_node(node_id)
