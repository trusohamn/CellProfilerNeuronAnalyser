import numpy
import cv2
import csv
import math
import copy
"""1.03.2016"""

def dict_edges(filename):
    #creating a callable dictionary for edges
    #transferring data from dictreader into dictonary with edge_id as a key (new numeration)
    edges_dict = []
    with open(filename) as edges:
        filenames = ['im_no','v1','v2','length','intensity']
        reader = csv.DictReader(edges, filenames)
        next (reader) #skipping first entry (headers)
        edge_id = 1
        for record in reader:
            edges_dict.append(record)
            edge_id+=1
    return edges_dict

def dict_vertices(filename):
    #creating a callable dictionary for vertices
    #transferring data from dictreader into dictonary with vertex_id as a key (new numeration)
    data = []
    with open(filename) as vertices:
        filenames = ['im_no','vertex_no','i','j','label','kind']
        reader = csv.DictReader(vertices, filenames)
        next (reader)#skipping first entry (headers)
        for record in reader:
            data.append(record)
    return data

def sorting(dictionary):
    img_list=[]
    sorted_dict={}
    for entry in dictionary:
        img_no = entry['im_no']
        if img_no not in img_list:
            img_list.append(img_no)
    if len(img_list)>1:
        for image in img_list:
            group = []
            for entry in dictionary:
                if entry['im_no'] == image:
                    group.append(entry)
            sorted_dict[image]=group
    else:
        sorted_dict[1] = dictionary
    return sorted_dict

def sorting_cells(dict_branches):
    cells_list=[]
    sorted_dict={}
    for entry in dict_branches:
        cell = entry['label']
        if cell not in cells_list:
            cells_list.append(str(cell))
    if len(cells_list)>1:
        for cell in cells_list:
            group = [] 
            for entry in dict_branches:
                if entry['label'] == cell:
                    group.append(entry)
            sorted_dict[cell]=group
    else:
        sorted_dict[1] = dict_branches
    return sorted_dict

def sort_edges_per_cell(dict_e1, list_v):
    data = list()
    for entry in dict_e1:
        if entry['v1'] in list_v or entry['v2'] in list_v:
            data.append(entry)
    return data
    
def list_vert(dict_v):
    list_v = list()
    list_kind = list()
    for item in dict_v:
        list_v.append(item['vertex_no'])
        list_kind.append(item['kind'])
    return tuple(list_v), tuple(list_kind)
    
    
def get_v_ends(dict_e, list_v):
    data = dict()
    for v in list_v:
        group = list()
        for e in dict_e:
            if e['v1']==v and e['v2'] not in group:
                group.append(e['v2'])
            elif e['v2']==v and e['v1'] not in group:
                group.append(e['v1'])
        data[v]=group
    return data

def get_branches(list_v, kind_v, dict_v, dict_e):
    dict_branches = dict()
    for index, kind in zip(list_v, kind_v):
        if kind == 'E':
            endpoint_id = index
            branches = branches_library(endpoint_id, dict_v, dict_e, list_v, kind_v, tuple_e)
            dict_branches[endpoint_id] = branches
    return dict_branches

def detect_next_points(point, points_all, tuple_e):
    #list of next points
    points = list(tuple_e[point])
    n = []
    for point in points:
        if point not in points_all:
            n.append(point)
    return n

def control_endpoint(point_x, list_v, kind_v):
    index = list_v.index(point_x)
    if kind_v[index] == 'T':
        return True
            
def branches_library(point, dict_v, dict_e, list_v, kind_v, tuple_e):
    """creates the list of dictionaries with key endpoint of possible branches for every endpoint"""
    branches=[[point]] #unfinished branches
    lista=[] # finished branches, possible branches started in endpoint and ended in trunkpoint
    next_points = []
    while branches != []:
        for branch in branches:
            next_points = detect_next_points(branch[-1], branch[:-1], tuple_e)
            temp_list=list()
            
            if len(next_points)==0:
                branches.remove(branch)
                continue
            for pointn in next_points:
                temp_list.append(branch+[pointn])
            
            branches.remove(branch)

            for br in temp_list:
                if control_endpoint(br[-1],list_v, kind_v)==1:
                    lista.append(br)
                else:
                    branches.append(br)
            if len(lista)>10:
                return lista
    return lista



