# Paper 56 - Figures for "Interpreting Hazard Ratios From TriNetX: A Bayesian Method, Simulation, and Calculator"
# Draws Figure 1, Figure 2, Supplementary Figures S1, S2 (simulation design), and S4 (all bias patterns), and the graphical abstract.
# Supplementary Figure S3 is a screenshot of the online calculator, not drawn here.
# Inputs (produced by Supplementary_Methods_S3_sim_v2.R): Simulation_v2_results.csv and Simulation_v2_results.xlsx
# Usage: python make_figures.py [input folder] [output folder]
# Tested with Python 3.13.9, pandas 2.3.3, numpy 2.3.5, matplotlib 3.10.6, openpyxl 3.1.5, Pillow 12.3.0.
# Figures use Arial; output is PNG and LZW-compressed TIFF at 600 dpi.

import sys, os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

IN = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
os.makedirs(OUT, exist_ok=True)
sim = pd.read_csv(os.path.join(IN, "Simulation_v2_results.csv"), keep_default_na=False)
ex = pd.read_excel(os.path.join(IN, "Simulation_v2_results.xlsx"), "Worked examples")
ex = ex[ex.Prior == "Skeptical"]
e1 = ex[ex.Example.str.startswith("1")].copy()
BASE = {"font.family": "Arial", "mathtext.fontset": "custom", "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold", "mathtext.default": "regular"}


def save(fig, name, **kw):
    png = os.path.join(OUT, name + ".png")
    fig.savefig(png, dpi=600, **kw)
    plt.close(fig)
    Image.open(png).convert("RGB").save(os.path.join(OUT, name + ".tif"), dpi=(600, 600), compression="tiff_lzw")
    print("saved", name)


RULES = [("P<0.05 benefit", "#7F7F7F", "o"), ("CI upper <0.90", "#ED7D31", "s"),
         ("Bayes P>0.80, assumed bias SD 0.1", "#70AD47", "^"), ("Bayes P>0.95, assumed bias SD 0.1", "#2F5597", "D")]

# ---------- Figure 1: worked example 1 ----------
plt.rcParams.update({**BASE, "font.size": 9})
fig, (a, b) = plt.subplots(1, 2, figsize=(7.5, 3.0), gridspec_kw={"width_ratios": [1, 1.35]})
vals = [100, 1000 * (1 - 0.90 ** 0.95)]
a.barh([1, 0], vals, color=["#7F7F7F", "#2F5597"], height=0.5)
a.set_yticks([1, 0]); a.set_yticklabels(["Comparator", "Treatment"])
for y, v in zip([1, 0], vals): a.text(v + 2, y, f"{v:.1f}", va="center")
a.set_xlim(0, 120); a.set_xlabel("Events per 1,000 patients at one year")
a.set_title("A", loc="left", fontweight="bold"); a.spines[["top", "right"]].set_visible(False)
ben = e1["P(meaningful benefit, HR<0.90)"].values * 100
triv = e1["P(trivial, 0.90-1.11)"].values * 100
harm = e1["P(meaningful harm, HR>1.11)"].values * 100
anyb = e1["P(any benefit, HR<1)"].values * 100
x = np.arange(4)
b.bar(x, ben, color="#2F5597", label="Meaningful benefit (HR < 0.90)")
b.bar(x, triv, bottom=ben, color="#BFBFBF", label="Too small to matter (0.90 to 1.11)")
b.bar(x, harm, bottom=ben + triv, color="#C00000", label="Meaningful harm (HR > 1.11)")
for i in range(4):
    b.text(i, 102, f"Any benefit\n{anyb[i]:.0f}%", ha="center", fontsize=7.5)
    if ben[i] >= 3: b.text(i, ben[i] / 2, f"{ben[i]:.0f}%", ha="center", va="center", color="white", fontsize=8)
    b.text(i, ben[i] + triv[i] / 2, f"{triv[i]:.0f}%", ha="center", va="center", fontsize=8)
b.set_xticks(x); b.set_xticklabels(["0 (none)", "0.05", "0.10", "0.20"]); b.set_ylim(0, 118)
b.set_xlabel("Assumed systematic error (SD, log hazard ratio scale)"); b.set_ylabel("Posterior probability (%)")
b.set_title("B", loc="left", fontweight="bold"); b.spines[["top", "right"]].set_visible(False)
b.legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.36), ncol=2)
fig.tight_layout()
save(fig, "Figure_1", bbox_inches="tight")

