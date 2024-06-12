import speech_recognition as sr
from googletrans import Translator
import pyaudio
import wave
import os
import tkinter as tk
import openai

# Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

def record_audio(filename, duration=5):
    """
    Records audio and saves it to a WAV file.

    Args:
        filename (str): Name of the file to save the audio to.
        duration (int): Duration of the recording in seconds. Default is 5 seconds.
    """
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=format, channels=channels,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)

    print("Recording...")
    frames = []

    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def malayalam_speech_to_text(audio_file):
    recognizer = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        # Recognize speech using Google Web Speech API
        text = recognizer.recognize_google(audio_data, language="ml-IN")
        return text
    except sr.UnknownValueError:
        return "സ്വന്തമായ വാക്കുകൾ പിന്തുടരുക..."
    except sr.RequestError:
        return "API അനുവദനീയത ലഭ്യമല്ല..."


def translate_to_english(malayalam_text):
    translator = Translator()
    translated = translator.translate(malayalam_text, src="ml", dest="en")
    return translated.text

def ask_gpt(question):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=question,
        max_tokens=50
    )
    return response.choices[0].text.strip()

def start_recording():
    global filename
    filename = "recorded_audio.wav"
    record_audio(filename)
    result = malayalam_speech_to_text(filename)
    translated_text = translate_to_english(result)
    response = ask_gpt(translated_text)
    text_display.config(state=tk.NORMAL)
    text_display.delete("1.0", tk.END)
    text_display.insert(tk.END, f"Malayalam Text:\n{result}\n\nTranslated to English:\n{translated_text}\n\nChatGPT Response:\n{response}")
    text_display.config(state=tk.DISABLED)

# Create the GUI window
root = tk.Tk()
root.title("Audio Transcription, Translation, and ChatGPT")

# Create a text widget for displaying the results
text_display = tk.Text(root, width=60, height=15)
text_display.pack(pady=20)
text_display.config(state=tk.DISABLED)

# Create "Start Recording" button
start_button = tk.Button(root, text="Start Recording", command=start_recording)
start_button.pack(pady=10)

# Create "Quit" button
quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack(pady=10)

root.mainloop()

# Delete the recorded audio file
if os.path.exists(filename):
    os.remove(filename)
