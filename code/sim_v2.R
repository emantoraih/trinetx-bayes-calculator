# Paper 56 - Simulation v2 (ADEMP)
# Aims: compare conventional and Bayesian readings of TriNetX-style HR/CI for declaring a
#       clinically meaningful benefit (HR < 0.90) under systematic error.
# Data generation: observed log HR = true log HR + study-specific systematic error + sampling error.
# Estimand: true HR; decision target: HR < 0.90.
# Methods: P<0.05; upper 95% CI < 0.90; bias-aware upper 95% CI < 0.90 (SE^2 + bias SD^2); Bayesian posterior P(HR<0.90) > 0.95 or > 0.80.
# Performance: % declaring benefit (false claims if true HR >= 0.90; detection if < 0.90),
#              interval coverage, Monte Carlo standard error (MCSE).

suppressPackageStartupMessages({library(data.table); library(openxlsx)})
set.seed(20261113)
out <- "./"
R <- 10000
MCID <- log(0.90); HARM <- log(1 / 0.90)

priors <- list(Skeptical = c(0, 0.136), Weak = c(0, 1.0), Enthusiastic = c(log(0.80), 0.136))
assumed <- c(0, 0.05, 0.10, 0.20)
bias_scen <- data.table(
  bias = c("None", "Symmetric SD 0.05", "Symmetric SD 0.10", "Symmetric SD 0.20",
           "Directional favoring treatment, mean -0.05, SD 0.05",
           "Directional favoring treatment, mean -0.10, SD 0.05",
           "Directional favoring comparator, mean +0.05, SD 0.05",
           "Heavy-tailed (t3) SD 0.10"),
  b_mu = c(0, 0, 0, 0, -0.05, -0.10, 0.05, 0),
  b_sd = c(0, 0.05, 0.10, 0.20, 0.05, 0.05, 0.05, 0.10),
  b_t  = c(rep(FALSE, 7), TRUE))
grid <- CJ(trueHR = c(0.80, 0.85, 0.90, 0.95, 1.00, 1.05), N = c(1000, 5000, 20000, 100000, 500000),
           p0 = c(0.01, 0.05, 0.20), bias = bias_scen$bias, sorted = FALSE)
grid <- merge(grid, bias_scen, by = "bias", sort = FALSE)
grid[, d0 := N * p0][, d1 := N * (1 - (1 - p0)^trueHR)][, se := sqrt(1 / d0 + 1 / d1)]

post <- function(y, se, sb, pr) {
  s2 <- se^2 + sb^2; v <- 1 / (1 / pr[2]^2 + 1 / s2); m <- v * (pr[1] / pr[2]^2 + y / s2)
  list(m = m, s = sqrt(v))
}
res <- vector("list", nrow(grid))
for (i in seq_len(nrow(grid))) {
  g <- grid[i]
  z <- if (g$b_t) rt(R, 3) / sqrt(3) else rnorm(R)
  y <- log(g$trueHR) + g$b_mu + g$b_sd * z + rnorm(R, 0, g$se)
  hi <- y + 1.96 * g$se; p <- 2 * pnorm(-abs(y / g$se)); th <- log(g$trueHR)
  o <- list(`P<0.05 benefit` = mean(p < 0.05 & y < 0), `CI upper <0.90` = mean(hi < MCID),
            `CI coverage` = mean(abs(th - y) <= 1.96 * g$se))
  # bias-aware frequentist rule: same total SE as the Bayesian model, no prior
  for (sb in assumed[assumed > 0]) {
    st <- sqrt(g$se^2 + sb^2)
    o[[sprintf("Bias-aware CI upper <0.90, assumed bias SD %s", sb)]] <- mean(y + 1.96 * st < MCID)
    o[[sprintf("Bias-aware CI coverage, assumed bias SD %s", sb)]] <- mean(abs(th - y) <= 1.96 * st)
  }
  for (pn in names(priors)) for (sb in assumed) {
    if (pn != "Skeptical" && sb != 0.10) next
    ps <- post(y, g$se, sb, priors[[pn]]); pb <- pnorm((MCID - ps$m) / ps$s)
    tag <- if (pn == "Skeptical") "" else paste0(pn, " prior, ")
    o[[sprintf("%sBayes P>0.95, assumed bias SD %s", tag, sb)]] <- mean(pb > 0.95)
    o[[sprintf("%sBayes P>0.80, assumed bias SD %s", tag, sb)]] <- mean(pb > 0.80)
    o[[sprintf("%sBayes 95%% CrI coverage, assumed bias SD %s", tag, sb)]] <- mean(abs(th - ps$m) <= 1.96 * ps$s)
  }
  res[[i]] <- c(g[, .(bias, trueHR, N, p0, se)], o)
}
summ <- rbindlist(res)
summ[, truth := fifelse(trueHR < 0.90, "Meaningful benefit (HR<0.90)", "Not meaningful (HR>=0.90)")]
mcse_max <- 100 * sqrt(0.25 / R)

