@echo off
REM �������� ui Ŀ¼������ .ui �ļ�
for %%f in (*.ui) do (
  echo ���ڱ��� %%f ...
  pyside6-uic "%%~f" -o "ui_%%~nf.py"
)
echo ������ɣ�
pause
