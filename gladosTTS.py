import os
import traceback
import wave
from random import randint
import _thread as thread
from threading import Timer
from gladosSerial import *
from gladosServo import *
from glados_functions import *
import sys
import urllib.parse
import re
import json
import random
from sys import modules as mod

try:
    import winsound
except ImportError:
    from subprocess import call

import shutil
from subprocess import call

import glados_settings
glados_settings.load_from_file()

if(glados_settings.settings["tts"]["api"] == ''): from glados_tts.engine import *
from glados_functions import *


synthFolder = glados_settings.settings["tts"]["cache_folder"] + "/"


def playFile(filename):
	# Play audio file
	print(filename)
	if "winsound" in mod:
		winsound.PlaySound(filename, winsound.SND_FILENAME)
	else:
		call(["aplay","-q", filename])
	

# Turns units etc into speakable text
def cleanTTSLine(line):
	line = line.replace("sauna", "incinerator")
	line = line.replace("'", "")
	line = line.lower()

	if re.search("-\d", line):
		line = line.replace("-", "negative ")
	
	return line

# Cleans filename for the sample
def cleanTTSFile(line):
	filename = "GLaDOS-tts-"+cleanTTSLine(line).replace(" ", "-")
	filename = filename.replace("!", "")
	filename = filename.replace("°c", "degrees celcius")
	filename = filename.replace("?", "")
	filename = filename.replace(":", "")
	filename = filename.replace(",", "")+".wav"
	
	return filename

# Return the path of a TTS sample if found in the library
def checkTTSLib(line):
	line = cleanTTSLine(line)
	filename = cleanTTSFile(line)

	if os.path.isfile(synthFolder+filename):
		return synthFolder+filename
	else:
		return False

# Get GLaDOS TTS Sample
def fetchTTSSample(line):
	
	# Local TTS Engine
	if(glados_settings.settings["tts"]["api"] == ''):	
		if(glados_tts(cleanTTSLine(line)) == True):
			print('Success: TTS sample "'+line+'" fetched')
			setEyeAnimation("idle")
			return True
	
	# Remote TTS Engine API
	else:
		text = urllib.parse.quote(cleanTTSLine(line))
		TTSCommand = 'curl -L --retry 5 --get --fail -o audio/GLaDOS-tts-temp-output.wav '+glados_settings.settings["tts"]["api"]+text
		setEyeAnimation("wait")
		TTSResponse = os.system(TTSCommand)

		if(TTSResponse == 0):
			print('Success: TTS sample "'+line+'" fetched')
			setEyeAnimation("idle")
			return True

	# Complain about speech synthesis core
	setEyeAnimation("angry")
	playFile(os.path.dirname(os.path.abspath(__file__))+"/audio/GLaDOS-tts-error.wav")
	return False


## Speak out the line
def speak(line, cache=False):
	# started_speaking()

	line = cleanTTSLine(line)
	# Generate filename
	file = checkTTSLib(line)

	# Check if file exists
	if file:
		# Animate eye
		if eye_position_script(line) == False:
			eye_position_random()

		print("\033[1;33mGLaDOS:\033[0;37m " + line.capitalize())
		# Speak from cache
		playFile(file)

	# TTS Sample not in cache...
	else:
		print("\033[1;94mINFO:\033[;97m The audio sample does not exist, generating...")
		setEyeAnimation("wait")

		# Generate line and save to TTS-folder
		if(fetchTTSSample(line)):

			setEyeAnimation("idle")

			if eye_position_script(line) == False:
				eye_position_random()

			print("\033[1;33mGLaDOS:\033[0;37m " + line.capitalize())

	    	# Speak
			playFile("./audio/GLaDOS-tts-temp-output.wav")
			
			if(cache):
				try:
					shutil.copyfile("./audio/GLaDOS-tts-temp-output.wav", synthFolder+cleanTTSFile(line))

				except Exception as e:
					print("Error: Could not cache TTS sample")
					traceback.print_exc()

	#stopped_speaking()
	#eye_position_default()


# Load greetings from a json file into a "playlist"
file = open("skills/glados_greetings.json")
greetings = json.load(file)

# Shuffle the list
random.shuffle(greetings)

# Global variable to make sure same greeting does not come up twice in a row
greeting_index = 0;

# Fetch the next greeting from the playlist
def fetch_greeting():
	global greeting_index

	greeting = greetings[greeting_index]["greeting"]
	greeting_index += 1;

	# Loop the "playlist"	
	if(greeting_index >= len(greetings)):
		greeting_index = 0
		random.shuffle(greetings)

	return greeting
