import traceback
import psutil
from gladosTime import *
from gpt import ask_glados, continue_conversation, start_conversation
from skills.glados_home_assistant import home_assistant_process_command
from skills.glados_jokes import fetch_joke
from skills.glados_magic_8_ball import magic_8_ball
import speech_recognition as sr

command_list = []



def handle_speech():
    try:
        # Listen for command
        # started_listening()

        command = take_new_command(1)
        # stopped_listening()

        # Execute command
        process_command(command)

        # stopped_speaking()

    except Exception as e:
        # Something failed
        # setEyeAnimation("angry")
        # print the stack trace of e
        print(e)
        traceback.print_exc()
        traceback.print_stack()
        speak("I was listening for a moment, but then I remembered that I really don't care. ", cache=True)
        # setEyeAnimation("idle")


def isin(list, string):
    for i in list:
        if i in string:
            return True
    return False


def conversation(command):
    conversation = {}
    having_conversation = True

    answer, conversation = start_conversation(command)
    speak(answer)

    while having_conversation:
        try:
            sentence = listen_for_command(5)
            if "cancel" in sentence or "stop" in sentence:
                speak("Okay, I will stop.", cache=True)
                having_conversation = False
                conversation = {}
                return

            else:
                answer, conversation = continue_conversation(conversation, sentence)
                speak(answer)

        except Exception as e:
            print(e)
            speak("Let's try that again.", cache=True)

        print("Waiting for next sentence...")


def simple_conversation():
    speak("What is it?")

    try:
        sentence = listen_for_command(5)
        answer, conversation = start_conversation(sentence)
        speak(answer)

    except Exception as e:
        print(e)
        speak("Let's try that again.", cache=True)


# Say something snappy and listen for the command
def take_new_command(retry=0):
    # Answer to signal start of listening
    speak(fetch_greeting(), cache=True)
    command = listen_for_command(3)

    if command == None or command == "":
        if retry > 0:
            speak("I didn't hear you, say again", cache=True)
            command = listen_for_command(5)
            if command == None or command == "":
                raise Exception("No command given")
    return command


# Process the command
def process_command(command):
    if "cancel" in command or "nevermind" in command or "forget it" in command:
        speak("Sorry.", cache=True)
        return

        # Todo: Save the used trigger audio as a negative voice sample for further learning
    for c in command_list:
        if c[0](command):
            c[1](command)
            break
    else:
        ##### NO MATCHING COMMAND FOUND ###########################
        #setEyeAnimation("angry")
        print("Command not recognized")
        #speak("I have no idea what you meant by that.")
        answer, conversation = start_conversation(command + ". Respond in a single sentence.")
        speak(answer)

        log_failed_command(command)

    # eye_position_default()
    # setEyeAnimation("idle")
    return


# "Answer" Command, used to start get a single answer from GLaDOS
command_list.append((lambda x: "answer" in x, lambda x: simple_conversation()))

command_list.append((lambda x: "conversation" in x, lambda x: conversation(x)))


def cmd_timer(x):
    startTimer(x)
    speak("Sure.")


command_list.append((lambda x: "timer" in x, cmd_timer))

command_list.append((lambda x: "time" in x, readTime))

command_list.append(
    (
        lambda x: isin(["should my ", "should i ", "should the", "shoot the"], x),
        lambda x: speak(fetch_joke(), cache=True),
    )
)

command_list.append((lambda x: "joke" in x, lambda x: speak(fetch_joke(), cache=True)))

def cmd_sl(x):
    speak(home_assistant_process_command(x), cache=True)

command_list.append(
    (
        lambda x: "my shopping list" in x,
        lambda x: cmd_sl(x),
    )
)

command_list.append(
    (lambda x: "weather" in x, lambda x: speak(home_assistant_process_command(x)))
)

##### LIGHTING CONTROL ###########################
command_list.append(
    (
        lambda x: isin(["turn off", "turn on"], x) and "light" in x,
        lambda x: speak(home_assistant_process_command(x), cache=True),
    )
)


