# Worker for the synthetic demo; calls the existing staged count function.
args <- commandArgs(TRUE)
if (length(args) != 2L) stop("Expected bundled fixture name and temporary output")
filearg <- grep("^--file=", commandArgs(FALSE), value=TRUE)
if (length(filearg) != 1L) stop("Cannot locate component worker")
root <- dirname(dirname(normalizePath(sub("^--file=", "", filearg), winslash="/", mustWork=TRUE)))
if (!args[1] %in% c("demo_counts.csv", "synthetic_counts.csv")) stop("Bundled fixture only")
destination <- normalizePath(dirname(args[2]), winslash="/", mustWork=TRUE)
if (destination == root || startsWith(destination, paste0(root,"/"))) stop("Output inside component")
source(file.path(root,"R/count_qc.R"))
fixture <- file.path(root,"fixtures",args[1])
if (file.info(fixture)$size > 16384) stop("Fixture size limit")
d <- read.csv(fixture, colClasses="character", check.names=FALSE, na.strings=NULL,
              stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
if (!identical(names(d),c("synthetic_id","a","b","c","d")) || nrow(d)<1 || nrow(d)>32) stop("Fixture schema")
if (anyDuplicated(d$synthetic_id) || !all(grepl("^SYNTHETIC_[A-Z0-9_]{1,48}$",d$synthetic_id))) stop("Synthetic labels required")
records <- list()
for (i in seq_len(nrow(d))) {
  tokens <- unlist(d[i,c("a","b","c","d")],use.names=FALSE)
  if (!all(grepl("^(0|[1-9][0-9]{0,15})$",tokens))) stop("Noncanonical count tokens")
  cells <- as.numeric(tokens)
  z <- metrics(cells[1],cells[2],cells[3],cells[4])
  fmt <- function(x) if (is.na(x)) "UNDEFINED" else trimws(formatC(x,format="g",digits=17,decimal.mark="."))
  records[[i]] <- data.frame(synthetic_id=d$synthetic_id[i],
    N=format(z["N"],scientific=FALSE,trim=TRUE,digits=22),
    ROR=fmt(z["ROR"]),PRR=fmt(z["PRR"]),LCL=fmt(z["LCL"]),UCL=fmt(z["UCL"]),
    state=if(any(is.na(z[-1]))) "UNDEFINED" else "DEFINED", stringsAsFactors=FALSE)
}
write.csv(do.call(rbind,records),args[2],row.names=FALSE)
