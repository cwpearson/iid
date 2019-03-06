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
    """ return false if s is not iid"""
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
    lb, ub = dist.interval(alpha)
    # print(numRuns, "w/in", lb, ub)
    return numRuns > lb and numRuns < ub


# https://en.wikipedia.org/wiki/Wald%E2%80%93Wolfowitz_runs_test
def exchangeable(s1, s2, n):
    avg = np.average(s1) - np.average(s2)

    s1_var = np.var(s1)
    s2_var = np.var(s2)
    var = s1_var - s2_var

    m = np.cov(np.stack((s1, s2), axis=0))
    # print(s1_var)
    # print(m)
    lb = (-1.0 * s1_var) / (n - 1)
    # print(m[0][1], lb)
    return m[0][1] >= lb, avg, var


cmd = sys.argv[1:]

times = []

NUM_SAMPLES = 3
NUM_VARS = 3
executions = 0
while True:
    # if we need more times, run the program more
    if len(times) < NUM_SAMPLES * NUM_VARS:
        print(".", end="")
        sys.stdout.flush()
        times.append(time_cmd(cmd))
        executions += 1
        continue

    allExch = True
    for i in range(NUM_VARS):
        for j in range(NUM_VARS):
            if i == j:
                continue
            s1 = times[i * NUM_SAMPLES: (i+1) * NUM_SAMPLES]
            s2 = times[j * NUM_SAMPLES: (j+1) * NUM_SAMPLES]
            cov, avg, var = exchangeable(s1, s2, NUM_VARS)
            print(i, j, cov, avg, var)
            if not cov:
                allExch = False
                break

    if allExch:
        print("")
        print("{} executions to produce {} mutually exchangeable squences of {} times".format(
            executions,
            NUM_VARS,
            NUM_SAMPLES))
        print(times)
        break

    # consume a time
    times = times[1:]