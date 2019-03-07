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
        return random.uniform(1, 1.1)
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



def my_corrcoef(x,y):
    assert len(x) == len(y)
    xBar = np.average(x)
    yBar = np.average(y)

    return np.dot(x - xBar, y-yBar) / len(x)

# https://www.cse.wustl.edu/~jain/iucee/ftp/k_27trg.pdf
def reject_same(s, cor_length, lag_length, alpha):
    """
    autocovariance at lag k is normally distributed with mean 0 and variance 1/(144(n-k))
    hypothesis: covariance is 0
    100(1-a)% confidence interfact for autocovariance is z_(1-a/2) / 12sqrt(n-k)
    test all covariance up to 
    hypothesis: all ss drawn from same distribution
    alpha: probability that the rejection is false
    """

    assert cor_length > lag_length

    stdev = 1.0/(12 * math.sqrt(cor_length - lag_length))
    # print("stdev", stdev)
    # conf = scipy.stats.norm.ppf(1.0-.1/2.0, scale=stdev)
    # print(.1, conf)
    # conf = scipy.stats.norm.ppf(1.0-.05/2.0, scale=stdev)
    # print(.05, conf)
    conf = scipy.stats.norm.ppf(1.0-alpha/2.0, scale=stdev)
    # print("conf interval", conf)
    autocor = [0 for l in range(lag_length)]
    for lag in range(lag_length):
        autocor[lag] = np.corrcoef(s[-cor_length:], s[-cor_length-lag-1:-lag-1])[0][1]
        autocor[lag] = my_corrcoef(s[-cor_length:], s[-cor_length-lag-1:-lag-1])
        # autocor[lag] = np.cov(s[-cor_length:], s[-cor_length-lag-1:-lag-1])[0][1]

    # print(autocor)
    # print(conf)
    # raw_input("key")


    rejects = [False for e in autocor]
    for i, cov in enumerate(autocor):
        lb = cov - conf
        ub = cov + conf
        print(lb, ub)
        if 0 < lb or 0 > ub:
            rejects[i] = True

    print(rejects)
    return any(rejects)



cmd = sys.argv[1:]

times = []


LAG_LENGTH = 5 # lag length to check out to
COR_LENGTH = 20 # size of auto-correlation
ALPHA = 0.90

executions = 0
while True:
    # if we need more times, run the program more
    if len(times) < LAG_LENGTH + COR_LENGTH:
        times.append(time_cmd(cmd))
        print(".", end="")
        sys.stdout.flush()
        executions += 1
        continue

    reject = reject_same(times, COR_LENGTH, LAG_LENGTH, ALPHA)

    if not reject:
        print("")
        print("{} executions to produce a sequence with ~0 autocovariances of length {} up to lag {}".format(
            executions,
            COR_LENGTH,
            LAG_LENGTH))
        print(times)
        break

    # consume a time
    times = times[1:]