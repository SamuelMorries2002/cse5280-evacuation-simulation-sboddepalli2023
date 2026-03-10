"""
animate_evacuation.py
─────────────────────
Standalone script that opens a native VTK window with the interactive
evacuation animation.  Called from the notebook via:

    import subprocess, sys
    subprocess.Popen([sys.executable, "animate_evacuation.py"])

The script reads simulation data saved by the notebook:
    sim_history.npy      — shape (frames, N, 3)
    sim_escaped.npy      — shape (N,)  bool
    sim_escape_step.npy  — shape (N,)  int

"""

import os, sys, platform
import numpy as np

# ── Locate data directory (same folder as this script) ───────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# ── Load simulation data ──────────────────────────────────────────────────────
def load_data():
    for fname in ("sim_history.npy", "sim_escaped.npy", "sim_escape_step.npy"):
        path = os.path.join(SCRIPT_DIR, fname)
        if not os.path.exists(path):
            sys.exit(f"ERROR: {path} not found.\n"
                     "Run the simulation cell in the notebook first "
                     "(it saves these files automatically).")
    history      = np.load(os.path.join(SCRIPT_DIR, "sim_history.npy"))
    escaped      = np.load(os.path.join(SCRIPT_DIR, "sim_escaped.npy")).tolist()
    escape_step  = np.load(os.path.join(SCRIPT_DIR, "sim_escape_step.npy")).tolist()
    return history, escaped, escape_step

# ── Import vedo AFTER forcing native backend ─────────────────────────────────
import vedo
vedo.settings.default_backend = "vtk"   

H = 3.0

# ── Building constants ────────────────────────────────────────────────────────
EXIT_A = np.array([0.,  7.5, 0.])
EXIT_B = np.array([17.5, 14., 0.])
RAMP1  = dict(A=np.array([19., 7.]), B=np.array([23., 7.]), z0=0.,  z1=H,   r=1.0)
RAMP2  = dict(A=np.array([23.,10.]), B=np.array([19.,10.]), z0=H,   z1=2*H, r=1.0)
RAMPS  = [RAMP1, RAMP2]

FLOOR_COLORS = ["#1f77b4", "#ff7f0e", "#d62728"]   # blue, orange, red

