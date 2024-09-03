import threading
import time
from pynput import keyboard, mouse
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key
from pynput.mouse import Controller  # Add this import at the top

# Global variables
key_buffer = []
tasks = []
task_index = 0
shift_pressed = False
modifiers = []
mouse_start = None
mouse_button = None
start_time = None
task_display = None

# File paths
TASKS_FILE = "tasks.txt"  
ACTIONS_FILE = "uiactions.txt"

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
}

def log_action(action,check=True):
    global task_display  # Ensure task_display is accessible
    try:
        # Get current mouse position
        mouse_controller = Controller()
        mouse_x, mouse_y = mouse_controller.position

        # Check if the mouse is within the messagebox region
        if check and task_display.messagebox and task_display.messagebox.winfo_exists():
            msg_x = task_display.messagebox.winfo_x()
            msg_y = task_display.messagebox.winfo_y()
            msg_width = task_display.messagebox.winfo_width()
            msg_height = task_display.messagebox.winfo_height()
            if msg_x <= mouse_x <= msg_x + msg_width and msg_y <= mouse_y <= msg_y + msg_height:
                return  # Do not log if within messagebox region

        with open(ACTIONS_FILE, "a", encoding="utf-8") as f:
            f.write(action + "\n")
            print("Wrote action",action)
    except Exception as e:
        print(f"Error in log_action: {e}",False)

def emit_keys():
    global key_buffer
    if key_buffer:
        log_action(f'type "{("".join(key_buffer))}"')
        key_buffer = []


def on_press(key):
    global key_buffer, shift_pressed, modifiers

    try:
        if key in (Key.shift, Key.ctrl, Key.alt, Key.cmd):
            if key not in modifiers:
                modifiers.append(key)
            if key == Key.shift:
                shift_pressed = True
        elif key == Key.space:
            key_buffer.append(' ')
            return
        elif key == Key.enter:
            print("Enter pressed")
            key_buffer.append(glyph_map.get(Key.enter))
            emit_keys()
        elif key in glyph_map:
            emit_keys()
            log_action(f"press {glyph_map.get(key)}")
        elif hasattr(key, 'char'):
            char = key.char.upper() if shift_pressed else key.char
            key_buffer.append(char)
        else:
            emit_keys()
            log_action(f"press {key}")
    except Exception as e:
        log_action(f"KEYBOARD: Error on key press: {e}")


def on_release(key):
    global key_buffer, pressed_keys, shift_pressed, modifiers
    try:
        if key in (Key.shift, Key.ctrl, Key.alt, Key.cmd):
            if key in modifiers:
                modifiers.remove(key)
            if key == Key.shift:
                shift_pressed = False
            return
    except Exception as e:
        print(f"KEYBOARD: Error on key release: {e}")

def on_click(x, y, button, pressed):
    global mouse_start, mouse_button, start_time
    if pressed:
        mouse_start = (x, y)
        mouse_button = button
        start_time = time.time()
        return

    if mouse_start and mouse_button:
        duration = time.time() - start_time
        if duration < 0.5:
            action = f"click {button} {mouse_start[0]}, {mouse_start[1]}"
        else:
            action = f"with mouse({button})\n    start {mouse_start}\n    end {(x, y)}\n    time {duration:.1f}"
        log_action(action)
        mouse_start = None

def heartbeat():
    while True:
        print("I am here")
        time.sleep(10)

def load_tasks():
    global tasks
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = f.read().splitlines()
    except FileNotFoundError:
        print(f"Error: {TASKS_FILE} not found")

class TaskDisplay:
    def __init__(self):
        self.root = None
        self.messagebox = None
        self.task_label = None

    def display_task(self):
        global task_index, task_display
        task_display = self
        if self.messagebox:
            self.messagebox.lift()
            self.messagebox.attributes('-topmost', True)
            return True
        if task_index < len(tasks):
            task = tasks[task_index]
            if not self.root:
                self.root = tk.Tk()
                self.root.withdraw()
            
            def update_task():
                global task_index
                task_index += 1
             
                if task_index < len(tasks):
                    new_task = tasks[task_index]
                    self.task_label.config(text=new_task)
                    log_action(f"## {new_task}",False)
                    print("update task ", task_index)
                else:
                    log_action("All tasks completed")
                    self.root.quit()
            
            self.messagebox = tk.Toplevel(self.root)
            self.messagebox.protocol("WM_DELETE_WINDOW", self.root.quit)
            self.messagebox.title("Task")
            self.messagebox.geometry("300x150")
            self.messagebox.configure(bg='#f0f0f0')
            self.messagebox.attributes('-topmost', True)
            
            frame = tk.Frame(self.messagebox, bg='#f0f0f0', padx=10, pady=10)
            frame.pack(expand=True, fill='both')
            
            tk.Label(frame, text="Current Task:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(pady=(0, 5))
            self.task_label = tk.Label(frame, text=task, font=("Arial", 10), bg='#f0f0f0', wraplength=280)
            self.task_label.pack(pady=(0, 10))
            
            tk.Button(frame, text="Next Task", command=update_task, 
                      bg='#4CAF50', fg='white', font=("Arial", 10),
                      activebackground='#45a049', relief=tk.FLAT).pack(pady=5)
            
            log_action(f"## {task}")
            return True
        else:
            if self.root:
                self.root.quit()
            return False
        


def main():
    load_tasks()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener = mouse.Listener(on_click=on_click)

    keyboard_listener.start()
    mouse_listener.start()

    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()

    with open(ACTIONS_FILE, 'w', encoding="utf-8") as f:
        f.write("####start\n")

    task_display = TaskDisplay()
    task_display.display_task()
    if task_display.root:
        task_display.root.mainloop()

    print("All tasks completed. Exiting.")
if __name__ == "__main__":
    main()

