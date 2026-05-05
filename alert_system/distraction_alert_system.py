import os
import time
import joblib
import pandas as pd
import numpy as np


from src.alert_live_data_logger import events,start_logging_data

window = 120
model = joblib.load('../tuned_model.pkl')

min_events = 150

keyboard_listener, mouse_listener = start_logging_data()
print("~Started the live data collection to detect focus state~")
print("First two minute window in process:")

while True:
    time.sleep(window)

    if len(events) ==0:
        continue

    df = pd.DataFrame(events)
    events.clear()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    total_events = len(df)

    if total_events < min_events:
        print("Not enough events for the window")
        continue

    keyboard_use_ratio = (df["event_type"] == "Keyboard_event").sum() / total_events
    scroll_ratio = (df["event_type"] == "Scroll_event").sum() / total_events
    trackpad_movement_ratio = (df["event_type"] == "Trackpad_movement_event").sum() / total_events
    click_ratio = (df["event_type"] == "Trackpad_event").sum() / total_events

    # derived ratios
    events_per_second = total_events / window
    tab_switch_frequency = (df["tab"] != df["tab"].shift()).sum()
    time_difference = df["timestamp"].diff().dt.total_seconds()
    idle_ratio = (time_difference > 2).sum() / total_events

    #category based derived ratios
    brainrot_ratio = (df["category"] == "brainrot").sum()/ total_events
    productive_ratio = (df["category"] == "productive").sum()/ total_events

    keyboard_to_scroll_ratio = keyboard_use_ratio/ (scroll_ratio + 1e-9)

    scroll_events = df[df["event_type"] == "Scroll_event"].sort_values("timestamp")
    if len(scroll_events) >= 2:
        vertical_direction = np.sign(scroll_events["scroll_dy"].fillna(0))
        scroll_direction_changes = vertical_direction.diff().fillna(0).ne(0).sum()
    else:
        scroll_direction_changes = 0

    event_rate_variance = (df.set_index("timestamp").resample("15s").size().var())

    X = pd.DataFrame([{
        "events_per_second_ratio": events_per_second,
        "idle_ratio": idle_ratio,
        "brainrot_ratio": brainrot_ratio,
        "productive_ratio": productive_ratio,
        "keyboard_to_scroll_ratio": keyboard_to_scroll_ratio,
        "event_rate_variance": event_rate_variance,
        "scroll_direction_changes": scroll_direction_changes
    }]).fillna(0)

    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0]
    confidence = max(probability)
    label = "distracted" if prediction == 1 else "focused"

    print(f'Model Prediction: The user is {label}, Confidence : {confidence}')

    if label == "distracted" and confidence > 0.60:
        os.system(
            'osascript -e \'display notification "Distracted!" with title "Focus Alert"\''
        )







