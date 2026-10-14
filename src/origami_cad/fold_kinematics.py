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


def _scheduled_matrices(model, schedule, t):
    hinges = [dict(h, angle_deg=float(a)) for h, a in zip(model['hinges'], schedule)]
    return fold_matrices(dict(model, hinges=hinges), t)


def transform_point(matrix, point):
    return [sum(matrix[i][j]*v for j, v in enumerate([*point, 0.0, 1.0])) for i in range(3)]


def _solve(matrix, rhs):
    n = len(rhs)
    rows = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for c in range(n):
        pivot = max(range(c, n), key=lambda r: abs(rows[r][c]))
        if abs(rows[pivot][c]) <= 1e-12:
            raise ArithmeticError('Singular normal equations')
        rows[c], rows[pivot] = rows[pivot], rows[c]
        for r in range(n):
            if r != c:
                factor = rows[r][c]/rows[c][c]
                rows[r] = [v-factor*w for v, w in zip(rows[r], rows[c])]
    return [rows[i][n]/rows[i][i] for i in range(n)]


def least_squares_schedule(model, seams, start, free, weight=.05, iterations=40):
    """Levenberg-Marquardt on free hinge angles: seam gaps at 100% plus weak pull to source."""
    source = [h['angle_deg'] for h in model['hinges']]

    def residuals(x):
        schedule = list(start)
        for k, i in enumerate(free):
            schedule[i] = x[k]
        matrices = _scheduled_matrices(model, schedule, 1.0)
        r = [pa-pb for a, b, axis in seams for p in axis
             for pa, pb in zip(transform_point(matrices[a], p), transform_point(matrices[b], p))]
        r.extend(weight*(x[k]-source[i])/90 for k, i in enumerate(free))
        return schedule, r
    x = [start[i] for i in free]
    schedule, r = residuals(x)
    cost, damping = sum(v*v for v in r), 1e-3
    for _ in range(iterations):
        columns = []
        for k in range(len(x)):
            probe = list(x)
            probe[k] += 1e-4
            columns.append([(a-b)/1e-4 for a, b in zip(residuals(probe)[1], r)])
        normal = [[sum(ci*cj for ci, cj in zip(columns[i], columns[j])) for j in range(len(x))]
                  for i in range(len(x))]
        gradient = [sum(ci*ri for ci, ri in zip(columns[i], r)) for i in range(len(x))]
        try:
            step = _solve([[v+(damping*v if i == j else 0) for j, v in enumerate(row)]
                           for i, row in enumerate(normal)], [-g for g in gradient])
        except ArithmeticError:
            damping *= 10
            continue
        trial = [a+b for a, b in zip(x, step)]
        trial_schedule, trial_r = residuals(trial)
        trial_cost = sum(v*v for v in trial_r)
        if trial_cost < cost:
            x, schedule, r, cost, damping = trial, trial_schedule, trial_r, trial_cost, damping/3
            if max(map(abs, step)) < 1e-9:
                break
        else:
            damping *= 10
    return schedule
