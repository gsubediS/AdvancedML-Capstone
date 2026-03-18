import pandas as pd
import matplotlib.pyplot as plt

#open the file
df = pd.read_csv('activity_dataset/session_1773634349.csv')



#Mouse Speed per app
average_speed = df.groupby("app")["speed"].mean().dropna().sort_values(ascending=False)

plt.figure()
average_speed.plot(kind="bar")
plt.title("Average Mouse Speed by Application")
plt.xlabel("Application")
plt.ylabel("Average Speed")
plt.tight_layout()
plt.show()

#Scroll event per app
scroll_events = df[df["event_type"]=="Scroll_event"]
scroll_average = scroll_events["app"].value_counts()
scroll_ratio = scroll_average/df["app"].value_counts()
scroll_ratio = scroll_ratio[scroll_ratio > 0].sort_values(ascending=False)

plt.figure()
scroll_ratio.plot(kind="bar")
plt.title("Scrolling Event by Application")
plt.xlabel("Application")
plt.ylabel("Scroll Event Ratio")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


#Trackpad event per app
trackpad_events = df[df["event_type"]=="Trackpad_movement_event"]
trackpad_average = trackpad_events["app"].value_counts()
trackpad_ratio = trackpad_average/df["app"].value_counts()
trackpad_ratio = trackpad_ratio.sort_values(ascending=False)

plt.figure()
trackpad_ratio.plot(kind="bar")
plt.title("Trackpad Event by Application")
plt.xlabel("Application")
plt.ylabel("Trackpad Event Ratio")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()