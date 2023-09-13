import math
import numpy as np

def projection_military( vertex ):
    from consts import view_size
    x,y,z = vertex
    return (
        x - y + view_size//2,
        x + y - z + view_size//2,
    )


def make_projection_perspective( fov ):

    fovf = (1/math.tan(math.radians(fov/2)))
 

    def projection_perspective( vertex ):
        from consts import view_size
        x,y,z = vertex
        return (
            (y / x) * fovf * view_size//2 + view_size//2,
            (z / x) * fovf * view_size//2 + view_size//2
        )

    return projection_perspective

def render_sort_xyz_sum( item ):
    face, _, mesh_index = item
    x,y,z = [ ( face[0][i] + face[1][i] + face[2][i] ) / 3 for i in range(3) ]
    return x + y + z


def render_sort_distance( item ):
    face, _, mesh_index = item
    x,y,z = [ ( face[0][i] + face[1][i] + face[2][i] ) / 3 for i in range(3) ]
    v = np.array([x,y,z])
    dist = np.linalg.norm(v)
    return -dist


colors = {
    (2,0): '#af520a',
    (2,1): '#280c0a',

    (0,0): '#ff85d4',
    (0,1): '#ff3899',
    (3,0): '#ff85d4',
    (3,1): '#ff3899',

    (1,0): '#3e241d',
    (1,1): '#2c1816',

    (4,1): '#6084b0',
    (4,0): '#192345',

}


configs = {

    0: {
        'rotate-object': [ [(0,1,0),math.pi], [(0,0,1), math.pi*0.5]  ],
        'projection_object': projection_military,
        'colors': colors,
        'render-sort': render_sort_xyz_sum,
    },

    1: {
        'rotate-object': [ 
            [(0,1,0),math.pi], [(0,0,1), math.pi*0.5],
            [(0,1,0), -math.pi*0.34+math.pi*0.0]
        ],
        'move-object': (-1300,0,0),
        'projection_object': make_projection_perspective( fov = 30 ),
        'colors': colors,
        'render-sort': render_sort_distance,
    }

}



