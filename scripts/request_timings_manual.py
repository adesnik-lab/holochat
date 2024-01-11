import time
import threading

import httpx



httpx.post('http://localhost:8000/msg/si', json={"message": "hello from si."})
httpx.post('http://localhost:8000/msg/ptb', json={"message": "hello from ptb."})

def repeated_gets():
    while True:
        httpx.get('http://localhost:8000/msg/si')
        time.sleep(0.2)
        
def timed_slow_gets():
    while True:
        start_time = time.perf_counter()
        httpx.get('http://localhost:8000/msg/ptb')
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f'GET request took {run_time:.3f}s')
        time.sleep(0.2)
        
# t = threading.Thread(target=repeated_gets, daemon=True)
t = threading.Thread(target=timed_slow_gets, daemon=True)
# t.start()
t.start()

print('GETs started.')

repeated_gets()
# timed_slow_gets()