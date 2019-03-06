from __future__ import print_function
import numpy as np
import random
from scipy.stats import norm
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

def num_runs(a):
    """return number of runs in a numpy array"""
    runStarts = np.not_equal(a[:-1], a[1:])
    return 1 + sum(np.not_equal(a[:-1], a[1:]))


# https://en.wikipedia.org/wiki/Wald%E2%80%93Wolfowitz_runs_test
def wald_wolfowitz(s, alpha):
    a = np.array(s)
    # remove median
    med = np.median(a)
    a = a[a != med]

    # convert to 1 and 0 for larger/smaller than median
    twoValued = np.where(a > med, 1, 0)
    # print(a, med, twoValued)


    Np = sum(twoValued) # number of positives
    Nn = len(twoValued) - Np # number of negatives

    avgNumRuns = float(2 * Np * Nn) / (Np + Nn) + 1
    varNumRuns = float((avgNumRuns - 1) * (avgNumRuns - 2)) / (Np + Nn - 1)
    numRuns = num_runs(twoValued)
    # print(avgNumRuns, "+=", varNumRuns, numRuns)

    # number of standard deviations above or below mean
    z = abs(float(numRuns - avgNumRuns) / math.sqrt(varNumRuns))
    print(z)

    dist = norm(loc=avgNumRuns, scale=varNumRuns)

    D, p = scipy.stats.kstest(numRuns, dist.cdf)
    return p > alpha


cmd = sys.argv[1:]

times = []

SEQ_LENGTH = 6
NUM_TESTS = 10
executions = 0
ALPHA=0.9
while True:
    # if we need more times, run the program more
    if len(times) < SEQ_LENGTH + NUM_TESTS:
        print(".", end="")
        sys.stdout.flush()
        times.append(time_cmd(cmd))
        executions += 1
        continue

    accept = 0
    for i in range(NUM_TESTS):
        start = -SEQ_LENGTH-i-1
        finish = -i-1
        t = times[start : finish]
        if wald_wolfowitz(t, ALPHA):
            accept += 1
    # print(accept, "/", NUM_TESTS)
    
    if accept >= ALPHA * NUM_TESTS:
        print("")
        print("{} executions to observe {} consecutive iid times (alpha = {})".format(
         executions,
         SEQ_LENGTH + NUM_TESTS,
         ALPHA
         ))
        avg = np.average(times)
        stddev = math.sqrt(np.var(times))
        print("app under test:", cmd)
        print("{}s +- {}s".format(avg, stddev))
        break

    # consume a time
    times = times[1:]