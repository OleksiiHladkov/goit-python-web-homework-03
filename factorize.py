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
    # logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    
    for i in factorize(128, 255, 99999, 10651060):
        logging.debug(i)