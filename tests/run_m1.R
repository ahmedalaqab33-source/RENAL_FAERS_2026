args <- commandArgs(TRUE)
root <- normalizePath(args[1]); output <- args[2]
e <- new.env(parent = baseenv())
before <- list.files(getwd(), all.files = TRUE, recursive = TRUE)
sys.source(file.path(root,"R/validate_sufficient_statistics.R"), envir=e)
stopifnot(identical(ls(e),"validate_sufficient_statistics"))
validate <- e$validate_sufficient_statistics
fields <- c("pair_id","a","b","c","d","n_drug","n_event")
decode <- function(token) {
  kind <- sub(":.*$","",token); value <- substring(token,nchar(kind)+2L)
  switch(kind, s=value, n=as.numeric(value), f=as.numeric(value),
    b=identical(value,"true"), nl=paste0(value,"\n"), cr=paste0(value,"\r"), na=NA_real_, nan=NaN, inf=Inf,
    neginf=-Inf, null=NULL, stop("Invalid synthetic token"))
}
build <- function(def) {
  if(def$variant=="empty") return(data.frame(pair_id=character(),a=numeric(),b=numeric(),c=numeric(),d=numeric(),n_drug=numeric(),n_event=numeric()))
  z <- strsplit(def$rows,"|",fixed=TRUE)[[1]]
  rows <- lapply(z,function(r)lapply(strsplit(r,";",fixed=TRUE)[[1]],decode))
  stopifnot(all(lengths(rows)==7L))
  x <- data.frame(pair_id=seq_along(rows))
  for(j in seq_along(fields)) {
    column <- lapply(rows,`[[`,j)
    numeric_plain <- all(vapply(column,function(v)typeof(v)%in%c("integer","double")&&length(v)==1L,logical(1)))
    string_plain <- all(vapply(column,function(v)is.character(v)&&length(v)==1L,logical(1)))
    logical_plain <- all(vapply(column,function(v)is.logical(v)&&length(v)==1L,logical(1)))
    x[[fields[j]]] <- if(numeric_plain||string_plain||logical_plain) unlist(column,use.names=FALSE) else I(column)
  }
  switch(def$variant,
    reorder={x<-x[rev(fields)]},
    missing_column={x$n_event<-NULL},
    extra_column={x$extra<-1},
    renamed_column={names(x)[names(x)=="n_event"]<-"other"},
    wrong_container={x<-list(x)},
    row_container={class(x)<-c("hostile","data.frame")},
    classed_count={x$b<-as.Date(x$b,origin="1970-01-01")},
    list_count={x$b<-I(lapply(x$b,function(v)c(v,v)))},
    hostile_id={class(x$pair_id)<-"hostile"})
  x
}
fmt <- function(x)format(x,scientific=FALSE,trim=TRUE,digits=22)
cases <- read.csv(file.path(root,"fixtures/m1_cases.csv"),colClasses="character",check.names=FALSE,na.strings=character())
cases <- rbind(cases,read.csv(file.path(root,"fixtures/m1_addendum_cases.csv"),colClasses="character",check.names=FALSE,na.strings=character()))
results <- list()
for(i in seq_len(nrow(cases))) {
  def <- as.list(cases[i,]);x<-build(def);snapshot<-serialize(x,NULL)
  answer<-tryCatch(validate(x),error=function(err)conditionMessage(err))
  accepted<-is.list(answer);code<-if(accepted)"" else answer
  good<-identical(if(accepted)"ACCEPT"else"REJECT",def$expected_status)&&identical(code,def$expected_error)
  if(accepted)good<-good&&identical(fmt(answer$N),def$expected_N)&&identical(as.character(answer$row_count),def$expected_rows)
  stopifnot(identical(snapshot,serialize(x,NULL)))
  results[[i]]<-data.frame(case_id=def$case_id,status=if(accepted)"ACCEPT"else"REJECT",error=code,passed=good,N=if(accepted)fmt(answer$N)else"",row_count=if(accepted)as.character(answer$row_count)else"",pair_ids=if(accepted)paste(answer$pair_ids,collapse="~")else"",margins=if(accepted)paste(paste(fmt(x$a+x$b),fmt(x$a+x$c),sep=":"),collapse="~")else"",stringsAsFactors=FALSE)
}
result<-do.call(rbind,results);write.csv(result,file.path(output,"r_cases.csv"),row.names=FALSE,na="")
stopifnot(all(result$passed))
base <- data.frame(pair_id="SYN_NATIVE",a=10,b=90,c=20,d=880,n_drug=100,n_event=30)
native<-list(
  logical_na=function(x){x$b<-NA;x},
  integer_na=function(x){x$b<-NA_integer_;x},
  logical_column=function(x){x$b<-TRUE;x},
  factor_column=function(x){x$b<-factor("90");x},
  date_column=function(x){x$b<-as.Date(90,origin="1970-01-01");x},
  named_count=function(x){z<-unclass(x);z$b<-setNames(90,"name");class(z)<-"data.frame";z},
  classed_double=function(x){x$b<-structure(90,class="odd");x},
  matrix_column=function(x){x$b<-matrix(90,1,1);x},
  complex_column=function(x){x$b<-90+0i;x},
  raw_column=function(x){x$b<-as.raw(90);x},
  list_column=function(x){x$b<-I(list(90));x},
  duplicate_names=function(x){names(x)[7]<-"n_drug";x},
  subclass=function(x){class(x)<-c("odd","data.frame");x},
  missing_id=function(x){x$pair_id<-NA_character_;x},
  attributed_id=function(x){attr(x$pair_id,"source")<-"synthetic";x},
  malformed_id_length=function(x){z<-unclass(x);z$pair_id<-c("SYN_A","SYN_B");class(z)<-"data.frame";z})
nr<-lapply(names(native),function(name){x<-native[[name]](base);ans<-try(validate(x),silent=TRUE);data.frame(case_id=name,passed=inherits(ans,"try-error"))})
nr<-do.call(rbind,nr);write.csv(nr,file.path(output,"r_native.csv"),row.names=FALSE);stopifnot(all(nr$passed))
stopifnot(identical(before,list.files(getwd(),all.files=TRUE,recursive=TRUE)))
writeLines(c(paste("shared_cases",nrow(result)),paste("native_cases",nrow(nr)),"import_binding_only TRUE","guard_directory_unchanged TRUE"),file.path(output,"r_scope.txt"))
cat("M1_R_PASS shared=",nrow(result)," native=",nrow(nr),"\n",sep="")
