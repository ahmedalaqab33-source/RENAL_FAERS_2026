a<-commandArgs(TRUE);root<-normalizePath(a[1]);e<-new.env(parent=baseenv());before<-list.files(getwd(),all.files=TRUE,recursive=TRUE)
sys.source(file.path(root,"R/count_qc.R"),e);sys.source(file.path(root,"R/validate_sufficient_statistics.R"),e)
x<-data.frame(pair_id="SYN_INTEGRATION",a=10,b=90,c=20,d=880,n_drug=100,n_event=30)
checks<-c(
bindings=identical(sort(ls(e)),sort(c("metrics","validate_sufficient_statistics"))),
shared_valid=e$validate_sufficient_statistics(x)$N==e$metrics(10,90,20,880)[["N"]],
zero_b_M1={z<-x;z$a<-1;z$b<-0;z$c<-4;z$d<-995;z$n_drug<-1;z$n_event<-5;isTRUE(e$validate_sufficient_statistics(z)$accepted)},
zero_b_QC=is.na(e$metrics(1,0,4,995)[["ROR"]]),
zero_a_M1={z<-x;z$a<-0;z$n_drug<-90;z$n_event<-20;inherits(try(e$validate_sufficient_statistics(z),silent=TRUE),"try-error")},
zero_a_QC=is.na(e$metrics(0,90,20,880)[["ROR"]]),
boolean_QC=inherits(try(e$metrics(TRUE,1,1,1),silent=TRUE),"try-error"),
unchanged_guard=identical(before,list.files(getwd(),all.files=TRUE,recursive=TRUE)))
write.csv(data.frame(check=names(checks),passed=unname(checks)),a[2],row.names=FALSE);stopifnot(all(checks));cat("R_COEXISTENCE_PASS 8\n")
