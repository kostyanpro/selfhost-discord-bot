import os
import shutil

source_file = "yandexmusic.py"

target_path = os.path.join("..", "winvenv", "Lib", "site-packages", "yt_dlp", "extractor", "yandexmusic.py")

def patch():
    if not os.path.exists(source_file):
        print(f"[-] Ошибка: Файл '{source_file}' не найден в папке yandexMusicPatch!")
        return

    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        print(f"[-] Ошибка: Путь не найден: {target_dir}")
        print("[!] Проверьте, что папка yandexPatch находится в той же директории, что и winvenv")
        return

    try:
        if os.path.exists(target_path):
            backup_path = target_path + ".bak"
            shutil.copy2(target_path, backup_path)
            print(f"[+] Создан бэкап оригинала: {backup_path}")

        # 4. Копируем новый файл
        shutil.copy2(source_file, target_path)
        print(f"[***] УСПЕХ! Файл {source_file} успешно заменен по пути:")
        print(f"      {os.path.abspath(target_path)}")

    except Exception as e:
        print(f"[-] Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    patch()
    input("\nНажмите Enter, чтобы выйти...")