"""
Author: Saeed Soukiah
Date: Monday, 26 May 2025
Version: 1.0
"""
# Import required libraries
import threading  # For handling multiple threads concurrently
import tkinter as tk  # For creating the GUI window
from tkinter import scrolledtext, ttk, messagebox  # For styled widgets in the GUI
import random  # For generating random responses based on different intents
import speech_recognition as sr  # For capturing and transcribing speech commands
import winsound  # For playing beep sounds as audible notifications
import pyttsx3  # For converting text to speech (TTS)
import datetime  # For obtaining the current date and time
import requests  # For making HTTP requests
from googletrans import Translator, LANGUAGES  # For translating text between languages
import re  # For regular expression matching
import wikipediaapi  # For fetching content from Wikipedia
import os  # For operating system functionality
import ctypes  # For accessing Windows API functions (e.g., locking the workstation)

import numpy as np          # For processing numerical arrays
import noisereduce as nr    # For noise reduction in audio

# Initialize the text-to-speech engine using pyttsx3
engine = pyttsx3.init()

# Set the speech rate (speed of spoken words)
rate = engine.getProperty('rate')
print(f"Current speech rate: {rate}")
engine.setProperty('rate', 145)

# Set the volume of the speech engine
volume = engine.getProperty('volume')
print(f"Current volume level: {volume}")
engine.setProperty('volume', 1.0)

def speak(text):
    """
    Convert the given text to speech and play it.
    """
    engine.say(text)
    engine.runAndWait()

# Initialize Wikipedia API with English language settings
wiki = wikipediaapi.Wikipedia('english')

def fetch_wikipedia_summary(query, max_sentences=2):
    """
    Returns a short summary from Wikipedia for the given query.
    """
    wiki = wikipediaapi.Wikipedia('english', extract_format=wikipediaapi.ExtractFormat.WIKI)
    page = wiki.page(query)
    if page.exists():
        summary = page.summary.split('. ')[:max_sentences]
        summary_text = '. '.join(summary)
        return summary_text + "."
    else:
        return f"Sorry, I couldn't find any information on '{query}' on Wikipedia."

# Define intents with associated trigger keywords
intents = {
    'greeting': ['hello', 'hi', 'hey'],
    'farewell': ['bye', 'goodbye'],
    'gratitude': ['thank you', 'thanks'],
    'query': ['how are you', 'what are you doing'],
    'weather': ['weather', 'temperature', 'forecast'],
    'time': ['time', 'current time'],
    'date': ['date', 'current date', "date"],
    'reminder': ['reminder', 'remind me'],
    'joke': ['joke', 'tell me a joke'],
    'fact': ['fact', 'interesting fact'],
    'meaning': ['meaning of'],
    'translate': ['translate'],
    'who_are_you': ['who are you', 'what is your name', 'who r u'],
    'what is your name': ['what is your name?', 'what is ur name'],
    'wikipedia': ['wikipedia', 'wiki', 'information', 'search'],
    'lock': ['lock windows', 'lock']
}

# Define standard responses for intents
responses = {
    'wikipedia': ['Here is some information from Wikipedia:', 'I found this on Wikipedia:', 'According to Wikipedia:'],
    'greeting': ['Hi there!', 'Hello!', 'Hey!'],
    'farewell': ['Goodbye!', 'See you later!', 'Bye!'],
    'gratitude': ["You're welcome!", 'No problem!', 'My pleasure!'],
    'query': ["I'm doing well, thank you!", 'Just assisting you!', 'Feeling great, thank you for asking!'],
    'weather': ['The weather is sunny today.', "It's cloudy with a chance of rain."],
    'time': ['The current time is ' + datetime.datetime.now().strftime("%I:%M %p")],
    'date': ['Today, the date is: ' + datetime.datetime.now().strftime("%d %B %Y")],
    'reminder': ['Sure, I will remind you.', 'Reminder set successfully.'],
    'joke': [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I'm reading a book on anti-gravity. It's impossible to put down!"
    ],
    'fact': [
        "Did you know that the shortest war in history was between Britain and Zanzibar on August 27, 1896? It lasted only 38 minutes!"
    ],
    'translate': ['Can you please provide a specific word or sentence to translate and the specified language.'],
    'who_are_you': ['I am X eighteen version 1, your AI assistant.'],
    'what is your name': ['My name is X eighteen.']
}

def lock_windows():
    """
    Lock the Windows workstation using the Windows API.
    """
    ctypes.windll.user32.LockWorkStation()

