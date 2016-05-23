"""
What you must do:

(1) Get the map.osm file
(2) Download the book's graph class
(3) Put the data returned by the getMap function into the books graph class
(4) Draw the graph on the screen. Draw those parts that fall within the
following latitude/longitude ranges
    minlon=121.4856
    minlat=31.2536
    maxlon=121.5792
    maxlat=31.2018
(5) Find the vertex nearest the mouse and draw its incident edges in red
(6) Find the connected component of the vertex nearest the mouse and
draw it in red
(7) Find the edges at most ten edges away from the vertex closest to the
mouse and draw it in red
(8) Do the same as 7 but make the color fade based on how many edges are on
the minimum-edge path to the vertex closest to the cursor
(9) Do domething else!

Hints:
-You are welcome to use the BFS/DFS code from the book.
-In the data set there are some duplicated edges, ignore them
-You may need to change the recursion limit for DFS to work. I did.

"""


import copy
import xml.etree.ElementTree as etree
from graph import Graph
import pygame
from pygame.locals import *
import sys
sys.setrecursionlimit(10000)
sys.path.append("ch09")
from adaptable_heap_priority_queue import *
import math


def getMap():
    """
This loads the map and returns a pair (V,E)
V contains the coordinates of the veritcies
E contains pairs of coordinates of the verticies
"""
    G=open("map.osm", encoding='utf8')    
    root = etree.parse(G).getroot()
    v={}
    for child in root:
        if (child.tag=="node"):
            v[child.attrib["id"]]=(float(child.attrib["lon"]),float(child.attrib["lat"]))
    e=[]
    for child in root:
        if (child.tag=="way"):
            a=[]
            for gc in child:
                if gc.tag=="nd":
                    a.append(v[gc.attrib["ref"]])
            for i in range(len(a)-1):
                e.append((a[i],a[i+1]))
    return list(v.values()),e

def main():
    map_graph=Graph()
    points,streets=getMap()
    minlon=121.4856
    minlat=31.2536
    maxlon=121.5792
    maxlat=31.2018
    resolution=12000
    point_vertex={}
    street_edge={}
    edge_element_list=[]
    for point in points:
        if minlon<=point[0]<=maxlon and minlat>=point[1]>=maxlat:
            vertex_element=(resolution*(point[0]-minlon),resolution*(minlat-point[1]))
            vertex=map_graph.insert_vertex(vertex_element)
            point_vertex[vertex_element]=vertex
    for street in streets:
        if minlon<=street[0][0]<=maxlon and minlat>=street[0][1]>=maxlat \
             and minlon<=street[1][0]<=maxlon and minlat>=street[1][1]>=maxlat:
            vertex_element1=(resolution*(street[0][0]-minlon),\
                resolution*(minlat-street[0][1]))
            vertex_element2=(resolution*(street[1][0]-minlon),\
                resolution*(minlat-street[1][1]))
            vertex1=point_vertex[vertex_element1]
            vertex2=point_vertex[vertex_element2]
            try:
                edge=map_graph.insert_edge(vertex1,vertex2,(vertex_element1,vertex_element2))
                street_edge[(vertex_element1,vertex_element2)]=edge
                edge_element_list.append((vertex_element1,vertex_element2))
            except ValueError:
                pass
    pygame.init()
    global width,height,dim
    (width,height) = (int(resolution*(maxlon-minlon)),int(resolution*(minlat-maxlat)))
    dim = (width,height)
    global screen
    screen = pygame.display.set_mode(dim, 0, 32)
    pygame.display.set_caption('Map')
    global font
    font = pygame.font.SysFont('楷体', 60)
    running=True
    one=False
    connected=False
    ten=False
    fade=False
    shortest=False
    get=False
    start=None
    global digit
    digit=False
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==KEYDOWN:
                if event.key==K_1:
                    one=not one
                elif event.key==K_2:
                    connected=not connected
                elif event.key==K_3:
                    ten=not ten
                elif event.key==K_4:
                    fade=not fade
                elif event.key==K_5:
                    shortest=not shortest
                elif event.key==K_e:
                    running=False
            elif event.type==pygame.MOUSEBUTTONDOWN:
                (x,y)=pygame.mouse.get_pos()
                start=findNearest(x,y,map_graph,None)
        screen.fill((255,255,255))
        text1=font.render(u"Shanghai Map",1,(0,0,0))
        screen.blit(text1, (width-300,0))
        if one:
            drawMap(edge_element_list,screen)
            queryOne(map_graph,screen)
        if connected:
            drawMap(edge_element_list,screen)
            queryAll(map_graph,screen)
        if ten:
            drawMap(edge_element_list,screen)
            queryTen(map_graph,screen)
        if fade:
            queryFade(map_graph,screen)
        if shortest:
            drawMap(edge_element_list,screen)
            if start is not None:
                get_shortest_path(map_graph,screen,start)
        pygame.display.update()

