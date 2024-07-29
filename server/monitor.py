from pynput import mouse
from pynput import keyboard
import time
import threading
import tkinter as tk  # Import tkinter for message boxes
import tkinter.messagebox as messagebox  # Import messagebox explicitly
import os
from pynput.keyboard import Key  # Import Key for special keys

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
        time.sleep(10) 

def read_tasks():
    with open('tasks.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]

def write_ui_action(action):
    with open('uiactions.txt', 'a') as f:
        f.write(action + '\n')

def show_task_and_log(task):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Make the window stay on top
    messagebox.showinfo("Task", task)  # Show message box
    write_ui_action(f'##task {task}')  # Log the task

tasks = read_tasks()
task_index = 0

# Modify on_press and on_release to log key events
key_buffer = []

shift_pressed = False  # Flag to track if Shift is pressed

charsdown = []  # Array to track currently pressed character keys

def on_press(key):
    global key_buffer, shift_pressed, charsdown
    if key == Key.shift:
        shift_pressed = True
        return  # Do not log shift press
    try:
        char = key.char.upper() if shift_pressed else key.char
        charsdown.append(char)  # Add to charsdown
        key_buffer.append(char)
        print('alphanumeric key {0} pressed'.format(char))
    except AttributeError:
        # Emit contents of key_buffer before processing special key
        if key_buffer:
            write_ui_action(f'type {"".join(key_buffer)}')
            key_buffer.clear()
        print('special key {0} pressed'.format(key))
        write_ui_action(f'press {key}')

def on_release(key):
    global key_buffer, shift_pressed, charsdown
    if key == Key.shift:
        shift_pressed = False
        return  # Do not log shift release
    if hasattr(key, 'char') and key.char:  # Guard against missing char attribute
        char = key.char
        if char in charsdown:
            charsdown.remove(char)  # Remove from charsdown
        if shift_pressed:
            char = char.upper()
        if key_buffer and char == key_buffer[-1]:  # If the same key is released
            return  # Do nothing
    if key_buffer:
        write_ui_action(f'type {"".join(key_buffer)}')
        key_buffer.clear()  # Clear buffer after logging
    print('{0} released'.format(key))
    write_ui_action(f'release {key}')

def on_click(x, y, button, pressed):
    action = f'click {x}, {y}, {button}'
    print(action)
    write_ui_action(action)


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


# Iterate through tasks
for task in tasks:
    show_task_and_log(task)
    task_index += 1
    if task_index >= len(tasks):
        break

# Close all files and exit
print("All tasks completed. Exiting.")

# Keep the program alive
listener.join()
mlistener.join()