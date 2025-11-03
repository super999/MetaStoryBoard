from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MetaStruct:
    name: str
    file_path: str = ""
    op_type: str = ""
    op_name: str = ""
    op_data: Any | None = None
