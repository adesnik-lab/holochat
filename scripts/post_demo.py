import httpx
import time

ROOT_URL = 'http://localhost:8000'

for i in range(8):
    httpx.post(
        f'{ROOT_URL}/msg/si', 
        json={"message": f"scanimage test message number {i}."}
    )
    time.sleep(0.1)
    if i < 5:
        httpx.get(f'{ROOT_URL}/msg/si')

time.sleep(1)    
for i in range(3):
    httpx.post(
        f'{ROOT_URL}/msg/daq', 
        json={"message": f"daq test message number {i}."}
    )

time.sleep(1)     
for i in range(5):
    httpx.post(
        f'{ROOT_URL}/msg/ptb', 
        json={"message": f"ptb test message number {i}."}
    )

time.sleep(1)     
for i in range(10):
    httpx.post(
        f'{ROOT_URL}/msg/holo', 
        json={"message": f"holo test message number {i}."}
    )
    time.sleep(0.1) 
    if i > 5:
        httpx.get(f'{ROOT_URL}/msg/holo')

time.sleep(1)    
httpx.post(
    f'{ROOT_URL}/config/daq', 
    json={
        "retloc": [8,5],
        "mouse_name": "will hendricks"
    }
)

while True:
    input('waiting for you to press enter...')
    httpx.delete(f'{ROOT_URL}/db')
    time.sleep(1)
    httpx.post(
        f'{ROOT_URL}/msg/si',
        json={"message": "new scanimage test message.", "sender":"si"}
    )