def fetch_word_meaning(word):
    """
    Fetch the definition of a word using a dictionary API.
    """
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    response = requests.get(url)
    data = response.json()
    if isinstance(data, list) and 'meanings' in data[0]:
        meanings = data[0]['meanings']
        definition = [meaning['definitions'][0]['definition'] for meaning in meanings]
        return " ".join(definition)
    else:
        return "Sorry, I couldn't find the meaning of that word."

def translate_text(text, dest_language):
    """
    Translate the given text to a specified language using googletrans.
    """
    translator = Translator()
    translated_text = translator.translate(text, dest_language).text
    return translated_text

def fetch_weather(location):
    """
    Retrieve current weather information for a given location using the OpenWeatherMap API,
    and return a detailed summary.
    """
    api_key = '7e760b7138d38407c12adc03973acb37'  # Replace with your own API key
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    if data.get('cod') == 200:
        city = data.get('name', location).title()
        country = data.get('sys', {}).get('country', '')
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data.get('wind', {}).get('speed', 0)
        return (f"In {city}, {country}, the weather is {weather}. The temperature is {temperature}°C, "
                f"humidity is at {humidity}% and wind speed is {wind_speed} m/s.")
    else:
        return "Sorry, I couldn't fetch the weather for that location."

def reduce_noise_audio(audio_data):
    """
    Apply noise reduction to the given AudioData using the noisereduce library.
    
    Parameters:
        audio_data (sr.AudioData): The captured audio.
        
    Returns:
        sr.AudioData: A new AudioData object with reduced background noise.
    """
    # Convert raw audio bytes to a numpy array of int16
    audio_array = np.frombuffer(audio_data.frame_data, dtype=np.int16)
    # Apply noise reduction using spectral gating
    reduced_audio = nr.reduce_noise(y=audio_array, sr=audio_data.sample_rate)
    # Convert the processed numpy array back to bytes
    reduced_bytes = reduced_audio.astype(np.int16).tobytes()
    # Return a new AudioData object with the cleaned bytes
    return sr.AudioData(reduced_bytes, audio_data.sample_rate, audio_data.sample_width)

def process_command(command):
    """
    Process a text command by determining its intent and executing the corresponding action.
    """
    command = command.lower()
    found_intent = False

    # Update status to processing (thread-safe)
    root.after(0, lambda: update_status("Processing"))

    # Lock system command
    if 'lock' in command:
        found_intent = True
        speak("locking your device")
        lock_windows()
        display_response("User: " + command + "\n" + "X eighteen: Windows locked.\n\n")
    
    # Fetch meaning command using regex
    meaning_match = re.search(r'meaning of (\w+)', command)
    if meaning_match:
        found_intent = True
        word = meaning_match.group(1)
        meaning = fetch_word_meaning(word)
        speak(meaning)
        display_response("User: " + command + "\n" + "X eighteen: " + meaning + "\n\n")
    
    # Translation command using regex "translate <text> to <language>"
    translate_match = re.search(r'translate (.+) to (\w+)', command)
    if translate_match:
        found_intent = True
        text_to_translate = translate_match.group(1)
        dest_language = translate_match.group(2)
        if dest_language in LANGUAGES.values():
            translated_text = translate_text(text_to_translate, dest_language)
        else:
            dest_language_code = next((code for code, lang in LANGUAGES.items() if lang == dest_language), None)
            if dest_language_code:
                translated_text = translate_text(text_to_translate, dest_language_code)
            else:
                translated_text = f"Sorry, I don't recognize the language '{dest_language}'."
        speak(translated_text)
        display_response("User: " + command + "\n" + "X eighteen: " + translated_text + "\n\n")
    
    # Weather command using regex; updated to handle multi-word locations
    weather_match = re.search(r'weather in ([\w\s]+)', command)
    if weather_match:
        found_intent = True
        location = weather_match.group(1).strip()
        weather_info = fetch_weather(location)
        display_response("User: " + command + "\n" + "X eighteen: " + weather_info + "\n\n")
    
    # Wikipedia search command
    if 'wikipedia' in command:
        found_intent = True
        query = command.replace('wikipedia', '').strip()
        summary = fetch_wikipedia_summary(query)
        speak(summary)
        display_response("User: " + command + "\n" + "X eighteen: " + summary + "\n\n")
    
    # Generic intents on keyword match
    if not found_intent:
        for intent, keywords in intents.items():
            if any(keyword in command for keyword in keywords):
                found_intent = True
                response = random.choice(responses[intent])
                speak(response)
                display_response("User: " + command + "\n" + "X eighteen: " + response + "\n\n")
                break
    # Fallback default
    if not found_intent:
        response = "Sorry, I didn't understand the command"
        speak(response)
        display_response("User: " + command + "\n" + "X eighteen: " + response + "\n\n")
    
    # Return status to idle
    root.after(0, lambda: update_status("Idle"))

