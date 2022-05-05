import csv

summary = 'summary.csv'
with open(summary, 'w', newline='') as fopen:
    writer = csv.writer(fopen)
    header = []
    header.append("CPU")
    header.append("GPU")
    header.append("Time (ms)")
    #header.append("Time improvement")
    header.append("CPU freq (MHz)")
    header.append("GR3D freq (MHz)")
    header.append("CPU MAX Load (%)")
    header.append("USED GR3D (%)")
    header.append("CPU Power (mW")
    header.append("GPU Power (mW")
    header.append("DDR Power (mW")
    header.append("CPU+GPU+DDR Power (mW)")
    header.append("Total Power (mW)")
    header.append("EDP (W*s^2)")
    #header.append("EDP improvement")
    writer.writerow(header)