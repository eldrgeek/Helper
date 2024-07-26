import pyautogui
import asyncio
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('Connection established')

@sio.event
async def disconnect():
    print('Disconnected from server')

async def connect_with_retries(url, retry_delay=2, error_interval=10):
    last_error_time = None
    while True:
        try:
            await sio.connect(url)
            await sio.wait()
            break
        except socketio.exceptions.ConnectionError as e:
            current_time = asyncio.get_event_loop().time()
            if last_error_time is None or current_time - last_error_time >= error_interval:
                print(f'Failed to connect: {e}. Retrying in {retry_delay} seconds...')
                last_error_time = current_time
            await asyncio.sleep(retry_delay)

async def main():
    await connect_with_retries('http://localhost:5000')

if __name__ == '__main__':
    asyncio.run(main())
