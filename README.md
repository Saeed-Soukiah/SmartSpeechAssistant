# Smart Speech Assistant

A comprehensive AI assistant built in Python that offers voice recognition, natural language processing, text-to-speech, Wikipedia queries, weather forecasting, translation, and noise reduction. This project integrates multiple functionalities into a sleek Tkinter GUI and provides wake word detection to seamlessly switch between passive and active listening modes.

## Features

- **Voice Recognition:** Processes voice commands using the `speech_recognition` library with noise reduction via `noisereduce` for enhanced accuracy.
- **Text-to-Speech:** Converts text to speech using `pyttsx3` to deliver audible responses.
- **Wake Word Detection:** Activates listening mode with a custom wake word.
- **Wikipedia Integration:** Fetches summaries from Wikipedia using `wikipediaapi`.
- **Translation:** Translates text between languages with `googletrans`.
- **Weather Information:** Retrieves current weather data via the OpenWeatherMap API.
- **System Utilities:** Performs actions like locking the Windows workstation.
- **Intents and Responses:** Supports various commands (greetings, farewells, jokes, etc.) for a conversational experience.
- **GUI Application:** A user-friendly interface built with Tkinter, featuring a conversation log, command input, and interactive control buttons.
  
## Dependencies:
-threading, tkinter, speech_recognition, winsound, pyttsx3, datetime,requests, googletrans, re, wikipediaapi, os, ctypes, numpy, noisereduce.
