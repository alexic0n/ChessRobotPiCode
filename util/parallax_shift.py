def parallax_shift(coordinate_point, coordinate_center, height_camera, height_pieces):
    return [int(coordinate_point[0] + (coordinate_point[0] - coordinate_center[0]) * height_pieces / height_camera),
            int(coordinate_point[1] + (coordinate_point[1] - coordinate_center[1]) * height_pieces / height_camera)]
