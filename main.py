import sys
import cv2
import numpy as np
from PIL import Image
import os
import optFunc as c
import csv

threshold = 60

def count_frames(path: str):
    try:
        return int(cv2.VideoCapture(path).get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    except:
        return int(count_frames_manual(cv2.VideoCapture(path)))

def count_frames_manual(video):
	# initialize the total number of frames read
	total = 0
	# loop over the frames of the video
	while True:
		(grabbed, frame) = video.read()
		if not grabbed:
			break
		total += 1
	return total

def clear():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def SaveResultAsPhotoList(patternList,frameList,width,height,patternSize):
    frameCount = 1
    frameBuffer = np.zeros((width,height,3),dtype=float)
    for frame in frameList:
        for i in range(int(width/l_pattern)):
            for j in range(int(height/l_pattern)):
                bufferSubframe = patternList[frame[i][j]]  
                for subframe_i in range(patternSize):
                    for subframe_j in range(patternSize):
                        if bufferSubframe[subframe_i][subframe_j]:
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][0] = 0
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][1] = 0
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][2] = 0
                        else:
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][0] = 255
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][1] = 255
                            frameBuffer[(i*patternSize)+(subframe_i)][(j*patternSize)+(subframe_j)][2] = 255
        cv2.imwrite(filename=f"{frameCount:05d}.png",img=frameBuffer)
        frameCount += 1

def solveSubframe(frameBuffer,totalFrames,width,height,l_pattern):
    l_subframesX = 2
    l_subframes = np.zeros(shape=(l_subframesX,l_pattern,l_pattern),dtype=bool)
    l_subframes[0] = np.asarray([
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False],
        [False,False,False,False,False,False,False,False]
        ])

    l_subframes[1] = np.asarray([
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True],
        [True,True,True,True,True,True,True,True]
        ])
    l_frames_compress = []
    total = 0
    sub_frame_not_finded = 0
    index = 2

    for frame in frameBuffer:
        subframe_map = np.zeros(shape=(int(width/l_pattern),int(height/l_pattern)),dtype=int)
        finded = False
        for i in range(len(subframe_map)):
            for j in range(len(subframe_map[0])):
                subframe = np.zeros(shape=(l_pattern,l_pattern),dtype=bool)
                for subframe_i in range(l_pattern):
                    for subframe_j in range(l_pattern):
                        subframe[subframe_i][subframe_j] = frame[(i*l_pattern)+(subframe_i)][(j*l_pattern)+(subframe_j)]
                
                try:
                    subframe_map[i][j] = np.where(np.all(l_subframes==subframe, axis=(1, 2)))[0][0]
                except IndexError:
                    l_subframesX += 1
                    l_subframes.resize((l_subframesX,l_pattern,l_pattern),refcheck=False)
                    l_subframes[index] = subframe
                    subframe_map[i][j] = index
                    index += 1
                    sub_frame_not_finded += 1
                total += 1
        l_frames_compress.append(subframe_map)
    
    return l_subframes, l_frames_compress, total, sub_frame_not_finded

args = sys.argv
#print(args)
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', './media/test.mp4', '-r', '240x256', '-lc']
if len(args) <= 1:
    print("You must give at least the video path")
    exit()
else:
    l_pattern = 8
    dither = False
    nex_i = False
    custom_res = False
    ready = False
    resize = False
    resample = Image.LANCZOS
    batch = False
    save_photo = False
    for i in range(len(args)):
        if i == 0:
            pass
        elif(args[i] == "-r"):
            height = int(args[i+1].split("x")[0])
            width = int(args[i+1].split("x")[1])
            custom_res = True
            nex_i = True
        elif args[i] == "-d":
            dither = True
        elif args[i] == "-sv":
            dither = True
        elif args[i] == "-lc" and resize == False:
            resample = cv2.INTER_LANCZOS4
            resize = True
        elif args[i] == "-lc" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-nr" and resize == False:
            resample = cv2.INTER_NEAREST
            resize = True
        elif args[i] == "-nr" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-bc" and resize == False:
            resample = cv2.INTER_CUBIC
            resize = True
        elif args[i] == "-bc" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-bl" and resize == False:
            resample = cv2.INTER_LINEAR
            resize = True
        elif args[i] == "-bl" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-b2" and resize == False:
            resample = cv2.INTER_BITS2
            resize = True
        elif args[i] == "-b2" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif args[i] == "-ar" and resize == False:
            resample = cv2.INTER_AREA
            resize = True
        elif args[i] == "-ar" and resize == True:
            print("You can only use 1 resize algoritm")
            exit()
        elif nex_i:
            nex_i = False
        elif args[i] == "-bt":
            batch=True
        elif custom_res:
            path = args[i]
        elif not custom_res and not ready:
            path = args[i]
            try:
                vid = cv2.VideoCapture(path)
            except FileNotFoundError:
                print("cv2 could not open the video file, please check the path or if the file is in use")
                exit()
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            ready = True
        elif not ready:
            path = args[i]
            try:
                vid = cv2.VideoCapture(path)
            except FileNotFoundError:
                print("cv2 could not open the video file, please check the path or if the file is in use")
                exit()
            ready = True
        else: 
            print(f"{args[i]} has not been recognize as a valid argument")

