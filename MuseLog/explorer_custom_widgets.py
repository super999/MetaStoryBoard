import json
import logging
import os
import re
import time
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget, QLabel
)

from MuseLog.GTools.download_service import DownloadService, MediaFileType
from MuseLog.explorer_signals import signal_manager

CustomWidgetBuilder = Callable[[QWidget, str, Dict[str, Any]], Sequence[QWidget]]

VIDEO_FOLDER_NAME = "视频"
SEQUENCE_FOLDER_NAME = "序列帧"
REF_FOLDER_NAME = "参考图"
SPINE_FOLDER_NAME = "spine"
SPINE_EXPORT_FOLDER_NAME = "spine-导出"
JSON42_FOLDER_NAME = "json42"

DEFAULT_FRAME_RATE = 4
DEFAULT_ANIMATION_TYPE = "待机"
DEFAULT_SEQUENCE_TEMPLATE_TYPE = "空白"
DEFAULT_VIDEO_TEMPLATE_TYPE = "空白动画"
ALL_ANIMATION_TYPES = ["走路", "待机", "死亡", "攻击"]

FRAME_RATE_PATTERN = re.compile(r"(\d+)帧")
ANIMATION_TYPE_PATTERN = re.compile(r"-(\S+)$")

CONFIG_DIR = Path.home() / ".muselog"
JSON42_HISTORY_FILE = CONFIG_DIR / "json42_history.json"
JSON42_HISTORY_LIMIT = 50
JSON42_HISTORY_KEY = "monster_numbers"

SPINE_TEMPLATE_SOURCE = Path(r"D:\美术资源\spine角色\地球危机-模板\僵尸模板\ske-template-01.spine")
GAME_MONSTER_BASE_PATH = Path(r"D:\cocos_workspace\oops-game-kit\assets\resources-spine\art-spine\monsters")
IMAGES_KEEP_FOLDER = "preds-BiRefNet_resize"


def _resolve_tab_id(widget: QWidget) -> Optional[str]:
    current: Optional[QWidget] = widget
    while current is not None:
        tab_id = current.property("tab_id")
        if isinstance(tab_id, str) and tab_id:
            return tab_id
        current = current.parent()
    return None


def resolve_custom_widget_builder(folder: str, meta: Dict[str, Any]) -> Optional[CustomWidgetBuilder]:
    """根据文件夹名称选择合适的自定义控件构建函数。"""
    folder_path = Path(os.path.normpath(folder))
    folder_name_lower = folder_path.name.lower()
    parent_dir_name = folder_path.parent.name

    if parent_dir_name == SEQUENCE_FOLDER_NAME:
        return build_sequence_frames_widgets
    if parent_dir_name == VIDEO_FOLDER_NAME:
        return build_video_modify_widgets
    if parent_dir_name == REF_FOLDER_NAME:
        return build_reference_drawings_widgets
    if folder_name_lower == SPINE_FOLDER_NAME:
        return build_spine_widgets
    if folder_name_lower == VIDEO_FOLDER_NAME:
        return build_video_widgets
    if folder_name_lower == REF_FOLDER_NAME:
        return build_reference_images_widgets
    if folder_name_lower == SEQUENCE_FOLDER_NAME:
        return build_sequence_frames_widgets_parent
    if folder_name_lower == SPINE_EXPORT_FOLDER_NAME:
        return build_spine_export_widgets
    if folder_name_lower == JSON42_FOLDER_NAME:
        return build_json42_widgets

    # 获取 父 父 文件夹名称
    grandparent_dir_name = folder_path.parent.parent.name
    if grandparent_dir_name == SEQUENCE_FOLDER_NAME:
        return build_sequence_frames_pngs_widgets

    return None


def _ensure_config_dir() -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        logging.debug("Failed to create config directory", exc_info=True)


def _load_json42_history() -> List[str]:
    _ensure_config_dir()
    if not JSON42_HISTORY_FILE.exists():
        return []
    try:
        with JSON42_HISTORY_FILE.open("r", encoding="utf-8") as handler:
            data = json.load(handler)
    except (OSError, json.JSONDecodeError):
        logging.debug("Failed to read json42 history", exc_info=True)
        return []

    if isinstance(data, dict):
        raw_items = data.get(JSON42_HISTORY_KEY, [])
    else:
        raw_items = data

    history: List[str] = []
    for item in raw_items:
        text = str(item).strip()
        if text and text not in history:
            history.append(text)
        if len(history) >= JSON42_HISTORY_LIMIT:
            break
    return history


