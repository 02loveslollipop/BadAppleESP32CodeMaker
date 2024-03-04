import sys
import cv2
import numpy as np
import os
import optFunc as c
import math
from collections import deque   


def tryVideoCapture(path: str):
    try:
        media = cv2.VideoCapture(path)
        return media
    except:
        print("cv2 could not open the video file, please check the path or if the file is in use")
        exit()

def printFrame(frame: np.ndarray) :
    
    buffer = ""
    for line in frame:
        for dot in line:
            if dot:
                buffer += "██"
            else:
                buffer += "░░"
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
  
def clear() -> None:
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def TestSavedVideo(byteStream: list, width: int, height: int) -> None:
    frameBuffer = np.ones((width, height), dtype=bool) # all True
    #imageBuffer all black
    ImageBuffer = np.zeros((width, height, 3), dtype=np.uint8)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # or use 'mp4v'
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height), False)

    deprecatedBytes = 0
    firstFF = False
    line = 0
    i = 0
    while i < len(byteStream)-1:
        if(deprecatedBytes > 0):
            deprecatedBytes -= 1
        elif byteStream[i] == 0xFF:
            if firstFF:
                out.write(ImageBuffer)  # write frame to video
                ImageBuffer = np.zeros((width, height, 3), dtype=np.uint8)  # reset ImageBuffer for next frame
                firstFF = False
                i -= 1
            else:
                line = byteStream[i + 1]
                deprecatedBytes += 1
                firstFF = True
        elif byteStream[i] == 0xFE:
            line = byteStream[i + 1]
            deprecatedBytes += 1
        elif byteStream[i] == 0xFD:
            first = byteStream[i + 1]
            last = byteStream[i + 2]
            deprecatedBytes += 2
            for j in range(last - first + 1):
                frameBuffer[line][j + first] = not frameBuffer[line][j + first]
                if frameBuffer[line][j + first]:
                    ImageBuffer[line][j + first] = [0, 0, 0]  # Black
                else:
                    ImageBuffer[line][j + first] = [255, 255, 255]  # White
        else:
            frameBuffer[line][byteStream[i]] = not frameBuffer[line][byteStream[i]]
            if frameBuffer[line][byteStream[i]]:
                ImageBuffer[line][byteStream[i]] = [0, 0, 0]  # Black
            else:
                ImageBuffer[line][byteStream[i]] = [255, 255, 255]  # White
        i += 1

    # Save the last frame
    if firstFF:
        out.write(np.uint8(ImageBuffer))

    # Release the VideoWriter when done
    out.release()

def TestSavedImages(byteStream: list, width: int, height: int) -> None:
    frameBuffer = np.ones((width, height), dtype=bool)
    ImageBuffer = np.zeros((width, height, 3), dtype=np.uint8)

    deprecatedBytes = 0
    firstFF = False
    line = 0
    frameCount = 0
    i = 0
    while i < len(byteStream)-1:
        if(deprecatedBytes > 0):
            deprecatedBytes -= 1
        elif byteStream[i] == 0xFF:
            if firstFF:
                cv2.imwrite(f'frame_{frameCount}.png', np.uint8(ImageBuffer))  # save frame as image
                firstFF = False
                frameCount += 1
                i -= 1
            else:
                line = byteStream[i + 1]
                deprecatedBytes += 1
                firstFF = True
        elif byteStream[i] == 0xFE:
            line = byteStream[i + 1]
            deprecatedBytes += 1
        elif byteStream[i] == 0xFD:
            first = byteStream[i + 1]
            last = byteStream[i + 2]
            deprecatedBytes += 2
            for j in range(last - first + 1):
                frameBuffer[line][j + first] = not frameBuffer[line][j + first]
                if frameBuffer[line][j + first]:
                    ImageBuffer[line][j + first] = [255, 255, 255]
                else:
                    ImageBuffer[line][j + first] = [0, 0, 0]
        else:
            frameBuffer[line][byteStream[i]] = not frameBuffer[line][byteStream[i]]
            if frameBuffer[line][byteStream[i]]:
                ImageBuffer[line][byteStream[i]] = [255, 255, 255]
            else:
                ImageBuffer[line][byteStream[i]] = [0, 0, 0]
        i += 1

    # Save the last frame
    if firstFF:
        cv2.imwrite(f'frame_{frameCount}.png', np.uint8(ImageBuffer))

