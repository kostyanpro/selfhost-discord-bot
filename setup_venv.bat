@echo off

if not exist requirements.txt (
    echo Файл requirements.txt не найден в текущей директории.
    exit /b 1
)

echo create venv...
python -m venv winvenv

echo activate venv...
call winvenv\Scripts\activate.bat

echo installing libs from requirements.txt...
pip install -r requirements.txt -U

deactivate

echo thats all!