def init_agent_floors(n=20, seed=42):
    """Reproduce the same starting-floor assignment as the notebook."""
    rng    = np.random.default_rng(seed)
    floors = []
    counts = [n//3, n//3, n - 2*(n//3)]
    def in_ramp(xy):
        for r in RAMPS:
            v = r['B']-r['A']; w = xy-r['A']
            t = np.clip(np.dot(w,v)/np.dot(v,v), 0., 1.)
            if np.linalg.norm(xy-(r['A']+t*v)) <= r['r']:
                return True
        return False
    for fi, cnt in enumerate(counts):
        for _ in range(cnt):
            while True:
                x = rng.uniform(1., 17.); y = rng.uniform(1., 13.)
                if not in_ramp(np.array([x, y])): break
            floors.append(fi)
    return floors

# ── Load floor geometry from your floor files ─────────────────────────────────
def load_building():
    _real = vedo.show
    vedo.show = lambda *a, **k: None
    for m in ["floor1", "floor2", "floor3"]:
        if m in sys.modules: del sys.modules[m]
    import floor1, floor2, floor3
    vedo.show = _real
    objs = [o for o in floor1.scene + floor2.scene + floor3.scene
            if type(o).__name__ not in ("Assembly", "Text3D")]
    return objs

# ═════════════════════════════════════════════════════════════════════════════
def main():
    print("Loading simulation data …")
    history, escaped, escape_step = load_data()
    N = history.shape[1]

    print("Loading building geometry …")
    building = load_building()

    start_floors = init_agent_floors(N, seed=42)
    AGENT_COLORS = [FLOOR_COLORS[f] for f in start_floors]

    RECORD_EVERY = 3
    FRAME_DT_MS  = 60
    render_frames = history[::RECORD_EVERY]
    n_frames      = len(render_frames)

    # ── Unified axes + title ─────────────────────────────────────────────────
    axes  = vedo.Axes(xrange=(0,26), yrange=(0,15), zrange=(0,3*H+2),
                      xtitle='x', ytitle='y', ztitle='z', axes_linewidth=2)
    title = vedo.Text3D("Crawford Building — Evacuation",
                        pos=(0.5, 0.3, 3*H+0.8), s=0.42, c="navy")

    # ── Agent spheres (mutated in-place each frame) ──────────────────────────
    agent_spheres = []
    for i in range(N):
        sph = vedo.Sphere(pos=render_frames[0][i] + np.array([0,0,0.28]), r=0.40)
        sph.color(AGENT_COLORS[i]).alpha(0.95)
        agent_spheres.append(sph)

    # ── HUD ──────────────────────────────────────────────────────────────────
    hud_step = vedo.Text2D(
        "Step    0    Escaped:  0/20",
        pos="top-left", s=1.15, c="navy", bg="white", alpha=0.72, font="Courier")
    hud_legend = vedo.Text2D(
        u"\u25cf Blue=Floor0  \u25cf Orange=Floor1  \u25cf Red=Floor2  "
        u"\u25cf Grey=Escaped  |  SPACE=play/pause  \u2190\u2192=step  Q=quit",
        pos="bottom-left", s=0.85, c="darkblue", bg="white", alpha=0.62, font="Courier")
    hud_status = vedo.Text2D(
        "PLAYING", pos="top-right", s=1.0, c="green",
        bg="white", alpha=0.72, font="Courier")

    state = dict(frame=0, playing=True, tid=None)

    # ── Frame update ─────────────────────────────────────────────────────────
    def update_frame(fi):
        pf       = render_frames[fi]
        sim_step = fi * RECORD_EVERY
        n_esc    = sum(1 for i in range(N)
                       if escaped[i] and escape_step[i] <= sim_step)
        for i in range(N):
            pos = pf[i]
            if escaped[i] and escape_step[i] <= sim_step:
                agent_spheres[i].pos(pos).color("#aaaaaa").alpha(0.28)
            else:
                agent_spheres[i].pos(pos + np.array([0,0,0.28]))
                agent_spheres[i].color(AGENT_COLORS[i]).alpha(0.95)
        hud_step.text(
            f"Step {sim_step:4d}    Escaped: {n_esc:2d}/{N}  [{fi+1}/{n_frames}]")
        hud_status.text("PLAYING" if state["playing"] else "PAUSED")
        hud_status.c("green"   if state["playing"] else "orange")

    def on_timer(evt):
        if not state["playing"]: return
        state["frame"] = (state["frame"] + 1) % n_frames
        update_frame(state["frame"])
        plt.render()

    def on_key(evt):
        k = evt.keypress.lower()
        if k in ("space", " "):
            state["playing"] = not state["playing"]
            hud_status.text("PLAYING" if state["playing"] else "PAUSED")
            hud_status.c("green"   if state["playing"] else "orange")
            plt.render()
        elif k in ("right", "d"):
            state["playing"] = False
            state["frame"]   = min(state["frame"] + 1, n_frames - 1)
            update_frame(state["frame"]); plt.render()
        elif k in ("left", "a"):
            state["playing"] = False
            state["frame"]   = max(state["frame"] - 1, 0)
            update_frame(state["frame"]); plt.render()

    # ── Assemble plotter ─────────────────────────────────────────────────────
    plt = vedo.Plotter(
        title = "Crawford Building — Evacuation Simulation",
        size  = (1280, 720),
        bg    = "#f5f5f0",
        bg2   = "#ddeeff",
    )
    for obj in building + [axes, title]:
        plt.add(obj)
    for sph in agent_spheres:
        plt.add(sph)
    plt.add(hud_step, hud_legend, hud_status)
    plt.add_callback("timer",    on_timer)
    plt.add_callback("KeyPress", on_key)

    CAM = dict(pos=(65,-22,45), focal_point=(12,7,4.5), viewup=(0,0,1))

    print(f"\n{'='*52}")
    print(f"  Evacuation Animation  —  {n_frames} frames")
    print(f"{'='*52}")
    print(f"{'='*52}\n")

    # start timer AFTER show() so the VTK interactor is initialised
    plt.show(camera=CAM, interactive=False)
    state["tid"] = plt.timer_callback("start", dt=FRAME_DT_MS)
    plt.interactive()
    plt.close()
    print("Window closed.")

if __name__ == "__main__":
    main()
