from gtts import gTTS 
import tkinter as tk
import threading
import time
import sys
import os
from together import Together
from dotenv import load_dotenv
import tempfile


# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

MODEL = "deepseek-ai/DeepSeek-V3"

# This will be the system message for every conversation
SYSTEM_MESSAGE = "You will act like goku from Dragon ball z"

def send_to_api_thread(user_input):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        full_response = ""
        for token in response:
            try:
                content = token.choices[0].delta.content
                if content:
                    output_text.insert(tk.END, content)
                    output_text.see(tk.END)
                    output_text.update()
                    full_response += content
            except Exception as e:
                output_text.config(state="normal")
                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, f"Error: {e}")
                output_text.config(state="disabled")
                return
        output_text.config(state="disabled")
        speak_text(full_response)
    except Exception as e:
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Error: {e}")
        output_text.config(state="disabled")
        return

def on_enter(event=None):
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        return
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Waiting for response...")
    output_text.config(state="disabled")
    threading.Thread(target=send_to_api_thread, args=(user_input,), daemon=True).start()
    input_text.delete("1.0", tk.END)

def speak_text(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        tempname = fp.name
    if sys.platform == "win32":
        os.system(f'start /min wmplayer /play /close "{tempname}"')
    else:
        os.system(f"mpg123 {tempname}")
    # Wait a bit to ensure playback starts, then delete the file
    time.sleep(2)
    try:
        os.remove(tempname)
    except Exception:
        pass

root = tk.Tk()

root.title("Goku")  # Change window title


# Set the icon to your Dragon Ball PNG (works with PyInstaller --add-data)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon = tk.PhotoImage(file=resource_path("hd-png-dragon-ball-z-dbz-crystal-ball-4-stars-701751694862279ebqx9sdnpz (1).png"))
root.iconphoto(False, icon)

root.geometry("900x600")
root.config(bg="white")

input_text = tk.Text(root, width=40, height=30)
input_text.grid(row=0, column=0, padx=(10,5), pady=10, sticky="nsew")
input_text.bind("<Return>", lambda event: (on_enter(), "break"))

output_text = tk.Text(root, width=40, height=30, state="disabled", bg="#f0f0f0")
output_text.grid(row=0, column=1, padx=(5,10), pady=10, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

root.mainloop()
