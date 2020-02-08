import numpy as np
import datetime
import argparse

def myTradingSystem(DATE, OPEN, HIGH, LOW, CLOSE, VOL, exposure, equity, settings):

    #
    # DATE is list of settings["lookback"] dates, in YYYYMMDD format, ascending order
    # Newest date has highest index
    #
    # OPEN, HIGH, LOW, CLOSE, VOL are values for [ticker(0), ...ticker(n-1)], per date
    #
    # exposure, equity are per date, ascending, but shifted down by one
    # exposure is array of weighted exposures, per ticker, per date
    # equity is dollar value, per ticker, per date
    #
    
    #print(datetime.datetime.strptime(str(DATE[0]),"%Y%m%d").weekday())
    #print("DATE = {}".format(DATE))
    #print("CLOSE = {}".format(CLOSE))
    #print("tickers = {}".format(settings["markets"]))
    #print("exposure = {}".format(exposure))

    lookback = settings['lookback']

    #print("Previous day: {}".format(DATE[lookback-1]))
    #print("Previous trading day positions: {}".format(exposure[lookback-2]))
    #print("Days passed: {}".format(settings['days_passed']))
    
    # Skip all days that are not Friday
    if datetime.datetime.strptime(str(DATE[lookback-1]),"%Y%m%d").weekday() != 4:
        # Return previous day position, or all cash, if no prev day available
        pos = exposure[lookback-2]
        if settings['days_passed'] == 0:
            # All cash on first day
            pos[0] = 1

        settings['days_passed'] += 1
        printStats(DATE, settings)
        
        #print("pos = {}".format(pos))
        return pos, settings
    
    #print("It's Friday {}".format(DATE[lookback-1]))
    #print("CLOSE = {}".format(CLOSE))
    
    # Parameters
    periodLonger = 140 # 28 weeeks * 5 days = 140
    periodShorter = 30 # 6 weeks * 5 days = 30
    fracOverSma = 1.3
    fracUnderMax = 0.90

    nTickers = CLOSE.shape[1]

    # Calculate Simple Moving Average (SMA)
    smaLongerPeriod = np.nansum(CLOSE[-periodLonger:, :], axis=0)/periodLonger
    smaShorterPeriod = np.nansum(CLOSE[-periodShorter:, :], axis=0)/periodShorter
    
    if smaShorterPeriod[1] > CLOSE[lookback-1][1]:
        settings['spy_under_short_sma'] += 1
        fracUnderMax = 0.90
    else:
        settings['spy_over_short_sma'] += 1
        fracUnderMax = 0.80
    
    CLOSE1 = np.nan_to_num(CLOSE)
    max = np.nanmax(CLOSE1, axis=0)
    #print("max={}".format(max))
    
    buy = CLOSE1[lookback-1] > smaLongerPeriod * fracOverSma
    sell = CLOSE1[lookback-1] < max * fracUnderMax
    hold = np.full(nTickers, True)
    hold[buy] = False
    hold[sell] = False

    #print("buy={}".format(buy))
    #print("sell={}".format(sell))
    #print("hold={}".format(hold))

    pos = np.zeros(nTickers)
    pos[0] = 1

    for i in range(1, nTickers):
        if buy[i] and not sell[i] and not exposure[lookback-2][i]:
            pos[i] = 1
            print("Buy {} on {}, price {}, {}-sma {}, max {}".format(settings["markets"][i], DATE[lookback-1], CLOSE[lookback-1][i], periodLonger, smaLongerPeriod[i], max[i]))
        elif sell[i] and exposure[lookback-2][i]:
            pos[i] = 0
            print("Sell {} on {}, price {}, {}-sma {}, max {}".format(settings["markets"][i], DATE[lookback-1], CLOSE[lookback-1][i], periodLonger, smaLongerPeriod[i], max[i]))
        elif exposure[lookback-2][i]:
            pos[i] = 1
        else:
            pos[i] = 0

        if pos[i]:
            pos[0] = 0
            
    #pos = pos/np.sum(abs(pos))
    #print("pos = {}".format(pos))

    settings['days_passed'] += 1

    printStats(DATE, settings)
    
    return pos, settings

