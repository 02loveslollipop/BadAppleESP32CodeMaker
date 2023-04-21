import sys
import cv2
import numpy as np
import os
import optFunc as c
import math

def tryVideoCapture(path: str):
    try:
        media = cv2.VideoCapture(path)
        return media
    except:
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
    clear()
    print(buffer)

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
            frameCounter += 1
        elif byteStream[i] == 0xFE:
            line = byteStream[i+1]
            deprecateNextByte = True
        elif deprecateNextByte:
            deprecateNextByte = False
        else:            
            frameBuffer[line][byteStream[i]] = not frameBuffer[line][byteStream[i]]
            if frameBuffer[line][byteStream[i]]:
                ImageBuffer[line][byteStream[i]][0] = 255
                ImageBuffer[line][byteStream[i]][1] = 255
                ImageBuffer[line][byteStream[i]][2] = 255
            else:
                ImageBuffer[line][byteStream[i]][0] = 0
                ImageBuffer[line][byteStream[i]][1] = 0
                ImageBuffer[line][byteStream[i]][2] = 0

def findDeltas(frameListBuffer: list, width: int, height: int, ):
    #Black is False
    #White is True
    currentFrame = np.full((width,height),fill_value=True,dtype=bool)
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
        #printFrame(currentFrame) #this is just for test
    return byteStream, byteStreamPointer

def findInterlacedDeltas(frameListBuffer: list, width: int, height: int,interlaceState: bool = True):
    #Black is False
    #White is True
    currentFrame = np.full((width,height),fill_value=True,dtype=bool)
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
                elif not interlaceState and (i%2) == 0:
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
                elif interlaceState and (i%2) != 0:
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
        if interlaceState:
            interlaceState = False
        else:
            interlaceState = True
                    
        #printFrame(currentFrame) #this is just for test
    return byteStream, byteStreamPointer

def findScanLineDeltas(frameListBuffer: list, width: int, height: int):
    #Black is False
    #White is True
    currentFrame = np.full((width,height),fill_value=True,dtype=bool)
    byteStream = []
    byteStreamPointer = -1

    for frame in frameListBuffer:
        byteStream.append(0xFF)
        byteStreamPointer += 1
        if np.array_equal(frame,currentFrame):
            pass
        else:
            for i in range(width):
                if np.array_equal(frame[i],currentFrame[i]) or (i%2) == 0:
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
        #printFrame(currentFrame) #this is just for test
    return byteStream, byteStreamPointer

#TODO: implementar el dithering en el algoritmo, y ver cuanto influye en el tamaño del delta map

args = sys.argv
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', './media/1.m4', '-r', '100x64', '-lc']
if len(args) < 1:
    print("There is not a valid path for the video, please check the arguments")
    exit()
else:
    threshold = 60
    dither = False
    scanLine = False
    deprecateNextArg = False
    customResolution = False
    pathReady = False
    ready = False
    resize = False
    resampleAlgoritm = cv2.INTER_LANCZOS4
    batchExport = False
    saveAsPhoto = False
    testResolution = False
    interlaced = False
    for i in range(len(args)):
        if i == 0:
            pass
        elif args[i] == "-r":
            height = int(args[i+1].split("x")[0])
            width = int(args[i+1].split("x")[1])
            customResolution = True
            deprecateNextArg = True
        elif args[i] == "-ts":
            frame = int(args[i+1])
            testResolution = True
            deprecateNextArg = True
        elif args[i] == "-t":
            threshold = int(args[i+1])
            deprecateNextArg = True 
        elif args[i] == "-scanLine" and not interlaced:
            scanLine = True
        elif args[i] == "-scanLine" and  interlaced:
            print("You can't use scan lines and interlaced at the same time")
            exit()
        elif args[i] == "-interlacedEven":
            interlaced = True
            evenFrames = True
        elif args[i] == "-interlacedOdd":
            interlaced = True
            evenFrames = False 
        elif args[i] == "-s":
            saveAsPhoto = True
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
            fps = sourceMedia.get(cv2.CAP_PROP_FPS)
            ready = True
        elif args[i].startswith("-") and not "/" in args[i] and not "\\" in args[i] : 
            print(f"{args[i]} has not been recognize as a valid argument")
            exit()
        elif args[i].endswith[".py"] or args[i].endswith[".pyw"]:
            pass
        else:
            path = args[i]

if ready:
    resize = True
    pass
elif pathReady:
    resize = True
    sourceMedia = tryVideoCapture(path=path)
    fps = sourceMedia.get(cv2.CAP_PROP_FPS)
else:
    print("There is not a valid path for the video, please check the arguments")
    exit()

if testResolution: saveTestPhoto(sourceMedia=sourceMedia,frame=frame,height=height,width=width,resampleAlgoritm=resampleAlgoritm)

if not batchExport:
    clear()
    print(f"-------SUMMARY-------\nFile path: {path}\nInterlaced: {interlaced}\nDither: {dither}\nSave as photo: {saveAsPhoto}\nResample algoritm: {resampleAlgoritm}\nHeight: {height}\nWidth: {width}\nPress any button to start the convertion")
    input()
    
if resize:
    frameListBuffer = c.convertionWithResize(width=width,height=height,video=sourceMedia,resample=resampleAlgoritm,threshold=threshold)
else:
    frameListBuffer = c.convertion(width=width,height=height,video=sourceMedia,threshold=threshold)

if not batchExport:
    clear()
    print("Finding deltas and creating byteStream")
 
if interlaced:
    byteStream, byteStreamPointer = findInterlacedDeltas(frameListBuffer=frameListBuffer, width=width, height=height,interlaceState= evenFrames)
elif scanLine:
    byteStream, byteStreamPointer = findScanLineDeltas(frameListBuffer=frameListBuffer, width=width, height=height)
else:
    byteStream, byteStreamPointer = findDeltas(frameListBuffer=frameListBuffer, width=width, height=height)


if not batchExport:
    clear()

while True: #Save "result.bin"
    try:
        print("Trying to save result.bin")  
        with open ('result.bin','wb') as f:
            f.write(bytearray(byteStream))
            print("result.bin saved susccesfuly")
            break    
    except PermissionError:
        print("File is in use, please close it to save the binary and then press enter")
        input()
        clear()




while True: #Save "byteStream.h"
    print("Trying to save byteStream.h")      
    try:
        with open ('esp32badApple/byteStream.h','w') as f:
            f.write(f"const int delayMS = {math.trunc((1/fps)*1000)};\nconst int delayUS = {(((1/fps)*1000)-math.trunc((1/fps)*1000))*1000};\nconst uint32_t totalFrames = {byteStreamPointer};\n"+"PROGMEM const unsigned char byteStream[] ={\n")
            buffer = ""
            for currentByte in byteStream:
                buffer += str(currentByte) + ","
            buffer = buffer[:-1]
            buffer += "};"
            f.write(buffer)
            print("byteStream.h saved susccesfuly")
            break
    except PermissionError:
        print("File is in use, please close it to save the binary and then press enter")
        input()
        clear()  


if saveAsPhoto:
    print("Saving result as images")
    TestSavedImages(byteStream=byteStream,height=height,width=width)
    print("Images saved susccesfuly")


        
             
            