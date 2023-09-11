# ---------------------------------------- 
# file: main.py
# author: coppermouse
# ----------------------------------------

import pygame
import math
import colorsys
import numpy as np
from glb_material_mesh_index import glb_material_mesh_index


view_size = 600
# color_type = 'MESH_INDEX'
color_type = 'MATERIAL'


def rotate( faces, axis, theta ):

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

    for i in range(3):
        faces[:, i] = faces[:, i].dot( rotation_matrix )


def p3dto2d( vertex ):
    # projection method.
    x,y,z = vertex
    r = (
        x - y + view_size//2,
        x + y - z + view_size//2,
    )
    return r


# --- load and transform object to view
with open('object.glb', 'rb') as f:
    faces, materials, mesh_indexes = glb_material_mesh_index(f)

rotate(faces, (0,1,0), math.pi )
rotate(faces, (0,0,1), math.pi*0.5 )
faces *= 250
faces += (0,0,120)

# ----


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

_quit = False
while not _quit:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _quit = True
        if event.type == pygame.KEYDOWN:
            _quit = True

    polygons = list()
    for face, material, mesh_index in sorted( zip( faces, materials, mesh_indexes ), key = render_sort ):

        if color_type == 'MATERIAL':
            color = material_colors[ material ]
        elif color_type == 'MESH_INDEX':
            color = mesh_index_colors[ mesh_index ]

        polygon = [ p3dto2d( vertex ) for vertex in face ]
        polygons.append( ( polygon, color ) )


    for polygon, color in polygons:
        pygame.draw.polygon( screen, color, polygon )

    clock.tick(60)
    pygame.display.update()


