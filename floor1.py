import numpy as np
import vedo

H = 3.0   # floor height (z = 0 → 3)
W = 0.2   # wall thickness

green  = [(0,6),(0,9),(16,14),(19,14)]          # exits
purple = [(6,5),(9,5),(12,5),                   # doors (classroom row south)
          (16,2),(18,2),(22,3),                 # doors (right block)
          (6,10),(9,10),(13,10)]                # doors (classroom row north)
orange = [(23,6),(23,8)]   # ramp top edge    — z = H  (was bottom)
red    = [(19,6),(19,8)]   # ramp bottom edge — z = 0  (was top)


wall_segments = [

    # ── Outer south wall  (y = 0) ────────────────────────────────────────────
    ((0,0),  (10,0)),
    ((10,0), (15,0)),
    ((15,0), (20,0)),
    ((20,0), (25,0)),

    # ── Outer west wall  (x = 0)  — EXIT gap between y=6 and y=9 ───────────
    ((0,0),  (0,5)),
    ((0,5),  (0,6)),    # wall stops at green exit (0,6)
    # [open: (0,6) → (0,9)  = exit doorway]
    ((0,9),  (0,10)),   # wall resumes after green exit (0,9)
    ((0,10), (0,14)),

    # ── Outer north wall  (y = 14) — EXIT gap between x=16 and x=19 ─────────
    ((0,14),  (10,14)),
    ((10,14), (15,14)),
    ((15,14), (16,14)), # wall stops at green exit (16,14)
    # [open: (16,14) → (19,14)  = exit doorway]
    ((19,14), (20,14)), # wall resumes after green exit (19,14)
    ((20,14), (25,14)),

    # ── Outer east wall  (x = 25) ────────────────────────────────────────────
    ((25,0),  (25,3)),
    ((25,3),  (25,11)),
    ((25,11), (25,14)),

    # ── Interior vertical  x = 10  (left zone | middle zone) ────────────────
    ((10,0),  (10,5)),
    # REMOVED: ((10,5), (10,10))  — open corridor
    ((10,10), (10,14)),

    # ── Interior vertical  x = 15  (middle zone | right zone) ───────────────
    ((15,0),  (15,2)),
    ((15,2),  (15,5)),
    # REMOVED: ((15,5), (15,10))  — open corridor
    ((15,10), (15,14)),

    # ── Interior vertical  x = 20  (right block west wall) ───────────────────
    # Ramp gap between y=6 (red) and y=8 (red)
    ((20,0),  (20,2)),
    ((20,2),  (20,3)),
    ((20,12), (20,14)),

    # ── Interior horizontal  y = 5  (south classroom divider, x = 0..15) ────
    
    ((0,5),   (6,5)),   # wall up to door gap
    ((9,5),   (10,5)),  # wall between the two gaps
    ((12,5),  (15,5)),  # wall resumes after door

    # ── Interior horizontal  y = 10  (north classroom divider, x = 0..15) ───
    ((0,10),  (6,10)),  # wall up to door gap
    ((9,10),  (13,10)), # wall between the two gaps

    # ── Right sub-block horizontals ───────────────────────────────────────────

    ((15,2),  (16,2)),  # wall up to door gap
    ((18,2),  (20,2)),  # wall resumes after door
    ((22,3),  (25,3)),  # wall resumes after door
    ((20,11), (25,11)), # y = 11 (bottom of top sub-block) — kept intact

]



def make_wall(p1, p2, z0=0, h=H, t=W):
    """Extrude a 2D wall segment into a 3D box at height z0, tall h, thick t."""
    x1, y1 = p1;  x2, y2 = p2
    length = float(np.hypot(x2 - x1, y2 - y1))
    if length < 0.01:
        return None
    cx, cy, cz = (x1+x2)/2, (y1+y2)/2, z0 + h/2
    angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
    box = vedo.Box(pos=(cx, cy, cz), size=(length, t, h))
    box.rotate_z(angle, around=(cx, cy, cz))
    return box.color('#e8e2d6').alpha(0.93)

def slab(x0, x1, y0, y1, z0, z1, color, alpha):
    """Axis-aligned flat box (floor/ceiling slab)."""
    return vedo.Box(pos=[x0,x1, y0,y1, z0,z1]).color(color).alpha(alpha)


# BUILD FLOOR

