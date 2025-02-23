from frontend.gui import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    AnswerModifier,
    QueryModifier,
    SetMicrophoneStatus,
    GetMicrophoneStatus,    
    GetAssistantStatus,
    TempDirectoryPath,
    get_focus_mode_stop_time )
from Backend.automation import Automation
from Backend.chatbot import Chatbot
from Backend.model import FirstlayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.speechtotext import SpeechRecognition
from Backend.texttospeech import TextToSpeech
from Backend.Focus_mode import focus_mode
from Backend.Focus_graph import focus_graph
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import re
import pyttsx3
import datetime

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "focus mode", "focus graph"]

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
            os.startfile("music.mp3")
            break

def ShowDefaultchatIfNochats():
    file = open(r'Data\ChatLog.json',"r", encoding='utf-8')
    if len(file.read())<5:
        with open(TempDirectoryPath('database.data'),'w', encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\Chatlog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User",Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('responses.data'),"w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultchatIfNochats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def parse_duration(duration_query):
    duration_query = duration_query.lower().strip()
    if "min" in duration_query:
        match = re.match(r"(\d+(\.\d+)?)\s*min", duration_query)
        if match:
            return float(match.group(1))
    elif ":" in duration_query:
        match = re.match(r"(\d+):(\d+)\s*(a\.m\.|p\.m\.)?", duration_query)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            if match.group(3) == "p.m." and hours != 12:
                hours += 12
            elif match.group(3) == "a.m." and hours == 12:
                hours = 0
            return hours * 60 + minutes
    else:
        try:
            return float(duration_query)
        except ValueError:
            return None
    return None

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")
    Decision = FirstlayerDMM(Query)

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in functions):
                if "focus mode" in queries:
                    confirmation_text = "Are you sure that you want to enter focus mode :- [ YES / NO]"
                    ShowTextToScreen(confirmation_text)
                    TextToSpeech(confirmation_text)
                    confirmation_query = SpeechRecognition()
                    ShowTextToScreen(f"{Username} : {confirmation_query}")
                    if "yes" in confirmation_query.lower():
                        TextToSpeech("Entering the focus mode....")
                        duration_text = "How long do you want to stay in focus mode? (e.g., 2 mins, 2:00 a.m., 2.31 mins)"
                        ShowTextToScreen(duration_text)
                        TextToSpeech(duration_text)
                        duration_query = SpeechRecognition()
                        ShowTextToScreen(f"{Username} : {duration_query}")
                        duration_minutes = parse_duration(duration_query)
                        if duration_minutes is not None:
                            focus_mode(duration_query)
                        else:
                            ShowTextToScreen("Invalid duration. Focus mode cancelled.")
                            TextToSpeech("Invalid duration. Focus mode cancelled.")
                    else:
                        ShowTextToScreen("Focus mode cancelled.")
                        TextToSpeech("Focus mode cancelled.")
                elif "focus graph" in queries:
                    focus_graph()
                elif "set an alarm" in queries:
                    alarm_text = "Please tell the time for the alarm (e.g., 10:00 a.m.)"
                    ShowTextToScreen(alarm_text)
                    TextToSpeech(alarm_text)
                    alarm_query = SpeechRecognition()
                    ShowTextToScreen(f"{Username} : {alarm_query}")
                    alarm(alarm_query)
                    TextToSpeech("Alarm set.")
                else:
                    try:
                        run(Automation(list(Decision)))
                    except Exception as e:
                        print(f"Error in Automation: {e}")
                TaskExecution = True

    if ImageExecution == True:
        with open(r"frontend\files\imagegeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            p1 = subprocess.Popen(['python', r'Backend\imagegeneration.py'], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)

        except Exception as e:
              print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True
    
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("thinking...")
                QueryFinal = Queries.replace("general ","")
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime ","")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering ...")
                os._exit(1)

def FirstThread():

    while True:

        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            MainExecution()

        else:
            AIStatus = GetAssistantStatus()

            if "Available ..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ...")

def SecondThread():
    GraphicalUserInterface()

def alarm(query):
    timehere = open("Backend/Alarmtext.txt", "w")
    timehere.write(query)
    timehere.close()
    os.startfile("Backend/alarm.py")

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()


