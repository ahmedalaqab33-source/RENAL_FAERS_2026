# Measured bounded synthetic performance

Windows x64, Python3.12.14, SQLite3.53.1; Intel Core i7-8665U,4cores/8logical CPUs. Generator v1 seed1729;2,000 and10,000 artificial parent+child physical rows;batch64/512;two repeats. The plan was recorded before benchmarks. All8 runs conserved rows and returned CLEAN with zero quarantined/orphan/ambiguous/conflicting groups;logical metrics and multiset fingerprints matched across batches/repeats.

|Rows|Batch|Repeat|Wall seconds|Rows/second|Observed peak MiB|Observed temp MiB|
|---:|---:|---:|---:|---:|---:|---:|
|2000|64|1|0.5339|3746.3|20.45|0.598|
|2000|64|2|0.5541|3609.5|20.46|0.587|
|2000|512|1|0.2989|6691.0|20.97|0.523|
|2000|512|2|0.3207|6235.8|20.91|0.523|
|10000|64|1|1.9796|5051.5|24.00|2.649|
|10000|64|2|1.9297|5182.2|24.09|2.677|
|10000|512|1|0.8809|11352.3|24.30|2.696|
|10000|512|2|0.8199|12197.3|24.22|2.696|

Timing is parent perf_counter wall time including fresh Python startup, source hashing, parsing/inserts, global SQL diagnostics, output finalization and cleanup. No data download time is involved. Order was size,batch,repeat;filesystem caching was not randomized or purged. Two repeats provide descriptive measurements,not inferential speed comparisons.

Memory is maximum observed child Windows PSAPI PeakWorkingSetSize, sampled20ms;includes Python+embeddedSQLite,excludes benchmark-controller memory and filesystem cache. The last short-lived peak may be missed, so this is observed evidence,not a guaranteed maximum or hard cap. Temporary footprint is the maximum of sampled work-directory file lengths and engine checkpoints;transient journals may be missed;these are apparent,not allocated bytes. Input/output byte volumes and raw observations are retained in the private benchmark CSV.

The final three additional tests checked timeout,lock collision and prepared-statement treatment of hostile text;they did not change the benchmarked engine/generator. Final31 tests pass. No historical FAERS dataset or production-scale benchmark was processed. Do not extrapolate these small synthetic rates to23million records or call the module production-ready. Linux,hosted CI,cold-cache and power-loss behavior remain untested.