def drawMap(edge_element_list,screen):
    for edge_element in edge_element_list:
        pygame.draw.line(screen,(0,0,0),edge_element[0],edge_element[1],1)

def findNearest(x,y,map_graph,v):
    near=1000000000000
    for vertex in map_graph.vertices():
        current=(vertex.element()[0]-x)**2+(vertex.element()[1]-y)**2
        if current<=near:
            near=current
            v=vertex
    return v


def queryOne(map_graph,screen):
    (x,y)=pygame.mouse.get_pos()
    v=None
    v=findNearest(x,y,map_graph,v)
    if v:
        for edge in map_graph.incident_edges(v):
            if edge.element():
                pygame.draw.line(screen,(255,0,0),edge.element()[0],edge.element()[1],6)

def queryAll(map_graph,screen):
    (x,y)=pygame.mouse.get_pos()
    v=None
    v=findNearest(x,y,map_graph,v)
    if v:
        _queryAll(map_graph,v,{})

def _queryAll(g, u, discovered):
    for e in g.incident_edges(u):
        v=e.opposite(u)
        if e.element():
            pygame.draw.line(screen,(255,0,0),e.element()[0],e.element()[1],6)
        if v not in discovered:
            discovered[v]=e
            _queryAll(g,v,discovered)


def queryTen(map_graph,screen):
    (x,y)=pygame.mouse.get_pos()
    v=None
    v=findNearest(x,y,map_graph,v)
    if v:
        _queryTen(map_graph,v,{},0)

def _queryTen(g, u, discovered, degree):
    if degree<=9:
        for e in g.incident_edges(u):
            v=e.opposite(u)
            if v not in discovered:
                discovered[v]=e
                if e.element():
                    pygame.draw.line(screen,(255,0,0),e.element()[0],e.element()[1],6)
                _queryTen(g,v,discovered,degree+1)
    else:
        return

def queryFade(map_graph,screen):
    (x,y)=pygame.mouse.get_pos()
    v=None
    v=findNearest(x,y,map_graph,v)
    if v:
        _queryFade(map_graph,v,{},0)

def _queryFade(g, u, discovered, degree):
    if degree<=9:
        for e in g.incident_edges(u):
            v=e.opposite(u)
            if v not in discovered:
                discovered[v]=e
                if e.element():
                    pygame.draw.line(screen,(255*0.8**degree,0,0),e.element()[0],e.element()[1],6)
                _queryFade(g,v,discovered,degree+1)
    else:
        return

def shortest_path_tree(g,s,end):
    d = {}
    cloud = {}
    pq = AdaptableHeapPriorityQueue()
    pqlocator = {}
    for v in g.vertices():
        if v is s:
            d[v] = 0
        else:
            d[v] = float('inf')
        pqlocator[v] = pq.add(d[v], v)

    while not pq.is_empty():
        key, u = pq.remove_min()
        cloud[u] = key
        del pqlocator[u]
        for e in g.incident_edges(u):
            v = e.opposite(u)
            if v not in cloud:
                wgt = e.element()
                distance=math.sqrt((wgt[0][0]-wgt[1][0])**2+(wgt[0][1]-wgt[1][1])**2)
                if d[u] + distance < d[v]:
                    d[v] = d[u] + distance
                    pq.update(pqlocator[v], d[v], v)

    tree = []
    while end is not s:
        for e in g.incident_edges(end):
            u = e.opposite(end)
            wgt = e.element()
            distance=math.sqrt((wgt[0][0]-wgt[1][0])**2+(wgt[0][1]-wgt[1][1])**2)
            if d[end] == d[u] + distance:
                tree.append((end,u))
                end=u
    for element in tree:
        point1=(element[0].element()[0],element[0].element()[1])
        point2=(element[1].element()[0],element[1].element()[1])
        pygame.draw.line(screen, (255,0,0),point1,point2,6)

def get_shortest_path(map_graph,screen,vertex):
    (x,y)=pygame.mouse.get_pos()
    v=findNearest(x,y,map_graph,None)
    if v:
        shortest_path_tree(map_graph,vertex,v)

main()

