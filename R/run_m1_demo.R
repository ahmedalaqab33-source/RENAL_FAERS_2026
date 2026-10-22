# Synthetic fixture adapter only; the validator itself performs no IO.
a <- commandArgs(TRUE)
stopifnot(length(a)==2L)
root <- normalizePath(a[1])
source(file.path(root,"R/validate_sufficient_statistics.R"),local=TRUE)
x <- read.csv(file.path(root,"fixtures/m1_demo.csv"),colClasses="character",check.names=FALSE,na.strings=character())
stopifnot(identical(names(x),c("pair_id","a","b","c","d","n_drug","n_event")))
for(nm in names(x)[-1L]) {
  stopifnot(all(grepl("\\A(?:0|[1-9][0-9]*)\\z",x[[nm]],perl=TRUE)))
  x[[nm]] <- as.numeric(x[[nm]])
}
ans <- validate_sufficient_statistics(x)
write.csv(data.frame(pair_id=ans$pair_ids,n_drug=x$n_drug,n_event=x$n_event,N=rep(ans$N,ans$row_count)),a[2],row.names=FALSE)
