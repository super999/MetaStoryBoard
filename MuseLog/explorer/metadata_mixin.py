from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence, Set

from PySide6.QtWidgets import QPushButton, QTableWidgetItem

from MuseLog.explorer.meta import MetaStruct


class MetadataMixin:
    """Collects directory metadata and populates the table."""

    _auto_trigger_ops: Set[str] = {"视频元数据"}

    def _init_metadata_state(self) -> None:
        self._table_row_meta: List[MetaStruct] = []

    def show_directory_metadata(self, folder: str) -> None:
        meta = self.collect_metadata(folder)
        self._clear_detail_widget()
        self._update_custom_widget(folder, meta)
        self.populate_table(meta)

    def populate_table(self, meta: Dict[str, MetaStruct]) -> None:
        self.ui.tableMeta.clearContents()
        self._table_row_meta = []
        rows = self._order_metadata(meta)
        self.ui.tableMeta.setRowCount(len(rows))
        for row_index, (key, value) in enumerate(rows):
            self._table_row_meta.append(value)
            self.ui.tableMeta.setItem(row_index, 0, QTableWidgetItem(str(key)))
            self.ui.tableMeta.setItem(row_index, 1, QTableWidgetItem(value.name))
            if value.op_type:
                button = QPushButton(value.op_name or "操作", self.ui.tableMeta)
                op_type = value.op_type
                op_data = value.op_data
                button.clicked.connect(
                    lambda _checked=False, opt=op_type, data=op_data: self.on_metadata_operation_clicked(opt, data)
                )
                self.ui.tableMeta.setCellWidget(row_index, 2, button)
        self.ui.tableMeta.resizeColumnToContents(0)

    def collect_metadata(self, folder: str) -> Dict[str, MetaStruct]:
        meta: Dict[str, MetaStruct] = {
            "目录": MetaStruct(folder, op_type="打开文件夹", op_name="打开", op_data=folder)
        }

        prompt_text_count = 0
        for name in ("提示词.txt", "prompt.txt", "prompts.txt", "neg_prompt.txt", "caption.txt"):
            path = os.path.join(folder, name)
            if self._check_file_exists(path):
                key = f"提示词_{prompt_text_count}"
                meta[key] = MetaStruct(name, op_type="打开文本文件", op_name="查看", op_data=path)
                prompt_text_count += 1

        json_data = self._read_first_json(
            [
                os.path.join(folder, name)
                for name in ("metadata.json", "params.json", "info.json")
            ]
        )
        if json_data:
            model = json_data.get("model") or json_data.get("model_name") or json_data.get("ckpt")
            if model:
                meta["模型名称"] = MetaStruct("模型名称", model)
            if "prompt" in json_data and "提示词" not in meta:
                meta["提示词"] = MetaStruct("提示词", str(json_data.get("prompt"))[:2000])
            meta["其他参数"] = MetaStruct("其他参数", json_data)

        videos = self._list_files(folder, {".mp4", ".mov", ".avi", ".mkv", ".webm"})
        for index, video in enumerate(videos):
            meta[f"视频文件_{index}"] = MetaStruct(
                os.path.basename(video),
                op_type="视频元数据",
                op_name="元数据",
                op_data=video,
            )

        refs: List[str] = []
        images = self._list_files(folder, {".png", ".jpg", ".jpeg", ".bmp", ".gif"})
        for image_path in images:
            lower_name = os.path.basename(image_path).lower()
            if "ref" in lower_name or "reference" in lower_name:
                refs.append(image_path)
        ref_dir = os.path.join(folder, "ref")
        if os.path.isdir(ref_dir):
            refs.extend(self._list_files(ref_dir, {".png", ".jpg", ".jpeg", ".bmp", ".gif"}))
        if refs:
            preview = ", ".join(os.path.basename(item) for item in refs[:20])
            if len(refs) > 20:
                preview += " ..."
            meta["参考图"] = MetaStruct("参考图", preview)

        return meta

    def on_table_cell_activated(self, row: int, column: int) -> None:
        if column != 1:
            return
        if row < 0 or row >= len(self._table_row_meta):
            return
        entry = self._table_row_meta[row]
        if not entry or not entry.op_type:
            return
        if entry.op_type not in self._auto_trigger_ops:
            return
        logging.debug("自动触发表格操作: row=%s, op_type=%s", row, entry.op_type)
        self.on_metadata_operation_clicked(entry.op_type, entry.op_data)

    # Helpers -------------------------------------------------------------
    @staticmethod
    def _order_metadata(meta: Dict[str, MetaStruct]) -> Sequence[tuple[str, MetaStruct]]:
        ordered: List[tuple[str, MetaStruct]] = []
        key_order = ["目录", "提示词", "模型名称", "视频文件", "参考图"]
        existing = set()
        for key in key_order:
            if key in meta:
                ordered.append((key, meta[key]))
                existing.add(key)
        for key, value in meta.items():
            if key not in existing:
                ordered.append((key, value))
        return ordered

    @staticmethod
    def _check_file_exists(path: str) -> bool:
        return os.path.isfile(path)

    @staticmethod
    def _read_first_text(paths: List[str]) -> Optional[str]:
        for path in paths:
            try:
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as handle:
                        return handle.read()
            except Exception:
                try:
                    with open(path, "r", encoding="gbk", errors="ignore") as handle:
                        return handle.read()
                except Exception:
                    continue
        return None

    @staticmethod
    def _read_first_json(paths: List[str]) -> Optional[Dict[str, Any]]:
        for path in paths:
            try:
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as handle:
                        return json.load(handle)
            except Exception:
                continue
        return None

    @staticmethod
    def _list_files(folder: str, exts: Set[str]) -> List[str]:
        results: List[str] = []
        try:
            for name in os.listdir(folder):
                path = os.path.join(folder, name)
                if os.path.isfile(path):
                    _, ext = os.path.splitext(name)
                    if ext.lower() in exts:
                        results.append(path)
        except Exception:
            pass
        return results

    # Callback placeholders to satisfy mypy / linters --------------------
    def _update_custom_widget(self, folder: str, meta: Dict[str, MetaStruct]) -> None:  # pragma: no cover
        raise NotImplementedError

    def on_metadata_operation_clicked(self, op_type: str, op_data):  # pragma: no cover
        raise NotImplementedError

    def _clear_detail_widget(self) -> None:  # pragma: no cover
        raise NotImplementedError
