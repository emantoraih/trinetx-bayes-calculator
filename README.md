# Bayesian Reading of Hazard Ratios (version 1.0, November 2026)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24213483.svg)](https://doi.org/10.5281/zenodo.24213483)

A free calculator that turns a hazard ratio (or risk ratio) and its 95% confidence interval, for example from TriNetX, into the probability that a treatment effect is large enough to matter, after allowing for systematic error (bias).

**Use it online:** https://emantoraih.github.io/trinetx-bayes-calculator/

**Archived version 1.0:** https://doi.org/10.5281/zenodo.24213483

## What it returns
- Posterior median hazard ratio (or risk ratio) with its 95% credible interval
- Probabilities of a meaningful benefit, an effect too small to matter, and meaningful harm (these add up to 100%), and the probability of any benefit
- Absolute effect in events per 1,000 patients, from the reported ratio and from the posterior (if the comparator risk is entered)
- A table showing how the answer changes with the allowance for systematic error
- A plain-language interpretation and a sentence for your Results section

## Method
SE = [ln(upper) − ln(lower)] / 3.92, assuming a two-sided 95% interval calculated on the log scale. Total variance = SE² + σb². Normal prior on the log ratio (skeptical: mean 0, SD 0.136). The posterior is normal and is calculated in closed form. Probabilities are areas of the posterior below, between, and above the chosen thresholds (default 0.90 and exactly 1/0.90, shown as 1.11). The P value shown is an approximate Wald P value recalculated from the interval.

Absolute effect: for a hazard ratio, treated risk = 1 − (1 − p0)^HR under proportional hazards; for a risk ratio, treated risk = p0 × RR; if this exceeds 100% for the reported RR or its upper credible limit, the inputs are inconsistent and the absolute effect is not shown.

The allowance for systematic error is centered on zero. It widens the uncertainty but does not correct a bias that consistently favors one group.

## Files
- `index.html`: the calculator (single file, no external dependencies, runs entirely in the browser; no data are sent anywhere)
- `code/sim_v2.R`: simulation study and worked examples (R 4.5.1, data.table 1.17.8, openxlsx 4.2.9) (720 scenarios × 10,000 studies, seed 20261113)
- `code/make_figures.py`: all figures (Python 3.13.9, matplotlib 3.10.6, pandas 2.3.3, NumPy 2.3.5, openpyxl 3.1.5, Pillow 12.3.0); run `python make_figures.py <folder with R output> <output folder>`

## Verification
The calculator's posterior estimates and probabilities agree with the R code to four decimal places for all three worked examples under every prior and allowance for systematic error (36 combinations, 252 values).

## Citation
Interpreting Hazard Ratios From TriNetX: A Bayesian Method, Simulation, and Calculator. [Journal, year, article DOI]

Software: Toraih EA, Hussein MH, Jishu JA, Fawzy MS. Bayesian Reading of Hazard Ratios: calculator and simulation code (version 1.0). Zenodo; 2026. https://doi.org/10.5281/zenodo.24213483

Not affiliated with or endorsed by TriNetX, LLC.

## License
MIT
