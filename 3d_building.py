import importlib, sys, vedo


_real_show = vedo.show
vedo.show = lambda *a, **kw: None  

import floor1, floor2, floor3

vedo.show = _real_show              

# ── Combine all three scenes ──────────────────────────────────────────────────
combined = floor1.scene + floor2.scene + floor3.scene

# ── Single unified axes + title ───────────────────────────────────────────────
H = 3.0
axes  = vedo.Axes(xrange=(0,26), yrange=(0,15), zrange=(0, 3*H+2),
                  xtitle='x', ytitle='y', ztitle='z', axes_linewidth=2)
label = vedo.Text3D('All Floors', pos=(0.5, 0.3, 3*H+0.6),
                    s=0.42, c='navy')

vedo.show(
    *combined, axes, label,
    title=' Floors 1–3',
    viewup='z',
    camera={
        'pos':         (65, -22, 45),
        'focal_point': (12,   7,  4.5),
        'viewup':      ( 0,   0,  1),
    },
    interactive=True,
)