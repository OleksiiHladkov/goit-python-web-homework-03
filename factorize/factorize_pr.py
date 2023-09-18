from multiprocessing import Pool, cpu_count
import logging
from time import time


logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def factorize(number) -> list[int]:
    result = []
    
    for div in range(1, number+1):
        if number % div == 0:
            result.append(div)
        
    return result


def callback(result):
    for i in result:
        logger.debug(i)



if __name__ == "__main__":
    start_time = time()
    
    with Pool(cpu_count()) as pool:
        # try to use map sync
        # result = pool.map(factorize, (128, 255, 99999, 10651060))
        # for i in result:
        #     logger.debug(i)
        
        # try to use map async
        pool.map_async(factorize, (128, 255, 99999, 10651060), callback=callback)
        pool.close()
        pool.join()

    logger.debug(f"Execution time is {time() - start_time} sec")