import openai
import speech_recognition as sr
import pyttsx3
import subprocess
import os
import json

messages = [{"role": "system", "content": 'You are a therapist who raps all your responses in a comedic way. Please respond in 50 words or less.'}]

engine = pyttsx3.init()


r = sr.Recognizer()
r.dynamic_energy_threshold = False
r.energy_threshold = 400

def speak(text):
    engine.say(text)
    engine.runAndWait()

def save_conversation(save_foldername):
    
    os.makedirs(save_foldername, exist_ok=True)

    base_filename = 'conversation'
    suffix = 0
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')

    while os.path.exists(filename):
        suffix += 1
        filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')

    with open(filename, 'w') as file:
        file.write("System Persona: {}\n".format(messages[0]['content']))

    return suffix

def save_inprogress(suffix, save_foldername, new_messages):

    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')

    with open(filename, 'a') as file:
        file.write(new_messages)
        
def whisper(audio):
    with open("speech.wav", "wb") as f:
        f.write(audio.get_wav_data())
    audio_file = open('speech.wav', 'rb')
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']
        
script_dir = os.path.dirname(os.path.abspath(__file__))
foldername = "voice_assistant"
save_foldername = os.path.join(script_dir,f"conversations/{foldername}")
suffix = save_conversation(save_foldername)

while True:
    with sr.Microphone() as source:
        print("Listening through Mic")
        r.adjust_for_ambient_noise(source, duration = 0.5)
        audio = r.listen(source)
        try:
            #user_input = r.recognize_google(audio)
            user_input = whisper(audio)
        except:
            continue
    
    messages.append({"role": "user", "content": user_input})
    save_inprogress(suffix, save_foldername, "User: {}\n".format(user_input))
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    
    response = response['choices'][0]['message']
    messages.append(response)
    subprocess.call(["say", response["content"]])
    save_inprogress(suffix, save_foldername, "Assistant: {}\n".format(response["content"]))
    
    print(response["content"])

#Inspired by: https://www.youtube.com/watch?v=u4oE49sWI4w&ab_channel=JarodsJourney

