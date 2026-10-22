# Independently decoded synthetic cases; base R only.
a <- commandArgs(TRUE)
root <- normalizePath(a[1], winslash="/", mustWork=TRUE)
destination <- normalizePath(dirname(a[2]), winslash="/", mustWork=TRUE)
if (destination == root || startsWith(destination, paste0(root,"/"))) stop("Write diagnostics outside component")
source(file.path(root,"R/count_qc.R"))
decode <- function(t) {
  if (startsWith(t,"n:")) return(as.numeric(substring(t,3)))
  if (startsWith(t,"f:")) return(as.numeric(substring(t,3)))
  switch(t, bool_true=TRUE, bool_false=FALSE, negative=-1,
    fractional=1.25, nan=NaN, posinf=Inf, neginf=-Inf,
    null=NULL, missing_real=NA_real_, missing_integer=NA_integer_,
    missing_logical=NA, char_number="1", blank="", vector=c(1,2),
    empty_vector=numeric(0), list=list(1), complex=1+1i,
    classed=structure(1,class="ambiguous_count"), named=c(label=1),
    above_limit=2^53, stop("Unknown synthetic tag"))
}
d <- read.csv(file.path(root,"fixtures/contract_cases.csv"),stringsAsFactors=FALSE)
records <- list()
for (i in seq_len(nrow(d))) {
  row <- d[i,]
  args <- lapply(c("a","b","c","d"), function(k) decode(row[[k]]))
  z <- tryCatch(do.call(metrics,args),error=function(e) NULL)
  actual <- if(is.null(z)) "REJECT" else "ACCEPT"
  vals <- if(is.null(z)) rep(NA_real_,5) else z[c("N","ROR","PRR","LCL","UCL")]
  records[[i]] <- data.frame(case_id=row$case_id, expected=row$expected, actual=actual,
    N=unname(vals[1]), ROR=unname(vals[2]), PRR=unname(vals[3]),
    LCL=unname(vals[4]), UCL=unname(vals[5]))
}
out <- do.call(rbind,records)
write.csv(out,a[2],row.names=FALSE)
cat("R_CONTRACT_CASES",nrow(out),"FAIL",sum(out$actual != out$expected),"\n")
stopifnot(all(out$actual==out$expected))
capture.output(sessionInfo(),file=a[3])
