import numpy as np
import vedo



H  = 3.0   # floor-to-floor height
Z0 = H     # floor 2 base elevation (z = 3)
W  = 0.2   # wall thickness


# Purple doors
purple = [(10,2),(10,4),(10,13),(10,11),(18,4)]

red    = [(19,6),(19,8)]
orange = [(23,6),(23,8)]
black = [(19,9),(19,11)]
green = [(23,9),(23,11)]

wall_segments = [

    # ── Outer south wall  y = 0 ──────────────────────────────────────────────
    ((0,0),   (10,0)),
    ((10,0),  (15,0)),
    ((15,0),  (25,0)),

    # ── Outer west wall  x = 0 ───────────────────────────────────────────────
    ((0,0),   (0,7)),
    ((0,7),   (0,14)),

    # ── Outer north wall  y = 14 ─────────────────────────────────────────────
    ((0,14),  (10,14)),
    ((10,14), (15,14)),
    ((15,14), (20,14)),
    ((20,14), (25,14)),   

    # ── Outer east wall  x = 25 ──────────────────────────────────────────────
    ((25,0),  (25,4)),
    ((25,4),  (25,14)),   

    # ── Inner wall  y = 4  (east sub-block boundary) ─────────────────────────
    ((18,4),  (20,4)),    # wall east of door gap
    ((20,4),  (25,4)),    # inner wall east of ramp zone

    # ── Inner vertical  x = 15  (south segment only) ─────────────────────────
    ((15,0),  (15,4)),   


    # ── Interior vertical  x = 10  (full height with door gaps) ──────────────
    ((10,0),  (10,2)),    # south to first door
    ((10,4),  (10,7)),    # between door and mid-divider
    ((10,7),  (10,11)),   # mid-divider to second door
    ((10,13), (10,14)),   # above second door to north wall

    # ── Interior horizontal  y = 7  ────────────────────────
    ((0,7),   (10,7)),

]


def make_wall(p1, p2, z0=Z0, h=H, t=W):
    x1,y1 = p1; x2,y2 = p2
    length = float(np.hypot(x2-x1, y2-y1))
    if length < 0.01:
        return None
    cx,cy,cz = (x1+x2)/2, (y1+y2)/2, z0+h/2
    angle = float(np.degrees(np.arctan2(y2-y1, x2-x1)))
    box = vedo.Box(pos=(cx,cy,cz), size=(length, t, h))
    box.rotate_z(angle, around=(cx,cy,cz))
    return box.color('#e8e2d6').alpha(0.93)

def slab(x0,x1,y0,y1,z0,z1,color,alpha):
    return vedo.Box(pos=[x0,x1,y0,y1,z0,z1]).color(color).alpha(alpha)


# BUILD FLOOR 2


# Unified floor & ceiling slab  x∈[0,25], y∈[0,14]
floor_slab = slab(0, 25, 0, 14, Z0-0.2, Z0,       '#c9b99a', 0.95)
ceil_slab  = slab(0, 25, 0, 14, Z0+H,   Z0+H+0.1, '#aaaaaa', 0.06)

# Walls
walls_3d = [w for p1,p2 in wall_segments for w in [make_wall(p1,p2)] if w]

# Door markers (purple spheres at mid-height of this floor)
doors_3d = [vedo.Sphere(pos=(x, y, Z0+1.5), r=0.22).color('#9467bd') for x,y in purple]

# ── Ramp 1: Floor1 → Floor2  red(bottom,z=0) → orange(top,z=Z0) ─────────────
ramp1_pts = np.array([
    [red[0][0],    red[0][1],    0.0],   # (20, 6, 0)  bottom-left
    [red[1][0],    red[1][1],    0.0],   # (20, 8, 0)  bottom-right
    [orange[1][0], orange[1][1], Z0 ],   # (24, 8, 3)  top-right
    [orange[0][0], orange[0][1], Z0 ],   # (24, 6, 3)  top-left
], dtype=float)
ramp1 = vedo.Mesh([ramp1_pts, [[0,1,2],[0,2,3]]]).color('darkorange').alpha(0.9)
ramp1.backface_culling(False)

ramp1_left       = vedo.Mesh([np.array([[19,6,0],[23,6,Z0],[19,6,Z0]], dtype=float), [[0,1,2]]])
ramp1_right      = vedo.Mesh([np.array([[19,8,0],[23,8,Z0],[19,8,Z0]], dtype=float), [[0,1,2]]])
ramp1_base_left  = vedo.Mesh([np.array([[19,6,0],[23,6,Z0],[23,6,0]],  dtype=float), [[0,1,2]]])
ramp1_base_right = vedo.Mesh([np.array([[19,8,0],[23,8,Z0],[23,8,0]],  dtype=float), [[0,1,2]]])
ramp1_left.color('sandybrown').alpha(0.8).backface_culling(False)
ramp1_right.color('sandybrown').alpha(0.8).backface_culling(False)
ramp1_base_left.color('sandybrown').alpha(0.8).backface_culling(False)
ramp1_base_right.color('sandybrown').alpha(0.8).backface_culling(False)

