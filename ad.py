from __future__ import print_function
import numpy as np
import random
import scipy.stats
import subprocess
import time
import math
import sys
import warnings

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
def reject_same(ss, alpha):
    """
    hypothesis: all ss drawn from same distribution
    alpha: probability that the rejection is false"""
    
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        stat, criticalVals, significance_level = scipy.stats.anderson_ksamp(ss)
    # print(stat, criticalVals, significance_level)
    if significance_level > alpha:
        return True
    return False



cmd = sys.argv[1:]

times = []

NUM_SAMPLES = 3
NUM_VARS = 3
executions = 0
ALPHA = 0.05
while True:
    # if we need more times, run the program more
    if len(times) < NUM_SAMPLES * NUM_VARS:
        times.append(time_cmd(cmd))
        print(".", end="")
        sys.stdout.flush()
        executions += 1
        continue


    ss = []
    for i in range(NUM_VARS):
        ss.append(times[i * NUM_SAMPLES: (i+1) * NUM_SAMPLES])
    reject = reject_same(ss, 0.05)


    if not reject:
        print("")
        print("{} executions to produce {} squences of {} samples that could have the same underlying distribution p < {}".format(
            executions,
            NUM_VARS,
            NUM_SAMPLES,
            ALPHA))
        print(times)
        break

    # consume a time
    times = times[1:]