import logging
from time import time


def execution_time(func):
    def inner(*args, **kwargs):
        timer = time()

        result = func(*args, *kwargs)

        logging.debug(f"Execution time of '{func.__name__}' is {time() - timer} sec")

        return result

    return inner

@execution_time
def factorize(*numbers) -> list[int]:
    result = []

    if not len(numbers):
        return result
    
    for num in numbers:
        div_list = []

        for div in range(1, num+1):
            if num % div == 0:
                div_list.append(div)
        
        result.append(div_list)

    return result



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    for i in factorize(128, 255, 99999, 10651060):
        logging.debug(i)

    # a, b, c, d  = factorize(128, 255, 99999, 10651060)

    # assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    # assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    # assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    # assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]