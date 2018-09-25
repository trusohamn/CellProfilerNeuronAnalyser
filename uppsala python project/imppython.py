import numpy
import cv2
import csv

def openimage():
    #read an image
    img1 = cv2.imread('1.tif')
    img2 = cv2.imread('2.tif')
    #show the image

    cv2.imshow('name of image', img1)
    cv2.imshow('name of image 2', img2)
    #close the image
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def opencsv(filename):
    #reading a csv file
    myfile = open(filename,'rb')
    read_file=csv.reader(myfile)
    return read_file
    myfile.close()


edges = opencsv('edges.csv')
#for row in edges:
 #   print row
vertices = opencsv('vertices.csv')
