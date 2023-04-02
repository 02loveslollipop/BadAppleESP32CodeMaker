import sys
import cv2
import numpy as np
from PIL import Image

def resizeImage(width: int,height: int,img,resample):
    return img.resize((width, height), resample=resample)


args = sys.argv
#args = ['c:/Users/Katana GF66 11UC/Documents/BadAppleESP32 Project/Code maker/main.py', 'C:\\Users\\Katana GF66 11UC\\Documents\\BadAppleESP32 Project\\Code maker\\main_1000.mp4']
if len(args)<=1:
    raise Exception ("You must give at least the video path")
else:
    dither = False
    nex_i = False
    custom_res = False
    ready = False
    resize = False
    resample = Image.LANCZOS
    batch = False
    for i in range(len(args)):
        if(args[i] == "-r"):
            height = args[i+1].split("x")[0]
            width = args[i+1].split("x")[1]
            custom_res = True
            next_i = False
        elif args[i] == "-d":
            dither = True
        elif args[i] == "-lc" and resize == False:
            resample = Image.LANCZOS
        elif args[i] == "-lc" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-nr" and resize == False:
            resample = Image.NEAREST
        elif args[i] == "-nr" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-bc" and resize == False:
            resample = Image.BICUBIC
        elif args[i] == "-bc" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-bl" and resize == False:
            resample = Image.BILINEAR
        elif args[i] == "-bl" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-ha" and resize == False:
            resample = Image.HAMMING
        elif args[i] == "-ha" and resize == True:
            print("You can only use 1 resize algoritm")
        elif args[i] == "-qd" and resize == False:
            resample = Image.QUAD
        elif args[i] == "-qd" and resize == True:
            print("You can only use 1 resize algoritm")
        elif nex_i == True:
            nex_i = False
        elif args[i] == "a":
            batch=True
        else:
            path = args[i]
            if not custom_res:
                vid = cv2.VideoCapture(path)
                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
                ready = True
            else:
                vid = cv2.VideoCapture(path)
                ready = True
if not batch:
    print(f"File path: {path}\nDither: {dither}\nResample algoritm: {resample}\nHeight: {height}\nWidth: {width}\nThe convertion will start, Press 1 to make a test of the resample algoritm\npress anything else to start the convertion. Starting the convertion.\n\nPress ESC to cancel the process")
    sel = input()
    if sel == "1":
        print("Write the frame you want to test: ")
        frame = int(input())
        sus = True
        con = 0
        while sus and frame != con:
            sus,img = vid.read()
            con += 1
        img = resizeImage(width=width,height=height,img=img,resample=resample)
        cv2.imwrite("test.jpg",img)
        print("File save as test.jpg, press any button to start convertion")
        input()
            
                


fps = vid.get(cv2.CAP_PROP_FPS)
count = 0
success = True
l_vectors = []
while success:
    vector = np.zeros(shape=(height,width),dtype=bool)
    success,image = vid.read()
    imgArray = np.asarray(image)
    print(imgArray.size)
    for i in range(height):
        for j in range(width-1):
            if np.array_equal(np.array([0,0,0]),imgArray[i][j]):
                vector[i][j] = False
            else:
                vector[i][j] = True
        print(f"finished line {i+1}")
    print(f"finished frame{count+1}")
    l_vectors.append(vector)

    if cv2.waitKey(100) == 27:
        exit()
        
    count += 1
  
