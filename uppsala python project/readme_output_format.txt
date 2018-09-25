VERTEX
###### line - row of comma separate vaulues
1 row - header(names files columns)
each next row - vertex in the neuron skeleton graph, either a branchpoint, trunk or endpoint

columns:
1 image_number
2 vertex_number (within the image)
3 i (i coordinate of the vertex)
4 j (the J coordinate of the vertex)
5 label (the label of the seed object associoated with the vertex)
6 kind (type T-trunk, B-branchpoint, E-endpoint)

######
EDGES
######
1 row - a header
next rows - represent edges or connections between two vertices(including betwen a vertex and itself for certain loops)

columns:
1 v1 the zero based index into the vertex table of the first vertex in the edge
2 v2 the zero based index into the vertez table of the second vertez in the edge
3 legth the number of pixels in the path connecting the two vertices including both vertex pixels
4 total_intensity the sum of the intensities of the pixels in the edge, including both vertex pixel intensities