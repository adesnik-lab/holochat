import functools
import threading
import time

import httpx
import uvicorn


run_fxn = functools.partial(uvicorn.run, 'holochat.main:app', host="localhost", 
                            port=8000, log_level='warning')

print('Starting server on another thread...')
thread = threading.Thread(target=run_fxn, daemon=True)
thread.start()
time.sleep(5)
print('Server started...\n')

httpx.post('http://localhost:8000/msg/si', json={"message": "hello from si."})
httpx.post('http://localhost:8000/msg/ptb', json={"message": "hello from ptb."})

def repeated_gets():
    while True:
        httpx.get('http://localhost:8000/msg/si')
        time.sleep(0.1)
        
def timed_slow_gets():
    while True:
        start_time = time.perf_counter()
        httpx.get('http://localhost:8000/msg/ptb')
        end_time = time.perf_counter()
        run_time = end_time - start_time
        with threading.Lock():
            print(f'GET request took {run_time:.3f}s')
        time.sleep(0.1)
        
t1 = threading.Thread(target=repeated_gets, daemon=True)
t2 = threading.Thread(target=timed_slow_gets, daemon=True)
t1.start()
t2.start()

print('GETs started.')
print('Rejoining server thread.')
thread.join()