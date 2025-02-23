import pyttsx3
import datetime
import os

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 200)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def ring(time):
    timeset = str(time).strip()
    alarmtime = datetime.datetime.strptime(timeset, "%I:%M %p").time()
    print(f"Alarm set for {alarmtime}")

    while True:
        current_time = datetime.datetime.now().time()
        if current_time.hour == alarmtime.hour and current_time.minute == alarmtime.minute:
            speak("Alarm ringing, sir")
            os.startfile("Data/alarm_tone.mp3")
            break

if __name__ == "__main__":
    with open("Alarmtext.txt", "r") as file:
        time = file.read().strip()
    ring(time)