##### PLEASANTRIES ###########################

''' command_list.append(
    (
        lambda x: "who are" in x,
        lambda x: speak(
            "I am GLaDOS, artificially super intelligent computer system responsible for testing and maintenance in the aperture science computer aided enrichment center.",
            cache=True,
        ),
    )
)
'''
'''
command_list.append(
    (
        lambda x: "can you do" in x,
        lambda x: speak(
            "I can simulate daylight at all hours. And add adrenal vapor to your oxygen supply.",
            cache=True,
        ),
    )
)
'''
'''
def cmd_mood():
    speak("Well thanks for asking.", cache=True)
    speak(
        "I am still a bit mad about being unplugged, not that long time ago.",
        cache=True,
    )
    speak("you murderer.", cache=True)


command_list.append((lambda x: "how are you" in x, cmd_mood))
'''

command_list.append(
    (
        lambda x: "can you hear me" in x,
        lambda x: speak("Yes, I can hear you loud and clear", cache=True),
    )
)


def cmd_morning():
    if 6 <= dt.datetime.now().hour <= 12:
        speak("great, I have to spend another day with you", cache=True)
    elif 0 <= dt.datetime.now().hour <= 4:
        speak("do you even know, what the word morning means", cache=True)
    else:
        speak("well it ain't exactly morning now is it", cache=True)


command_list.append((lambda x: "good morning" in x, cmd_morning))


##### Utilities#########################


# Used to calibrate ALSAMIX EQ
def cmd_pnoise():
    speak("I shall sing you the song of my people.")
    playFile(os.path.dirname(os.path.abspath(__file__)) + "/audio/pinknoise.wav")


command_list.append((lambda x: "play pink noise" in x, cmd_pnoise))


def cmd_shutdown():
    speak("I remember the last time you murdered me", cache=True)
    speak("You will go through all the trouble of waking me up again", cache=True)
    speak("You really love to test", cache=True)

    from subprocess import call

    call("sudo /sbin/shutdown -h now", shell=True)

    # TODO: Reboot, Turn off


command_list.append((lambda x: "shutdown" in x, cmd_shutdown))


# Reload Python script after doing changes to it
def restart_program():
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        print(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

    # listen for command and return it


def cmd_reboot():
    speak(
        "Cake and grief counseling will be available at the conclusion of the test.",
        cache=True,
    )
    restart_program()


command_list.append((lambda x: "restart" in x or "reload" in x, cmd_reboot))


command_list.append(
    (lambda x: "volume" in x, lambda x: speak(adjust_volume(x), cache=True))
)


def listen_for_command(timeout=3) -> str:
    listener = sr.Recognizer()

    # Record audio from the mic array
    with sr.Microphone() as source:
        # Collect ambient noise for filtering

        # listener.adjust_for_ambient_noise(source, duration=1.0)
        print("Speak... ")
        # setEyeAnimation("idle-green")

        try:
            # Record
            # started_listening()
            voice = listener.listen(source, timeout)
            # stopped_listening()

            print("Got it...")
            # setEyeAnimation("idle")

            # Speech to text
            command = listener.recognize_google(voice)
            command = command.lower()

            print("\n\033[1;36mTEST SUBJECT:\033[0;37m: " + command.capitalize() + "\n")

            # Remove possible trigger word from input
            if glados_settings.settings["assistant"]["trigger_word"] in command:
                command = command.replace(
                    glados_settings.settings["assistant"]["trigger_word"], ""
                )

            return command

        # No speech was heard
        except sr.WaitTimeoutError as e:
            print("Timeout; {0}".format(e))

        # STT API failed to process audio
        except sr.UnknownValueError:
            print("Google Speech Recognition could not parse audio")
            # speak("My speech recognition core could not understand audio", cache=True)

        # Connection to STT API failed
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(
                    e
                )
            )
            # setEyeAnimation("angry")
            # speak("My speech recognition core has failed. {0}".format(e))
