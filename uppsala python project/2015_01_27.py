import numpy
import cv2
import csv

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

def branches_library(point):
    """creates the list of dictionaries with key endpoint of possible branches for every endpoint"""
    branches=[[point]] #unfinished branches
    lista=[] # finished branches, possible branches started in endpoint and ended in trunkpoint
    next_points = []
    x=1
    
    while x<12:
        x+=1
        for branch in branches:
            #print "\n", "branches: ", branches, "\n", "Branch: ", branch
            next_points = detect_next_points(branch[-1], branch[:-1])
            #print "next points:", next_points, len(next_points)
            temp_list=[]
            if len(next_points)==3:
                branch1 = branch + [next_points[0]]
                branch2 = branch + [next_points[1]]
                branch3 = branch + [next_points[2]]
                temp_list = [branch1, branch2, branch3]
            elif len(next_points)==2:
                branch1 = branch +[next_points[0]]
                branch2 = branch + [next_points[1]]
                temp_list = [branch1, branch2]
            elif len(next_points)==1:
                branch1 = branch + [next_points[0]]
                temp_list = [branch1]
            elif len(next_points)==0:
                branches.remove(branch)
                continue
            branches.remove(branch)

            for br in temp_list:
                #print "temp list: ", temp_list
                if control_endpoint(br[-1])==1:
                    lista.append(br)
                else:
                    branches.append(br)
        #print "lista : ", lista
    return lista
                                
def control_endpoint(x):
    data = vertex_dict[x]
    if data['kind']=='T':
        return True

def detect_next_points(point, points_all):
    #list of next points
    next_points=[]
    for edge in edges_dict:
        data_edge = edges_dict[edge]
        if data_edge['v1']== point or data_edge['v2']== point:
            if data_edge['v1']== point:
                next_id = data_edge['v2']
            elif data_edge['v2']== point:
                next_id = data_edge['v1']
            if next_id not in points_all:
                next_points.append(next_id)
    return next_points

def count_len_int(branch):
    #print branch
    total_length = 0
    total_intensity = 0
    branch_points=0
    for edge in edges_dict:
        data_edge = edges_dict[edge]
        if (data_edge['v1'] in branch and data_edge['v2'] in branch):
            total_length+= float(data_edge['length'])
            total_intensity+= float(data_edge['intensity'])
            branch_points+=1
            
    punctation=100*(total_intensity/(total_length**4))
    return punctation, total_length, total_intensity

def openimage(directory):
    #read an image
    img = cv2.imread(directory)
    return img
def showimage(image, name):
    #show the image
    cv2.imshow(name, image)
    #close the image
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def trunkpoint_detection(branch):
    return branch[len(branch)-1]

def list_trunkpoints(dictionary):
    trunkpoints=[]
    for branch_no in dictionary:
        branch_data=dictionary[branch_no]
        trunkpoint = branch_data['trunkpoint']

        if trunkpoint not in trunkpoints:
            trunkpoints.append(trunkpoint)
    return trunkpoints


############
#detection of branches
############
"""creating dictonaries od edges and vertex from csv files"""
edges_dict = dict_edges()
vertex_dict = dict_vertices()

""" getting list of all branches"""
dict_branches={}
for entry in vertex_dict:
    data = vertex_dict[entry]
    kind = data['kind']
    if kind == 'E':
        endpoint_id = data['vertex_no']
        branch = branches_library(endpoint_id)
        dict_branches[endpoint_id] = branch
#for key in dict_branches:
   # print key, "\n", dict_branches[key]

"""proccesing list of all branches,
#filtering to get one, strongest one"""
dict_strongest_branches={}
branch_no=1
for endpoint in dict_branches:
    strongest_branch = 0
    strongest_punctation = 0
    strongest_length = 0
    strongest_intensity = 0
    for branch in dict_branches[endpoint]:
        (punctation, length, intensity) = count_len_int(branch)
        if punctation> strongest_punctation:
            strongest_punctation = punctation
            strongest_branch = branch
            strongest_length = length
            strongest_intensity = intensity           
    data={}
    data['endpoint']=str(endpoint)
    data['branch']=strongest_branch
    data['trunkpoint'] = trunkpoint_detection(strongest_branch)
    data['length']=strongest_length
    data['intensity']=strongest_intensity
    #data['punctation']=strongest_punctation
    dict_strongest_branches[branch_no]=data
    branch_no+=1

for key in dict_strongest_branches:
    print dict_strongest_branches[key]

"""filterint to get the longest of the branches coming from the same trunkpoint
getting a list of trunkpoints"""
trunkpoints = list_trunkpoints(dict_strongest_branches)
!!!!!!!!!!!!!!!!!!!!!!!
dict_longest_strongest_branches={}
for trunkpoint in trunkpoints:
    longest_branch = 0
    max_length = 0
    max_branch_no=0
    data={}
    for branch_no in dict_strongest_branches:
        branch_data=dict_strongest_branches[branch_no]
        trunkpoint_1 = branch_data['trunkpoint']
        branch = branch_data['branch']
        if trunkpoint_1 == trunkpoint:
            if branch_data['length']>max_length:
                max_length=length
                longest_branch = branch
                max_branch_no=branch_no
                data = branch_data
    dict_longest_strongest_branches[max_branch_no]= data

for key in dict_longest_strongest_branches:
    print dict_longest_strongest_branches[key]
    """
#shortening branches which sprout from the longest branches
#to avoid overlapping

#creating a list of all points in longest_strongest branches,
#they will be treated as points finishing branch for the shortest
#branches sprouting from them

def list_points(dictonary):
    lists=[]
    for branch_no in dictonary:
        branch_data=dict_strongest_branches[branch_no]
        branch=branch_data['branch']
        for point in branch:
            if point not in lists:
                lists.append(point)
    return lists

list_of_points = list_points(dict_longest_strongest_branches)

new_dict_strongest_branches=removing_points(dict_strongest_branches,list_of_points)

print new_dict_strongest_branches
  """
#openning the image
img_1=openimage('1.tif')
img_2= openimage('1.tif')
#visualisation of branches
for endpoint in dict_strongest_branches:
    data = dict_strongest_branches[endpoint]
    branch = data['branch']
    for x in range(0,len(branch)-1):
        point_1=vertex_dict[branch[x]]
        point_2=vertex_dict[branch[x+1]]
        i1 = int(point_1['i'])
        j1 = int(point_1['j'])
        i2 = int(point_2['i'])
        j2 = int(point_2['j'])
        img_2 = cv2.line(img_2, (j1,i1) , (j2,i2) ,(255,255,255),1)

for endpoint in dict_longest_strongest_branches:
    data = dict_strongest_branches[endpoint]
    branch = data['branch']
    for x in range(0,len(branch)-1):
        point_1=vertex_dict[branch[x]]
        point_2=vertex_dict[branch[x+1]]
        i1 = int(point_1['i'])
        j1 = int(point_1['j'])
        i2 = int(point_2['i'])
        j2 = int(point_2['j'])
        img_2 = cv2.line(img_2, (j1,i1) , (j2,i2) ,(0,255,255),1)
showimage(img_2,'result')

            
            
            
            
            
           
            
        
        
    







    
