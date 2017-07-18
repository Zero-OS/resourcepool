#!/usr/bin/python
import json, sys

results_write=[]
results_read=[]
for f in sys.argv[1:]:
    print("Analyzing %s" % f)
    with open(f, 'r+') as fd:
        tests = json.load(fd)
        for test in tests['jobs']:
            results_write.append(test['write']['iops'])
            results_read.append(test['read']['iops'])

avg_write = sum(results_write) / len(results_write)
avg_read = sum(results_read) / len(results_read)
total_write = sum(results_write)
total_read = sum(results_read)
total_iops = total_write + total_read

print("avg read: %s iops" % avg_read)
print("avg write: %s iops" % avg_write)
print("total read: %s iops" % total_read)
print("total write: %s iops" % total_write)
print("total iops: %s iops" % total_iops)
            
