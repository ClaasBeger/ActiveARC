"""astra on P-ARC, official-item accuracy: strong with given evidence, weak as an active discoverer."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

fams = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = next((f for f in ("Helvetica Neue", "Helvetica", "Arial") if f in fams), "DejaVu Sans")

INK, SUB = "#111827", "#6b7280"
BASE, ACCENT = "#c5ccd4", "#e4572e"

# official-item accuracy (%), mean over runs: static 92/94, random-K 76/84, active-K 70/74 (branched draws), active free 68
arms = [
    ("Static", "authored examples", 93, False),
    ("Random-K", "randomly drawn examples", 80, False),
    ("Active-K", "astra chooses k queries", 72, True),
    ("Active free", "astra decides what and how much to ask", 68, True),
]

fig, ax = plt.subplots(figsize=(9, 4.4), dpi=240)
n = len(arms)
ys = [3.3, 2.3, 1.0, 0.0]          # small gap between the given-evidence and active groups
H = 0.56
for y, (name, sub, v, active) in zip(ys, arms):
    col = ACCENT if active else BASE
    ax.add_patch(FancyBboxPatch((0, y - H / 2), v, H, boxstyle="round,pad=0,rounding_size=0.28",
                                facecolor=col, edgecolor="none", zorder=2, mutation_aspect=0.06))
    ax.text(v + 1.8, y, f"{v}", ha="left", va="center", fontsize=13.5, fontweight="bold",
            color=ACCENT if active else INK)
    ax.text(-2.5, y + 0.09, name, ha="right", va="center", fontsize=11.5, fontweight="bold",
            color=ACCENT if active else INK)
    ax.text(-2.5, y - 0.2, sub, ha="right", va="center", fontsize=8.5, color=SUB)

# gap bracket: static vs active free
x0 = 106
ax.plot([arms[0][2] + 8, x0, x0, arms[-1][2] + 8], [ys[0], ys[0], ys[-1], ys[-1]], color=ACCENT, lw=1.3,
        solid_capstyle="round", clip_on=False)
ax.text(x0 + 2, (ys[0] + ys[-1]) / 2, f"−{arms[0][2] - arms[-1][2]}\npoints", ha="left", va="center",
        fontsize=15, fontweight="bold", color=ACCENT, linespacing=1.0, clip_on=False)

ax.set_xlim(0, 100)
ax.set_ylim(-0.55, 3.85)
ax.axis("off")

fig.text(0.02, 0.975, "Given examples, astra solves most tasks …", fontsize=16, fontweight="bold",
         color=INK, ha="left", va="top")
fig.text(0.02, 0.905, "gpt-6-astra on P-ARC (50 tasks) · official test item correct, % · mean of two runs"
         "", fontsize=9.5, color=SUB, ha="left", va="top")
fig.text(0.02, 0.045, "… but as an active discoverer, choosing its own examples, it falls far behind",
         fontsize=16, fontweight="bold", color=ACCENT, ha="left", va="bottom")
plt.subplots_adjust(left=0.29, right=0.84, top=0.8, bottom=0.17)
out = "/Users/claasbeger/Documents/Research/ActiveARC/ActiveARC/experiments/figures/astra_parc_official.png"
fig.savefig(out, facecolor="white")
fig.savefig(out.replace(".png", ".pdf"), facecolor="white")
print(out)
