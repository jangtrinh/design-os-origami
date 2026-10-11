"""Parent-relative Rodrigues transforms for the serialized hinge tree."""
import math


def identity():
    return [[float(i == j) for j in range(4)] for i in range(4)]


def multiply(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def rotation_about_axis(axis, angle_deg):
    """Original XY axis; compose parent * rotation, never rotate about world axis."""
    a, b = axis
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    if not math.isfinite(length) or length <= 1e-7:
        raise ValueError('Invalid hinge axis')
    x, y, z = dx/length, dy/length, 0.0
    c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    v = 1-c
    matrix = identity()
    matrix[:3] = [[c+x*x*v, x*y*v-z*s, x*z*v+y*s, 0.0],
                  [y*x*v+z*s, c+y*y*v, y*z*v-x*s, 0.0],
                  [z*x*v-y*s, z*y*v+x*s, c+z*z*v, 0.0]]
    origin = [*a, 0.0]
    for i in range(3):
        matrix[i][3] = origin[i]-sum(matrix[i][j]*origin[j] for j in range(3))
    return matrix


def fold_matrices(model, t):
    if not math.isfinite(t) or not 0 <= t <= 1:
        raise ValueError('Fold progress must be finite and within [0, 1]')
    if not model['available']:
        return {}
    ids = {f['id'] for f in model['faces']}
    if len(ids) != len(model['faces']) or model['root'] not in ids:
        raise ValueError('Invalid fold faces or root')
    matrices = {model['root']: identity()}
    for hinge in model['hinges']:
        parent, child = hinge['parent'], hinge['child']
        if parent not in matrices or child in matrices or child not in ids:
            raise ValueError('Hinges must span faces in parent-before-child order')
        if not math.isfinite(hinge['angle_deg']):
            raise ValueError('Nonfinite fold angle')
        matrices[child] = multiply(matrices[parent],
                                   rotation_about_axis(hinge['axis'], t*hinge['angle_deg']))
    if matrices.keys() != ids:
        raise ValueError('Incomplete hinge tree')
    return matrices


def fold_vertices(model, t):
    """Return face id -> transformed outer vertices in source millimetres."""
    matrices = fold_matrices(model, t)
    return {f['id']: [[sum(matrices[f['id']][i][j]*v for j, v in
                          enumerate([*p, 0.0, 1.0])) for i in range(3)]
                      for p in f['vertices']] for f in model['faces']}
