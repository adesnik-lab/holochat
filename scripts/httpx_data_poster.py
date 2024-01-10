import httpx
import uvicorn
import functools
from threading import Thread
import time

from holochat.main import app

run_fxn = functools.partial(uvicorn.run, app, host="localhost", port=8000)

print('Starting server on another thread...')
thread = Thread(target=run_fxn, daemon=True)
thread.start()
time.sleep(3)
print('Server started...\n')

for i in range(4):
    httpx.post(
        'http://localhost:8000/msg/si', 
        json={"message": f"scanimage test message number {i}."}
    )

httpx.get(
    'http://localhost:8000/msg/si'
)
    
httpx.post(
    'http://localhost:8000/msg/daq', 
    json={"message": "daq test message."}
)

httpx.post(
    'http://localhost:8000/msg/ptb', 
    json={"message": "ptb test message."}
)
time.sleep(3)
httpx.get(
    'http://localhost:8000/msg/ptb'
)

httpx.post(
    'http://localhost:8000/msg/holo',
    json={"message": "holo test message."}
)

print('POSTs complete.')
print('Joined server thread.')
thread.join()