def strongest(dict_v, dict_e, dict_branches):
    """important function, searching for the strongest branches and saving their properties in dict"""
    dict_strongest_branches={}
    branch_no=0
    for endpoint in dict_branches:
        #print "I am processing : ", endpoint
        strongest_branch = 0
        strongest_punctation = 0
        strongest_length = 0
        strongest_intensity = 0
        for branch in dict_branches[endpoint]:
            (punctation, length, intensity) = count_len_int(branch, dict_e)
            if punctation> strongest_punctation:
                strongest_punctation = punctation
                strongest_branch = branch
                strongest_length = length
                strongest_intensity = intensity           
        data=dict()
        data['endpoint']=str(endpoint)
        data['image'] = image
        data['branch']=strongest_branch
        data['trunkpoint'] = branch[len(branch)-1]
        data['length']=strongest_length
        data['intensity']=round(strongest_intensity,2)
        data['end_x_y_trunk_x_y'],data['label']=get_ends_coord_label(data['endpoint'],data['trunkpoint'], dict_v)
        data['angle']=get_angle(data['end_x_y_trunk_x_y'],0)
        dict_strongest_branches[branch_no]=data
        branch_no+=1
    return dict_strongest_branches

def count_len_int(branch, dict_e):
    total_length = 0
    total_intensity = 0
    branch_points=0
    for edge in dict_e:
        if (edge['v1'] in branch and edge['v2'] in branch):
            indeks1 = branch.index(edge['v1'])
            indeks2 = branch.index(edge['v2'])
            if abs(indeks1-indeks2) == 1:
                total_length+= float(edge['length'])
                total_intensity+= float(edge['intensity'])
                branch_points+=1
            
    punctation=100*(total_intensity/total_length**2)
    return punctation, total_length, total_intensity

def get_total_length(dict_strongest_branches):
    total=0
    for entry in dict_strongest_branches:
        total+= dict_strongest_branches[entry]['length']
    return total


def draw_on_image(dict_strongest_branches,img, dict_v):      
    #visualisation of branches

    font = cv2.FONT_HERSHEY_SIMPLEX
    for endpoint in dict_strongest_branches:
        data = dict_strongest_branches[endpoint]
        branch = data['branch']
        if branch == 0:
            continue
        #draw a line
        
        for x in range(0,len(branch)-1):
            for entry in dict_v:
                if entry['vertex_no']==branch[x]:
                    point_1=entry
                elif entry['vertex_no']==branch[x+1]:         
                    point_2=entry
            i1 = int(point_1['i'])
            j1 = int(point_1['j'])
            i2 = int(point_2['i'])
            j2 = int(point_2['j'])
            img = cv2.line(img, (j1,i1) , (j2,i2) ,(255,255,100),1)
        #draw an endpoints id
        for entry in dict_v:
            if entry['vertex_no']== data['endpoint']:
                end_data=entry
                end_i=int(end_data['i'])
                end_j=int(end_data['j'])
        cv2.putText(img,data['endpoint'],(end_j,end_i), font, 0.3,(255,255,255),01,cv2.LINE_AA)
    return img

def openimage(directory):
    #read an image
    img = cv2.imread(directory)
    return img

def showimage(image, name):
    #show the image
    cv2.imshow(name, image)
    #close the image
    cv2.waitKey(1)
    #cv2.destroyAllWindows()

def show_all_vertices(dict_v,img):
    font = cv2.FONT_HERSHEY_PLAIN
    for entry in dict_v:
        i=int(entry['i'])
        j=int(entry['j'])
        name = entry['vertex_no']
        if entry['kind']=='B':
            cv2.putText(img,name,(j,i), font, 0.4,(255,255,255),01,cv2.LINE_AA)
        elif entry['kind']=='E':
            cv2.putText(img,name,(j,i), font, 0.4,(0,255,255),01,cv2.LINE_AA)
        elif entry['kind']=='T':
            cv2.putText(img,name,(j,i), font, 0.4,(0,0,255),01,cv2.LINE_AA)
    return img


def show_all_edges(dict_v,dict_e,img):
    for edge in dict_e:
        v1 = edge['v1']
        v2 = edge['v2']
        #searching of coordinates
        for vertix in dict_v:
            if vertix['vertex_no']==v1:
                data_v1 = vertix
            elif vertix['vertex_no']==v2:
                data_v2 = vertix    
        i1 = int(data_v1['i']) 
        j1 = int(data_v1['j'])
        i2 = int (data_v2['i'])
        j2 = int (data_v2['j'])
        img = cv2.line(img, (j1,i1) , (j2,i2) ,(255,255,255),1)
        #optional:
        img = dot_vertices(dict_v,img)
    return img

def dot_vertices(dict_v,img):
    for entry in dict_v:
        i=int(entry['i'])
        j=int(entry['j'])
        name = entry['vertex_no']
        if entry['kind']=='B':
            draw_circle(img, i, j,(255,255,255) )
        elif entry['kind']=='E':
            draw_circle(img, i, j,(0,255,255) )
        elif entry['kind']=='T':
            draw_circle(img, i, j,(0,0,255) )
    return img