# ---------- Figure 2: simulation, symmetric systematic error SD 0.10, comparator risk 5% ----------
k = sim[(sim.bias == "Symmetric SD 0.10") & (sim.p0 == 0.05)]
names = ["P < 0.05", "Upper 95% CI < 0.90", "Bayesian, probability > 0.80", "Bayesian, probability > 0.95"]
fig, axs = plt.subplots(1, 3, figsize=(7.5, 2.9), sharey=True)
for ax, hr, ttl in zip(axs, [1.00, 0.95, 0.80], ["A  True HR 1.00 (no effect)", "B  True HR 0.95 (too small)", "C  True HR 0.80 (meaningful)"]):
    d = k[k.trueHR == hr].sort_values("N")
    for (col, c, m), nm in zip(RULES, names):
        ax.plot(d.N, d[col] * 100, color=c, marker=m, ms=3.5, lw=1.2, label=nm)
    ax.set_xscale("log"); ax.set_xticks([1e3, 1e4, 1e5, 5e5]); ax.set_xticklabels(["1,000", "10,000", "100,000", "500,000"], fontsize=7.5)
    ax.set_title(ttl, loc="left", fontsize=9, fontweight="bold"); ax.set_ylim(-2, 102)
    ax.spines[["top", "right"]].set_visible(False); ax.set_xlabel("Patients per group")
axs[0].set_ylabel("Studies declaring benefit (%)")
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, -0.06))
fig.tight_layout(rect=(0, 0.06, 1, 1))
save(fig, "Figure_2", bbox_inches="tight")

# ---------- Supplementary Figure S1: PubMed records mentioning TriNetX by year ----------
# Counts from a PubMed search for TriNetX [All Fields] run on November 12, 2026 (n = 5,087); 2026 is a partial year.
years = list(range(2018, 2027))
counts = [2, 3, 17, 77, 144, 272, 565, 1313, 2694]
plt.rcParams.update({**BASE, "font.size": 9})
fig, ax = plt.subplots(figsize=(6.5, 3.8))
cols = ["#4472C4"] * 8 + ["#A9C3E8"]
ax.bar(years, counts, color=cols, edgecolor="#2F5597", linewidth=0.6, width=0.8)
for yv, c in zip(years, counts): ax.text(yv, c + 30, f"{c:,}", ha="center", va="bottom")
ax.text(2026, counts[-1] + 230, "to Nov 12", ha="center", va="bottom", style="italic", fontsize=8)
ax.set_xticks(years); ax.set_ylim(0, 3000)
ax.set_xlabel("Publication year"); ax.set_ylabel("PubMed records, n")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
save(fig, "Supplementary_Figure_S1", bbox_inches="tight")

# ---------- Supplementary Figure S4: all patterns of systematic error ----------
plt.rcParams.update({**BASE, "font.size": 8})
pats = ["None", "Symmetric SD 0.05", "Symmetric SD 0.10", "Symmetric SD 0.20",
        "Directional favoring treatment, mean -0.05, SD 0.05", "Directional favoring treatment, mean -0.10, SD 0.05",
        "Directional favoring comparator, mean +0.05, SD 0.05", "Heavy-tailed (t3) SD 0.10"]
plab = ["No systematic error", "Symmetric, SD 0.05", "Symmetric, SD 0.10", "Symmetric, SD 0.20",
        "Favoring treatment,\nmean −0.05", "Favoring treatment,\nmean −0.10", "Favoring comparator,\nmean +0.05", "Heavy-tailed (t, 3 df),\nSD 0.10"]
names = ["P < 0.05", "Upper 95% CI < 0.90", "Bayesian > 0.80", "Bayesian > 0.95"]
fig, axs = plt.subplots(3, 8, figsize=(13, 5.8), sharey=True, sharex=True)
for j, (pt, pl) in enumerate(zip(pats, plab)):
    for i, hr in enumerate([1.00, 0.95, 0.80]):
        ax = axs[i, j]; dd = sim[(sim.bias == pt) & (sim.trueHR == hr) & (sim.p0 == 0.05)].sort_values("N")
        for (col, c, mk), nm in zip(RULES, names): ax.plot(dd.N, dd[col] * 100, color=c, marker=mk, ms=2.5, lw=1, label=nm)
        ax.set_xscale("log"); ax.set_ylim(-2, 102); ax.spines[["top", "right"]].set_visible(False)
        ax.set_xticks([1e3, 1e4, 1e5]); ax.set_xticklabels(["1k", "10k", "100k"])
        if i == 0: ax.set_title(pl, fontsize=7.5, fontweight="bold")
        if j == 0: ax.set_ylabel(f"True HR {hr:.2f}\nDeclaring benefit (%)")
        if i == 2: ax.set_xlabel("Patients per group")
