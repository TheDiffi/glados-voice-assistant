#!/usr/bin/python3
# 	   _____ _           _____   ____   _____
# 	  / ____| |         |  __ \ / __ \ / ____|
# 	 | |  __| |     __ _| |  | | |  | | (___
# 	 | | |_ | |    / _` | |  | | |  | |\___ \
# 	 | |__| | |___| (_| | |__| | |__| |____) |
# 	  \_____|______\__,_|_____/ \____/|_____/
# ___________________________________________________
#
# 	Open source voice assistant by nerdaxic
#
# 	Local TTS engine based on https://github.com/NeonGeckoCom/neon-tts-plugin-glados
# 	Local keyword detection using PoketSphinx
# 	Using Google speech recognition API
# 	Works with Home Assistant
#
# 	https://github.com/nerdaxic/glados-voice-assistant/
# 	https://www.henrirantanen.fi/
#
# 	Rename settings.env.sample to settings.env
# 	Edit settings.env to match your setup
#

##from gladosTTS import *
import traceback
from gladosTime import *
from gladosSerial import *
from gladosServo import *
from glados_functions import *

from skills.glados_jokes import *
from skills.glados_magic_8_ball import *
from skills.glados_home_assistant import *
from pocketsphinx import LiveSpeech
from gpt import *
from handle_command import handle_speech, listen_for_command, process_command, take_new_command
import subprocess

# from importlib import import_module
import glados_settings

glados_settings.load_from_file()


def start_up():
    # Show regular eye-texture, this stops the initial loading animation
    # setEyeAnimation("idle")
    home_assistant_initialize()
    # eye_position_default()
    # respeaker_pixel_ring()

    # Start notify API in a subprocess
    # print("\033[1;94mINFO:\033[;97m Starting notification API...\n")
    # subprocess.Popen(["python3 "+os.path.dirname(os.path.abspath(__file__))+"/gladosNotifyAPI.py"], shell=True)

    # Let user know the script is running
    speak("oh, its you", cache=True)
    # time.sleep(0.25)
    # speak("it's been a long time", cache=True)
    # time.sleep(1.0)
    speak("how have you been", cache=True)
    print(
        "\nWaiting for keyphrase: "
        + glados_settings.settings["assistant"]["trigger_word"].capitalize()
    )

    # eye_position_default()
    main_loop()


def main_loop():
    # Local keyword detection loop
    speech = LiveSpeech(
        lm=False,
        keyphrase=glados_settings.settings["assistant"]["trigger_word"],
        kws_threshold=1e-20,
    )

    for phrase in speech:
        print("\nKeyphrase detected!")
        handle_speech()
        print("\nWaiting for trigger...")


def test1():
    speak("test 1", cache=True)
    process_command("my shopping list")


def test2():
    speak("test 2", cache=True)

    handle_speech()


a = input("0 for start up, 1-9 for test:")

if a == "1":
    test1()
elif a == "2":
    test2()
else:
    start_up()
