# Mixed-effects analysis for speech-recognition WER
# Run with working directory set to the folder containing mixed_effects_data_matrix.csv.
# Important: in this dataset Language is perfectly nested within DataRegime; m1 may be
# rank-deficient/singular. Items are unique to rows, so (1|Item) is not estimable as a
# population variance with one observation per item. Review convergence before inference.

library(lme4)
library(lmerTest)
library(sjPlot)
library(emmeans)

# Load analysis matrix; WER retained as wer for the model formula.
df <- read.csv("mixed_effects_data_matrix.csv", stringsAsFactors = FALSE,
               check.names = FALSE)
df$wer <- df$WER
df$Language <- factor(df$Language, levels = c("AZB", "HEB_SCO"))
df$DataRegime <- factor(df$DataRegime)
df$Speaker <- factor(df$Speaker)
df$Item <- factor(df$Item)

# Requested exact model formulation:
m1 <- lmer(wer ~ Language * DataRegime + (1 | Speaker) + (1 | Item), data = df)
print(summary(m1))
print(VarCorr(m1))

# Post-hoc comparisons. These can fail or be non-estimable for the aliased
# Language-by-regime cells; retain the warnings and interpret only estimable contrasts.
emm_regime <- emmeans(m1, ~ DataRegime)
print(emm_regime)
print(pairs(emm_regime, adjust = "tukey"))
emm_language_by_regime <- emmeans(m1, ~ Language | DataRegime)
print(emm_language_by_regime)
print(pairs(emm_language_by_regime, adjust = "holm"))

# Model diagnostics: fitted vs residual, residual distribution and normal Q-Q.
res <- resid(m1)
fit <- fitted(m1)
par(mfrow = c(2, 2))
plot(fit, res, xlab = "Fitted values", ylab = "Residuals",
     main = "Residuals vs fitted")
abline(h = 0, lty = 2, col = "red")
hist(res, main = "Residual distribution", xlab = "Conditional residuals")
qqnorm(res, main = "Normal Q-Q plot of residuals")
qqline(res, col = "red", lwd = 2)
plot(df$wer, res, xlab = "Observed WER", ylab = "Residuals",
     main = "Residual checks by observed WER")
abline(h = 0, lty = 2, col = "red")
par(mfrow = c(1, 1))
