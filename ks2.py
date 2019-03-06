from __future__ import print_function
import numpy as np
import random
import scipy.stats
import subprocess
import time
import math
import sys

def time_cmd(cmd):
    if not cmd:
        return random.uniform(1, 1 + 0.1)
    else:
        # attempt to measure overhead of Popen / communicate
        p = subprocess.Popen(["true"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        start = time.time()
        out, err = p.communicate()
        end = time.time()
        off = end - start
        assert off >= 0
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # p = subprocess.Popen(cmd)
        start = time.time()
        out, err = p.communicate()
        end = time.time()
        assert p.returncode == 0
        return end-start-off


# https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test
def reject_same(s1, s2, alpha):
    D, p = scipy.stats.ks_2samp(s1, s2)
    # c_a = sqrt(-.5 ln a)
    c_a = {
        .1: 1.073,
        0.05: 1.224,
    }
    lb = c_a[alpha] * math.sqrt(float(len(s1) + len(s2)) / len(s1) * len(s2))
    print(D, lb)
    if D < 0.05 or p > 0.05:
        return False, D, p
    return True, D, p
    if D > lb:
        return True, D, p
    return False, D, p



cmd = sys.argv[1:]

times = []

NUM_SAMPLES = 200
NUM_VARS = 3
executions = 0
while True:
    # if we need more times, run the program more
    if len(times) < NUM_SAMPLES * NUM_VARS:
        times.append(time_cmd(cmd))
        print(".", end="")
        sys.stdout.flush()
        executions += 1
        continue

    couldBeSame = True
    for i in range(NUM_VARS):
        for j in range(NUM_VARS):
            if i <= j:
                continue
            s1 = times[i * NUM_SAMPLES: (i+1) * NUM_SAMPLES]
            s2 = times[j * NUM_SAMPLES: (j+1) * NUM_SAMPLES]
            reject, D, p = reject_same(s1, s2, 0.1)
            print(i, j, reject, D, p)
            couldBeSame = not reject

    if couldBeSame:
        print("")
        print("{} executions to produce {} squences of {} samples that could have the same underlying distribution".format(
            executions,
            NUM_VARS,
            NUM_SAMPLES))
        print(times)
        break

    # consume a time
    times = times[1:]