h, l = axs[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.04, 1, 1))
save(fig, "Supplementary_Figure_S4", bbox_inches="tight")

# ---------- Graphical abstract ----------
plt.rcParams.update(BASE)
def g(hr, c): return 100 * float(sim[(sim.bias == "Symmetric SD 0.10") & (sim.trueHR == hr) & (sim.N == 100000) & (sim.p0 == 0.05)][c].iloc[0])
def pc(v): return "<0.1%" if v < 0.05 else f"{v:.1f}%"
e = e1[e1["Assumed bias SD"] == 0.10].iloc[0]
NAVY, BLUE, SLATE, TEAL, BG, ROWA, ROWB, MUTED = "#15293f", "#245b96", "#44566b", "#0f7563", "#edf2f6", "#f3f6f9", "#ecf3f5", "#4a5a6b"
W, H = 25.6, 14.56
fig = plt.figure(figsize=(W / 2.54, H / 2.54)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
fig.patch.set_facecolor(BG)
def rbox(x, y, w, h, fc, r=0.25): ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec="none"))
T = lambda x, y, t, **kw: ax.text(x, y, t, va="center", **kw)
rbox(0.8, 11.8, 24.0, 2.2, NAVY)
T(1.45, 13.45, "TRINETX METHODS STUDY", fontsize=8.5, fontweight="bold", color="#8fd3c7")
T(1.45, 12.5, "How likely is a clinically meaningful benefit?", fontsize=21, fontweight="bold", color="white")
rbox(0.8, 3.4, 6.75, 7.9, "white")
T(1.3, 10.6, "A  Hypothetical result", fontsize=12.5, fontweight="bold", color=NAVY)
T(1.3, 9.5, "HR 0.95", fontsize=26, fontweight="bold", color=BLUE)
T(1.3, 8.6, "95% CI 0.92–0.98; P=0.001", fontsize=10, color=SLATE)
T(1.3, 7.6, "One-year events per 1,000", fontsize=10.5, fontweight="bold", color=NAVY)
T(1.3, 6.9, "Comparator", fontsize=9.5, color=SLATE)
ax.add_patch(Rectangle((1.3, 6.25), 4.1, 0.3, fc=SLATE)); T(6.9, 6.4, "100", fontsize=10, fontweight="bold", color=SLATE, ha="right")
T(1.3, 5.6, "Treatment", fontsize=9.5, color=SLATE)
ax.add_patch(Rectangle((1.3, 4.95), 4.1 * 0.952, 0.3, fc=BLUE)); T(6.9, 5.1, "95.2", fontsize=10, fontweight="bold", color=BLUE, ha="right")
T(1.3, 4.0, "4.8 fewer events per 1,000", fontsize=11.5, fontweight="bold", color=BLUE)
rbox(7.9, 3.4, 6.75, 7.9, "white")
T(8.4, 10.6, "B  Bayesian interpretation", fontsize=12.5, fontweight="bold", color=NAVY)
T(8.4, 9.55, "Skeptical prior + allowance for\nresidual bias (SD 0.10)", fontsize=10.5, color=SLATE, linespacing=1.4)
T(8.4, 8.3, "Probability that the true effect is:", fontsize=10, fontweight="bold", color=NAVY)
RED = "#9b3b2f"
for k, (lab, col, colr) in enumerate([("Meaningful benefit (HR<0.90)", "P(meaningful benefit, HR<0.90)", BLUE),
                                      ("Too small to matter (HR 0.90–1.11)", "P(trivial, 0.90-1.11)", TEAL),
                                      ("Meaningful harm (HR>1.11)", "P(meaningful harm, HR>1.11)", RED)]):
    yy = 7.6 - k * 1.15; v = 100 * e[col]
    T(8.4, yy, lab, fontsize=9.5, color=SLATE)
    ax.add_patch(Rectangle((8.4, yy - 0.62), 4.6, 0.32, fc="#e3e9ef"))
    ax.add_patch(Rectangle((8.4, yy - 0.62), 4.6 * v / 100, 0.32, fc=colr))
    T(14.25, yy - 0.46, f"{v:.0f}%" if v >= 10 else f"{v:.1f}%", fontsize=11, fontweight="bold", color=colr, ha="right")
