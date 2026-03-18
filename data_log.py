from pynput import keyboard,mouse
import pandas as pd
from datetime import datetime
import time
import os
from AppKit import NSWorkspace
import subprocess
import threading
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

#LOGGER
#log events
def log_event(event, **kwargs):
    row = {
        "timestamp" : datetime.now(),
        "event_type" : event,
        "app" : get_active_app()
    }

    row.update(kwargs)
    events.append(row)
#Helpers
def save_data():
    df = pd.DataFrame(events)
    filename = f"activity_dataset/session_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print("Data saved!",filename)

#Listeners
keyboard_listener = keyboard.Listener(on_press=on_keyboard_event)
mouse_listener = mouse.Listener(on_move=on_trackpad_movement_event,on_click=on_trackpad_click,on_scroll=on_scroll_event)

keyboard_listener.start()
mouse_listener.start()


try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    save_data()



