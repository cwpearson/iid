import numpy as np
import math
import random
import matplotlib.pyplot as plt

def sample(a):
    return random.uniform(1,2)


def pilot_study():
    samples = [sample(None) for i in range(5)]
    return np.average(samples), math.sqrt(np.var(samples))

# H1: mean >= H
# H2: mean <= H
H = 1.5

# acceptable risk of error
# alpha: chance of rejecting H1 when H1 is correct
# beta: chance of rejecting H2 when H2 is correct
alpha = 0.05
beta = 0.05

# Hypothesis 1: mean <= u1
# Hypothesis 2: mean >= u2
# s: estimate of stddev
# alpha: chance of rejecting H1 when H1 is correct
# beta: chance of rejecting H2 when H2 is correct
def ss_normal(u1, u2, s, alpha, beta):
    # assert(u1 < u2)
    b = (u1+u2) / 2.0 # slope
    A = math.log((1.0-alpha)/beta)
    B = math.log((1.0-beta)/alpha)
    h1 = B*(s**2)/(u1-u2)
    h2 = A*(s**2)/(u2-u1)
    print(b, h1, h2)

    accept_h1 = lambda y,n: y < b * n + h1
    accept_h2 = lambda y,n: y > b * n + h2

    conclusion = 0 # uncertain

    samples = []
    while True:
        samples += [sample(None)]
        y = sum(samples)

        if accept_h1(y, len(samples)):
            conclusion = -1 # mean < u1
            break
        if accept_h2(y, len(samples)):
            conclusion = 1 # mean > u2
            break

    plotSamples = np.cumsum(samples)
    plotX = np.array([i+1 for i in range(len(samples))])
    plotY1 = b * plotX + h1
    plotY2 = b * plotX + h2
    plt.plot(plotX, plotY1)
    plt.plot(plotX, plotY2)
    plt.plot(plotX, plotSamples, 'bo')
    plt.show()

    return conclusion, len(samples)


while True:
    # conduct pilot study to estimate mean and standard deviation
    # initial estimate of std dev
    u, s = pilot_study()

    print("pilot study std dev:", s)

    # binary search from u-6s to u+6s?
    h1 = (u-6.0*s) + (u  +6.0*s) / 3
    h2 = 2.0 * h1

    ## conduct search with sequential sampling to determine window of true results


    

    result = test_normal(1.47, 1.49, s, alpha, beta)
    print(result)

    ## conduct final study to measure results

    ## if not within sequential sampling window, start over