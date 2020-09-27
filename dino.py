import os
import subprocess
import threading
import time
import RPi.GPIO as GPIO
import random
import sys
import traceback

PIN_LIGHT=23
PIN_BUTTON=24

INACTIVITY_TIMEOUT=300

songsets = {"all": ["sounds/zapsplat_animals_dinosaur_herbivore_eating_plant_001_20180.mp3",
                    "sounds/zapsplat_animals_dinosaur_herbivore_eating_plant_002_20181.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_001_10838.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_001_10838.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_002_10839.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_003_10840.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_004_10841.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_005_10842.mp3"
                    ],

            "one": ["sounds/zapsplat_animals_dinosaur_herbivore_eating_plant_001_20180.mp3",
                    "sounds/zapsplat_animals_dinosaur_herbivore_eating_plant_002_20181.mp3"],

            "two": ["sounds/zapsplat_animal_dinosuar_vocalisation_growl_001_10838.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_001_10838.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_002_10839.mp3"],

            "three": ["sounds/zapsplat_animal_dinosuar_vocalisation_growl_003_10840.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_004_10841.mp3",
                    "sounds/zapsplat_animal_dinosuar_vocalisation_growl_005_10842.mp3"]
}

class dino(threading.Thread):
    def __init__(self, songList, autoShutdown=False, invert=False, quiet=False, pinLight=PIN_LIGHT, pinButton=PIN_BUTTON):
        threading.Thread.__init__(self)
        self.songList = songList
        self.daemon = True
        self.pinLight = pinLight
        self.pinButton = pinButton
        self.ledPeriod = 0.5
        self.ledState = False
        self.lastButtonState = False
        self.plays = []
        self.active = True
        self.autoShutdown = autoShutdown
        self.invert = invert
        self.quiet = quiet

        self.lastLedFlipTime = time.time()

        self.lastButtonElapsed = 0
        self.lastTickTime = time.time()

        GPIO.setup(self.pinButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pinLight, GPIO.OUT)

        
    def playRandomSong(self):
        song = random.choice(self.songList)
 
        if self.quiet:
            song_cmd = "mpg123 --scale 2000  %s" % song
        else:
            song_cmd = "mpg123 %s" % song

        data = {}
        data["fn"] = song_cmd
        data["p"] = subprocess.Popen(song_cmd, shell=True)
        self.plays.append(data)


    def buttonDownEvent(self):
        if len(self.plays)<10:
            self.playRandomSong()
        else:
            print "plays = %d" % len(self.plays)


    def cancel(self, tag=None):
        for p in self.plays[:]:
            if (not tag) or (p.get(tag)==tag):
                p["p"].terminate()


    def run(self):
        while self.active:
            if (time.time()-self.lastLedFlipTime) > self.ledPeriod:
                self.lastLedFlipTime = time.time()
                self.ledState = not self.ledState
                GPIO.output(self.pinLight, self.ledState)

            buttonState = GPIO.input(self.pinButton)

            if self.invert:
                buttonState = not buttonState

            if (not buttonState) and (self.lastButtonState):
                self.buttonDownEvent()
                self.lastButtonElapsed = 0
            self.lastButtonState = buttonState

            for p in self.plays[:]:
                if p["p"].poll() is not None:
                    self.plays.remove(p)

            # Weird shit happens with system time at bootup, and sometimes we see
            # a huge jump in timestamp, that would trip the inactivity timer. So
            # limit it so we can only increment by 1 second at a time.
            tNowInt = int(time.time())
            if (tNowInt != self.lastTickTime):
                self.lastButtonElapsed += 1
                self.lastTickTime = tNowInt

            tNow = time.time()
            if (self.autoShutdown) and (self.lastButtonElapsed>INACTIVITY_TIMEOUT):
                print "lastButtonElapsed = %d, triggering autoshutdown" % self.lastButtonElapsed
                try:
                    os.system("/sbin/shutdown -h now")
                except:
                    traceback.print_exc()
                print "Exiting"
                sys.exit(0)

            time.sleep(0.01)
        GPIO.output(self.pinLight, True)


def main():
    songset = "all"
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            if not (arg.startswith("-")):
                songset = arg

    autoShutdown = False
    if "--autoshutdown" in sys.argv:
        autoShutdown = True

    invert = False
    if "--invert" in sys.argv:
        invert = True

    quiet = False
    if "--quiet" in sys.argv:
        quiet = True

    GPIO.setmode(GPIO.BCM)
    threadDino = dino(songsets[songset], autoShutdown=autoShutdown, invert=invert, quiet=quiet)
    threadDino.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        threadDino.cancel()
        threadDino.activ = False
        time.sleep(0.1)


if __name__ == "__main__":
    main()
