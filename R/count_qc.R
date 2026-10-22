# Synthetic arithmetic only; not a clinical analysis pipeline.
metrics <- function(a, b, c, d) {
  cells <- list(a, b, c, d)
  limit <- 2^53 - 1
  valid <- vapply(cells, function(x) {
    length(x) == 1L && typeof(x) %in% c("integer", "double") &&
      is.null(attributes(x)) && is.finite(x) && x >= 0 &&
      x == floor(x) && x <= limit
  }, logical(1))
  if (!all(valid)) stop("invalid counts")
  v <- unlist(cells, use.names = FALSE)
  if (sum(v) > limit) stop("table total exceeds exact integer range")
  out <- c(N=sum(v), ROR=NA_real_, PRR=NA_real_, LCL=NA_real_, UCL=NA_real_)
  if (any(v == 0)) return(out)
  o <- a*d/(b*c)
  se <- sqrt(sum(1/v))
  out[c("ROR", "PRR", "LCL", "UCL")] <- c(
    o, (a/(a+b))/(c/(c+d)), exp(log(o)-1.96*se), exp(log(o)+1.96*se))
  out
}
