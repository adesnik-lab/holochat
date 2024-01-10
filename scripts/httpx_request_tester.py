import time
import httpx
import rich
from threading import Thread
import uvicorn
import functools
import sys

from holochat.main import app

run_fxn = functools.partial(uvicorn.run, app, host="localhost", port=8000)

print('Starting server on another thread...')
thread = Thread(target=run_fxn, daemon=True)
thread.start()
time.sleep(3)
print('Server started...\n')

r = httpx.get('http://localhost:8000/')
print(r)
rich.print_json(r.text)

r = httpx.post(
    'http://localhost:8000/msg/pc1', 
    json={"message": "Hello, Adesnik Lab."}
)
print(r)
rich.print_json(r.text)

r = httpx.post(
    'http://localhost:8000/msg/pc2', 
    json={"message": "Holography is fun."}
)
print(r)
rich.print_json(r.text)

r = httpx.post(
    'http://localhost:8000/msg/pc3', 
    json={"message": "Should be unaccessed."}
)
print(r)
rich.print_json(r.text)

time.sleep(1)
r = httpx.get(
    'http://localhost:8000/msg/pc1'
)
print(r)
rich.print_json(r.text)

time.sleep(2)
r = httpx.get(
    'http://localhost:8000/msg/pc2'
)
print(r)
rich.print_json(r.text)

time.sleep(3)
r = httpx.get(
    'http://localhost:8000/msg/pc2'
)
print(r)
rich.print_json(r.text)

r = httpx.post(
    'http://localhost:8000/msg/pc2', 
    json={"message": "SSTs are my favorite neuron."}
)
print(r)
rich.print_json(r.text)

time.sleep(12)
r = httpx.get(
    'http://localhost:8000/msg/pc2'
)
print(r)
rich.print_json(r.text)

r = httpx.get(
    'http://localhost:8000/msg/pc2'
)
print(r)
rich.print_json(r.text)

r = httpx.get(
    'http://localhost:8000/msg/latest'
)
print(r)
rich.print_json(r.text)


# stop the server thread
print('Stopping server...')
sys.exit(4) # this is a hacky way to stop the server thread