T(8.4, 3.9, "P=0.001, yet a meaningful\nbenefit is unlikely", fontsize=10, fontweight="bold", color=TEAL, linespacing=1.3)
rbox(15.0, 3.4, 9.8, 7.9, "white")
T(15.5, 10.6, "C  Simulation results", fontsize=12.5, fontweight="bold", color=NAVY)
T(15.5, 9.75, "720 scenarios × 10,000 simulated studies", fontsize=10, color=SLATE)
T(15.5, 9.15, "Illustration with 100,000 patients per group", fontsize=9, color=SLATE)
cols3 = [(19.45, "CI rule$^{1}$"), (22.2, "Bias-aware CI$^{2}$"), (24.3, "Bayes$^{3}$")]
for xx, t in cols3: T(xx, 8.3, t, fontsize=10, fontweight="bold", color=NAVY, ha="right")
for i, (hr, fc) in enumerate([(1.00, ROWA), (0.95, ROWA), (0.80, ROWB)]):
    y = 7.45 - i * 0.92
    ax.add_patch(Rectangle((15.35, y - 0.4), 9.1, 0.8, fc=fc, ec="none"))
    T(15.6, y + 0.15, f"True HR {hr:.2f}", fontsize=10, fontweight="bold", color=NAVY)
    T(15.6, y - 0.22, "true benefit" if hr < 0.90 else "false claim", fontsize=7.5, color=MUTED)
    for (xx, _), c, colr in zip(cols3, ["CI upper <0.90", "Bias-aware CI upper <0.90, assumed bias SD 0.1", "Bayes P>0.95, assumed bias SD 0.1"], [NAVY, NAVY, TEAL]):
        T(xx, y, pc(g(hr, c)), fontsize=10, fontweight="bold", color=colr, ha="right")
T(15.5, 4.45, "Percentage of studies declaring meaningful benefit", fontsize=9.5, color=SLATE)
T(15.5, 3.85, "Comparator risk 5% · true and assumed bias SD 0.10", fontsize=8.5, color=SLATE)
rbox(0.8, 1.75, 24.0, 1.25, NAVY)
T(1.35, 2.38, "At these cutoffs, allowing for bias cut false claims but also detected fewer real benefits.", fontsize=14, fontweight="bold", color="white")
T(0.95, 1.15, "$^{1}$Upper 95% CI below 0.90      $^{2}$Upper limit of a 95% CI widened for bias (SD 0.10) below 0.90      $^{3}$Posterior probability of HR below 0.90 exceeds 95%", fontsize=8.2, color=MUTED)
T(0.95, 0.6, "HR, hazard ratio; CI, confidence interval; SD, standard deviation on the log HR scale. Panels A and B show a hypothetical example.", fontsize=8.2, color=MUTED)
save(fig, "Graphical_abstract", facecolor=BG)

# ---------- Supplementary Figure S2: simulation design (histogram is an illustrative draw, not the stored simulation) ----------
plt.rcParams.update({**BASE, "font.size": 8})
NV, BL, LB, GR = "#1F3864", "#2F5597", "#DEE6F3", "#595959"
fig = plt.figure(figsize=(7.5, 4.3)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 30); ax.set_ylim(0, 17.2); ax.axis("off")
def box(x, y, w, h, fc=LB, ec="none", r=0.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=0.8))
def arrow(x0, x1, y):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="-|>", color=GR, lw=1.2, mutation_scale=12))
cols = [(0.3, "1  Set the truth", "720 scenarios"), (7.75, "2  Simulate studies", "10,000 per scenario"),
        (15.2, "3  Apply the five rules", "to every simulated study"), (22.65, "4  Score each decision", "4 threshold rules vs true HR")]
