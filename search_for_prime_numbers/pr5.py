import multiprocessing
import time
from datetime import datetime


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def find_primes(start, end, result_queue):
    primes = []
    for num in range(start, end + 1):
        if is_prime(num):
            primes.append(num)
    result_queue.put(primes)


def save_worker(result_queue, stop_event):
    saved_count = 0
    file_count = 0
    while not stop_event.is_set() or not result_queue.empty():
        if not result_queue.empty():
            primes = result_queue.get()
            if primes:  # Сохраняем только если есть результаты
                filename = f"primes_result_{file_count}.txt"
                with open(filename, 'w') as f:
                    f.write("\n".join(map(str, primes)))
                saved_count += len(primes)
                file_count += 1
                print(f"Сохранено {len(primes)} чисел в {filename}")
        else:
            time.sleep(0.1)
    print(f"Всего сохранено {saved_count} простых чисел в {file_count} файлах")


if __name__ == '__main__':
    print("Поиск простых чисел с использованием многопроцессорности")
    n = int(input("Введите число, до которого искать простые числа: "))

    max_processes = multiprocessing.cpu_count()
    print(f"Доступно ядер процессора: {max_processes}")

    p_count = int(input(f"Сколько процессов использовать (1-{max_processes}): "))
    p_count = max(1, min(p_count, max_processes))

    result_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    saver = multiprocessing.Process(
        target=save_worker,
        args=(result_queue, stop_event)
    )
    saver.start()

    step = (n - 1) // p_count
    start = 2
    processes = []

    for i in range(p_count):
        end = start + step
        if i == p_count - 1:
            end = n
        p = multiprocessing.Process(
            target=find_primes,
            args=(start, end, result_queue)
        )
        processes.append(p)
        p.start()
        start = end + 1

    for p in processes:
        p.join()

    stop_event.set()
    saver.join()

    all_primes = []
    while not result_queue.empty():
        all_primes.extend(result_queue.get())

    if all_primes:
        all_primes.sort()
        print("\nИтоговые результаты:")
        print(f"Всего найдено {len(all_primes)} простых чисел")
        print("Первые 10:", all_primes[:10])
        print("Последние 10:", all_primes[-10:])
    else:
        print("Простые числа не найдены")