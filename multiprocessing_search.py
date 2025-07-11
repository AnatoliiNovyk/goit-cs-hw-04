import multiprocessing
import time
from collections import defaultdict
from pathlib import Path
import os

# --- Функція для пошуку ключових слів у файлі ---
def search_in_file(file_path, keywords, queue):
    """
    Шукає ключові слова у файлі та відправляє результати в чергу.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for keyword in keywords:
                if keyword in content:
                    queue.put((keyword, str(file_path)))
    except (IOError, OSError) as e:
        print(f"Помилка при обробці файлу {file_path}: {e}")
    except Exception as e:
        print(f"Невідома помилка при роботі з файлом {file_path}: {e}")

# --- Розподіл роботи між процесами ---
def process_worker(files, keywords, queue):
    """
    Цільова функція для процесу, що обробляє свою частину файлів.
    """
    for file in files:
        search_in_file(file, keywords, queue)

# --- Головна функція для багатопроцесорного підходу ---
def main_multiprocessing(source_dir, keywords):
    """
    Організовує багатопроцесорний пошук ключових слів у файлах.
    """
    start_time = time.time()
    
    file_paths = [p for p in Path(source_dir).rglob('*') if p.is_file()]
    if not file_paths:
        print("У вказаній директорії файли не знайдені.")
        return {}
    
    num_processes = os.cpu_count() or 4
    processes = []
    queue = multiprocessing.Queue()
    results = defaultdict(list)
    files_per_process = (len(file_paths) + num_processes - 1) // num_processes

    for i in range(num_processes):
        start_index = i * files_per_process
        end_index = start_index + files_per_process
        process_files = file_paths[start_index:end_index]

        if process_files:
            process = multiprocessing.Process(target=process_worker, args=(process_files, keywords, queue))
            processes.append(process)
            process.start()

    for process in processes:
        process.join()

    # Збір результатів з черги
    while not queue.empty():
        keyword, file_path = queue.get()
        results[keyword].append(file_path)

    execution_time = time.time() - start_time
    print(f"Час виконання багатопроцесорної версії: {execution_time:.4f} секунд.")
    return dict(results)

if __name__ == '__main__':
    # Створення тестових файлів (аналогічно до попереднього скрипта)
    source_directory = "test_files"
    Path(source_directory).mkdir(exist_ok=True)
    with open(f"{source_directory}/file1.txt", "w", encoding="utf-8") as f:
        f.write("Python є потужною мовою програмування.")
    with open(f"{source_directory}/file2.txt", "w", encoding="utf-8") as f:
        f.write("Java також популярна, але Python простіший.")
    with open(f"{source_directory}/file3.txt", "w", encoding="utf-8") as f:
        f.write("Вивчаємо паралелізм з Python.")
    
    keywords_to_search = ["Python", "Java"]

    print("\n--- Запуск багатопроцесорного пошуку ---")
    multiprocessing_results = main_multiprocessing(source_directory, keywords_to_search)
    print("\nРезультати:")
    print(multiprocessing_results)