def findDeltas(frameListBuffer: list, width: int, height: int) -> list:
    currentFrame = np.full((width,height),fill_value=True,dtype=bool)
    byteStream = deque()
    #Black is False
    #White is True
    for frame in frameListBuffer:
        byteStream.append(0xFF)
        if not np.array_equal(frame,currentFrame):
            for i in range(width):
                if not np.array_equal(frame,currentFrame):
                    if byteStream[-1] == 0xFF:
                        byteStream.append(i)
                    else:
                        byteStream.extend([0xFE, i])
                    diff_indices = np.where(frame[i] != currentFrame[i])[0]
                    byteStream.extend(diff_indices)
                    currentFrame[i, diff_indices] = frame[i, diff_indices]

    while byteStream[0] == 0xFF and byteStream[1] == 0xFF:
        byteStream.popleft()

    return list(byteStream)

def findInterlacedDeltas(frameListBuffer: list, width: int, height: int,interlaceState: bool = True) -> list:
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
                        byteStream.extend([0xFE,i])
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
                        byteStream.extend([0xFE,i])
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
def findScanLineDeltas(frameListBuffer: list, width: int, height: int) -> list:
    currentFrame = np.full((width,height),fill_value=True,dtype=bool)
    byteStream = deque()

    for frame in frameListBuffer:
        byteStream.append(0xFF)
        if not np.array_equal(frame,currentFrame):
            for i in range(width):
                if (not np.array_equal(frame,currentFrame)) and (i%2) != 0:
                    if byteStream[-1] == 0xFF:
                        byteStream.append(i)
                    else:
                        byteStream.extend([0xFE, i])
                    diff_indices = np.where(frame[i] != currentFrame[i])[0]
                    byteStream.extend(diff_indices)
                    currentFrame[i, diff_indices] = frame[i, diff_indices]


    while byteStream[0] == 0xFF and byteStream[1] == 0xFF:
        byteStream.popleft()

    return list(byteStream)
def findScanLineDeltasCompressed(frameListBuffer: list, width: int, height: int) -> list:
    #Black is False
    #White is True
    currentFrame = np.full((width,height),fill_value=True,dtype=bool)
    byteStream = deque()

    for frame in frameListBuffer:
        byteStream.append(0xFF)
        
        if not np.array_equal(frame,currentFrame):
            for i in range(width):
                is_scanline = (i%2) != 0    
                if not np.array_equal(frame[i],currentFrame[i]) and is_scanline:
                    if byteStream[-1] == 0xFF:
                        byteStream.append(i)
                    else:
                        byteStream.extend([0xFE, i])
                    diff_indices = np.where(frame[i] != currentFrame[i])[0]
                    byteStream.extend(diff_indices)
                    currentFrame[i, diff_indices] = frame[i, diff_indices]
    
    #Se simplifican las parte
    byteStream = list(byteStream)
    byteStream.append(0xFF)
    for i in range(len(byteStream)):
        if(byteStream[i]==0xFF and byteStream[i+1]==0xFF):
            byteStream.insert(i+1,0x00)
    jumpFrameRepetido = False
    while not jumpFrameRepetido:
        if byteStream[0] == 0xFF and byteStream[1] ==0xFF:
            byteStream.pop(0)
        else:
            jumpFrameRepetido = True
    passnPoints = 0
    firstValue = -1
    end = False
    i=0
    redundances = 0
    compressions = 0 
    originalLen = len(byteStream)
    while i < len(byteStream):
        if passnPoints > 0:
            passnPoints-=1
        elif firstValue == -1:
            
            if (byteStream[i] == 0xFF):
                passnPoints+=1
            elif (byteStream[i] == 0xFE):
                passnPoints+=1;
            elif byteStream[i] == 0xFD:
                passnPoints+=2
            elif byteStream[i]==(byteStream[i+1]-1): 
                firstValue = byteStream[i]
                indexFirstValue = i
            
        else:
            if byteStream[i] == 0xFF or byteStream[i] == 0xFE:
                passnPoints+=1
                indexLastValue = i
                if indexLastValue-indexFirstValue>=3:
                    lastValue = byteStream[i]
                    index=indexFirstValue+3
                    byteStream[indexFirstValue] = 0
                    byteStream[indexFirstValue+1] = 0
                    byteStream[indexFirstValue+2] = 0
                    while index!=indexLastValue:
                        byteStream.pop(index)
                        index+=1
                    byteStream[indexFirstValue] = 0xFD
                    byteStream[indexFirstValue+1] = firstValue
                    byteStream[indexFirstValue+2] = lastValue
                    i=indexFirstValue+2
                    redundances+=indexLastValue-indexFirstValue
                    compressions +=1
                firstValue=-1
            elif byteStream[i] == 0xFD:
                passnPoints+=2
                indexLastValue = i
                if indexLastValue-indexFirstValue>=3:
                    lastValue = byteStream[i]
                    index=indexFirstValue+3
                    byteStream[indexFirstValue] = 0
                    byteStream[indexFirstValue+1] = 0
                    byteStream[indexFirstValue+2] = 0
                    while index!=indexLastValue:
                        byteStream.pop(index)
                        index+=1
                    byteStream[indexFirstValue] = 0xFD
                    byteStream[indexFirstValue+1] = firstValue
                    byteStream[indexFirstValue+2] = lastValue
                    i=indexFirstValue+2
                    redundances+=indexLastValue-indexFirstValue
                    compressions+=1
                firstValue=-1
            elif byteStream[i]!=byteStream[i+1]-1:
                indexLastValue = i
                if indexLastValue-indexFirstValue>=3:
                    lastValue = byteStream[i]
                    
                    index=indexFirstValue+3
                    indexPerm = index
                    byteStream[indexFirstValue] = 0
                    byteStream[indexFirstValue+1] = 0
                    byteStream[indexFirstValue+2] = 0
                    while index!=indexLastValue+1:
                        byteStream.pop(indexPerm)
                        index+=1
                    byteStream[indexFirstValue] = 0xFD
                    byteStream[indexFirstValue+1] = firstValue
                    byteStream[indexFirstValue+2] = lastValue
                    i=indexFirstValue+2
                    redundances+=indexLastValue-indexFirstValue
                    compressions+=1
                firstValue=-1
        i+=1
    
    print(f"{redundances} redundant points were removed, the new size is {originalLen-redundances+(3*compressions)}B, the total compression was {redundances-(3*compressions)}B, the original size was {originalLen}B, and the compression ratio was {(1-((redundances-(3*compressions))/originalLen))*100}%")            
    
    return byteStream
