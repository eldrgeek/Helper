from pynput import mouse
from pynput import keyboard
import time
import threading

# Change to synchronous client
def on_press (key) :
    try:
        print( 'alphanumeric key {0} pressed'. format (key.char ))
        return
    except AttributeError:
        print('special key {0} pressed'. format (key) )
        return

def on_click(x, y, button, pressed):
    print('{0} at {1}'. format ( 'Pressed' if pressed else 'Released', (x, y)))

def on_release (key):
    print ('{0} released'. format (key) )

def send_heartbeat():
    while True:
        print("I am here")
        time.sleep(1)

listener = keyboard.Listener (
   on_press=on_press, 
   on_release=on_release)
listener.start()

mlistener = mouse.Listener (
    on_click=on_click)

mlistener.start()

print("started")

# Start the heartbeat thread
heartbeat_thread = threading.Thread(target=send_heartbeat)
heartbeat_thread.daemon = True  # Allows the thread to exit when the main program does
heartbeat_thread.start()

# Keep the program alive
listener.join()
mlistener.join()