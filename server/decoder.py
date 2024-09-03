import tkinter as tk
from tkinter import font as tkfont
from pynput import mouse, keyboard
from pynput.keyboard import Key
import time
from components.glyphmap import get_glyph_to_key
# Use the mappings
glyph_map = get_glyph_to_key()


def decode_actions(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("###start") and not line.startswith("Task displayed:")]

def decode_glyph(key):
    return glyph_map.get(key)

def decode_action(action):
    if action.startswith("press "):
        _, key = action.split(" ", 1)
        return f"press {decode_glyph(key)}"
    elif action.startswith("type "):
        return action
    elif action.startswith("click "):
        return action
    else:
        return action

def execute_action(action, mouse_controller, keyboard_controller):
    decoded_action = decode_action(action)
    
    if decoded_action.startswith("click"):
        try:
            parts = decoded_action.split()
            if len(parts) == 4:
                _, button, x, y = parts
                x, y = int(x.rstrip(',')), int(y)
                button_attr = button.lower().split('.')[-1]
                mouse_controller.position = (x, y)
                time.sleep(0.2)
                if button_attr == 'left':
                    mouse_controller.click(mouse.Button.left)
                elif button_attr == 'right':
                    mouse_controller.click(mouse.Button.right)
                else:
                    raise ValueError(f"Invalid button type: {button}")
            else:
                raise ValueError
        except ValueError:
            pass
    
    elif decoded_action.startswith("type"):
        try:
            text = decoded_action.split(maxsplit=1)[1].strip('"')
            for char in text:
                key = decode_glyph(char)
                if isinstance(key, Key):
                    keyboard_controller.press(key)
                    keyboard_controller.release(key)
                else:
                    keyboard_controller.press(char)
                    keyboard_controller.release(char)
        except IndexError:
            pass
    
    elif decoded_action.startswith("press"):
        try:
            _, key = action.split(maxsplit=1)
            key_obj = decode_glyph(key)
            if key_obj is None:
                key_obj = key
            keyboard_controller.press(key_obj)
            keyboard_controller.release(key_obj)
        except Exception:
            pass
    
    time.sleep(0.3)

class ActionWindow:
    def __init__(self, actions, mouse_controller, keyboard_controller):
        self.actions = actions
        self.current_action_index = 0
        self.mouse_controller = mouse_controller
        self.keyboard_controller = keyboard_controller

        self.window = tk.Tk()
        self.window.title("Action Execution")
        self.window.geometry("300x150")
        self.window.configure(bg="#f0f0f0")
        self.window.attributes('-topmost', True)

        self.title_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.action_font = tkfont.Font(family="Courier", size=10)

        self.create_widgets()
        self.position_window()

    def create_widgets(self):
        title_label = tk.Label(self.window, text="Current Action", font=self.title_font, bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=(10, 5))

        self.action_frame = tk.Frame(self.window, bg="white", bd=2, relief=tk.SUNKEN, padx=5, pady=5)
        self.action_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.action_label = tk.Label(self.action_frame, text="", font=self.action_font, bg="white", fg="#0066cc", wraplength=260, justify=tk.LEFT)
        self.action_label.pack(fill=tk.BOTH, expand=True)

    def position_window(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = 0
        y = screen_height - 200

        self.window.geometry(f"300x150+{x}+{y}")

    def update_action_display(self):
        if self.current_action_index < len(self.actions):
            self.action_label.config(text=self.actions[self.current_action_index])
        else:
            self.action_label.config(text="All actions completed")
            self.window.after(1000, self.window.quit)

    def execute_next_action(self):
        if self.current_action_index < len(self.actions):
            execute_action(self.actions[self.current_action_index], self.mouse_controller, self.keyboard_controller)
            self.current_action_index += 1
            self.update_action_display()
            self.window.after(300, self.execute_next_action)
        else:
            self.update_action_display()

    def run(self):
        self.update_action_display()
        self.window.after(300, self.execute_next_action)
        self.window.mainloop()

def main():
    file_path = "uiactions.txt"
    actions = decode_actions(file_path)
    
    mouse_controller = mouse.Controller()
    keyboard_controller = keyboard.Controller()

    action_window = ActionWindow(actions, mouse_controller, keyboard_controller)
    action_window.run()

if __name__ == "__main__":
    main()