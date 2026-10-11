"""Outward miter envelope as the union of blank, edge strips and corner wedges."""
import math
from origami_cad.geometry import Point2D

EPS = 1e-7


def area(points):
    return sum(a.x*b.y-b.x*a.y for a,b in zip(points,points[1:]+points[:1]))/2


def inside(p, polygon):
    hit = False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:
            hit = not hit
    return hit


def outward_envelope(points, distance):
    if distance == 0:
        return list(points)
    sign = 1 if area(points)>0 else -1
    shifted, pieces, candidates = [], [points], []
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dy=b.x-a.x,b.y-a.y
        length=math.hypot(dx,dy)
        nx,ny=sign*dy/length*distance,-sign*dx/length*distance
        p,q=Point2D(a.x+nx,a.y+ny),Point2D(b.x+nx,b.y+ny)
        if any(not math.isfinite(v) for pt in (p,q) for v in (pt.x,pt.y)):
            raise ValueError('Bleed arithmetic overflow')
        shifted.append((p,q))
        pieces.append([a,b,q,p])
        candidates.append((p,q))
    for i,v in enumerate(points):
        a,b=points[i-1],points[(i+1)%len(points)]
        dx,dy=v.x-a.x,v.y-a.y
        ex,ey=b.x-v.x,b.y-v.y
        den=dx*ey-dy*ex
        if den*sign <= EPS:
            continue  # Concave joins arise from overlap of outward edge strips.
        p,q=shifted[i-1][1],shifted[i][0]
        t=((q.x-p.x)*ey-(q.y-p.y)*ex)/den
        m=Point2D(p.x+t*dx,p.y+t*dy)
        if not math.isfinite(m.x) or not math.isfinite(m.y):
            raise ValueError('Bleed arithmetic overflow')
        pieces.append([v,p,m,q])
        candidates.extend([(p,m),(m,q)])
    boundary=[]
    for i,(a,b) in enumerate(candidates):
        dx,dy=b.x-a.x,b.y-a.y
        length=math.hypot(dx,dy)
        if length<=EPS:continue
        cuts=[0.0,1.0]
        for j,(c,d) in enumerate(candidates):
            if i==j:continue
            ex,ey=d.x-c.x,d.y-c.y
            den=dx*ey-dy*ex
            if abs(den)<1e-12:continue
            t=((c.x-a.x)*ey-(c.y-a.y)*ex)/den
            u=((c.x-a.x)*dy-(c.y-a.y)*dx)/den
            if -EPS<=t<=1+EPS and -EPS<=u<=1+EPS:cuts.append(max(0,min(1,t)))
        cuts=sorted(set(round(t,12) for t in cuts))
        for t,u in zip(cuts,cuts[1:]):
            if (u-t)*length<=EPS:continue
            mid=Point2D(a.x+(t+u)/2*dx,a.y+(t+u)/2*dy)
            delta=min(1e-5,distance*1e-5,(u-t)*length*1e-4)
            left=Point2D(mid.x-dy/length*delta,mid.y+dx/length*delta)
            right=Point2D(mid.x+dy/length*delta,mid.y-dx/length*delta)
            in_left=any(inside(left,poly) for poly in pieces)
            in_right=any(inside(right,poly) for poly in pieces)
            if in_left!=in_right:
                p=Point2D(a.x+t*dx,a.y+t*dy)
                q=Point2D(a.x+u*dx,a.y+u*dy)
                boundary.append((p,q) if in_left else (q,p))
    # Trace exterior and any closed cavities; only the exterior is a bleed contour.
    vertices, outgoing = [], {}
    def node(p):
        for i,v in enumerate(vertices):
            if p.distance_to(v)<=EPS:return i
        vertices.append(p)
        return len(vertices)-1
    for a,b in boundary:
        i,j=node(a),node(b)
        if i in outgoing and outgoing[i]!=j:
            raise ValueError('Ambiguous bleed boundary')
        outgoing[i]=j
    loops=[]
    while outgoing:
        start=next(iter(outgoing)); current=start; loop=[]
        while current in outgoing:
            loop.append(vertices[current]);current=outgoing.pop(current)
            if current==start:break
        if current!=start or len(loop)<3:raise ValueError('Open bleed boundary')
        loops.append(loop)
    if not loops:raise ValueError('Empty bleed boundary')
    return max(loops,key=lambda p:abs(area(p)))
