@echo off
REM �л����ű�����Ŀ¼����֤���·����ȷ
cd /d "%~dp0"

REM �������� ui Ŀ¼������ .ui �ļ���ֻ���� ui_ ǰ׺����
for %%f in (*.ui) do (
  echo ���ڱ��� %%f ...
  if exist "%%~nf_ui.py" del "%%~nf_ui.py"
  pyside6-uic "%%~f" -o "ui_%%~nf.py"
)

echo ������ɣ�
