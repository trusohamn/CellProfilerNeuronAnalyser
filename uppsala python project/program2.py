import numpy
import cv2
import csv

def openimage(directory):
    #read an image
    img = cv2.imread(directory)
    #show the image

    #cv2.imshow('name of image', img)
    
    #close the image
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return img

def opencsv(filename):
    #reading a csv file
    myfile = open(filename,'rb')
    read_file=csv.reader(myfile)
    return read_file
    myfile.close()

def dictcsv_edges(filename):
    #reading and saving as a dictionary
    myfile = open(filename,'rb')
    filenames = ['im_no','v1','v2','length','intensity']
    reader = csv.DictReader(myfile, filenames)
    return reader
    myfile.close()
    
def dictcsv_vertices(filename):
    #reading and saving as a dictionary
    myfile = open(filename,'rb')
    filenames = ['im_no','vertex_no','i','j','label','kind']
    reader = csv.DictReader(myfile, filenames)
    return reader
    myfile.close()

def draw_circle(img, i, j, color):
    #drawing a circle (image, coordinates, size, color, )
    cv2.circle(img,(j,i), 3, color, -1)

def draw_circle_onimg(img,i,j):
    image = openimage(img)
    draw_circle(image, i, j)
    #cv2.imshow('name of imagewith circle', image)
    #close the image
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return image

def draw_line(img, coord1, coord2):
    img = cv2.line(img, coord1, coord2,(255,0,0),1)

def dict_edges():
    #creating a callable dictionary for edges
    #transferring data from dictreader into dictonary with edge_id as a key (new numeration)
    edges_dict = {}
    with open('edges.csv') as edges:
        filenames = ['im_no','v1','v2','length','intensity']
        reader = csv.DictReader(edges, filenames)
        next (reader) #skipping first entry (headers)
        edge_id = 1
        for record in reader:
            edges_dict[str(edge_id)] = {k:v for k,v in record.items() if k <> str(edge_id)}
            edge_id+=1
    return edges_dict

def dict_vertices():
    #creating a callable dictionary for vertices
    #transferring data from dictreader into dictonary with vertex_id as a key (new numeration)
    data = {}
    with open('vertices.csv') as vertices:
        filenames = ['im_no','vertex_no','i','j','label','kind']
        reader = csv.DictReader(vertices, filenames)
        next (reader)#skipping first entry (headers)
        vertex_id = 1
        for record in reader:
            data[str(vertex_id)] = {k:v for k,v in record.items() if k <> str(vertex_id)}
            vertex_id+=1
    return data

def detect_branch(endpoint_id):
    branch={}
    total_length = 0
    total_intensity = 0
    
    branch['endpoint_id']=endpoint_id
    for edge in edges_dict:
            data_edge = edges_dict[edge]
            if data_edge['v1']==endpoint_id or data_edge['v2']==endpoint_id:
                #working with 1 segment
                branch['1_segment']=data_edge
                total_length += float(data_edge['length'])
                total_intensity += float(data_edge ['intensity'])

                #getting data from second point
                if data_edge['v1']==endpoint_id:
                    sec_point_id = data_edge['v2']
                elif data_edge['v2']==endpoint_id:
                    sec_point_id = data_edge['v1']
                sec_point = vertex_dict[sec_point_id]
                branch ['2_point']= sec_point_id
                if sec_point['kind']=='T':
                    return branch
                else:
                    return True
    
############
#detection of branches
############
edges_dict = dict_edges()
vertex_dict = dict_vertices()

edges_dictcsv = dictcsv_edges('edges.csv')
next(edges_dictcsv) #skipping first entry (headers)

vertices_dictcsv = dictcsv_vertices('vertices.csv')
next(vertices_dictcsv) #skipping first entry (headers)


for entry in vertex_dict:
    data = vertex_dict[entry]
    kind = data['kind']
    if kind == 'E':
        endpoint_id = data['vertex_no']
        branch = detect_branch(endpoint_id)
        print branch
        

########
#viev of vertices
########
vertices = dictcsv_vertices('vertices.csv')

next(vertices) #skipping first entry (headers)

img= openimage('1.tif')

for row in vertices:
    i=int(row['i'])
    j=int(row['j'])
    if row['kind']=='B':
        #print row['kind']+row['i']+row['j']
        draw_circle(img, i, j,(255,255,255) )
    elif row['kind']=='E':
        draw_circle(img, i, j,(0,255,255) )
    elif row['kind']=='T':
        draw_circle(img, i, j,(0,0,255) )

########
#view of edges
########
edges = dictcsv_edges('edges.csv')
next(edges) #skipping first entry (headers)
#transferring data from dictreader into dictonary with 'vertex_no' as a key
data = {}
with open('vertices.csv') as vertices:
    filenames = ['im_no','vertex_no','i','j','label','kind']
    reader = csv.DictReader(vertices, filenames)
    next (reader)
    for record in reader:
        data[record['vertex_no']] = {k:v for k,v in record.items() if k <> 'vertex_no'}
#opening again the raw image
img_2= openimage('1.tif')
img_3= openimage('1.tif')
img_1= openimage('1.tif')
for row in edges:
    # getting the i and j coordinates of the edge's v1 and v2
    v1=row['v1']
    v2=row['v2']
    entry_v1= data.get(v1,'failed')
    entry_v2= data.get(v2,'failed')
    i1 = int(entry_v1['i']) 
    j1 = int(entry_v1['j'])
    i2 = int (entry_v2['i'])
    j2 = int (entry_v2['j'])
    #getting intensity anf filtering
    intens = float(row['intensity'])
    #if intens>5:
        #drawing a line
    img_2 = cv2.line(img_2, (j1,i1) , (j2,i2) ,(255,0,0),1)
    img_3 = cv2.line(img, (j1,i1) , (j2,i2) ,(255,0,0),1)

##############
#visualisation
##############
#cv2.namedWindow('raw image',cv2.WINDOW_NORMAL)
#cv2.imshow('raw image', img_1)
#cv2.namedWindow('vertices+edges',cv2.WINDOW_NORMAL)
#cv2.imshow('vertices+edges', img)
#cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
#cv2.imshow('edges', img_2)
#closing images
#cv2.waitKey(0)
#cv2.destroyAllWindows()


# checks whether pt1 is in circ
def inCircle(pt1, circ):

    # get the distance between pt1 and circ using the
    # distance formula
    dx = pt1.getX() - circ.getCenter().getX()
    dy = pt1.getY() - circ.getCenter().getY()
    dist = math.sqrt(dx*dx + dy*dy)

    # check whether the distance is less than the radius
    return dist <= circ.getRadius()


