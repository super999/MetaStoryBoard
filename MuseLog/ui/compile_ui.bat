@echo off
REM 批量编译 ui 目录下所有 .ui 文件
for %%f in (*.ui) do (
  echo 正在编译 %%f ...
  pyside6-uic "%%~f" -o "ui_%%~nf.py"
)
echo 编译完成！
pause