def draw_circle(img, i, j, color):
    #drawing a circle (image, coordinates, size, color, )
    cv2.circle(img,(j,i), 2, color, -1)

def get_mean_angle(dict_strongest_branches):
    total=0
    count = 0
    for entry in dict_strongest_branches:
        total+= dict_strongest_branches[entry]['angle']
        count += 1
    average = total/count
    return round(average,3)

def get_angle(coordinates, axis):
    [x1,y1,x2,y2] = coordinates
    """ neurits with orientation towards the skin (left i guess) the angle is negative"""
    """returns arc tangensin radians
    axis - radians"""
    #getting the radians 0-2pi
    XtoY = abs(x1-x2)/abs(y1-y2)
    if y1>y2 and x2>=x1:        #I
        radian = math.atan(XtoY)
    elif y1<y2 and x2>x1:       #II 
        radian = (math.pi) - math.atan(XtoY)
    elif y1<y2 and x2<=x1:      #III
        radian = math.atan(XtoY)+math.pi
    elif y1>y2 and x2<x1:       #IV
        radian = (math.pi*2) - math.atan(XtoY)
    elif y1==y2 and x2>x1:
        radian = math.pi*0.5
    elif y1==y2 and x2<x1:
        radian = math.pi*1.5
    else:
        print 'problem with radians'
    #convert radians to 0-90 degrees scale in reference to axis
    angle = math.degrees(radian)
    #add the axis
    angle += axis
    if angle <=90:          #I
        angle = angle
    elif angle <= 180:      #II
        angle = 180 - angle
    elif angle <= 270:      #III
        angle = 180 - angle
    elif angle <=450:       #IV and I
        angle = angle - 360
    elif angle > 450:       #II
        angle = 540 - angle  
    
    return round(angle,2)

def get_ends_coord_label(endpoint,trunkpoint, dict_v):
    for entry in dict_v:
            if entry['vertex_no']==endpoint:
                x2 = float(entry['j'])
                y2 = float(entry['i'])
                label = entry['label']
            elif entry['vertex_no']==trunkpoint:
                x1 = float(entry['j'])
                y1 = float(entry['i'])
    return [x1, y1, x2, y2], label

def draw_on_image_angle(dict_strongest_branches, dict_v, img):      

    font = cv2.FONT_HERSHEY_SIMPLEX
    for endpoint in dict_strongest_branches:
        data = dict_strongest_branches[endpoint]
        branch = data['branch']
        #draw a line
        for x in range(0,len(branch)-1):
            for entry in dict_v:
                if entry['vertex_no']==branch[x]:
                    point_1=entry
                elif entry['vertex_no']==branch[x+1]:         
                    point_2=entry
            i1 = int(point_1['i'])
            j1 = int(point_1['j'])
            i2 = int(point_2['i'])
            j2 = int(point_2['j'])
            img = cv2.line(img, (j1,i1) , (j2,i2) ,(255,255,100),1)
        #draw an endpoints id
        for entry in dict_v:
            if entry['vertex_no']== data['endpoint']:
                end_data=entry
                end_i=int(end_data['i'])
                end_j=int(end_data['j'])
        cv2.putText(img,str(data['angle']),(end_j,end_i), font, 0.3,(255,255,255),01,cv2.LINE_AA)
    return img

def get_lowest_mean_angle(dict1):
    mean_angle = get_mean_angle(dict1)
    
    min_mean = mean_angle
    min_dict = copy.deepcopy(dict1)
    min_i = 0
    
    for i in range(1,1800):
        new_dict = change_axis_in_dict(dict1, (float(i)/10.0))
        new_mean = get_mean_angle(new_dict)
        
        if abs(new_mean)<abs(min_mean):
            min_mean = new_mean
            min_dict = copy.deepcopy(new_dict)
            min_i = i
    print 'mniejszy', min_mean, float(min_i)/10
    for item, item2 in zip(dict1, min_dict):
        print dict1[item]['end_x_y_trunk_x_y'],dict1[item]['angle'], min_dict[item2]['angle']

    return (min_mean), min_dict, (min_i/10)

def change_axis_in_dict(dict1,i):
    new_dict = copy.deepcopy(dict1)
    for entry in new_dict:
            ang = get_angle(new_dict[entry]['end_x_y_trunk_x_y'], float(i))
            new_dict[entry]['angle'] = ang
    return new_dict

def draw_axis(angle, center_coor, img):
    #converts angle from degrees to radians
    print 'degrees',angle
    angle = math.radians(angle)
    print 'radians', angle
    #calculates the coordinates
    XtoY = math.tan(angle)
    x = 200.0
    y = int(x/XtoY)
    coor = (int((center_coor[0]+x)),int((center_coor[1]+y)))
    op_coor =( int(center_coor[0]-x),int(center_coor[1]-y))
    #draw a line
    img = cv2.line(img, center_coor , coor ,(255,255,255),1)
    img = cv2.line(img, center_coor , op_coor ,(255,255,255),1)
    return img