def display_response(response):
    """
    Display the conversation in the GUI's chat log.
    """
    conversation_log.tag_configure("user", justify='left')
    conversation_log.tag_configure("X eighteen", justify='right')
    
    if response.startswith("User:"):
        conversation_log.insert(tk.END, response, "user")
    elif response.startswith("X eighteen:"):
        conversation_log.insert(tk.END, response, "X eighteen")
    else:
        conversation_log.insert(tk.END, response)
    
    conversation_log.insert(tk.END, "\n")
    conversation_log.see(tk.END)

def update_status(new_status):
    """
    Update the status label to reflect the assistant's current mode.
    """
    status_label.config(text=f"Status: {new_status}")

# Functions for interactive controls

def lock_action():
    """
    Action for Lock System button.
    """
    update_status("Processing")
    speak("locking your device")
    lock_windows()
    display_response("User (Button): Lock System pressed\n" + "X eighteen: Windows locked.\n")
    update_status("Idle")

def get_weather_popup():
    """
    Popup window to receive a location for weather information.
    """
    def fetch_and_display():
        loc = location_entry.get().strip()
        if loc:
            weather_info = fetch_weather(loc)
            speak(weather_info)
            display_response("User (Button): Weather for " + loc + "\n" + "X eighteen: " + weather_info + "\n")
            popup.destroy()
            update_status("Idle")
        else:
            messagebox.showerror("Input Error", "Please enter a location.")

    update_status("Waiting for Weather Input")
    popup = tk.Toplevel(root)
    popup.title("Get Weather")
    tk.Label(popup, text="Enter location:").grid(row=0, column=0, padx=10, pady=10)
    location_entry = tk.Entry(popup)
    location_entry.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(popup, text="OK", command=fetch_and_display).grid(row=1, column=0, columnspan=2, pady=10)

def open_translate_popup():
    """
    Popup window to translate text.
    """
    def perform_translation():
        text_input = text_entry.get("1.0", tk.END).strip()
        dest_lang = language_entry.get().strip()
        if text_input and dest_lang:
            if dest_lang in LANGUAGES.values():
                result = translate_text(text_input, dest_lang)
            else:
                dest_language_code = next((code for code, lang in LANGUAGES.items() if lang == dest_lang), None)
                if dest_language_code:
                    result = translate_text(text_input, dest_language_code)
                else:
                    result = f"Sorry, I don't recognize the language '{dest_lang}'."
            speak(result)
            display_response("User (Button): Translate\n" + "X eighteen: " + result + "\n")
            popup.destroy()
            update_status("Idle")
        else:
            messagebox.showerror("Input Error", "Please provide both text and target language.")
    
    update_status("Waiting for Translation Input")
    popup = tk.Toplevel(root)
    popup.title("Translate Text")
    
    tk.Label(popup, text="Text to translate:").grid(row=0, column=0, padx=10, pady=5, sticky="nw")
    text_entry = tk.Text(popup, height=5, width=40)
    text_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(popup, text="Target language:").grid(row=1, column=0, padx=10, pady=5)
    language_entry = tk.Entry(popup)
    language_entry.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Button(popup, text="Translate", command=perform_translation).grid(row=2, column=0, columnspan=2, pady=10)

