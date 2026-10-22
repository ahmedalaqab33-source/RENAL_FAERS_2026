# Pure contract extraction; no data access, estimation, mutation or output writes.
validate_sufficient_statistics <- function(x) {
  required <- c("pair_id", "a", "b", "c", "d", "n_drug", "n_event")
  counts <- required[-1L]
  limit <- 2^53 - 1
  fail <- function(code) stop(code, call. = FALSE)
  if (!identical(class(x), "data.frame")) fail("M1_E_CONTAINER")
  if (anyDuplicated(names(x)) || !setequal(names(x), required) || length(names(x)) != 7L) fail("M1_E_SCHEMA")
  n <- nrow(x)
  if (n == 0L) fail("M1_E_EMPTY")
  ids <- x[["pair_id"]]
  if (length(ids) != n || typeof(ids) != "character" || !is.null(attributes(ids))) fail("M1_E_ID_TYPE")
  if (anyNA(ids) || any(!grepl("\\A[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\\z", ids, perl = TRUE))) fail("M1_E_ID")
  if (anyDuplicated(ids)) fail("M1_E_DUPLICATE_ID")
  for (nm in counts) {
    v <- x[[nm]]
    if (!typeof(v) %in% c("integer", "double") || !is.null(attributes(v))) fail("M1_E_COUNT_TYPE")
    if (length(v) != n || any(!is.finite(v)) || any(v < 0 | v > limit) || any(v != floor(v))) fail("M1_E_COUNT_VALUE")
  }
  totals <- numeric(n)
  for (i in seq_len(n)) {
    if (x$a[i] <= 0) fail("M1_E_A_POSITIVE")
    accumulator <- 0
    for (nm in c("a", "b", "c", "d")) {
      v <- x[[nm]][i]
      # Every evaluated sum is already proven representable exactly.
      if (accumulator > limit - v) fail("M1_E_TOTAL_BOUND")
      accumulator <- accumulator + v
    }
    if (x$a[i] + x$b[i] != x$n_drug[i]) fail("M1_E_MARGIN_DRUG")
    if (x$a[i] + x$c[i] != x$n_event[i]) fail("M1_E_MARGIN_EVENT")
    totals[i] <- accumulator
  }
  if (length(unique(totals)) != 1L) fail("M1_E_SHARED_N")
  list(accepted = TRUE, row_count = n, N = totals[1L], pair_ids = ids)
}