def _save_json42_history(history: List[str]) -> None:
    _ensure_config_dir()
    payload = {JSON42_HISTORY_KEY: history[:JSON42_HISTORY_LIMIT]}
    try:
        with JSON42_HISTORY_FILE.open("w", encoding="utf-8") as handler:
            json.dump(payload, handler, ensure_ascii=False, indent=2)
    except OSError:
        logging.debug("Failed to persist json42 history", exc_info=True)


def _parse_sequence_folder_name(folder_name: str) -> tuple[int, str]:
    frame_rate = DEFAULT_FRAME_RATE
    animation_type = DEFAULT_ANIMATION_TYPE

    match = FRAME_RATE_PATTERN.search(folder_name)
    if match:
        frame_rate = int(match.group(1))

    match = ANIMATION_TYPE_PATTERN.search(folder_name)
    if match:
        animation_type = match.group(1)

    return frame_rate, animation_type


def _build_sequence_folder_name(frame_rate: int, animation_type: str) -> str:
    safe_animation_type = animation_type or DEFAULT_ANIMATION_TYPE
    return f"(秒抽{frame_rate}帧)-{safe_animation_type}"


def _build_video_default_folder_name(folder: Path) -> str:
    name_count = 1
    folder_name = f'{DEFAULT_VIDEO_TEMPLATE_TYPE}_{name_count}'
    while (folder / folder_name).exists():
        name_count += 1
        folder_name = f'{DEFAULT_VIDEO_TEMPLATE_TYPE}_{name_count}'
    return folder_name


def _build_video_folder_name_by_type(parent: Path, animation_type: str) -> str:
    name_count = 1
    safe_animation_type = animation_type or DEFAULT_ANIMATION_TYPE
    folder_name = f'{safe_animation_type}_{name_count}'
    while (parent / folder_name).exists():
        name_count += 1
        folder_name = f'{safe_animation_type}_{name_count}'
    return folder_name


def _emit_rename_request(container: QWidget, folder_path: Path, new_name: str) -> None:
    tab_id = _resolve_tab_id(container)
    if not tab_id:
        logging.debug("缺少 tab_id，无法发送重命名请求: %s", folder_path)
        return
    new_path = folder_path.with_name(new_name)
    signal_manager.rename_folder.emit(tab_id, str(folder_path), str(new_path))


def _make_spacer(container: QWidget) -> QWidget:
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return spacer


