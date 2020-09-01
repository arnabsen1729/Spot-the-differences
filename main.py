from PIL import Image
import cv2
from matplotlib import pyplot as plt
from imutils import contours
from skimage import measure
import numpy as np
import argparse
import imutils

def threshold(tup1, tup2):
    val=0
    if(abs(tup1[0]-tup2[0])>=25):
        val+=1
    if(abs(tup1[1]-tup2[1])>=25):
        val+=1
    if(abs(tup1[2]-tup2[2])>=25):
        val+=1

    if(val>=2):
        return True
    else:
        return False


def main(IMG1, IMG2):
    img1 = Image.open(IMG1)
    img2 = Image.open(IMG2)
    resultImg = img1.copy()
    x, y = min(img1.size[0], img2.size[0]), min(img1.size[1], img2.size[1])
    grid = [[0]*y]*x
    pixImg1 = img1.load()
    pixImg2 = img2.load()
    resultPix = resultImg.load()
    for i in range(x):
        for j in range(y):
            if(threshold(pixImg1[i,j], pixImg2[i,j])):
            # if(pixImg1[i, j]!=pixImg2[i, j]):
                grid[i][j]=1
                resultPix[i,j]=(255, 255, 255)
            else:
                resultPix[i, j]=(0, 0, 0)
    # resultImg.save('result.png')
    finalDetect(IMG1, IMG2, resultImg)


def finalDetect(IMG1, IMG2, res):
    orgImage1 = cv2.imread(IMG1)
    orgImage2 = cv2.imread(IMG2)
    img = np.array(res)
    dst = cv2.fastNlMeansDenoisingColored(img,None,180,180,7,21)
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    
    thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)
    labels = measure.label(thresh, connectivity=2, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue
        # otherwise, construct the label mask and count the
        # number of pixels 
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 300:
            mask = cv2.add(mask, labelMask)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = contours.sort_contours(cnts)[0]
    # loop over the contours
    for (i, c) in enumerate(cnts):
        # draw the bright spot on the image
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        cv2.circle(orgImage1, (int(cX), int(cY)), int(radius), (0, 0, 255), 3)
        cv2.circle(orgImage2, (int(cX), int(cY)), int(radius), (0, 0, 255), 3)
        cv2.circle(orgImage1, (int(cX), int(cY)), int(radius), (0, 0, 255), 3)
        cv2.putText(orgImage2, "#{}".format(i + 1), (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    invertImg1 = cv2.cvtColor(orgImage1, cv2.COLOR_BGR2RGB)
    invertImg2 = cv2.cvtColor(orgImage2, cv2.COLOR_BGR2RGB)
    plt.subplot(121), plt.imshow(invertImg1)
    plt.subplot(122), plt.imshow(invertImg2)
    plt.show()


if __name__ == "__main__":
    IMG1 = input('Enter path to image 1: ')
    IMG2 = input('Enter path to image 2: ')
    main(IMG1, IMG2)