for x, t, s in cols:
    box(x, 14.9, 7.05, 2.0, fc=NV)
    ax.text(x + 0.35, 16.25, t, color="white", fontsize=9.5, fontweight="bold", va="center")
    ax.text(x + 0.35, 15.45, s, color="#C9D6EC", fontsize=8, va="center")
    box(x, 0.3, 7.05, 14.3, fc="#F4F7FB")
for x0 in (7.35, 14.8, 22.25): arrow(x0 + 0.02, x0 + 0.38, 9.5)
# panel 1: factors
fac = [("True hazard ratio", "6", "0.80, 0.85, 0.90, 0.95, 1.00, 1.05"),
       ("Patients per group", "5", "1,000 to 500,000"),
       ("Comparator risk", "3", "1%, 5%, 20%"),
       ("Systematic error", "8", "none, symmetric, directional,\nheavy-tailed patterns")]
for i, (n, k, v) in enumerate(fac):
    y = 12.6 - i * 2.75
    box(0.6, y - 0.95, 6.45, 2.3, fc="white", ec="#C9D6EC")
    ax.text(0.95, y + 0.72, n, fontsize=8, fontweight="bold", color=NV, va="center")
    ax.text(0.95, y - 0.2, v, fontsize=7, color=GR, va="center", linespacing=1.15)
    ax.text(6.7, y + 0.72, f"× {k}" if i else k, fontsize=11, fontweight="bold", color=BL, va="center", ha="right")
box(0.6, 0.75, 6.45, 1.6, fc=BL)
ax.text(3.83, 1.55, "6 × 5 × 3 × 8 = 720", color="white", fontsize=10.5, fontweight="bold", ha="center", va="center")
# panel 2: model + example histogram
ax.text(8.05, 13.75, "For one scenario, each study gives", fontsize=7.5, color=GR, va="center")
ax.text(8.05, 12.95, "observed log HR =", fontsize=8, color=NV, fontweight="bold", va="center")
ax.text(8.05, 12.1, "true log HR + systematic error\n+ sampling error", fontsize=8, color=NV, va="center", linespacing=1.2)
ax.text(8.05, 10.45, "Example: true HR 0.95,\n100,000 patients per group,\ncomparator risk 5%, bias SD 0.10", fontsize=7, color=GR, va="center", linespacing=1.2)
rng = np.random.default_rng(20261113)
d0 = 1e5 * 0.05; d1 = 1e5 * (1 - 0.95 ** 0.95); se = np.sqrt(1 / d0 + 1 / d1)
yv = np.exp(np.log(0.95) + rng.normal(0, 0.10, 10000) + rng.normal(0, se, 10000))
ia = fig.add_axes([8.15 / 30, 1.6 / 17.2, 6.3 / 30, 6.9 / 17.2])
ia.hist(yv, bins=np.linspace(0.6, 1.5, 46), color="#A9C3E8", edgecolor="white", linewidth=0.3)
ia.axvline(0.95, color=NV, lw=1.2); ia.axvline(0.90, color="#C00000", lw=1, ls="--")
ia.text(0.965, ia.get_ylim()[1] * 0.97, "true 0.95", fontsize=6.5, color=NV, va="top")
ia.text(0.895, ia.get_ylim()[1] * 0.97, "0.90", fontsize=6.5, color="#C00000", va="top", ha="right")
ex_y = np.log(0.877); ex_lo, ex_hi = np.exp(ex_y - 1.96 * se), np.exp(ex_y + 1.96 * se)
ia.plot([0.877], [ia.get_ylim()[1] * 0.12], marker="v", color="#C00000", ms=6)
ia.text(0.87, ia.get_ylim()[1] * 0.2, "example\nstudy", fontsize=6.3, color="#C00000", ha="right", linespacing=1.1)
ia.set_xlabel("Observed HR, 10,000 studies", fontsize=7); ia.set_yticks([]); ia.tick_params(labelsize=6.5)
ia.set_facecolor("white"); [ia.spines[s].set_visible(False) for s in ("top", "right", "left")]
# panel 3: rules
ex_st = np.sqrt(se ** 2 + 0.10 ** 2); ex_ba = np.exp(np.log(0.877) + 1.96 * ex_st)
ex_s2 = se ** 2 + 0.10 ** 2; ex_v = 1 / (1 / 0.136 ** 2 + 1 / ex_s2); ex_m = ex_v * np.log(0.877) / ex_s2
from math import erf
ex_pb = 0.5 * (1 + erf((np.log(0.90) - ex_m) / np.sqrt(ex_v) / np.sqrt(2)))
verdicts = ["Yes: P<0.001", f"No: upper {np.exp(np.log(0.877) + 1.96 * se):.3f}", f"No: upper {ex_ba:.2f}", f"No: {100 * ex_pb:.0f}%", f"No: {100 * ex_pb:.0f}%"]
rules = [("P<0.05 with HR<1", "#7F7F7F", "HR<1.00"),
         ("Upper 95% CI <0.90", "#ED7D31", "HR<0.90"),
         ("Bias-aware CI: upper <0.90", "#BF9000", "HR<0.90"),
         ("Bayes P(HR<0.90) >0.95", "#2F5597", "HR<0.90"),
         ("Bayes P(HR<0.90) >0.80", "#70AD47", "HR<0.90")]
