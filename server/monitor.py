from pynput import mouse
from pynput import keyboard
from pynput.mouse import Button
import time
import threading
import tkinter as tk  # Import tkinter for message boxes
import tkinter.messagebox as messagebox  # Import messagebox explicitly
import os
from pynput.keyboard import Key  # Import Key for special keys
from tkinter import *
    
# Glyph mapping for modifiers and special keys
glyph_map = {
    Key.cmd: '⌘',
    Key.shift: '⇧',
    Key.alt: '⌥',
    Key.ctrl: '⌃',
    Key.enter: '⏎',
    Key.backspace: '⌫',
    Key.delete: '⌦',
    Key.tab: '⇥',
    Key.esc: '⎋',
    Key.left: '←',
    Key.right: '→',
    Key.up: '↑',
    Key.down: '↓',
    # Add more mappings as needed
}

# Modify on_press and on_release to log key events
key_buffer = []
shift_pressed = False  # Flag to track if Shift is pressed
modifiers = []  # Track active modifiers
mouse_start = None  # Track mouse click start position
mouse_button = None  # Track which mouse button is pressed

charsdown = []  # Define charsdown list to track pressed characters

def on_press(key):
    global key_buffer, shift_pressed, modifiers, mouse_start, mouse_button
    # Check for modifier keys
    if key == Key.shift:
        shift_pressed = True
    if key in (Key.shift, Key.ctrl, Key.alt, Key.cmd):  # Add other modifiers as needed
        if key not in modifiers:
            modifiers.append(key)
        return  # Do not log modifier press

    # Handle space and other keys
    if key == Key.space:
        key_buffer.append(' ')  # Add space to key_buffer
        print('space key pressed')
        return
    elif key == Key.enter:
        key_buffer.append(glyph_map.get(key))
        emit_typing()
        return
    elif key in (Key.tab, Key.backspace):  # Handle Key.tab and Key.backspace
        print("key is ", key)
        emit_typing()
        write_ui_action(f'press {glyph_map.get(key)}')  # Log key press
        return
   
    if hasattr(key, 'char'):
        char = key.char.upper() if shift_pressed else key.char
        key_buffer.append(char)
        # print('alphanumeric key {0} pressed'.format(char))
    else:
        emit_typing()
        print('special key {0} pressed'.format(key))
        write_ui_action(f'press {glyph_map.get(key)}')

def emit_typing():
     global key_buffer
     if key_buffer:
        write_ui_action(f'type "{"".join(key_buffer)}"')
        key_buffer.clear()  # Clear buffer after logging
    

def on_release(key):
    global key_buffer, shift_pressed, modifiers, mouse_start, mouse_button
    if key in (Key.shift, Key.ctrl, Key.alt, Key.cmd):  # Add other modifiers as needed
        if key in modifiers:
            modifiers.remove(key)
        if key == Key.shift:
            shift_pressed = False
        
        return  # Do
    if hasattr(key, 'char'):  # Guard against missing char attribute
        char = key.char
        if char in charsdown:
            charsdown.remove(char)  # Remove from charsdown
        if shift_pressed:
            char = char.upper()
        if key_buffer and char == key_buffer[-1]:  # If the same key is released
            return  # Do nothing
    
 
def on_click(x, y, button, pressed):
    global mouse_start, mouse_button, start_time  # Add start_time to global variables
    if pressed:
        mouse_start = (x, y)
        mouse_button = button
        start_time = time.time()  # Define start_time when the mouse is pressed
        return

    if mouse_start and mouse_button:
        duration = time.time() - start_time  # Calculate duration
        if duration < 0.5:  # Check if duration is less than 0.5 seconds
            action = f'click left {mouse_start[0]}, {mouse_start[1]}'  # New format for quick clicks
        else:
            action = f'with mouse({mouse_button})\n    start {mouse_start}\n    end {(x, y)}\n    time {duration:.1f}'
        write_ui_action(action)
        mouse_start = None  # Reset for next click


def send_heartbeat():
    while True:
        print("I am here")
        time.sleep(10) 

def read_tasks():
    with open('tasks.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]

def write_ui_action(action):
    # global topwindow  # Access the topwindow variable
    # mouse_x, mouse_y = mou.position  # Get current mouse position
    # if topwindow.winfo_x() <= mouse_x <= topwindow.winfo_x() + topwindow.winfo_width() and \
    #    topwindow.winfo_y() <= mouse_y <= topwindow.winfo_y() + topwindow.winfo_height():
    #     return  # Do not write to file if mouse is in the bounding box of topwindow
    with open('uiactions.txt', 'a') as f:  # Overwrite the file each time
        f.write(action + '\n')

def print_ui_actions():
    with open('uiactions.txt', 'r') as f:
        print(f.read())  # Print the contents of the file

def show_top_window():
    global task_index  # Add task_index to the global scope
    topwindow = Toplevel()
    topwindow.title('Enter Room Inventory')
    topwindow.geometry("200x200+500+100")
    topwindow.attributes('-topmost', True)

    # Display the current task in the top window
    task_label = tk.Label(topwindow, text=tasks[task_index])  # Show current task
    task_label.pack(pady=10)

    # Button to go to the next task
    next_button = tk.Button(topwindow, text="Next Task", command=lambda: next_task(task_label))
    next_button.pack(pady=10)

    topwindow.mainloop()

def next_task(task_label):
    global task_index
    task_index += 1
    if task_index < len(tasks):
        task_label.config(text=tasks[task_index])  # Update the label with the next task
    else:
        task_label.config(text="No more tasks")  # Handle case when no more tasks are available
        root.quit()  # Exit the program when all tasks are completed

# Hide the main Tkinter window
root = tk.Tk()
root.withdraw()  # Hide the main window

tasks = read_tasks()
task_index = 0


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

with open('uiactions.txt', 'w') as f:  # Overwrite the file each time
        f.write("####start\n")
# Iterate through tasks
# for task in tasks:
#     show_task_and_log(task)
#     task_index += 1
#     if task_index >= len(tasks):
#         break


show_top_window()# Close all files and exit
print_ui_actions()  # Print the contents of uiactions.txt before exiting
print("All tasks completed. Exiting.")

# # Keep the program alive

# listener.join()
# mlistener.join()