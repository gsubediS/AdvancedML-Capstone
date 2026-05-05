import pandas as pd
import numpy as np
import glob
import os

window = 120
overlap = 60
raw_data_folder = "activity_dataset"
processed_file = "processed_dataa.csv"


def set_category(tab):
    tab = str(tab).lower()
    productive_apps = ["pycharm", "google docs", "docs", "finder", "canvas", "openai", "zoom", "chatgpt","youtube"]
    brainrot_apps = ["instagram", "facebook", "reddit", "uscis", "reels", "shorts", "stories"]

    if any(app in tab for app in productive_apps):
        return "productive"
    elif any(app in tab for app in brainrot_apps):
        return "brainrot"
    else:
        return "any"

def set_label(filename):
    filename = str(filename).lower()

    if "focused" in filename:
        return "focused"
    elif "distracted" in filename:
        return "distracted"
    else:
        return None

rows = []

raw_data_files = glob.glob(f"{raw_data_folder}/*.csv")

for raw_file in raw_data_files:
    df = pd.read_csv(raw_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    #ser ground-truth label
    label = set_label(os.path.basename(raw_file))
    if label is None:
        continue

    #reset category labels:
    # df["category"] = df["tab"].apply(set_category)

    #overlapping window
    session_start = df["timestamp"].min()
    session_end = df["timestamp"].max()
    total_session_len = (session_end-session_start).total_seconds()

    start = 0
    while start + window <= total_session_len:
        window_start = session_start + pd.Timedelta(seconds=start)
        window_end = window_start +  pd.Timedelta(seconds=window)
        group_df = df[(df["timestamp"] >= window_start)  & (df["timestamp"] < window_end)]
        start += overlap

        total_events = len(group_df)

        if total_events < 150:
            continue

        #simple features
        keyboard_use_ratio = (group_df["event_type"] == "Keyboard_event").sum() / total_events
        scroll_ratio = (group_df["event_type"] == "Scroll_event").sum() / total_events
        trackpad_movement_ratio = (group_df["event_type"] == "Trackpad_movement_event").sum() / total_events
        click_ratio = (group_df["event_type"] == "Trackpad_event").sum() / total_events

        # derived ratios
        events_per_second = total_events / window
        tab_switch_frequency = (group_df["tab"] != group_df["tab"].shift()).sum()
        time_difference = group_df["timestamp"].diff().dt.total_seconds()
        idle_ratio = (time_difference > 2).sum() / total_events

        #category based derived ratios
        brainrot_ratio = (group_df["category"] == "brainrot").sum()/ total_events
        productive_ratio = (group_df["category"] == "productive").sum()/ total_events

        keyboard_to_scroll_ratio = keyboard_use_ratio/ (scroll_ratio + 1e-9)

        keyboard_events = group_df[group_df["event_type"] == "Keybaord_event"].sort_values("timestamp")
        if len(keyboard_events) >2:
            keyboard_gaps = keyboard_events["timestamp"].diff().dt.total_seconds().fillna(0)
            burst_ids = (keyboard_gaps > 2.0).cumsum()
            burst_size = keyboard_events.groupby(burst_ids).size()
            avg_burst_len = burst_size.mean()
        else:
            avg_burst_len = 0



        scroll_events = group_df[group_df["event_type"] == "Scroll_event"].sort_values("timestamp")
        if len(scroll_events) >= 2:
            vertical_direction = np.sign(scroll_events["scroll_dy"].fillna(0))
            scroll_direction_changes = vertical_direction.diff().fillna(0).ne(0).sum()
        else:
            scroll_direction_changes = 0

        event_rate_variance = (group_df.set_index("timestamp").resample("15s").size().var())


        row = {
            "label": label,
            # "keyboard_use_ratio": keyboard_use_ratio,
            # "scroll_ratio": scroll_ratio,
            # "trackpad_movement_ratio": trackpad_movement_ratio,
            # "click_ratio": click_ratio,

            "events_per_second_ratio": events_per_second,
            # "tab_switch_frequency_ratio": tab_switch_frequency,
            "idle_ratio": idle_ratio,
            "brainrot_ratio":brainrot_ratio,
            "productive_ratio":productive_ratio,
            "keyboard_to_scroll_ratio":keyboard_to_scroll_ratio,
            # "avg_burst_len": avg_burst_len,
            "event_rate_variance" :event_rate_variance,
            "scroll_direction_changes":scroll_direction_changes

        }

        rows.append(row)

processed = pd.DataFrame(rows)
# processed = processed[processed["label"] != "unknown"]
processed = processed.fillna(0)

processed.to_csv(processed_file, index=False)

print("Data Processed", processed_file)
print(processed.head())
print("Columns: ", processed.columns.tolist())









