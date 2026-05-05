from pynput import keyboard,mouse
import pandas as pd
from datetime import datetime
import time
import os
from AppKit import NSWorkspace
import subprocess
import math


events = []

last_mouse_y = None
last_mouse_x = None
last_mouse_time = None


#EVENTS
#when trackpad is clicked
def on_trackpad_click(x,y,button,pressed):
    try:
        if pressed:
            log_event(
                "Trackpad_event",
                x=x,y=y,
                button=str(button))
    except Exception as ex:
        print("Trackpad event error",ex)

#When the user scrolls
def on_scroll_event(x,y,dx,dy):
    try:
        log_event(
            "Scroll_event",
            x=x,
            y=y,
            scroll_dx = dx,
            scroll_dy = dy
        )
    except Exception as ex:
        print("Scroll event error",ex)

#When the user presses keys on the keyboard
def on_keyboard_event(key):
    try:
        key_name = str(key)
        key_name = key_name.replace("Key.","")
        if key_name in ["up","down","left","right","space","shift","cmd"]:
            key_category = key_name
        else:
            key_category = "Other"
        log_event("Keyboard_event",key_category=key_category)
    except Exception as ex:
        print("Keyboard event error",ex)

#When user moves the cursor
def on_trackpad_movement_event(x,y):
    global last_mouse_x, last_mouse_y, last_mouse_time
    try:
        current_time = time.time()

        if last_mouse_x is None:
            last_mouse_x = x
            last_mouse_y = y
            last_mouse_time = current_time

            return

        dx = x - last_mouse_x
        dy = y - last_mouse_y

        trackpad_distance = math.sqrt(dx*dx + dy*dy)
        dt = current_time - last_mouse_time
        if dt > 0:
            trackpad_speed = trackpad_distance/dt
        else:
            trackpad_speed = 0

        log_event("Trackpad_movement_event",
                  x = x, y = y,
                  dx = dx, dy = dy,
                  speed = trackpad_speed)

        last_mouse_x = x
        last_mouse_y = y
        last_mouse_time = current_time
    except Exception as ex:
        print("Trackpad movement event error",ex)


#Get what application the user is on
def get_active_app():
    try:
        app = NSWorkspace.sharedWorkspace().activeApplication()
        if app is None:
            return None
        return app["NSApplicationName"]
    except Exception as ex:
        print("get_active_app error",ex)

def get_safari_tab():
    try:
        script = '''
        tell application "Safari"
            if it is running then
                return URL of current tab of front window
            else
                return "n/a"
            end if
        end tell
        '''
        tab = subprocess.run(["osascript", "-e",script],
              capture_output=True, text=True)
        return tab.stdout.strip()
    except:
        return "n/a"

def get_category(tab_name):

    if not tab_name or tab_name == "n/a":
        return "other"

    tab_name = tab_name.lower()

    if any(tb in tab_name for tb in ["openai","chatgpt","canva","pycharm","acrobat","vt"]):
        return "productive"
    elif any(tb in tab_name for tb in ["reddit","facebook","instagram","youtube","finder"]):
        return "brainrot"
    else:
        return "other"




#LOGGER
#log events
def log_event(event, **kwargs):
    current_active_tab = get_active_app()
    if current_active_tab== "Safari":
        tab_name = get_safari_tab()
    else:
        tab_name = current_active_tab

    category = get_category(tab_name)

    row = {
        "timestamp" : datetime.now(),
        "event_type" : event,
        "app" : current_active_tab,
        "tab": tab_name,
        "category": category

    }

    row.update(kwargs)
    events.append(row)

#Listeners
def start_logging_data():
    keyboard_listener = keyboard.Listener(on_press=on_keyboard_event)
    mouse_listener = mouse.Listener(on_move=on_trackpad_movement_event,on_click=on_trackpad_click,on_scroll=on_scroll_event)

    keyboard_listener.start()
    mouse_listener.start()

    return keyboard_listener, mouse_listener