def printStats(DATE, settings):
    lookback = settings['lookback']
    #print("Stats for {}".format(DATE[lookback-1]))

    #print("settings['spy_under_short_sma'] = {}".format(settings['spy_under_short_sma']))
    #print("settings['spy_over_short_sma'] = {}".format(settings['spy_over_short_sma']))


##### Do not change this function definition #####
def mySettings():
    '''Define your market list and other settings here.

    The function name "mySettings" should not be changed.

    Default settings are shown below.'''

    # Default competition and evaluation mySettings
    settings = {}

    if 0:
        settings['markets']=['CASH', 'AAPL','MSFT']

    # S&P 100 stocks
    if 1:
        settings['markets']=['CASH', 'F_ES', 'AAPL','ABBV','ABT','ACN','AEP','AIG','ALL',
                             'AMGN','AMZN','APA','APC','AXP','BA','BAC','BAX','BK','BMY','BRKB','C',
                             'CAT','CL','CMCSA','COF','COP','COST','CSCO','CVS','CVX','DD','DIS','DOW',
                             'DVN','EBAY','EMC','EMR','EXC','F','FB','FCX','FDX','FOXA','GD','GE',
                             'GILD','GM','GOOGL','GS','HAL','HD','HON','HPQ','IBM','INTC','JNJ','JPM',
                             'KO','LLY','LMT','LOW','MA','MCD','MDLZ','MDT','MET','MMM','MO','MON',
                             'MRK','MS','MSFT','NKE','NOV','NSC','ORCL','OXY','PEP','PFE','PG','PM',
                             'QCOM','RTN','SBUX','SLB','SO','SPG','T','TGT','TWX','TXN','UNH','UNP',
                             'UPS','USB','UTX','V','VZ','WAG','WFC','WMT','XOM']

    # Futures Contracts
    if 0:
        settings['markets'] = ['CASH', 'F_AD', 'F_AE', 'F_AH', 'F_AX', 'F_BC', 'F_BG', 'F_BO', 'F_BP', 'F_C',  'F_CA',
                               'F_CC', 'F_CD', 'F_CF', 'F_CL', 'F_CT', 'F_DL', 'F_DM', 'F_DT', 'F_DX', 'F_DZ', 'F_EB',
                               'F_EC', 'F_ED', 'F_ES', 'F_F',  'F_FB', 'F_FC', 'F_FL', 'F_FM', 'F_FP', 'F_FV', 'F_FY',
                               'F_GC', 'F_GD', 'F_GS', 'F_GX', 'F_HG', 'F_HO', 'F_HP', 'F_JY', 'F_KC', 'F_LB', 'F_LC',
                               'F_LN', 'F_LQ', 'F_LR', 'F_LU', 'F_LX', 'F_MD', 'F_MP', 'F_ND', 'F_NG', 'F_NQ', 'F_NR',
                               'F_NY', 'F_O',  'F_OJ', 'F_PA', 'F_PL', 'F_PQ', 'F_RB', 'F_RF', 'F_RP', 'F_RR', 'F_RU',
                               'F_RY', 'F_S',  'F_SB', 'F_SF', 'F_SH', 'F_SI', 'F_SM', 'F_SS', 'F_SX', 'F_TR', 'F_TU',
                               'F_TY', 'F_UB', 'F_US', 'F_UZ', 'F_VF', 'F_VT', 'F_VW', 'F_VX',  'F_W', 'F_XX', 'F_YM',
                               'F_ZQ']

    settings['beginInSample'] = '2011101'
    settings['endInSample'] = '20200101'
    settings['lookback'] = 200
    settings['budget'] = 10**6
    settings['slippage'] = 0.05
    settings['participation'] = 0.1

    settings['days_passed'] = 0
    settings['spy_under_short_sma'] = 0
    settings['spy_over_short_sma'] = 0
    
    return settings

# Evaluate trading system defined in current file.
if __name__ == '__main__':
    import quantiacsToolbox

    parser = argparse.ArgumentParser(description='Run strategy backtrace.')
    args = parser.parse_args()
    
    results = quantiacsToolbox.runts(__file__)
