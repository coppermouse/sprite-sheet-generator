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


configs = {

    0: {
        'rotate-object': [ [(0,1,0),math.pi], [(0,0,1), math.pi*0.5]  ],
        'projection_object': projection_military
    },

    1: {
        'rotate-object': [ 
            [(0,1,0),math.pi], [(0,0,1), math.pi*0.5],
            [(0,1,0), -math.pi*0.34+math.pi*0.5]
        ],
        'move-object': (-800,0,0),
        'projection_object': projection_perspective,
    }

}



