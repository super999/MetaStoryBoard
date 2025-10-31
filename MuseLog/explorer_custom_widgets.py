import logging
import os
import re
import shutil
from typing import Any, Dict, Optional, Sequence, Callable
from MuseLog.explorer_signals import signal_manager
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QSizePolicy, QMessageBox

CustomWidgetBuilder = Callable[[QWidget, str, Dict[str, Any]], Sequence[QWidget]]


def resolve_custom_widget_builder(folder: str, meta: Dict[str, Any]) -> Optional[CustomWidgetBuilder]:
    parent_dir_name = os.path.basename(os.path.dirname(os.path.normpath(folder)))
    folder_name = os.path.basename(os.path.normpath(folder))
    if parent_dir_name == "序列帧":
        return build_sequence_frames_widgets
    if folder_name.lower() == "spine":
        return build_spine_widgets
    if folder_name.lower() == "序列帧":
        return build_sequence_frames_widgets_parent
    if folder_name.lower() == "spine-导出":
        return build_spine_export_widgets
    if folder_name.lower() == "json42":
        return build_json42_widgets
    return None


ALL_ANIMATION_TYPES = ["走路", "待机", "死亡", "攻击"]


def build_sequence_frames_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    folder_name = os.path.basename(os.path.normpath(full_folder))
    frame_rate = 4  # 默认帧率
    animation_type = "待机"  # 默认动画类型
    # folder 格式如： (秒抽8帧)-攻击
    # 分析 folder 中 的 帧率
    pattern_frame_rate = r"(\d+)帧"
    frame_rate_match = re.search(pattern_frame_rate, folder_name)
    if frame_rate_match:
        frame_rate = int(frame_rate_match.group(1))
    # 分析 folder 中 的 动画类型
    pattern_animation_type = r"-(\S+)$"
    animation_type_match = re.search(pattern_animation_type, folder_name)
    if animation_type_match:
        animation_type = animation_type_match.group(1)
    # 尝试从 folder 名称中提取动画类型

    btn_modify_frame_rate = QPushButton("修改帧率", container)
    input_frame_rate = QLineEdit(container)
    input_frame_rate.setMaximumWidth(60)
    input_frame_rate.setText(str(frame_rate))
    # 绑定 按钮 事件
    def on_modify_frame_rate_clicked():
        new_frame_rate_str = input_frame_rate.text().strip()
        if not new_frame_rate_str.isdigit():
            QMessageBox.warning(container, "输入错误", "请输入有效的帧率（正整数）")
            return
        new_frame_rate = int(new_frame_rate_str)
        # 重命名文件夹
        parent_dir = os.path.dirname(full_folder)
        new_folder_name = re.sub(r"\(\S+?帧\)", f"(秒抽{new_frame_rate}帧)", folder_name)
        new_full_folder = os.path.join(parent_dir, new_folder_name)
        # 发送信号通知更新
        signal_manager.rename_folder.emit(full_folder, new_full_folder)        
    btn_modify_frame_rate.clicked.connect(on_modify_frame_rate_clicked)
    
    btn_modify_animation_type = QPushButton("修改动画类型", container)
    combo_animation_type = QComboBox(container)
    
    combo_animation_type.addItems(ALL_ANIMATION_TYPES)
    if animation_type in ALL_ANIMATION_TYPES:
        pass
    else:
        combo_animation_type.addItem(animation_type)
    combo_animation_type.setCurrentText(animation_type)
    # combo_animation_type 默认太短， 设置最小宽度
    combo_animation_type.setMinimumWidth(100)
    # 绑定动画类型修改事件
    def on_modify_animation_type_clicked():
        new_animation_type = combo_animation_type.currentText()
        # 重命名文件夹
        parent_dir = os.path.dirname(full_folder)
        new_folder_name = f"(秒抽{frame_rate}帧)-{new_animation_type}"
        new_full_folder = os.path.join(parent_dir, new_folder_name)
        # 发送信号通知更新
        signal_manager.rename_folder.emit(full_folder, new_full_folder)
    btn_modify_animation_type.clicked.connect(on_modify_animation_type_clicked)
    
    btn_delete_animation_sequence = QPushButton("删除选中的动画", container)

    def on_delete_animation_sequence_clicked():
        # 弹框确认删除
        reply = QMessageBox.question(container, "确认删除", "您确定要删除选中的动画吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 发送删除信号，这里假设有一个全局的信号管理器 signal_manager
            signal_manager.delete_selected_animation_sequence.emit()
    btn_delete_animation_sequence.clicked.connect(on_delete_animation_sequence_clicked)
    # 最后加一个 spacer
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [
        btn_modify_frame_rate,
        input_frame_rate,
        btn_modify_animation_type,
        combo_animation_type,
        btn_delete_animation_sequence,
        spacer,
    ]


def build_spine_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    btn_create_spine_export = QPushButton("创建 spine-导出 文件夹", container)
    def on_create_spine_export_clicked():
        parent_dir = os.path.dirname(full_folder)
        spine_export_folder = os.path.join(parent_dir, "spine-导出")
        os.makedirs(spine_export_folder, exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {spine_export_folder}")
    btn_create_spine_export.clicked.connect(on_create_spine_export_clicked)
    #  拷贝 序列帧 到 images
    btn_copy_sequence_frames = QPushButton("拷贝 序列帧 到 images", container)
    def on_copy_sequence_frames_clicked():
        logging.info(f"Copying sequence frames to images folder at: {full_folder}")
        parent_dir = os.path.dirname(full_folder)
        sequence_frames_source_folder = os.path.join(parent_dir, "序列帧")
        images_folder = os.path.join(full_folder, "images")
        # 先创建 images 文件夹
        os.makedirs(images_folder, exist_ok=True)
        shutil.copytree(sequence_frames_source_folder, images_folder, dirs_exist_ok=True)        
        QMessageBox.information(container, "操作成功", f"已成功将序列帧拷贝到 {images_folder}")
    btn_copy_sequence_frames.clicked.connect(on_copy_sequence_frames_clicked)
    # 清理 images 里 多余的文件夹， 格式如： spine\images\XXX\preds-BiRefNet_resize, 若 XXX 下有多个文件夹， 且有preds-BiRefNet_resize， 则删除 同级下的 其他文件夹和文件
    btn_clean_extra_folders = QPushButton("清理 images", container)
    def on_clean_extra_folders_clicked():
        images_dir = os.path.join(full_folder, "images")
        if not os.path.exists(images_dir):
            QMessageBox.warning(container, "操作失败", f"{images_dir} 不存在")
            return
        for item in os.listdir(images_dir):
            item_path = os.path.join(images_dir, item)
            if os.path.isdir(item_path):
                subfolders = os.listdir(item_path)
                preds_folder = 'preds-BiRefNet_resize'
                if preds_folder in subfolders:
                    for f in subfolders:
                        if f != preds_folder:
                            folder_to_remove = os.path.join(item_path, f)
                            if os.path.isfile(folder_to_remove):
                                os.remove(folder_to_remove)
                            elif os.path.isdir(folder_to_remove):
                                shutil.rmtree(folder_to_remove)
                            logging.info(f"Removed extra folder: {folder_to_remove}")
        QMessageBox.information(container, "操作成功", "已清理 images 多余文件夹")
    btn_clean_extra_folders.clicked.connect(on_clean_extra_folders_clicked)
    # 创建 spine 模板， 从 D:\美术资源\spine角色\地球危机-模板\僵尸模板\ske-template-01.spine 拷贝到 spine 文件夹内，并重命名为 XXX.spine ， XXX 为 当前 spine 文件夹的上级文件夹名称
    btn_create_spine_template = QPushButton("创建 spine 模板", container)
    def on_create_spine_template_clicked():
        template_source_path = r"D:\\美术资源\\spine角色\\地球危机-模板\\僵尸模板\\ske-template-01.spine"
        if not os.path.exists(template_source_path):
            QMessageBox.warning(container, "操作失败", f"模板文件不存在: {template_source_path}")
            return
        parent_dir_name = os.path.basename(os.path.dirname(full_folder))
        template_dest_path = os.path.join(full_folder, f"{parent_dir_name}.spine")
        shutil.copyfile(template_source_path, template_dest_path)
        QMessageBox.information(container, "创建成功", f"已成功创建模板文件: {template_dest_path}")
    btn_create_spine_template.clicked.connect(on_create_spine_template_clicked)    
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [btn_create_spine_export, btn_copy_sequence_frames, btn_clean_extra_folders, btn_create_spine_template, spacer]

def build_spine_export_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    # 创建 json42 按钮
    btn_create_spine_export = QPushButton("创建 json42 文件夹", container)
    def on_create_spine_export_clicked():
        json42_folder = os.path.join(full_folder, "json42")
        os.makedirs(json42_folder, exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {json42_folder}")
    btn_create_spine_export.clicked.connect(on_create_spine_export_clicked)
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [btn_create_spine_export, spacer]

def build_json42_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    # 拷贝 json42 文件夹 到 游戏项目的怪物文件夹下 如 D:\cocos_workspace\oops-game-kit\assets\resources-spine\art-spine\monsters\jiangshi_08
    btn_copy_json42_file = QPushButton("拷贝 json42 文件夹 到 游戏项目怪物文件夹", container)
    input_game_monster_number = QLineEdit(container) # 怪物编号输入框
    input_game_monster_number.setMaximumWidth(100)
    base_game_monster_path = r"D:\\cocos_workspace\\oops-game-kit\\assets\\resources-spine\\art-spine\\monsters"
    monster_folder_name = f'jiangshi_{meta.get("monster_number", "00")}'
    def on_copy_json42_file_clicked():
        game_monster_number = input_game_monster_number.text().strip()
        if not game_monster_number:
            QMessageBox.warning(container, "操作失败", "请填写怪物编号")
            return
        source_folder = full_folder
        dest_folder = os.path.join(base_game_monster_path, f"jiangshi_{game_monster_number}")
        shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
        # 修改 xx.json 为 .atlas 同名的文件名
        all_files = os.listdir(dest_folder)
        # 查找 .atlas 文件
        atlas_file = None
        for f in all_files:
            if f.endswith('.atlas'):
                atlas_file = f
                break
        # 修改同名的 .json 文件
        json_file = None
        for f in all_files:
            if f.endswith('.json'):
                json_file = f
                break
        if atlas_file and json_file:
            new_json_file_name = atlas_file.replace('.atlas', '.json')
            old_json_file_path = os.path.join(dest_folder, json_file)
            new_json_file_path = os.path.join(dest_folder, new_json_file_name)
            os.rename(old_json_file_path, new_json_file_path)
            logging.info(f"Renamed {old_json_file_path} to {new_json_file_path}")
        QMessageBox.information(container, "拷贝成功", f"已成功拷贝 {source_folder} 到 {dest_folder}")
        # 弹出资源管理器打开目标文件夹
        os.startfile(dest_folder)
    btn_copy_json42_file.clicked.connect(on_copy_json42_file_clicked)
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [btn_copy_json42_file, input_game_monster_number, spacer]

def build_sequence_frames_widgets_parent(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    btn_create_animation_sequence = QPushButton("创建 动画序列帧", container)

    def on_create_animation_sequence_clicked():
        # (秒抽XX帧)-YY
        frame_rate = 4  # 默认帧率
        animation_type = "空白"  # 默认动画类型
        animation_sequence_folder_name = f"(秒抽{frame_rate}帧)-{animation_type}"
        animation_sequence_folder = os.path.join(full_folder, animation_sequence_folder_name)
        logging.info(f"Creating animation sequence folder at: {animation_sequence_folder}")
        os.makedirs(animation_sequence_folder, exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {animation_sequence_folder}")

    btn_create_animation_sequence.clicked.connect(on_create_animation_sequence_clicked)

    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [btn_create_animation_sequence, spacer]


__all__ = [
    "CustomWidgetBuilder",
    "resolve_custom_widget_builder",
    "build_sequence_frames_widgets",
    "build_spine_widgets",

]
