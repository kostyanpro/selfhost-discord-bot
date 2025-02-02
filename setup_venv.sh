if [ ! -f "requirements.txt" ]; then
  echo "Файл requirements.txt не найден в текущей директории."
  exit 1
fi

echo "create venv..."
python3 -m venv linuxvenv

echo "activate venv..."
source linuxvenv/bin/activate

echo "installing libs from requirements.txt..."
pip install -r requirements.txt -U

deactivate

echo "thats all!"