def get_center_coord(dict_v):
    x = 0
    y = 0
    i = 0
    for item in dict_v:
        if item['kind'] == 'T':
            x+= int(item['j'])
            y += int(item['i'])
            i+=1
    return (int(x/i),int(y/i))

def showimage(image, name):
    #show the image
    cv2.imshow(name, image)
    #close the image
    cv2.waitKey(1)
    #cv2.destroyAllWindows()
                                            
#######################
#detection of branches#
#######################

    
"""creating dictonaries od edges and vertex from csv files"""
edges_dict = dict_edges('edges.csv')
vertex_dict = dict_vertices('vertices.csv')

"""dividing dictionaries of edges and vertices according to img_no and label"""

sorted_edges = sorting (edges_dict)
sorted_vertices = sorting (vertex_dict)

header = False

for image in sorted_vertices:
    print 'image', image
    
    img_filename = str(image)+'.tif'
    img_raw = openimage(img_filename)
    img_branches = openimage(img_filename)
    img_all_vertices = openimage(img_filename)
    img_all_edges = openimage(img_filename)
    img_branches_angles = openimage(img_filename)
    img_min_angles = openimage(img_filename)
    """sorting for images"""
    dict_v1=sorted_vertices[image]
    dict_e1 =sorted_edges[image]
    sorted2_vertices = sorting_cells(dict_v1)  
        
    for cell in sorted2_vertices:
        print 'cell', cell
        """sorting for cells"""
        dict_v = sorted2_vertices[cell]
        list_v, kind_v = list_vert ( dict_v)
        dict_e = sort_edges_per_cell(dict_e1, list_v)  
        #getting tuples from edges
        tuple_e = get_v_ends(dict_e, list_v)
        """getting all possible branches for endpoints"""
        dict_branches = get_branches(list_v, kind_v, dict_v, dict_e)
        """proccesing list of all branches, estimating 'the strongest'
        branch for each endpoint"""
        dict_strongest_branches = strongest(dict_v, dict_e, dict_branches)
        """calculating the total length of neurits"""
        total_length = get_total_length(dict_strongest_branches)
        print "\nTotal length of neurits in the image:",image , "cell", cell, "is", total_length

        """calculating the mean angle of neurits"""
        mean_angle = get_mean_angle(dict_strongest_branches)
        print "\nMean angle of neurits in the image:",image , "cell", cell, "is", mean_angle,"\n"

        """calculating the minimal angle for mean angle of neurits"""
        min_mean, min_dict, min_i = get_lowest_mean_angle(dict_strongest_branches)
        center_coord = get_center_coord(dict_v)
        
        axis = min_i
        while True:
            img_min_angles = draw_on_image_angle(min_dict, dict_v,img_min_angles)
            img_min_angles = draw_axis(axis, center_coord ,img_min_angles)
            img_to_show = copy.deepcopy(img_min_angles)
            showimage(img_to_show, 'changing the axis'+str(axis)+' degrees')

            inp = raw_input('change the axis: value 1-180, ok to accept: ')
            if inp == 'ok':
                break
            axis = float(inp)
            min_dict = change_axis_in_dict(min_dict, float(inp))
            img_min_angles = copy.deepcopy(img_raw)
            cv2.destroyAllWindows()
      
            
        """saving into csv file"""
        with open('output_branches.csv', 'ab') as csvfile:
            fieldnames = dict_strongest_branches[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if header == False:
                writer.writeheader()
                header = True
            for branch in dict_strongest_branches:
                writer.writerow(dict_strongest_branches[branch])

        """ VISUALISATION"""
        
        img_branches = draw_on_image(dict_strongest_branches,img_branches, dict_v)
        img_all_vertices = show_all_vertices(dict_v,img_all_vertices) 
        img_all_edges = show_all_edges(dict_v,dict_e,img_all_edges)
        img_branches_angles = draw_on_image_angle(dict_strongest_branches, dict_v,img_branches_angles)
        
        """saving images into files"""
        cv2.imwrite(str(image)+'_branches.tif', img_branches)
        cv2.imwrite(str(image)+'_all_vertices.tif', img_all_vertices)
        cv2.imwrite(str(image)+'_all_edges.tif', img_all_edges)
        cv2.imwrite(str(image)+'_branches_angles.tif', img_branches_angles)
        cv2.imwrite(str(image)+'_min_angles.tif', img_min_angles)


    
                
