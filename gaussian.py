from math import sqrt, log, exp, pi

def at(x):
    mean = 0
    stddev = 1

    multiplier = 1.0/(stddev*sqrt(2*pi))
    exp_part = exp((-1.0*(x-mean)**2)/(2*stddev**2))
    return multiplier*exp_part

def error_cdf(x):
    z = abs(x)
    t = 2.0/(2.0+z)
    ty = 4*t - 2

    coefficients = [
        -1.3026537197817094, 6.4196979235649026e-1,
        1.9476473204185836e-2, -9.561514786808631e-3, -9.46595344482036e-4,
        3.66839497852761e-4, 4.2523324806907e-5, -2.0278578112534e-5,
        -1.624290004647e-6, 1.303655835580e-6, 1.5626441722e-8, -8.5238095915e-8,
        6.529054439e-9, 5.059343495e-9, -9.91364156e-10, -2.27365122e-10,
        9.6467911e-11, 2.394038e-12, -6.886027e-12, 8.94487e-13, 3.13092e-13,
        -1.12708e-13, 3.81e-16, 7.106e-15, -1.523e-15, -9.4e-17, 1.21e-16, -2.8e-17
    ]
    ncof = len(coefficients)

    d = 0.0
    dd = 0.0
    for j in range(1, ncof)[::-1]:
        tmp = d
        d = ty*d - dd + coefficients[j]
        dd = tmp

    ans = t*exp(-z*z + 0.5*(coefficients[0] + ty*d) - dd)
    if x >= 0.0:
        return ans
    else:
        return 2.0 - ans

def cdf(x):
    invsqrt2 = -0.707106781186547524400844362104
    result = error_cdf(invsqrt2*x)
    return 0.5 * result

def inverse_error_cdf(p):
    if p >= 2.0:
        return -100
    if p <= 0:
        return 100

    if p < 1.0:
        pp = p
    else:
        pp = 2 - p
    t = sqrt(-2*log(pp/2.0))
    x = -0.70711*((2.30753 + t*0.27061)/(1.0 + t*(0.99229 + t*0.04481)) - t)

    for j in range(3):
        err = error_cdf(x) - pp
        x += err/(1.12837916709551257*exp(-(x*x)) - x*err)

    if p < 1.0:
        return x
    else:
        return -x

def inverse_cdf(x, mean, stddev):
    return mean - sqrt(2)*stddev*inverse_error_cdf(2*x)

