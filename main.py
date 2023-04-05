import sys
import cv2
import numpy as np
from PIL import Image
import os
import optFunc as c
import csv

threshold = 60

def tryVideoCapture(path: str):
    try:
        media = cv2.VideoCapture(path)
        return media
    except FileNotFoundError:
        print("cv2 could not open the video file, please check the path or if the file is in use")
        exit()

def printFrame(frame: np.ndarray):
    buffer = ""
    for line in frame:
        for dot in line:
            if dot:
                buffer += "█"
            else:
                buffer += "░"
        buffer += "\n"
    return str(buffer)

def saveTestPhoto(sourceMedia,frame: int,height: int,width: int,resampleAlgoritm: int):
    success = True
    con = 0
    while success and frame != con:
        success,img = sourceMedia.read()
        con += 1
    imgTest = cv2.resize(src=img,dsize=(height,width),interpolation=resampleAlgoritm)
    cv2.imwrite(filename="test.png",img=imgTest)
    return
    
def clear():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def TestSavedImages(byteStream: bytearray,width: int,height: int):
    frameBuffer = np.zeros((width,height),dtype=bool)
    ImageBuffer = np.full((width,height,3),255.0)
    frameCounter = 0
    deprecateNextByte = False
    for i in range(len(byteStream)-1):
        if byteStream[i] == 0xFF:
            line = byteStream[i+1]
            deprecateNextByte = True
            cv2.imwrite(filename=f"{frameCounter:05d}.png",img=ImageBuffer)
            frameCounter += 1 #Esto no hace falta en el codigo del ESP32
        elif byteStream[i] == 0xFE:
            line = byteStream[i+1]
            deprecateNextByte = True
        elif deprecateNextByte:
            deprecateNextByte = False
        else:            
            frameBuffer[line][byteStream[i]] = not frameBuffer[line][byteStream[i]]
            #De aca pa abajo solo es para pasarlo a imagen, en el caso del esp32 no es necesario
            if frameBuffer[line][byteStream[i]]:
                ImageBuffer[line][byteStream[i]][0] = 0
                ImageBuffer[line][byteStream[i]][1] = 0
                ImageBuffer[line][byteStream[i]][2] = 0
            else:
                ImageBuffer[line][byteStream[i]][0] = 255
                ImageBuffer[line][byteStream[i]][1] = 255
                ImageBuffer[line][byteStream[i]][2] = 255
        
        
        
        


#TODO: implementar el dithering en el algoritmo, y ver cuanto influye en el tamaño del delta map

args = sys.argv
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', './media/1.mp4', '-r', '100x64', '-lc']
if len(args) < 1:
    print("There is not a valid path for the video, please check the arguments")
    exit()
else:
    dither = False
    deprecateNextArg = False
    customResolution = False
    pathReady = False
    ready = False
    resize = False
    resampleAlgoritm = Image.LANCZOS #Lanczos set as default
    batchExport = False
    saveAsPhoto = False
    testResolution = False
    for i in range(len(args)):
        if i == 0:
            pass
        elif(args[i] == "-r"):
            height = int(args[i+1].split("x")[0])
            width = int(args[i+1].split("x")[1])
            customResolution = True
            deprecateNextArg = True
        elif args[i] == "--testInFrame":
            frame = int(args[i+1])
            testResolution = True
            deprecateNextArg = True
        elif args[i] == "-d":
            dither = True
        elif args[i] == "-sv":
            dither = True
        elif args[i] == "-lc" and resize == False:
            resampleAlgoritm = cv2.INTER_LANCZOS4
            resize = True
        elif args[i] == "-lc" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-nr" and resize == False:
            resampleAlgoritm = cv2.INTER_NEAREST
            resize = True
        elif args[i] == "-nr" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-bc" and resize == False:
            resampleAlgoritm = cv2.INTER_CUBIC
            resize = True
        elif args[i] == "-bc" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-bl" and resize == False:
            resampleAlgoritm = cv2.INTER_LINEAR
            resize = True
        elif args[i] == "-bl" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-b2" and resize == False:
            resampleAlgoritm = cv2.INTER_BITS2
            resize = True
        elif args[i] == "-b2" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-ar" and resize == False:
            resampleAlgoritm = cv2.INTER_AREA
            resize = True
        elif args[i] == "-ar" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif deprecateNextArg:
            deprecateNextArg = False
        elif args[i] == "-bt":
            batchExport=True
        elif not customResolution and not ready:
            path = args[i]
            sourceMedia = tryVideoCapture(path=path)
            height = int(sourceMedia.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(sourceMedia.get(cv2.CAP_PROP_FRAME_WIDTH))
            ready = True
        elif args[i].startswith("-") and not "/" in args[i] and not "\\" in args[i] : 
            print(f"{args[i]} has not been recognize as a valid argument")
        elif args[i].endswith[".py"] or args[i].endswith[".pyw"]:
            pass
        else:
            path = args[i]

if ready:
    pass
elif not ready and pathReady: sourceMedia = tryVideoCapture(path=path)
else:
    print("There is not a valid path for the video, please check the arguments")
    exit()

if testResolution: saveTestPhoto(sourceMedia=sourceMedia,frame=frame,height=height,width=width,resampleAlgoritm=resampleAlgoritm)

if not batchExport:
    clear()
    print(f"-------SUMMARY-------\nFile path: {path}\nDither: {dither}\nResample algoritm: {resampleAlgoritm}\nHeight: {height}\nWidth: {width}\nPress any button to start the convertion")
    input()
    
if resize:
    frameListBuffer = c.convertionWithResize(width=width,height=height,video=sourceMedia,resample=resampleAlgoritm,threshold=threshold)
else:
    frameListBuffer = c.convertion(width=width,height=height,video=sourceMedia,threshold=threshold)

if not batchExport:
    clear()
    print("Finding deltas and creating deltaFrameStream")

#Black is False
#White is True

currentFrame = np.zeros((width,height),dtype=bool)
byteStream = []
byteStreamPointer = -1

for frame in frameListBuffer:
    byteStream.append(0xFF)
    byteStreamPointer += 1
    if np.array_equal(frame,currentFrame):
        pass
    else:
        for i in range(width):
            if np.array_equal(frame[i],currentFrame[i]):
                pass
            else:
                if byteStream[byteStreamPointer] == 0xFF:
                    byteStream.append(i)
                    byteStreamPointer += 1
                else:
                    byteStream.append(0xFE)
                    byteStream.append(i)
                    byteStreamPointer += 2
                for j in range(height):
                    if frame[i][j] != currentFrame[i][j]:
                        byteStream.append(j)
                        currentFrame[i][j] = not currentFrame[i][j]
                        byteStreamPointer += 1

if not batchExport:
    clear()

while True: #Save "result.bin"
    try:
        print("Trying to save result.bin")  
        with open ('result.bin','wb') as f:
            f.write(bytearray(byteStream))
            break    
    except PermissionError:
        print("File is in use, please close it to save the binary and then press enter")
        input()
        clear()
print("result.bin saved susccesfuly")

TestSavedImages(byteStream=byteStream,height=height,width=width)


        
             
            