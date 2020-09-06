import subprocess
import threading
import time
import RPi.GPIO as GPIO
import random

PIN_LIGHT=23
PIN_BUTTON=24

songsets = {"all": ["sounds/zapsplat_animals_dinosaur_herbivore_eating_plant_001_20180.mp3",
                    "sounds/zapsplat_animals_dinosaur_herbivore_eating_plant_002_20181.mp3"]

}

class dino(threading.Thread):
    def __init__(self, songList, pinLight=PIN_LIGHT, pinButton=PIN_BUTTON):
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

        self.lastLedFlipTime = time.time()

        GPIO.setup(self.pinButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pinLight, GPIO.OUT)

        
    def playRandomSong(self):
        song = random.choice(self.songList)

        song_cmd = "mpg123 %s" % song
        data = {}
        data["fn"] = song_cmd
        data["p"] = subprocess.Popen(song_cmd, shell=True)
        self.plays.append(data)


    def buttonDownEvent(self):
        self.playRandomSong()


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
            if (not buttonState) and (self.lastButtonState):
                self.buttonDownEvent()
            self.lastButtonState = buttonState

            for p in self.plays[:]:
                if p["p"].poll() is not None:
                    self.plays.remove(p)

            time.sleep(0.01)
        GPIO.output(self.pinLight, True)


def main():
    GPIO.setmode(GPIO.BCM)
    threadDino = dino(songsets["all"])
    threadDino.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        threadDino.cancel()
        threadDino.active=False
        time.sleep(0.1)


if __name__ == "__main__":
    main()
