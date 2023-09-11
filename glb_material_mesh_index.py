# ---------------------------------------- 
# file: main.py
# author: coppermouse
# ----------------------------------------

import json
import numpy as np

def glb_material_mesh_index( file_obj ):

    # Disclaimer: 
    # ----
    # I have borrowed a lot of code from the trimesh code base.
    # https://github.com/mikedh/trimesh
    #
    # Specifically this file: https://github.com/mikedh/trimesh/blob/main/trimesh/exchange/gltf.py
    # 
    # I do however cleared out eveything not needed for this project but added my own trigon list 
    # builder and also connected materials and the original mesh indexes to it.
    #

    _dtypes = { 5123: '<u2', 5126: '<f4'}
    _shapes = { 'SCALAR': 1, 'VEC2': 2, 'VEC3': 3 }

    start = file_obj.tell()
    head_data = file_obj.read(20)
    head = np.frombuffer(head_data, dtype='<u4')
    length, chunk_length = head[2:4]
    json_data = file_obj.read( int(chunk_length) )
    header = json.loads( json_data )
    buffers = []
    while (file_obj.tell() - start) < length:
        chunk_head = file_obj.read(8)
        chunk_length, chunk_type = np.frombuffer( chunk_head, dtype='<u4' )
        chunk_data = file_obj.read( int(chunk_length) )
        buffers.append( chunk_data )

    views = [None] * len( header['bufferViews'] )
    for i, view in enumerate( header['bufferViews'] ):
        start = view['byteOffset']
        end = start + view['byteLength']
        views[i] = buffers[view['buffer']][start:end]
        assert len( views[i] ) == view['byteLength']

    access = [None] * len( header['accessors'] )
    for index, a in enumerate(header["accessors"]):
        count = a['count']
        dtype = np.dtype( _dtypes[ a['componentType'] ])
        per_item = _shapes[ a['type'] ]
        shape = np.append( count, per_item )
        per_count = np.abs( np.prod( per_item ))
        data = views[ a['bufferView'] ]
        start = a.get( 'byteOffset', 0 )
        length = dtype.itemsize * count * per_count
        access[ index ] = np.frombuffer( data[start:start + length], dtype=dtype ).reshape( shape )

    final_faces, materials, mesh_indexes, mesh_indexes_thresholds = [], [], [], []
    current_mesh_index = 0
    for mesh_index, m in enumerate( header['meshes'] ):

        if current_mesh_index != mesh_index:
            end = len(final_faces)
            start = 0 if not mesh_indexes_thresholds else mesh_indexes_thresholds[-1][1] 
            mesh_indexes_thresholds.append( (start,end) )
            current_mesh_index = mesh_index

        for p in m['primitives']:
            vertices = access[ p['attributes']['POSITION'] ]
            for indices in access[ p['indices'] ].reshape( (-1, 3) ):
                final_faces.append( [ vertices[i] for i in indices ] )
                materials.append( p['material'] )
                mesh_indexes.append( mesh_index )

    start = 0 if not mesh_indexes_thresholds else mesh_indexes_thresholds[-1][1] 
    end = len(final_faces)
    mesh_indexes_thresholds.append( (start,end) )
    return np.array(final_faces), materials, mesh_indexes, mesh_indexes_thresholds