def compressByteStream(byteStream: list) -> list:
    byteStream.append(0xFF)
    for i in range(len(byteStream)):
        if(byteStream[i]==0xFF and byteStream[i+1]==0xFF):
            byteStream.insert(i+1,0x00)
    jumpFrameRepetido = False
    while not jumpFrameRepetido:
        if byteStream[0] == 0xFF and byteStream[1] ==0xFF:
            byteStream.pop(0)
        else:
            jumpFrameRepetido = True
    passnPoints = 0
    firstValue = -1
    end = False
    i=0
    redundances = 0
    compressions = 0 
    originalLen = len(byteStream)
    while i < len(byteStream):
        if passnPoints > 0:
            passnPoints-=1
        elif firstValue == -1:
            
            if (byteStream[i] == 0xFF):
                passnPoints+=1
            elif (byteStream[i] == 0xFE):
                passnPoints+=1;
            elif byteStream[i] == 0xFD:
                passnPoints+=2
            elif byteStream[i]==(byteStream[i+1]-1): 
                firstValue = byteStream[i]
                indexFirstValue = i
            
        else:
            if byteStream[i] == 0xFF or byteStream[i] == 0xFE:
                passnPoints+=1
                indexLastValue = i
                if indexLastValue-indexFirstValue>=3:
                    lastValue = byteStream[i]
                    index=indexFirstValue+3
                    byteStream[indexFirstValue] = 0
                    byteStream[indexFirstValue+1] = 0
                    byteStream[indexFirstValue+2] = 0
                    while index!=indexLastValue:
                        byteStream.pop(index)
                        index+=1
                    byteStream[indexFirstValue] = 0xFD
                    byteStream[indexFirstValue+1] = firstValue
                    byteStream[indexFirstValue+2] = lastValue
                    i=indexFirstValue+2
                    redundances+=indexLastValue-indexFirstValue
                    compressions +=1
                firstValue=-1
            elif byteStream[i] == 0xFD:
                passnPoints+=2
                indexLastValue = i
                if indexLastValue-indexFirstValue>=3:
                    lastValue = byteStream[i]
                    index=indexFirstValue+3
                    byteStream[indexFirstValue] = 0
                    byteStream[indexFirstValue+1] = 0
                    byteStream[indexFirstValue+2] = 0
                    while index!=indexLastValue:
                        byteStream.pop(index)
                        index+=1
                    byteStream[indexFirstValue] = 0xFD
                    byteStream[indexFirstValue+1] = firstValue
                    byteStream[indexFirstValue+2] = lastValue
                    i=indexFirstValue+2
                    redundances+=indexLastValue-indexFirstValue
                    compressions+=1
                firstValue=-1
            elif byteStream[i]!=byteStream[i+1]-1:
                indexLastValue = i
                if indexLastValue-indexFirstValue>=3:
                    lastValue = byteStream[i]
                    
                    index=indexFirstValue+3
                    indexPerm = index
                    byteStream[indexFirstValue] = 0
                    byteStream[indexFirstValue+1] = 0
                    byteStream[indexFirstValue+2] = 0
                    while index!=indexLastValue+1:
                        byteStream.pop(indexPerm)
                        index+=1
                    byteStream[indexFirstValue] = 0xFD
                    byteStream[indexFirstValue+1] = firstValue
                    byteStream[indexFirstValue+2] = lastValue
                    i=indexFirstValue+2
                    redundances+=indexLastValue-indexFirstValue
                    compressions+=1
                firstValue=-1
        i+=1
    
    print(f"{redundances} redundant points were removed, the new size is {originalLen-redundances+(3*compressions)}B, the total compression was {redundances-(3*compressions)}B, the original size was {originalLen}B, and the compression ratio was {(1-((redundances-(3*compressions))/originalLen))*100}%")  
    
    return byteStream

