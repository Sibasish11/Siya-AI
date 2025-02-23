import time
import datetime
import ctypes, sys
import re
from frontend.gui import ShowTextToScreen, SetAssistantStatus, get_focus_mode_stop_time
from Backend.texttospeech import TextToSpeech

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def convert_time_to_minutes(time_str):
    time_str = time_str.lower().strip()
    if "min" in time_str:
        match = re.match(r"(\d+(\.\d+)?)\s*min", time_str)
        if match:
            return float(match.group(1))
    elif ":" in time_str:
        match = re.match(r"(\d+):(\d+)\s*(a\.m\.|p\.m\.)?", time_str)
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
            return float(time_str)
        except ValueError:
            return None
    return None

def focus_mode(duration):
    if is_admin():
        duration_minutes = convert_time_to_minutes(duration)
        if duration_minutes is None:
            ShowTextToScreen("Invalid duration. Focus mode cancelled.")
            TextToSpeech("Invalid duration. Focus mode cancelled.")
            return

        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(minutes=duration_minutes)
        host_path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
        redirect = '127.0.0.1'

        ShowTextToScreen(f"Current time: {current_time.strftime('%H:%M')}")
        time.sleep(2)
        website_list = ["www.facebook.com", "facebook.com", "www.instagram.com", "instagram.com", "web.whatsapp.com", "whatsapp.com", "www.twitter.com", "twitter.com", "www.netflix.com", "netflix.com", "www.amazon.com", "amazon.com", "www.flipkart.com", "flipkart.com", "www.snapdeal.com", "snapdeal.com", "www.ebay.com", "ebay.com", "www.aliexpress.com", "aliexpress.com", "www.tiktok.com", ]
        try:
            with open(host_path, "r+") as file:  # r+ is writing+ reading
                content = file.read()
                time.sleep(2)
                for website in website_list:
                    if website in content:
                        pass
                    else:
                        file.write(f"{redirect} {website}\n")
                        ShowTextToScreen("DONE")
                        time.sleep(1)
            ShowTextToScreen("FOCUS MODE TURNED ON !!!!")
        except Exception as e:
            ShowTextToScreen(f"Error: {e}")

        while datetime.datetime.now() < end_time:
            time.sleep(1)

        try:
            with open(host_path, "r+") as file:
                content = file.readlines()
                file.seek(0)

                for line in content:
                    if not any(website in line for website in website_list):
                        file.write(line)

                file.truncate()

                ShowTextToScreen("Websites are unblocked !!")
                with open("focus.txt", "a") as file:
                    file.write(f",{duration_minutes}")  # Write a 0 in focus.txt before starting
                TextToSpeech("Focus mode is turned off.")
        except Exception as e:
            ShowTextToScreen(f"Error: {e}")
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

if __name__ == "__main__":
    duration = input("Enter duration for focus mode (e.g., 2 mins, 2:00 a.m., 2.31 mins): ")
    focus_mode(duration)