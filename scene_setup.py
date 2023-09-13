import math

def projection_military( vertex ):
    from consts import view_size
    x,y,z = vertex
    return (
        x - y + view_size//2,
        x + y - z + view_size//2,
    )

def projection_perspective( vertex ):
    from consts import view_size
    x,y,z = vertex
    return (
        (y / x) * view_size//2 + view_size//2,
        (z / x) * view_size//2 + view_size//2

    )


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
    },

    1: {
        'rotate-object': [ 
            [(0,1,0),math.pi], [(0,0,1), math.pi*0.5],
            [(0,1,0), -math.pi*0.34+math.pi*0.0]
        ],
        'move-object': (-2100,0,0),
        'projection_object': projection_perspective,
        'colors': colors,
    }

}