ax.text(15.5, 13.95, "Example study: HR 0.877", fontsize=7.6, color="#C00000", fontweight="bold", va="center")
ax.text(15.5, 13.35, f"(95% CI {ex_lo:.3f}–{ex_hi:.3f}); true HR 0.95", fontsize=6.9, color=GR, va="center")
ax.text(15.5, 12.75, f"Posterior P(HR<0.90) = {100 * ex_pb:.0f}%", fontsize=6.9, color=GR, va="center")
ax.text(15.5, 12.15, "(skeptical prior, assumed bias SD 0.10)", fontsize=6.9, color=GR, va="center")
for i, (r, c, tg) in enumerate(rules):
    y = 10.95 - i * 2.0
    box(15.5, y - 0.85, 6.45, 1.75, fc="white", ec="#C9D6EC")
    ax.add_patch(Rectangle((15.5, y - 0.85), 0.28, 1.75, fc=c, ec="none"))
    ax.text(16.05, y + 0.3, r, fontsize=7.6, fontweight="bold", color=NV, va="center")
    ax.text(16.05, y - 0.4, "Target: " + tg, fontsize=6.8, color=GR, va="center")
    ax.text(21.8, y - 0.4, verdicts[i], fontsize=6.8, fontweight="bold", color=BL if verdicts[i].startswith("Yes") else GR, va="center", ha="right")
ax.text(15.5, 1.05, "Assumed bias SD (0, 0.05, 0.10,\n0.20) and prior varied separately\nfrom the true pattern", fontsize=6.6, color=GR, va="center", linespacing=1.2)
# panel 4: scoring
box(22.95, 9.35, 6.45, 4.6, fc="white", ec="#C9D6EC")
ax.text(23.3, 13.25, "True HR below 0.90", fontsize=8, fontweight="bold", color="#0f7563", va="center")
ax.text(23.3, 12.25, "A declaration of meaningful\nbenefit is a", fontsize=7.3, linespacing=1.15, color=GR, va="center")
ax.text(23.3, 11.15, "correct detection", fontsize=8.5, fontweight="bold", color="#0f7563", va="center")
ax.text(23.3, 10.3, "(higher is better)", fontsize=7, color=GR, va="center")
box(22.95, 4.35, 6.45, 4.6, fc="white", ec="#C9D6EC")
ax.text(23.3, 8.25, "True HR 0.90 or higher", fontsize=8, fontweight="bold", color="#C00000", va="center")
ax.text(23.3, 7.25, "A declaration of meaningful\nbenefit is a", fontsize=7.3, linespacing=1.15, color=GR, va="center")
ax.text(23.3, 6.3, "false claim", fontsize=8.5, fontweight="bold", color="#C00000", va="center")
ax.text(23.3, 5.6, "(lower is better)", fontsize=7, color=GR, va="center")
ax.text(23.3, 4.85, "Example study (true HR 0.95): the\nfour No decisions avoid a false claim", fontsize=6.6, color="#C00000", va="center", linespacing=1.15)
ax.text(23.0, 2.75, "Reported per scenario:\n% of studies declaring benefit\nand 95% interval coverage", fontsize=7.3, color=NV, va="center", linespacing=1.3)
ax.text(23.0, 0.95, "P<0.05 is a reference for current\npractice, not scored against 0.90", fontsize=6.6, color=GR, va="center", linespacing=1.2)
save(fig, "Supplementary_Figure_S2", facecolor="white")
