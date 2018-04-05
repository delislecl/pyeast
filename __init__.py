import pandas as pd
import numpy as np
from scipy.stats import norm
from math import *
import datetime

def BlackScholesPrice(spot, strike, dmat, retAnnual, volAnnual, typ):
    if dmat > 0:
        d1 = (log(spot / strike) + (retAnnual + 0.5 * volAnnual * volAnnual) * (dmat / 252)) / (
        volAnnual * sqrt(dmat / 252))
        d2 = d1 - volAnnual * sqrt(dmat / 252)
        nd1 = norm.cdf(d1)
        nd2 = norm.cdf(d2)
        nd1n = norm.cdf(-d1)
        nd2n = norm.cdf(-d2)

        if typ == "CALL" or typ == "Call" or typ == "C" or typ == "c":
            priceBS = spot * nd1 - strike * exp(-retAnnual * (dmat / 252)) * nd2
        else:
            priceBS = strike * exp(-retAnnual * (dmat / 252)) * nd2n - spot * nd1n
    else:
        priceBS = GetPayoff(spot, strike, typ)

    return priceBS


def BlackScholesVol(spot, strike, dmat, retAnnual, price, typ):
    if dmat > 0:
        volMin = 0.00
        volMax = 1000.00
        volMid = (volMin + volMax) / 2

        premium = BlackScholesPrice(spot, strike, dmat, retAnnual, volMid, typ)
        err = (price - premium)
        iteration = 0

        while (abs(err) > 0.001) and (iteration < 1000):
            if err > 0:
                volMin = volMid
                volMid = (volMin + volMax) / 2
            else:
                volMax = volMid
                volMid = (volMin + volMax) / 2

            premium = BlackScholesPrice(spot, strike, dmat, retAnnual, volMid, typ)
            err = (price - premium)
            iteration = iteration + 1
        return volMid
    else:
        return 0


def BlackScholesGrecques(spot, price, strike, dmat, retAnnual, typ, grecques):
    result = 0.0
    if dmat > 0:
        volAnnual = BlackscholesVol(spot, strike, dmat, retAnnual, price, typ)
        d1 = (log(spot / strike) + (retAnnual + 0.5 * volAnnual * volAnnual) * (dmat / 252)) / (
        volAnnual * sqrt(dmat / 252))
        d2 = d1 - volAnnual * sqrt(dmat / 252)
        nd1 = norm.cdf(d1)
        nd2 = norm.cdf(d2)
        nd1n = norm.cdf(-d1)
        nd2n = norm.cdf(-d2)
        n_dash_d1 = 1 / (sqrt(2 * pi)) * exp(-d1 * d1 / 2)
        if grecques == 'Delta':
            if typ == "CALL" or typ == "Call" or typ == "C":
                result = nd1
            else:
                result = nd1 - 1
        elif grecques == 'Vega':
            result = spot * sqrt(dmat / 252) * n_dash_d1
        elif grecques == 'Theta':
            result = -(spot * n_dash_d1 * volAnnual) / (2 * sqrt(dmat / 252)) - (
            retAnnual * strike * exp(-retAnnual * (dmat / 252)) * nd2)
        elif grecques == 'Gamma':
            result = n_dash_d1 / (spot * volAnnual * sqrt(dmat / 252))
        else:
            result = np.nan
    return result


def GetPayoff(spotMat, strike, typ):
    if typ == "PUT" or typ == "Put" or typ == "P" or typ == "p":
        payoff = max(strike - spotMat, 0)
    else:
        payoff = max(spotMat - strike, 0)

    return payoff


def BlackScholesGrecquesWithIV(spot, iv, strike, dmat, retAnnual, typ, grecques):
    result = 0.0
    if dmat > 0:
        volAnnual = iv
        d1 = (log(spot / strike) + (retAnnual + 0.5 * volAnnual * volAnnual) * (dmat / 252)) / (
        volAnnual * sqrt(dmat / 252))
        d2 = d1 - volAnnual * sqrt(dmat / 252)
        nd1 = norm.cdf(d1)
        nd2 = norm.cdf(d2)
        nd1n = norm.cdf(-d1)
        nd2n = norm.cdf(-d2)
        n_dash_d1 = 1 / (sqrt(2 * pi)) * exp(-d1 * d1 / 2)
        if grecques == 'Delta':
            if typ == "CALL" or typ == "Call" or typ == "C":
                result = nd1
            else:
                result = nd1 - 1
        elif grecques == 'Vega':
            result = spot * sqrt(dmat / 252) * n_dash_d1
        elif grecques == 'Theta':
            result = -(spot * n_dash_d1 * volAnnual) / (2 * sqrt(dmat / 252)) - (
            retAnnual * strike * exp(-retAnnual * (dmat / 252)) * nd2)
        elif grecques == 'Gamma':
            result = n_dash_d1 / (spot * volAnnual * sqrt(dmat / 252))
        else:
            result = np.nan
    return result

#Add dates after end of 2018
def GetMat(endDate):
    # Parameters
    seconds_in_hour = 3600
    hours_in_day = 6.5
    startDate = datetime.datetime.today()

    # Holidays
    closedList = ["01/02/2017", "01/16/2017", "02/20/2017", "04/14/2017", "05/29/2017", "07/04/2017", "09/04/2017",
                  "11/23/2017", "12/25/2017", "01/01/2018", "01/15/2018", "02/19/2018", "03/30/2018", "05/28/2018",
                  "07/04/2018", "09/03/2018", "11/22/2018", "12/25/2018"]
    holidays_list = [datetime.datetime.strptime(date, "%m/%d/%Y").date() for date in closedList]

    # NbDays
    NbDays = np.busday_count(startDate, endDate, holidays=holidays_list)
    NbDays = np.maximum(NbDays, 0)

    # NbSeconds
    end_of_day = datetime.datetime(startDate.year, startDate.month, startDate.day, 16, 0, 0)
    NbSeconds = max(min((end_of_day - startDate).seconds / (seconds_in_hour * hours_in_day), hours_in_day), 0)

    return NbDays + NbSeconds
