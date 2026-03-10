import numpy as np
import vedo


H  = 3.0    # floor-to-floor height
Z0 = 2 * H  # floor 3 base elevation (z = 6)
W  = 0.2    # wall thickness



purple = [(10,2),(10,4),(10,13),(10,11),(18,4)]

green = [(23,9),(23,11)]   # ramp entrance on this floor  z = Z0 = 6
black = [(19,9),(19,11)]   # ramp exit down to floor 2    z = Z0-H = 3


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
    # [open: (15,4) → (18,4) = one-sided door]
    ((18,4),  (20,4)),
    ((20,4),  (25,4)),

    # ── Inner vertical  x = 15  (south segment only) ─────────────────────────
    ((15,0),  (15,4)),

    # ── Interior vertical  x = 10  (full height with door gaps) ──────────────
    ((10,0),  (10,2)),
    # [open: (10,2) → (10,4) = door gap]
    ((10,4),  (10,7)),
    ((10,7),  (10,11)),
    # [open: (10,11) → (10,13) = door gap]
    ((10,13), (10,14)),

    # ── Interior horizontal  y = 7  (x = 0..10 only) ────────────────────────
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

# BUILD FLOOR3


# Floor & ceiling slabs
floor_slab = slab(0, 25, 0, 14, Z0-0.2, Z0,       '#c9b99a', 0.95)
ceil_slab  = slab(0, 25, 0, 14, Z0+H,   Z0+H+0.1, '#aaaaaa', 0.06)

# Walls
walls_3d = [w for p1,p2 in wall_segments for w in [make_wall(p1,p2)] if w]

# Door markers
doors_3d = [vedo.Sphere(pos=(x, y, Z0+1.5), r=0.22).color('#9467bd') for x,y in purple]

# ── Ramp 2: Floor3 → Floor2  green(top,z=Z0) → black(bottom,z=Z0-H) ──────────
# Ramp descends from green at z=Z0 down to black at z=Z0-H=3
ramp2_pts = np.array([
    [black[0][0], black[0][1], Z0],   # (20,  9, 3)  bottom-left
    [black[1][0], black[1][1], Z0],   # (20, 11, 3)  bottom-right
    [green[1][0], green[1][1], Z0-H  ],   # (24, 11, 6)  top-right
    [green[0][0], green[0][1], Z0-H  ],   # (24,  9, 6)  top-left
], dtype=float)
ramp2 = vedo.Mesh([ramp2_pts, [[0,1,2],[0,2,3]]]).color('darkorange').alpha(0.9)
ramp2.backface_culling(False)

left_tri2       = vedo.Mesh([np.array([[19,9, Z0-H],[23,9, Z0-H],[19,9, Z0]], dtype=float), [[0,1,2]]])
right_tri2      = vedo.Mesh([np.array([[19,11,Z0-H],[23,11,Z0-H],[19,11,Z0]], dtype=float), [[0,1,2]]])
base_left_tri2  = vedo.Mesh([np.array([[23,9, Z0-H],[19,9, Z0],[23,9, Z0]],   dtype=float), [[0,1,2]]])
base_right_tri2 = vedo.Mesh([np.array([[23,11,Z0-H],[19,11,Z0],[23,11,Z0]],   dtype=float), [[0,1,2]]])
left_tri2.color('sandybrown').alpha(0.8).backface_culling(False)
right_tri2.color('sandybrown').alpha(0.8).backface_culling(False)
base_left_tri2.color('sandybrown').alpha(0.8).backface_culling(False)
base_right_tri2.color('sandybrown').alpha(0.8).backface_culling(False)

# Support columns at black points (19,9) and (19,11): from z=Z0-H down to z=Z0 (this floor base)
# i.e. columns span from z=Z0 (floor 3 base) down to z=Z0-H (floor 2 base)
support_cols = [
    vedo.Cylinder(pos=[(19, 9,  Z0-H), (19, 9,  Z0)], r=0.18, c='#8B7355', alpha=0.95),
    vedo.Cylinder(pos=[(19, 11, Z0-H), (19, 11, Z0)], r=0.18, c='#8B7355', alpha=0.95),
]

# Green at top (z=Z0), black at bottom (z=Z0-H)
green_sph = [vedo.Sphere(pos=(x, y, Z0-H+0.15),   r=0.28).color('green') for x,y in green]
black_sph = [vedo.Sphere(pos=(x, y, Z0+0.15), r=0.28).color('black') for x,y in black]

# Axes + label
axes  = vedo.Axes(xrange=(0,26), yrange=(0,15), zrange=(0,Z0+H+2),
                  xtitle='x', ytitle='y', ztitle='z', axes_linewidth=2)
label = vedo.Text3D('Floor 3  (z = 6)', pos=(0.5, 0.3, Z0+H+0.5), s=0.42, c='navy')

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE & SHOW
# ─────────────────────────────────────────────────────────────────────────────
scene = (
    [floor_slab, ceil_slab, label]
    + walls_3d
    + doors_3d
    + [ramp2, left_tri2, right_tri2, base_left_tri2, base_right_tri2]
    + support_cols
    + green_sph + black_sph
    + [axes]
)

vedo.show(
    *scene,
    title='Floor 3',
    viewup='z',
    camera={
        'pos':         (55, -18, 45),
        'focal_point': (12,   7,  7.5),
        'viewup':      ( 0,   0,  1),
    },
    interactive=True,
)