args = sys.argv
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', './media/1.mp4', '-r', '120x75', '-lc','-c','-s']
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
    scanLineCompressed = False
    compressed = False
    for i in range(len(args)):
        if i == 0:
            pass
        elif args[i] == "--help":
            print("--------------BadAppleESP32CodeMaker--------------\n\nThis program is used to convert a video into a C binary array file that can be used to display the video on a ESP32 with a composite output\n\nArguments:\n\n-r [resolution] : Set the resolution of the video, the default is the resolution of the video\n\n-ts [frame] : Save a photo of the frame specified\n\n-t [threshold] : Set the threshold of the video, the default is 60\n\n-s : Save the video as a sequence of images\n\n-d : Dither the video\n\n-sv : Dither the video and save it as a sequence of images\n\n-lc : Use Lanczos4 as the resample algoritm\n\n-nr : Use Nearest as the resample algoritm\n\n-bc : Use Bicubic as the resample algoritm\n\n-bl : Use Linear as the resample algoritm\n\n-b2 : Use Bits2 as the resample algoritm\n\n-ar : Use Area as the resample algoritm\n\n-c : Compress the byteStream.h\n\n-scanLine : Use scan lines to compress the byteStream.h\n\n-scanLineCompressed : Use scan lines to compress the byteStream.h\n\n-interlacedEven : Use interlaced frames\n\n-interlacedOdd : Use interlaced frames\n\n-bt : Batch export\n\n--help : Show this message\n\n")
            exit()
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
        elif args[i] == "-scanLineCompressed" and (not interlaced or not scanLineCompressed):
            scanLineCompressed = True
        elif args[i] == "-scanLine" and (not interlaced or not scanLineCompressed):
            scanLine = True
        elif args[i] == ("-scanLine" or "-scanLineCompressed") and (interlaced or scanLineCompressed):
            print("You can't use scan lines and scanlinescompressed or interlaced at the same time")
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
        elif args[i] == "-c":
            compressed=True
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
    for i in range(len(frameListBuffer)):
        frameListBuffer[i] = frameListBuffer[i].astype(bool)
else:
    frameListBuffer = c.convertion(width=width,height=height,video=sourceMedia,threshold=threshold)
 
if interlaced:
    byteStream = findInterlacedDeltas(frameListBuffer=frameListBuffer, width=width, height=height,interlaceState= evenFrames)
elif scanLine:
    byteStream = findScanLineDeltas(frameListBuffer=frameListBuffer, width=width, height=height)
elif scanLineCompressed:
    byteStream = findScanLineDeltasCompressed(frameListBuffer=frameListBuffer, width=width, height=height)
else:
    byteStream = findDeltas(frameListBuffer=frameListBuffer, width=width, height=height)

if compressed:
    byteStream = compressByteStream(byteStream=byteStream)

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
            f.write(f"const int delayMS = {math.trunc((1/fps)*1000)};\nconst int delayUS = {math.modf((1/fps)*1000)[1]*1000};\nconst uint32_t totalFrames = {len(byteStream)};\n"+"PROGMEM const unsigned char byteStream[] ={\n")
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
    #TestSavedVideo(byteStream=byteStream,height=height,width=width) TODO: this doesn't work
    print("Images saved susccesfuly")