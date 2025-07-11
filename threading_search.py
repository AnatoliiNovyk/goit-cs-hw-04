import threading
import time
from collections import defaultdict
from pathlib import Path
import os

# --- Функція для пошуку ключових слів у файлі ---
def search_in_file(file_path, keywords, results):
    """
    Шукає ключові слова у вказаному файлі та зберігає результати.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    # Використовуємо блокування для безпечного доступу до спільного ресурсу
                    with lock:
                        results[keyword].append(str(file_path))
    except (IOError, OSError) as e:
        print(f"Помилка при обробці файлу {file_path}: {e}")
    except Exception as e:
        print(f"Невідома помилка при роботі з файлом {file_path}: {e}")

# --- Розподіл роботи між потоками ---
def thread_worker(files, keywords, results):
    """
    Цільова функція для потоку, що обробляє свою частину файлів.
    """
    for file in files:
        search_in_file(file, keywords, results)

# --- Головна функція для багатопотокового підходу ---
def main_threading(source_dir, keywords):
    """
    Організовує багатопотоковий пошук ключових слів у файлах.
    """
    start_time = time.time()
    
    file_paths = [p for p in Path(source_dir).rglob('*') if p.is_file()]
    if not file_paths:
        print("У вказаній директорії файли не знайдені.")
        return {}

    num_threads = os.cpu_count() or 4 # Використовуємо кількість ядер CPU або 4 потоки
    threads = []
    results = defaultdict(list)
    files_per_thread = (len(file_paths) + num_threads - 1) // num_threads

    global lock
    lock = threading.Lock()

    for i in range(num_threads):
        start_index = i * files_per_thread
        end_index = start_index + files_per_thread
        thread_files = file_paths[start_index:end_index]
        
        if thread_files:
            thread = threading.Thread(target=thread_worker, args=(thread_files, keywords, results))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    execution_time = time.time() - start_time
    print(f"Час виконання багатопотокової версії: {execution_time:.4f} секунд.")
    return dict(results)

if __name__ == '__main__':
    # Створення тестових файлів для демонстрації
    source_directory = "test_files"
    Path(source_directory).mkdir(exist_ok=True)
    with open(f"{source_directory}/file1.txt", "w", encoding="utf-8") as f:
        f.write("Python є потужною мовою програмування.")
    with open(f"{source_directory}/file2.txt", "w", encoding="utf-8") as f:
        f.write("Java також популярна, але Python простіший.")
    with open(f"{source_directory}/file3.txt", "w", encoding="utf-8") as f:
        f.write("Вивчаємо паралелізм з Python.")

    keywords_to_search = ["Python", "Java"]
    
    print("--- Запуск багатопотокового пошуку ---")
    threading_results = main_threading(source_directory, keywords_to_search)
    print("\nРезультати:")
    print(threading_results)
