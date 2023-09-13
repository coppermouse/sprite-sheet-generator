# ---------------------------------------- 
# file: main.py
# author: coppermouse
# ----------------------------------------

import sys
import pygame
import math
import colorsys
import numpy as np
from consts import view_size
from scene_setup import configs
from glb_material_mesh_index import glb_material_mesh_index


hvs = half_view_size = view_size // 2

# color_type = 'MESH_INDEX'
color_type = 'MATERIAL'

config_index = int(sys.argv[1])


def rotate( faces, axis, theta, _slice = None, point = None ):

    # I based this code on numpy-stl rotation logic.
    # I wouldn't know how to figure out this math myself.

    # --- calc rotation matrix
    axis = np.asarray(axis)
    theta = 0.5 * np.asarray(theta)
    axis = axis / np.linalg.norm(axis)

    a = math.cos(theta)
    b, c, d = - axis * math.sin(theta)
    angles = a, b, c, d
    powers = [x * y for x in angles for y in angles]
    aa, ab, ac, ad = powers[0:4]
    ba, bb, bc, bd = powers[4:8]
    ca, cb, cc, cd = powers[8:12]
    da, db, dc, dd = powers[12:16]

    rotation_matrix = np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
    # ---
        
    if _slice:
        faces = faces[ _slice[0] : _slice[1] ]

    if point:
        point = np.array(point)
        for i in range(3):
            faces[:, i] = ( faces[:, i] - point ).dot( rotation_matrix ) + point
    else:
        for i in range(3):
            faces[:, i] = faces[:, i].dot( rotation_matrix )


config = configs[ config_index ]

# --- load and transform object to view
with open('object2.glb', 'rb') as f:
    faces, materials, mesh_indexes, mesh_indexes_thresholds = glb_material_mesh_index(f)

for axis, theta in config['rotate-object']:
    rotate(faces, axis, theta )
#rotate(faces, (0,1,0), -math.pi*0.34 )

move = config.get('move-object', (0,0,0) )
faces *= [[250,250,250],[250,250,250],[250,250,250],[1,1,1]] # TODO: this is just temp...
faces += [move,move,move,[0,0,0]] # TODO: this is just temp...

#rotate(faces, (1,0,0), math.pi*1.5, mesh_indexes_thresholds[6], [0,-68,28] )
#rotate(faces, (1,0,0), math.pi*0.5, mesh_indexes_thresholds[3], [0,68,28] )

# ----


p3dto2d = config['projection_object']


# --- setup color lists
materials_values = set()
mesh_index_values = set()

for material, mesh_index in zip( materials, mesh_indexes ):
    materials_values.add( material )
    mesh_index_values.add( mesh_index )

material_colors = []
for i in range(len(materials_values)):
    material_colors.append( tuple(
        [ int(c*255) for c in colorsys.hsv_to_rgb( (1/len( materials_values ))*i,1,1 )]))

mesh_index_colors = []
for i in range(len(mesh_index_values)):
    mesh_index_colors.append( tuple(
        [ int(c*255) for c in colorsys.hsv_to_rgb( (1/len( mesh_index_values ))*i,1,1 )]))
# ---


def render_sort( item ):
    face, _, mesh_index = item
    x,y,z = [ ( face[0][i] + face[1][i] + face[2][i] ) / 3 for i in range(3) ]
    return x + y + z

pygame.init()
screen = pygame.display.set_mode( (view_size,)*2 )

clock = pygame.time.Clock()

sun_vectors = [ np.array(v) for v in [ (10,10,0),(-10,-10,0) ] ]

_quit = False

hover = None
hold = None

view = [0,1] # what axis is x,y on screen.


def project_view( v ): # project 3d point to screen based on view
    return [ v[d] + hvs for d in view ]


def unproject_view( p ): # unproject a screen point to 3d point based on view
    x, y = p
    return ( view[0], x-hvs ), ( view[1], y-hvs )


def get_sun_vector():
    a,b = sun_vectors
    v = a-b
    norm = np.linalg.norm(v)
    r = v / norm
    return r


selected_color = {
    'h': 0,
    's': 0,
    'v': 0,
}

selected_color_index = 0

while not _quit:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _quit = True
        elif event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            hold = hover


            for e, color in enumerate(material_colors):
                rect = pygame.Rect(( 0, e*40, 40, 40 ))
                if rect.collidepoint( event.pos ):
                    selected_color_index = e

            for e, t in enumerate(('h','s','v')):
                if event.pos[1] >= 570+e*10 and event.pos[1] < 580+e*10:
                    selected_color[t] = event.pos[0]/600


                    material_colors[selected_color_index] = pygame.Color(np.array(colorsys.hsv_to_rgb(**selected_color))*255 )

        elif event.type == pygame.MOUSEBUTTONUP:
            hold = None

    # switch between x,y and x,z by holdning left ctrl
    if pygame.key.get_pressed()[pygame.K_LCTRL]:
        view = [0,2]
    else:
        view = [0,1]

    if hold:
        for e, c in enumerate(sun_vectors):
            if hold == ('sv',e):
                for i, v in unproject_view( pygame.mouse.get_pos() ):
                    c[i] = v

    else:
        hover = None
        for e, c in enumerate(sun_vectors):
            a = project_view(c)
            b = np.array(pygame.mouse.get_pos())
            dist = np.linalg.norm(a-b)
            if dist < 8:
                hover = ('sv',e)        

    #rotate(faces, (0,1,0), math.pi*0.01, mesh_indexes_thresholds[3], [0,68,28] )

    polygons = list()
    for face, material, mesh_index in sorted( zip( faces, materials, mesh_indexes ), key = render_sort ):

        if color_type == 'MATERIAL':
            color = material_colors[ material ]
        elif color_type == 'MESH_INDEX':
            color = mesh_index_colors[ mesh_index ]

        polygon = [ p3dto2d( vertex ) for vertex in face[:3] ]
        v = face[3].dot( get_sun_vector()  )
        v = (v+1)/2
        if 0 < v < 1:
            polygons.append( ( polygon, pygame.Color(color).lerp( '#000000', v )))

    screen.fill( 0x112233 )
    for polygon, color in polygons:
        pygame.draw.polygon( screen, color, polygon )


    
    pygame.draw.line( screen, 'yellow', *[ project_view(sv) for sv in sun_vectors] )
    for e, c in enumerate( sun_vectors ):
        pygame.draw.circle( screen, 'blue' if not hover == ('sv',e) else 'white', project_view(c), 8,1  )


    for e, t in enumerate(('h','s','v')):
        for c in range(600):
            rgb = colorsys.hsv_to_rgb( **selected_color | {t:c/600} )
            color = pygame.Color(np.array(rgb)*255)
            pygame.draw.rect( screen, color, (c,570+e*10,1,10) )


    for e, color in enumerate(material_colors):
        pygame.draw.rect( screen, color, (0,e*40,40,40) )

    pygame.draw.rect( screen, 'white', (0,hvs,view_size,1) )
    pygame.draw.rect( screen, 'white', (hvs,0,1,view_size) )


    clock.tick(60)
    pygame.display.update()


