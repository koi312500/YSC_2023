import openai
import requests
from urllib import parse
import speech_recognition as sr
import time
from pygame import mixer

import config

openai.api_key = config.OPENAI_API_KEY
model = "gpt-3.5-turbo"

mixer.init()

last_message = ""
error = True

while True:
    mic = sr.Recognizer()
    with sr.Microphone() as source:
        print("(Waiting for your voice)\nUser : ", end = '')
        speech = mic.listen(source)

    try:
        input_audio = mic.recognize_google(speech, language="ko-KR")
        print(input_audio)
    except sr.UnknownValueError:
        print("[Error] Your speech can not understand")
        error = True
        continue
    except sr.RequestError as e:
        print("[Error] Request Error!; {0}".format(e))
        error = True
        continue

    query = input_audio
    if error:
        query = "<Past Message>\n" + "None" + "\n<Query>\n" + input_audio
    else:
        query = "<Past Message>\n" + last_message + "\n<Query>\n" + input_audio
    error = True
    messages = [
        {"role": "system", "content": "You are very kind assitant. Please answer to the <Query> with Korean refer <Past Message>"},
        {"role": "user", "content": query}
    ]

    response_text = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    answer = response_text['choices'][0]['message']['content']

    url = "https://tts-translate.kakao.com/newtone?message=" + answer + "&format=wav-16k"
    #url = parse.quote(url)

    music = requests.get(url)
    with open(config.audio_file_name, 'wb') as f:
        f.write(music.content)
    
    mixer.music.load(config.audio_file_name)
    mixer.music.play()
    print(f"GPT : {answer}")
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)