def build_sequence_frames_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    folder_path = Path(full_folder)
    frame_rate, animation_type = _parse_sequence_folder_name(folder_path.name)

    frame_rate_value = frame_rate
    animation_type_value = animation_type

    btn_modify_frame_rate = QPushButton("修改帧率", container)
    frame_rate_input = QLineEdit(container)
    frame_rate_input.setValidator(QIntValidator(1, 240, frame_rate_input))
    frame_rate_input.setMaximumWidth(60)
    frame_rate_input.setText(str(frame_rate_value))

    btn_modify_animation_type = QPushButton("修改动画类型", container)
    animation_type_combo = QComboBox(container)
    animation_type_combo.setMinimumWidth(120)
    animation_type_combo.addItems(ALL_ANIMATION_TYPES)
    if animation_type_value not in ALL_ANIMATION_TYPES:
        animation_type_combo.addItem(animation_type_value)
    animation_type_combo.setCurrentText(animation_type_value)

    def on_modify_frame_rate_clicked() -> None:
        nonlocal frame_rate_value
        text = frame_rate_input.text().strip()
        if not text:
            QMessageBox.warning(container, "输入错误", "请输入有效的帧率")
            return
        new_rate = int(text)
        if new_rate <= 0:
            QMessageBox.warning(container, "输入错误", "帧率必须大于 0")
            return
        if new_rate == frame_rate_value:
            return
        frame_rate_value = new_rate
        new_name = _build_sequence_folder_name(frame_rate_value, animation_type_combo.currentText().strip())
        _emit_rename_request(container, folder_path, new_name)

    def on_modify_animation_type_clicked() -> None:
        nonlocal animation_type_value
        new_type = animation_type_combo.currentText().strip()
        if not new_type:
            QMessageBox.warning(container, "输入错误", "动画类型不能为空")
            return
        if new_type == animation_type_value:
            return
        animation_type_value = new_type
        new_name = _build_sequence_folder_name(frame_rate_value, animation_type_value)
        _emit_rename_request(container, folder_path, new_name)
    btn_modify_frame_rate.clicked.connect(on_modify_frame_rate_clicked)
    btn_modify_animation_type.clicked.connect(on_modify_animation_type_clicked)

    btn_delete_sequence = QPushButton("删除选中的动画", container)

    def on_delete_sequence_clicked() -> None:
        reply = QMessageBox.question(container, "确认删除", "确定要删除选中的动画吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            tab_id = _resolve_tab_id(container)
            if not tab_id:
                logging.debug("缺少 tab_id，无法发送删除动画序列请求: %s", folder_path)
                return
            signal_manager.delete_selected_animation_sequence.emit(tab_id)
    btn_delete_sequence.clicked.connect(on_delete_sequence_clicked)

    # 扫描/拷贝下载的最新文件到当前目录(移动最新的下载文件)
    btn_scan_latest = QPushButton("自动下载最新文件", container)
    def on_scan_latest_clicked() -> None:
        DownloadService().scan_and_move_latest_download(str(folder_path))
        QMessageBox.information(container, "操作完成", f"已完成扫描并拷贝最新下载文件到 {folder_path}。")
        # 发送刷新信号
        tab_id = _resolve_tab_id(container)
        if tab_id:
            signal_manager.gui_fresh_tab_collect_metadata.emit(tab_id)
        
    btn_scan_latest.clicked.connect(on_scan_latest_clicked)
    
    return [
        btn_modify_frame_rate,
        frame_rate_input,
        btn_modify_animation_type,
        animation_type_combo,
        btn_delete_sequence,
        btn_scan_latest,
        _make_spacer(container),
    ]


def build_sequence_frames_pngs_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    folder_path = Path(full_folder)    
    # 把序列帧图片扣除背景
    btn_pngs_remove_bg = QPushButton("扣除背景", container)
    def on_pngs_remove_bg_clicked() -> None:
        tab_id = _resolve_tab_id(container)
        if not tab_id:
            logging.debug("缺少 tab_id，无法发送扣除背景请求: %s", folder_path)
            return
        signal_manager.remove_background_from_sequence_frames.emit(tab_id, str(folder_path))
    btn_pngs_remove_bg.clicked.connect(on_pngs_remove_bg_clicked)
    # 序列帧转为缩放为标准大小（512x512）
    btn_pngs_resize = QPushButton("缩放为标准大小", container)
    def on_pngs_resize_clicked() -> None:
        tab_id = _resolve_tab_id(container)
        if not tab_id:
            logging.debug("缺少 tab_id，无法发送缩放请求: %s", folder_path)
            return
        signal_manager.resize_sequence_frames.emit(tab_id, str(folder_path))
    btn_pngs_resize.clicked.connect(on_pngs_resize_clicked)
    return [
        btn_pngs_remove_bg,
        btn_pngs_resize,
        _make_spacer(container),
    ]


def build_video_modify_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    folder_path = Path(full_folder)
    animation_type = folder_path.name
    btn_modify_video = QPushButton("修改视频占位符", container)
    label_info = QLabel("动画名称", container)
    animation_type_combo = QComboBox(container)
    animation_type_combo.setMinimumWidth(120)
    animation_type_combo.addItems(ALL_ANIMATION_TYPES)
    if animation_type not in ALL_ANIMATION_TYPES:
        animation_type_combo.addItem(animation_type)

    def on_modify_video_clicked() -> None:
        new_name = _build_video_folder_name_by_type(folder_path.parent, animation_type_combo.currentText().strip())
        _emit_rename_request(container, folder_path, new_name)
    btn_modify_video.clicked.connect(on_modify_video_clicked)
    # 扫描并优化视频文件名称
    btn_optimize_video = QPushButton("优化视频文件名称", container)

    def on_optimize_video_clicked() -> None:
        tab_id = _resolve_tab_id(container)
        if not tab_id:
            logging.debug("缺少 tab_id，无法发送优化视频名称请求: %s", folder_path)
            return
        signal_manager.optimize_video_filenames.emit(tab_id, str(folder_path))
    btn_optimize_video.clicked.connect(on_optimize_video_clicked)
    # 自动下载视频
    btn_scan_latest = QPushButton("自动下载最新文件", container)
    def on_scan_latest_clicked() -> None:
        DownloadService().scan_and_move_latest_download(str(folder_path), media_type=MediaFileType.VIDEO)
        QMessageBox.information(container, "操作完成", f"已完成扫描并拷贝最新下载文件到 {folder_path}。")
        # 发送刷新信号
        tab_id = _resolve_tab_id(container)
        if tab_id:
            signal_manager.gui_fresh_tab_collect_metadata.emit(tab_id)
    btn_scan_latest.clicked.connect(on_scan_latest_clicked)
    return [
        btn_modify_video,
        label_info,
        animation_type_combo,
        btn_optimize_video,
        btn_scan_latest,
        _make_spacer(container),
    ]


def build_spine_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    spine_path = Path(full_folder)

    def create_spine_export_folder() -> None:
        target = spine_path.parent / SPINE_EXPORT_FOLDER_NAME
        target.mkdir(exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {target}")

    def copy_sequence_frames_to_images() -> None:
        source = spine_path.parent / SEQUENCE_FOLDER_NAME
        if not source.exists():
            QMessageBox.warning(container, "操作失败", f"{source} 不存在")
            return
        images_folder = spine_path / "images"
        images_folder.mkdir(exist_ok=True)
        shutil.copytree(source, images_folder, dirs_exist_ok=True)
        QMessageBox.information(container, "拷贝成功", f"已成功拷贝序列帧到 {images_folder}")

    def clean_extra_image_folders() -> None:
        images_dir = spine_path / "images"
        if not images_dir.exists():
            QMessageBox.warning(container, "操作失败", f"{images_dir} 不存在")
            return
        for sub_dir in images_dir.iterdir():
            if not sub_dir.is_dir():
                continue
            keep_dir = sub_dir / IMAGES_KEEP_FOLDER
            if not keep_dir.exists():
                continue
            for item in list(sub_dir.iterdir()):
                if item == keep_dir:
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                logging.info("Removed extra path: %s", item)
        QMessageBox.information(container, "清理成功", "已清理 images 目录多余内容")

    def create_spine_template() -> None:
        if not SPINE_TEMPLATE_SOURCE.exists():
            QMessageBox.warning(container, "操作失败", f"模板文件不存在: {SPINE_TEMPLATE_SOURCE}")
            return
        parent_name = spine_path.parent.name or "spine"
        target = spine_path / f"{parent_name}.spine"
        shutil.copyfile(SPINE_TEMPLATE_SOURCE, target)
        QMessageBox.information(container, "创建成功", f"已成功创建模板文件: {target}")

    btn_create_export = QPushButton("创建 spine-导出 文件夹", container)
    btn_create_export.clicked.connect(create_spine_export_folder)

    btn_copy_sequence = QPushButton("拷贝 序列帧 到 images", container)
    btn_copy_sequence.clicked.connect(copy_sequence_frames_to_images)

    btn_clean_images = QPushButton("清理 images", container)
    btn_clean_images.clicked.connect(clean_extra_image_folders)

    btn_create_template = QPushButton("创建 spine 模板", container)
    btn_create_template.clicked.connect(create_spine_template)

    return [
        btn_create_export,
        btn_copy_sequence,
        btn_clean_images,
        btn_create_template,
        _make_spacer(container),
    ]


def build_spine_export_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    spine_export_path = Path(full_folder)

    def create_json42_folder() -> None:
        target = spine_export_path / JSON42_FOLDER_NAME
        target.mkdir(exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {target}")

    btn_create_json42 = QPushButton("创建 json42 文件夹", container)
    btn_create_json42.clicked.connect(create_json42_folder)

    return [btn_create_json42, _make_spacer(container)]


def build_json42_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    source_path = Path(full_folder)

    btn_copy_json42 = QPushButton("拷贝 json42 文件夹到游戏项目怪物文件夹", container)
    monster_combo = QComboBox(container)
    monster_combo.setEditable(True)
    monster_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    monster_combo.setMaxVisibleItems(JSON42_HISTORY_LIMIT)
    monster_combo.setMaximumWidth(150)
    monster_combo.setMinimumWidth(100)

    history_values = _load_json42_history()

    def refresh_monster_combo(current_text: str) -> None:
        monster_combo.blockSignals(True)
        monster_combo.clear()
        if history_values:
            monster_combo.addItems(history_values)
        monster_combo.setCurrentText(current_text)
        monster_combo.blockSignals(False)

    default_monster = str(meta.get("monster_number", "") or "").strip()
    if not default_monster and history_values:
        default_monster = history_values[0]
    refresh_monster_combo(default_monster)

    line_edit = monster_combo.lineEdit()
    if line_edit is not None:
        line_edit.setPlaceholderText("怪物编号")
        line_edit.setClearButtonEnabled(True)

    def copy_json42_to_game() -> None:
        nonlocal history_values
        monster_number = monster_combo.currentText().strip()
        if not monster_number:
            QMessageBox.warning(container, "操作失败", "请填写怪物编号")
            return
        destination = GAME_MONSTER_BASE_PATH / f"jiangshi_{monster_number}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_path, destination, dirs_exist_ok=True)

        atlas_file = next((p for p in destination.iterdir() if p.suffix == ".atlas"), None)
        json_file = next((p for p in destination.iterdir() if p.suffix == ".json"), None)
        if atlas_file and json_file:
            target_json = atlas_file.with_suffix(".json")
            if target_json.exists():
                target_json.unlink()
            json_file.rename(target_json)
            logging.info("Renamed json file to match atlas: %s", target_json)

        QMessageBox.information(container, "拷贝成功", f"已成功拷贝 {source_path} 到 {destination}")
        os.startfile(str(destination))

        history_values = [item for item in history_values if item != monster_number]
        history_values.insert(0, monster_number)
        history_values = history_values[:JSON42_HISTORY_LIMIT]
        _save_json42_history(history_values)
        refresh_monster_combo(monster_number)

    btn_copy_json42.clicked.connect(copy_json42_to_game)

    return [btn_copy_json42, monster_combo, _make_spacer(container)]


def build_sequence_frames_widgets_parent(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    parent_path = Path(full_folder)

    def create_sequence_folder() -> None:
        target = parent_path / _build_sequence_folder_name(DEFAULT_FRAME_RATE, DEFAULT_SEQUENCE_TEMPLATE_TYPE)
        target.mkdir(exist_ok=True)
        logging.info("Created animation sequence folder at %s", target)
        QMessageBox.information(container, "创建成功", f"已成功创建 {target}")

    btn_create_sequence = QPushButton("创建 动画序列帧", container)
    btn_create_sequence.clicked.connect(create_sequence_folder)

    return [btn_create_sequence, _make_spacer(container)]


def build_video_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    video_path = Path(full_folder)

    def create_video_placeholder() -> None:
        target = video_path / _build_video_default_folder_name(video_path)
        target.mkdir(exist_ok=True)
        logging.info("Created video placeholder folder at %s", target)
        QMessageBox.information(container, "创建成功", f"已成功创建 {target}")
    btn_create_placeholder = QPushButton("创建视频占位符文件夹", container)
    btn_create_placeholder.clicked.connect(create_video_placeholder)
    return [btn_create_placeholder, _make_spacer(container)]


def get_folder_next_counter(folder_path: Path) -> int:
    max_counter = 0
    for item in folder_path.iterdir():
        if not item.is_dir():
            continue
        # 如果 item 不是 文件夹，跳过
        if not item.is_dir():
            continue
        match = re.search(r".*-(\d+)$", item.name)
        if match:
            try:
                counter = int(match.group(1))
                if counter > max_counter:
                    max_counter = counter
            except ValueError:
                continue
    return max_counter + 1

def build_reference_images_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    ref_path = Path(full_folder)
    # 创建参考图占位符文件夹
    btn_create_ref_placeholder = QPushButton("创建参考图占位符文件夹", container)
    def on_create_ref_placeholder_clicked() -> None:
        counter = get_folder_next_counter(ref_path)
        draw_platform_name = "未知平台"
        creature_name = "未知生物"
        # 获取 参考图上一级的文件夹名称，作为 生物名称
        parent_name = ref_path.parent.name
        if parent_name:
            creature_name = parent_name
            # 如果 生物名称 包含 '-'，取第一个部分
            if '-' in parent_name:
                creature_name = parent_name.split('-', 1)[0]
        folder_name = f"{draw_platform_name}-{creature_name}-{counter}"
        target = ref_path / folder_name
        target.mkdir(exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {target}")
    btn_create_ref_placeholder.clicked.connect(on_create_ref_placeholder_clicked)
    return [
        btn_create_ref_placeholder,
        _make_spacer(container)
    ]


def build_reference_drawings_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    ref_path = Path(full_folder)
    # 1.0 编辑参考图文件夹的名称
    btn_rename_ref_folder = QPushButton("重命名参考图文件夹", container)
    label_name_platform = QLabel("平台", container)
    line_edit_name = QLineEdit(container)
    line_edit_name.setPlaceholderText("请输入平台名称")
    label_name_creature = QLabel("生物", container)
    line_edit_creature = QLineEdit(container)
    line_edit_creature.setPlaceholderText("请输入生物名称")
    counter = 1
    # 正则匹配
    pattern = re.compile(r"^(?P<platform>[^-]+)-(?P<creature>[^-]+)-(?P<counter>\d+)$")
    match = pattern.match(ref_path.name)
    if match:
        line_edit_name.setText(match.group("platform"))
        line_edit_creature.setText(match.group("creature"))
        counter = int(match.group("counter")) if match.group("counter").isdigit() else 1
    def on_rename_ref_folder_clicked() -> None:
        platform_name = line_edit_name.text().strip() or "未知平台"
        creature_name = line_edit_creature.text().strip() or "未知生物"
        new_folder_name = f"{platform_name}-{creature_name}-{counter}"
        shutil.move(str(ref_path), str(ref_path.parent / new_folder_name))
    btn_rename_ref_folder.clicked.connect(on_rename_ref_folder_clicked)
    
    # 2.0 优化文件夹内的图片名称
    btn_optimize_ref_images = QPushButton("优化参考图文件名", container)
    def on_optimize_ref_images_clicked() -> None:
        tab_id = _resolve_tab_id(container)
        if not tab_id:
            logging.debug("缺少 tab_id，无法发送优化参考图名称请求: %s", ref_path)
            return
        signal_manager.optimize_reference_image_filenames.emit(tab_id, str(ref_path))
    btn_optimize_ref_images.clicked.connect(on_optimize_ref_images_clicked)
    
    # 3.0 复制文件夹名称，并新建 counter + 1 的文件夹
    btn_copy_ref_folder = QPushButton("复制参考图文件夹", container)
    if match:
        btn_copy_ref_folder.setEnabled(True)
        def on_copy_ref_folder_clicked() -> None:
            counter_2 = get_folder_next_counter(ref_path.parent)
            new_folder_name = f"{match.group('platform')}-{match.group('creature')}-{counter_2}"
            target = ref_path.parent / new_folder_name
            os.makedirs(target, exist_ok=True)
            QMessageBox.information(container, "创建成功", f"已成功创建 {target}")
        btn_copy_ref_folder.clicked.connect(on_copy_ref_folder_clicked)
    else:
        btn_copy_ref_folder.setEnabled(False)   
        
    # 4.0 按时间序列，重命名参考图文件
    btn_rename_file_folder = QPushButton("时间序列重命名", container)
    def on_rename_ref_folder_clicked() -> None:
        # 前提是 图片, jpeg, png, jfif 等文件名
        # 遍历文件夹内的图片文件，按修改时间排序，然后重命名为 202511-21-114259-01.png, 202511-21-114259-02.png ...
        list_of_images = []
        for item in ref_path.iterdir():
            if item.is_file() and item.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".jfif"}:
                list_of_images.append(item)
        list_of_images.sort(key=lambda x: x.stat().st_mtime)
        year_month_str = f"{time.strftime('%Y%m')}"
        day_str = f"{time.strftime('%d')}"
        time_str = f"{time.strftime('%H%M%S')}"
        filename_suffix_str = f'{year_month_str}-{day_str}-{time_str}'
        ext_rage = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".jfif"]
        file_counter = 1
        for index, image_path in enumerate(list_of_images, start=1):
            ext = image_path.suffix.lower()
            if ext not in ext_rage:
                continue
            new_filename = f"{filename_suffix_str}-{file_counter:02d}{ext}"
            new_filepath = ref_path / new_filename
            image_path.rename(new_filepath)
            file_counter += 1
        signal_manager.gui_fresh_tab_collect_metadata.emit(_resolve_tab_id(container) or "")
        QMessageBox.information(container, "重命名完成", f"已完成按时间序列重命名参考图文件，共重命名 {file_counter - 1} 个文件。")           
    btn_rename_file_folder.clicked.connect(on_rename_ref_folder_clicked)
    return [
        btn_rename_ref_folder,
        label_name_platform,
        line_edit_name,
        label_name_creature,
        line_edit_creature,
        btn_optimize_ref_images,
        btn_copy_ref_folder,
        btn_rename_file_folder,
        _make_spacer(container)
    ]


__all__ = [
    "CustomWidgetBuilder",
    "resolve_custom_widget_builder",
    "build_sequence_frames_widgets",
    "build_spine_widgets",
    "build_spine_export_widgets",
    "build_json42_widgets",
    "build_sequence_frames_widgets_parent",
    "build_video_widgets",
]
