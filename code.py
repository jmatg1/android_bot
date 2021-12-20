import os
import time
from datetime import datetime
from PIL import Image
from tkinter import Tk, Button, Text, END
from tkinter import ttk
import re

import threading
from subprocess import check_output

tkWindow = Tk()
tkWindow.geometry('400x250')
tkWindow.title('Android Bot By Jmatg1')


class Bot:
    work = 1
    screenshot = 0
    t1 = 0
    fight = 1
    device = 0
    controlsUnderBuilding = [(576, 431), (1059, 768)]

    # def __init__(self):
    def shadeVariation(self, col, col2, shade=0):
        if shade == 0:
            return col == col2
        rezult = (abs(col[0] - col2[0]), abs(col[1] - col2[1]), abs(col[2] - col2[2]))
        shadowCount = 0
        for rgb in rezult:
            if rgb <= shade:
                shadowCount += 1
        return shadowCount == 3

    def getXYByColor(self, color, isGetSCreen=True, shade=0, startXY=(0, 0), endXY=(0, 0)):
        if (isGetSCreen):
            self.getScreen()
        img = self.screenshot
        coordinates = False

        if endXY[0] == 0 and endXY[1] == 0:
            endXY = (img.size[0], img.size[1])
        for x in range(img.size[0]):
            if not (startXY[0] < x < endXY[0]):
                continue

            for y in range(img.size[1]):
                if not (startXY[1] < y < endXY[1]):
                    continue
                if self.shadeVariation(img.getpixel((x, y))[:3], color, shade):
                    coordinates = (x, y)
                    continue
        return coordinates

    def pixelSearch(self, x1, y1, color):  # x2=1600, y2=900,
        # im = ImageOps.crop(im, (x1, y1, x2, y2))
        colorPixel = self.screenshot.getpixel((x1, y1))[:3]
        if colorPixel == color:
            return True
        else:
            return False

    def getScreen(self):
        self.shell(f'/system/bin/screencap -p /sdcard/{self.device}-screenshot.png')
        # os.system('hd-adb shell /system/bin/screencap -p /sdcard/screenshot.png')
        # Using the adb command to upload the screenshot of the mobile phone to the current directory

        os.system(f'hd-adb -s {self.device} pull /sdcard/{self.device}-screenshot.png')
        try:
            self.screenshot = Image.open(f"{self.device}-screenshot.png")
        except ValueError:
            print(ValueError)
            self.getScreen()

    def getPixelColor(self, x1, y1):
        self.getScreen()
        im = Image.open(f"{self.device}-screenshot.png")
        # im1 = ImageOps.crop(im, (0, 0, 1000, 300))
        # im1.show()
        pixelRGB = im.getpixel((x1, y1))[:3]
        return pixelRGB

    def click(self, x, y, timer=True):
        if (timer):
            time.sleep(1)
        # os.system(f'hd-adb shell input tap {x} {y}')
        self.shell(f'input tap {x} {y}')
        if (timer):
            time.sleep(1)

    # Здесь главный цикл. Проверяется на каждый экран в игре и выполняется дейсвие в зависимости от экрана
    def main(self):
        while self.work:

            self.getScreen()
            self.skipAds() #Пропускаем рекламу и прочие предложения

            if self.isMainScreen(): # Главный экран
                self.log('Main Screen')
                if self.isEventActive():
                    self.log('isEventActive')
                else:
                    self.clickPlay()
                continue

    def skipAds(self):
        if self.pixelSearch(926, 770, (110, 204, 22)):  # Skip league
            self.click(926, 770)
            time.sleep(3)
            self.keyBack()
        if self.pixelSearch(566, 560, (238, 72, 35)):  # Повышение level
            self.click(566, 560)

    def isMainScreen(self):
        if self.pixelSearch(1345, 35, (25, 52, 135)):  # 1340, 30, 1350, 40,
            return True
        else:
            return False

    def isEventActive(self):
        if self.pixelSearch(1345, 35, (25, 52, 135)):  # 1340, 30, 1350, 40,
            return True
        else:
            return False

    def clickPlay(self):
        self.click(1366, 866)

    def clickBack(self):
        self.click(67, 50)

    def keyW(self, ms):
        self.shell(f'input swipe 250 700 250 600 {ms}')

    def keyQ(self):
        self.shell(f'input keyevent 45')

    def keyE(self):
        self.shell(f'input keyevent 33')

    def keyBack(self):
        self.shell(f'input keyevent 4')

    def start(self):
        self.device = inputDevice.get()
        self.work = 1
        self.t1 = threading.Thread(target=self.main, args=[])
        self.t1.start()

    def stop(self):
        self.work = 0

    def closeWindow(self):
        self.work = 0
        tkWindow.destroy()

    def shell(self, cmd):
        os.system(f'hd-adb -s {self.device} shell {cmd}')

    def log(self, value):
        timeVal = datetime.now().strftime("%D %H:%M:%S")
        logString = "%s %s" % (timeVal, value)
        text.insert(END, logString + " \r\n")
        text.see("end")
        f = open("log.txt", "a")
        f.write(logString + " \r")
        f.close()

    def selectedDevice(self, event):
        self.device = inputDevice.get()


bot = Bot()
buttonStart = Button(tkWindow, text='Start', command=bot.start)
buttonStart.pack()
buttonStop = Button(tkWindow, text='Stop', command=bot.stop)
buttonStop.pack()

tkWindow.protocol("WM_DELETE_WINDOW", bot.closeWindow)
devList = check_output("hd-adb devices")
text = Text(tkWindow, height=10, width=50)
text.insert(END, devList)

print(devList)
devListArr = re.compile(r'emulator-\d\d\d\d').findall(str(devList))
print('ARRAY DEVICES', devListArr)
rezArr = []
for x in devListArr:
    if (x.startswith('emulator-')):
        rezArr.append(x)
print(rezArr)

inputDevice = ttk.Combobox(tkWindow, width=15)
inputDevice['values'] = rezArr
inputDevice.bind("<<ComboboxSelected>>", bot.selectedDevice)
inputDevice.current(0)
inputDevice.pack()
text.pack()

tkWindow.mainloop()
