"""astra on P-ARC vs Claude Opus 5 on ARC-AGI-2, official-item accuracy: strong with given evidence, weaker as active discoverers."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

fams = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = next((f for f in ("Helvetica Neue", "Helvetica", "Arial") if f in fams), "DejaVu Sans")
INK, SUB, BASE, ACCENT = "#111827", "#6b7280", "#c5ccd4", "#e4572e"
r = lambda v: int(math.floor(v + 0.5))

# Official-item accuracy (%), mean over runs.
# astra, P-ARC (50):     static 92/94 | random-K 76/84 | active-K 70/74 (branched draws s0_b, s0_b_rep2) | active free 68
# Opus, ARC-AGI-2 (200): static 93.5  | random-K 89.0/94.0 | active-K 79.0/79.0 (branched draws) | active free 72.5
ARMS = [("Static", "authored examples", False), ("Random-K", "randomly drawn examples", False),
        ("Active-K", "model chooses k queries", True), ("Active free", "model chooses unlimited queries", True)]
MODELS = [("gpt-6-astra", "P-ARC · 50 tasks", [93.0, 80.0, 72.0, 68.0]),
          ("Claude Opus 5", "ARC-AGI-2 · 200 tasks", [93.5, 91.5, 79.0, 72.5])]
YS = [3.3, 2.3, 1.0, 0.0]
H = 0.56

fig = plt.figure(figsize=(11, 4.9), dpi=240)
lab = fig.add_axes([0.0, 0.15, 0.22, 0.60])
panels = [fig.add_axes([0.235, 0.15, 0.27, 0.60]), fig.add_axes([0.625, 0.15, 0.27, 0.60])]
for a in [lab] + panels:
    a.set_ylim(-0.55, 3.85); a.axis("off")
lab.set_xlim(0, 1)
for y, (name, sub, active) in zip(YS, ARMS):
    lab.text(0.98, y + 0.09, name, ha="right", va="center", fontsize=11.5, fontweight="bold", color=ACCENT if active else INK)
    lab.text(0.98, y - 0.2, sub, ha="right", va="center", fontsize=8.5, color=SUB)

for ax, (model, bench, vals) in zip(panels, MODELS):
    ax.set_xlim(0, 100)
    shown = [r(v) for v in vals]
    for y, v, (_, _, active) in zip(YS, shown, ARMS):
        ax.add_patch(FancyBboxPatch((0, y - H / 2), v, H, boxstyle="round,pad=0,rounding_size=0.28",
                                    facecolor=ACCENT if active else BASE, edgecolor="none", mutation_aspect=0.06))
        ax.text(v + 2, y, f"{v}", ha="left", va="center", fontsize=13, fontweight="bold", color=ACCENT if active else INK)
    lo = min((i for i in (2, 3)), key=lambda i: shown[i])
    x0 = 111
    ax.plot([shown[0] + 9, x0, x0, shown[lo] + 9], [YS[0], YS[0], YS[lo], YS[lo]], color=ACCENT, lw=1.3,
            solid_capstyle="round", clip_on=False)
    ax.text(x0 + 2.5, (YS[0] + YS[lo]) / 2, f"−{shown[0] - shown[lo]}\npoints", ha="left", va="center",
            fontsize=13.5, fontweight="bold", color=ACCENT, linespacing=1.0, clip_on=False)
    ax.text(0, 4.22, model, ha="left", va="bottom", fontsize=12.5, fontweight="bold", color=INK)
    ax.text(0, 3.93, bench, ha="left", va="bottom", fontsize=9.5, color=SUB)

fig.text(0.02, 0.985, "Given examples, state-of-the-art models solve most tasks …", fontsize=16, fontweight="bold",
         color=INK, ha="left", va="top")
fig.text(0.02, 0.915, "Official test item correct, % · mean of two runs",
         fontsize=9.5, color=SUB, ha="left", va="top")
fig.text(0.02, 0.035, "… but as active discoverers, choosing their own examples, they fall far behind",
         fontsize=16, fontweight="bold", color=ACCENT, ha="left", va="bottom")
out = "/Users/claasbeger/Documents/Research/ActiveARC/ActiveARC/experiments/figures/astra_parc_opus_arc2_official.png"
fig.savefig(out, facecolor="white")
fig.savefig(out.replace(".png", ".pdf"), facecolor="white")
print(out)