# Support columns at orange points (23,6) and (23,8): from z=0 up to z=Z0
ramp1_support_cols = [
    vedo.Cylinder(pos=[(23, 6, 0), (23, 6, Z0)], r=0.18, c='#8B7355', alpha=0.95),
    vedo.Cylinder(pos=[(23, 8, 0), (23, 8, Z0)], r=0.18, c='#8B7355', alpha=0.95),
]

red_sph    = [vedo.Sphere(pos=(x, y, 0.28),    r=0.28).color('red')    for x,y in red]
orange_sph = [vedo.Sphere(pos=(x, y, Z0+0.15), r=0.28).color('orange') for x,y in orange]

# ── Ramp 2: Floor2 → Floor3  green(bottom,z=Z0) → black(top,z=Z0+H) ──────────

ramp2_pts = np.array([
    [green[0][0], green[0][1], Z0  ],    # (24,  9, 3)  bottom-left
    [green[1][0], green[1][1], Z0  ],    # (24, 11, 3)  bottom-right
    [black[1][0], black[1][1], Z0+H],   # (20, 11, 6)  top-right
    [black[0][0], black[0][1], Z0+H],   # (20,  9, 6)  top-left
], dtype=float)
ramp2 = vedo.Mesh([ramp2_pts, [[0,1,2],[0,2,3]]]).color('darkorange').alpha(0.9)
ramp2.backface_culling(False)

left_tri2       = vedo.Mesh([np.array([[23,9, Z0],[19,9, Z0+H],[23,9, Z0+H]], dtype=float), [[0,1,2]]])
right_tri2      = vedo.Mesh([np.array([[23,11,Z0],[19,11,Z0+H],[23,11,Z0+H]], dtype=float), [[0,1,2]]])
base_left_tri2  = vedo.Mesh([np.array([[23,9, Z0],[19,9, Z0+H],[19,9, Z0]],   dtype=float), [[0,1,2]]])
base_right_tri2 = vedo.Mesh([np.array([[23,11,Z0],[19,11,Z0+H],[19,11,Z0]],   dtype=float), [[0,1,2]]])
left_tri2.color('sandybrown').alpha(0.8).backface_culling(False)
right_tri2.color('sandybrown').alpha(0.8).backface_culling(False)
base_left_tri2.color('sandybrown').alpha(0.8).backface_culling(False)
base_right_tri2.color('sandybrown').alpha(0.8).backface_culling(False)

# Support columns at green points (23,9) and (23,11): from z=Z0 up to z=Z0+H
ramp2_support_cols = [
    vedo.Cylinder(pos=[(19, 9,  Z0), (19, 9,  Z0+H)], r=0.18, c='#8B7355', alpha=0.95),
    vedo.Cylinder(pos=[(19, 11, Z0), (19, 11, Z0+H)], r=0.18, c='#8B7355', alpha=0.95),
]

green_sph = [vedo.Sphere(pos=(x, y, Z0+0.15),   r=0.28).color('green') for x,y in green]
black_sph = [vedo.Sphere(pos=(x, y, Z0+H+0.15), r=0.28).color('black') for x,y in black]

# Axes + label
axes  = vedo.Axes(xrange=(0,26), yrange=(0,15), zrange=(0,Z0+H+2),
                  xtitle='x', ytitle='y', ztitle='z', axes_linewidth=2)
label = vedo.Text3D('Floor 2  (z = 3)', pos=(0.5, 0.3, Z0+H+0.5), s=0.42, c='navy')

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE & SHOW
# ─────────────────────────────────────────────────────────────────────────────
scene = (
    [floor_slab, ceil_slab, label]
    + walls_3d
    + doors_3d
    + [ramp1, ramp1_left, ramp1_right, ramp1_base_left, ramp1_base_right]
    + ramp1_support_cols
    + red_sph + orange_sph
    + [ramp2, left_tri2, right_tri2, base_left_tri2, base_right_tri2]
    + ramp2_support_cols
    + green_sph + black_sph
    + [axes]
)

vedo.show(
    *scene,
    title='Floor 2',
    viewup='z',
    camera={
        'pos':         (55, -18, 35),
        'focal_point': (12,   7,  4.5),
        'viewup':      ( 0,   0,  1),
    },
    interactive=True,
)