# worked examples under all priors and assumed bias SDs
ex <- data.table(Example = c("1 Large cohort, small effect", "2 Moderate effect, wide CI", "3 Non-significant"),
                 HR = c(0.95, 0.88, 0.90), L = c(0.92, 0.80, 0.78), U = c(0.98, 0.97, 1.04))
ex[, `:=`(y = log(HR), se = (log(U) - log(L)) / 3.92)][, p := 2 * pnorm(-abs(y / se))]
exl <- rbindlist(lapply(names(priors), function(pn) rbindlist(lapply(assumed, function(sb) {
  e <- copy(ex); ps <- post(e$y, e$se, sb, priors[[pn]])
  e[, `:=`(Prior = pn, `Assumed bias SD` = sb, `Posterior HR` = exp(ps$m),
           `95% CrI low` = exp(ps$m - 1.96 * ps$s), `95% CrI high` = exp(ps$m + 1.96 * ps$s),
           `P(any benefit, HR<1)` = pnorm(-ps$m / ps$s),
           `P(meaningful benefit, HR<0.90)` = pnorm((MCID - ps$m) / ps$s),
           `P(trivial, 0.90-1.11)` = pnorm((HARM - ps$m) / ps$s) - pnorm((MCID - ps$m) / ps$s),
           `P(meaningful harm, HR>1.11)` = 1 - pnorm((HARM - ps$m) / ps$s))]
}))))
exl[, `Events per 1,000 avoided (p0=10%)` := 1000 * (0.10 - (1 - 0.90^HR))][, c("y", "se") := NULL]

wb <- createWorkbook()
addWorksheet(wb, "README")
writeData(wb, "README", data.frame(Item = c("Design", "Replicates", "Priors (log HR scale)", "Thresholds", "Sampling SE",
  "Rules", "Interpretation", "Monte Carlo SE", "Seed"),
  Value = c("ADEMP simulation; 720 scenarios (6 true HR x 5 N x 3 comparator risks x 8 bias patterns)",
  paste(R, "simulated studies per scenario"),
  "Skeptical N(0, 0.136^2) primary; weakly informative N(0, 1^2); enthusiastic N(ln 0.80, 0.136^2)",
  "Meaningful benefit HR<0.90; trivial 0.90-1.11; meaningful harm HR>1.11", "sqrt(1/d0 + 1/d1) from expected events",
  "P<0.05 with HR<1; upper 95% CI<0.90; bias-aware upper 95% CI<0.90 using sqrt(SE^2 + assumed bias SD^2); Bayesian P(HR<0.90)>0.95 or >0.80",
  "CI and Bayesian rules: true HR>=0.90 = false claims, true HR<0.90 = detection; P<0.05 tests HR<1",
  sprintf("At most %.2f percentage points for any percentage", mcse_max), "20261113")))
addWorksheet(wb, "Scenario results"); writeData(wb, "Scenario results", summ)
addWorksheet(wb, "Worked examples"); writeData(wb, "Worked examples", exl)
saveWorkbook(wb, paste0(out, "Simulation_v2_results.xlsx"), overwrite = TRUE)
fwrite(summ, paste0(out, "Simulation_v2_results.csv"))
cat("done", nrow(summ), "scenarios; max MCSE", round(mcse_max, 2), "\n")