totalFrames = count_frames(path)

if not batch:
    clear()
    print(f"----SUMMARY----\nFile path: {path}\nDither: {dither}\nResample algoritm: {resample}\nHeight: {height}\nWidth: {width}\nPress 1 to make a test of the algoritm method\nPress any other button to start the convertion")
    sel = input()
    if sel == "1":
        clear()
        print("Frame to test: ")
        frame = int(input())
        sus = True
        con = 0
        while sus and frame != con:
            sus,img = vid.read()
            con += 1
        imgTest = cv2.resize(src=img,dsize=(height,width),interpolation=resample)
        cv2.imwrite(filename="test.png",img=imgTest)
        clear()
        print("File save as test.png, press any button to start convertion\n\nDuring convertion press ESC to cancel the process")
        input()
    else:     
        clear()
        print("Press any button to start convertion\n\nDuring convertion press ESC to cancel the process")

if resize:
    lFrames = c.convertionWithResize(width=width,height=height,video=vid,resample=resample,threshold=threshold)
else:
    lFrames = c.convertion(width=width,height=height,video=vid,threshold=threshold)

if not batch:
    clear()
print("Creating subfameBuffer and solving subframes")
    
l_subframes, l_frames_compress, total, sub_frame_not_finded = c.solveSubframe(frameBuffer=lFrames,totalFrames=totalFrames,width=width,height=height,l_pattern = l_pattern)
#l_subframes, l_frames_compress, total, sub_frame_not_finded = solveSubframe(frameBuffer=lFrames,totalFrames=totalFrames,width=width,height=height,l_pattern = l_pattern)

if not batch:
    clear()
print(f"Total subframes: {total}\nCompress subframes: {total-sub_frame_not_finded}\nNot compress subframes: {sub_frame_not_finded}")


while True: #Save "binarySubframeList.bin"
    try:
        print("Trying to save binarySubframeList.bin")    
        # 1 is white, 0 is black 
        with open ('binarySubframeList.bin','wb') as f:
            binaryListBuffer = []
            byteBuffer = 0
            k = 0
            for subframe in l_subframes:
                for i in range(len(subframe)):
                    for j in range(len(subframe[0])):
                        if k == 8:
                            binaryListBuffer.append(byteBuffer)
                            byteBuffer = 0
                            k = 0
                        if subframe[i][j]:
                            byteBuffer+=(1*(2**k))
                        k+=1
            
            f.write(bytearray(binaryListBuffer))
            f.close()
            break    
    except PermissionError:
        print("File is in use, please close it to save the binary and then press enter")
        input()
        clear()
        
while True: #Save "binaryCompressFrame.bin"
    try:
        # 1 is white, 0 is black 
        print("Trying to save binaryCompressFrame.bin")  
        with open ('binaryCompressFrame.bin','wb') as f:
            binaryCompressFrame = []

            for frame in l_frames_compress:
                for line in frame:
                    for dot in line:
                        f.write(int(dot).to_bytes(8,"big"))
            
            f.close()
            break    
    except PermissionError:
        print("File is in use, please close it to save the binary and then press enter")
        input()
        clear()

while True: #Save "l_frames_compressed.ztfl"
    try: 
        
        with open ('l_frames_compressed.ztfl','w') as f:
            write = csv.writer(f)
            write.writerows(l_frames_compress)
        break
    except PermissionError:
        clear()
        print("File is in use, please close it to save the binary and then press enter")
        input()

while True: #Save "l_subframes.ztsl"
    try:
        with open ('l_subframes.ztsl','w') as f:
            write = csv.writer(f)
            write.writerows(l_subframes)
        break
    except PermissionError:
        clear()
        print("File is in use, please close it to save the binary and then press enter")
        input()
        
if save_photo:
    SaveResultAsPhotoList(l_subframes,l_frames_compress,width,height,l_pattern)
else:
    clear()
    print("Press 1 to save result as Photo list\nPress anything else to exit the program")
    if input() == "1":
        SaveResultAsPhotoList(l_subframes,l_frames_compress,width,height,l_pattern)