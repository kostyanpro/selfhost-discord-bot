if [ ! -f "requirements.txt" ]; then
  echo "Файл requirements.txt не найден в текущей директории."
  exit 1
fi

echo "create venv..."
python3 -m venv linuxvenv

echo "activate venv..."
source linuxvenv/bin/activate

echo "installing libs from requirements.txt..."
pip install --upgrade -r requirements.txt

deactivate

echo "thats all!"