def open_settings():
    """
    Popup window for customization options: theme, font size, voice rate, and volume.
    """
    def apply_settings():
        chosen_theme = theme_var.get()
        try:
            style.theme_use(chosen_theme)
        except tk.TclError:
            messagebox.showerror("Theme Error", f"Theme '{chosen_theme}' not available.")
        
        new_font = (font_var.get(), int(font_size_var.get()))
        conversation_log.config(font=new_font)
        
        try:
            new_rate = int(rate_var.get())
            new_volume = float(volume_var.get())
            engine.setProperty('rate', new_rate)
            engine.setProperty('volume', new_volume)
        except ValueError:
            messagebox.showerror("Input Error", "Rate must be an integer and Volume a float between 0.0 and 1.0.")
        
        settings_popup.destroy()

    settings_popup = tk.Toplevel(root)
    settings_popup.title("Settings")
    
    tk.Label(settings_popup, text="Theme:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    theme_var = tk.StringVar(value=style.theme_use())
    theme_options = ttk.Combobox(settings_popup, textvariable=theme_var, values=style.theme_names())
    theme_options.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(settings_popup, text="Font:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    font_var = tk.StringVar(value="Helvetica")
    tk.Entry(settings_popup, textvariable=font_var).grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(settings_popup, text="Font Size:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    font_size_var = tk.StringVar(value="12")
    tk.Entry(settings_popup, textvariable=font_size_var).grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(settings_popup, text="Voice Rate:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    rate_var = tk.StringVar(value=str(engine.getProperty('rate')))
    tk.Entry(settings_popup, textvariable=rate_var).grid(row=3, column=1, padx=10, pady=5)
    
    tk.Label(settings_popup, text="Volume (0.0-1.0):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    volume_var = tk.StringVar(value=str(engine.getProperty('volume')))
    tk.Entry(settings_popup, textvariable=volume_var).grid(row=4, column=1, padx=10, pady=5)
    
    tk.Button(settings_popup, text="Apply", command=apply_settings).grid(row=5, column=0, columnspan=2, pady=10)

# New function to allow manual input of a command through the GUI
def submit_command():
    """
    Retrieve the command from the input field and process it.
    """
    command = command_entry.get().strip()
    if command:
        process_command(command)
        command_entry.delete(0, tk.END)

# Voice assistant state and processing functions

WAKE_WORD = "rice"  # Word to activate listening mode
STOP_WORD = "die"    # Word to deactivate listening mode
listening = False    # Flag to indicate active listening

def wake_up():
    """
    Activate listening mode for voice commands.
    """
    global listening
    listening = True
    root.after(0, lambda: update_status("Active Listening"))
    play_beep_sound()
    speak("Yes master")

def sleep():
    """
    Deactivate listening mode.
    """
    global listening
    listening = False
    root.after(0, lambda: update_status("Idle"))
    speak("Goodbye!")

def process_voice_commands():
    """
    Continuously listen for voice commands and process them.
    Noise reduction is applied to help remove background noise.
    """
    global listening
    recognizer = sr.Recognizer()

    # Adjust recognition settings for better accuracy
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8
    recognizer.non_speaking_duration = 0.5

    with sr.Microphone() as source:
        # Calibrate for ambient noise for 1 second
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ambient noise energy threshold set to:", recognizer.energy_threshold)
        
        while True:
            if not listening:
                print("Listening for the wake word...")
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    # Apply noise reduction
                    clean_audio = reduce_noise_audio(audio)
                    command = recognizer.recognize_google(clean_audio).lower()
                    print("You said (wake word):", command)
                    if WAKE_WORD in command:
                        wake_up()
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Error from speech service: {e}")
            else:
                print("Listening for commands...")
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    clean_audio = reduce_noise_audio(audio)
                    command = recognizer.recognize_google(clean_audio).lower()
                    print("You said (command):", command)
                    if STOP_WORD in command:
                        sleep()
                    else:
                        process_command(command)
                except sr.WaitTimeoutError:
                    print("No command detected, please try speaking again.")
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio.")
                except sr.RequestError as e:
                    print(f"Error from speech service: {e}")

def play_beep_sound():
    """
    Play a beep to indicate a mode change.
    """
    winsound.Beep(500, 100)

# Create the main application window
root = tk.Tk()
root.title("AI Assistant")

# Set up the style for the GUI
style = ttk.Style()
style.theme_use('clam')  # Default theme

# Status label for assistant state (Row 0)
status_label = tk.Label(root, text="Status: Idle", font=("Helvetica", 12), padx=10, pady=5)
status_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

# Conversation log (chat log) (Row 1)
conversation_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, font=("Helvetica", 12))
conversation_log.grid(row=1, column=0, padx=10, pady=5)

# Command input frame (Row 2)
command_frame = tk.Frame(root)
command_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
command_entry = tk.Entry(command_frame, font=("Helvetica", 12), width=70)
command_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
btn_send = tk.Button(command_frame, text="Send", command=submit_command, width=10)
btn_send.grid(row=0, column=1, padx=5, pady=5)
# Bind the Return/Enter key to submit the command
command_entry.bind("<Return>", lambda event: submit_command())

# Interactive controls frame (Row 3)
controls_frame = tk.Frame(root)
controls_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
btn_lock = tk.Button(controls_frame, text="Lock System", command=lock_action, width=15)
btn_lock.grid(row=0, column=0, padx=5, pady=5)
btn_weather = tk.Button(controls_frame, text="Get Weather", command=get_weather_popup, width=15)
btn_weather.grid(row=0, column=1, padx=5, pady=5)
btn_translate = tk.Button(controls_frame, text="Translate", command=open_translate_popup, width=15)
btn_translate.grid(row=0, column=2, padx=5, pady=5)
btn_settings = tk.Button(controls_frame, text="Settings", command=open_settings, width=15)
btn_settings.grid(row=0, column=3, padx=5, pady=5)

# Start voice command processing on a separate thread (daemon mode for clean exit)
threading.Thread(target=process_voice_commands, daemon=True).start()

# Start the Tkinter main loop
root.mainloop()