# Floor & ceiling slabs
floor_slab = slab(0, 25, 0, 14, -0.2, 0.0, '#c9b99a', 0.95)
ceil_slab  = slab(0, 25, 0, 14,  H,   H+0.12, '#aaaaaa', 0.06)

# Walls
walls_3d = [w for p1,p2 in wall_segments for w in [make_wall(p1, p2)] if w]

# Door markers (purple spheres at mid-height)
doors_3d = [vedo.Sphere(pos=(x, y, 1.5), r=0.22).color('#9467bd') for x, y in purple]

# Exit markers (green column + sphere above)
exits_3d = []
for x, y in green:
    exits_3d.append(slab(x-.12, x+.12, y-.12, y+.12, 0, H, '#2ca02c', 0.7))
    exits_3d.append(vedo.Sphere(pos=(x, y, H+0.45), r=0.35).color('#2ca02c'))

# Ramp surface   red (20,6),(20,8) = z=0 edge  (bottom)
#                orange (24,6),(24,8) = z=H edge (top)
ramp_pts = np.array([
    [red[0][0],    red[0][1],    0.0],   # (19, 6, 0)  bottom-left
    [red[1][0],    red[1][1],    0.0],   # (19, 8, 0)  bottom-right
    [orange[1][0], orange[1][1], H  ],   # (23, 8, 3)  top-right
    [orange[0][0], orange[0][1], H  ],   # (23, 6, 3)  top-left
], dtype=float)
ramp = vedo.Mesh([ramp_pts, [[0,1,2],[0,2,3]]]).color('darkorange').alpha(0.9)
ramp.backface_culling(False)

# Ramp side triangles (close the open sides)
left_tri  = vedo.Mesh([np.array([[19,6,0],[23,6,H],[19,6,H]], dtype=float), [[0,1,2]]])
right_tri = vedo.Mesh([np.array([[19,8,0],[23,8,H],[19,8,H]], dtype=float), [[0,1,2]]])
base_right_tri = vedo.Mesh([np.array([[19,8,0],[23,8,H],[23,8,0]], dtype=float), [[0,1,2]]])
base_left_tri  = vedo.Mesh([np.array([[19,6,0],[23,6,H],[23,6,0]], dtype=float), [[0,1,2]]])
left_tri.color('sandybrown').alpha(0.8).backface_culling(False)
right_tri.color('sandybrown').alpha(0.8).backface_culling(False)
base_right_tri.color('sandybrown').alpha(0.8).backface_culling(False)
base_left_tri.color('sandybrown').alpha(0.8).backface_culling(False)
# Reference spheres (red at z=0 bottom, orange at z=H top)
red_sph    = [vedo.Sphere(pos=(x, y, 0.28),  r=0.30).color('red')    for x,y in red]
orange_sph = [vedo.Sphere(pos=(x, y, H+0.1), r=0.30).color('orange') for x,y in orange]

# Support columns — vertical pillars from orange points (z=H) down to floor (z=0)
# (23,6): orange[0], (23,8): orange[1]
support_col_r = 0.18   # column radius
support_cols = [
    vedo.Cylinder(pos=[(23, 6, 0), (23, 6, H)], r=support_col_r, c='#8B7355', alpha=0.95),
    vedo.Cylinder(pos=[(23, 8, 0), (23, 8, H)], r=support_col_r, c='#8B7355', alpha=0.95),
]

# Axes + label
axes = vedo.Axes(xrange=(0,26), yrange=(0,15), zrange=(0,H+2),
                 xtitle='x', ytitle='y', ztitle='z', axes_linewidth=2)
label = vedo.Text3D('Floor 1  (H = 3)', pos=(0.5, 0.3, H+0.55), s=0.42, c='navy')

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE & SHOW
# ─────────────────────────────────────────────────────────────────────────────
scene = (
    [floor_slab, ceil_slab, label]
    + walls_3d
    + doors_3d
    + exits_3d
    + [ramp, left_tri, right_tri,base_right_tri,base_left_tri]
    + support_cols
    + orange_sph + red_sph
    + [axes]
)

vedo.show(
    *scene,
    title='Floor 1',
    viewup='z',
    camera={
        'pos':         (55, -18, 30),
        'focal_point': (12,   7,  1.5),
        'viewup':      ( 0,   0,  1),
    },
    interactive=True,   # set False and add .screenshot('out.png') for headless
)