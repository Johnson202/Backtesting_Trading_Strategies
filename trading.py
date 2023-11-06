import pandas as pd
import numpy as np

def EMA(df, closeCol, numPeriods):
    """
    Function takes in dataframe, name of column containing Close Price data, and 
    length of the period of EMA to compute. Calculation of this is populated 
    in the column f'{n}_period_EMA'.

    Args:
        df (pandas.DataFrame): inputted df
        closeCol (str): name of column containing Close Price data
        numPeriods (int): period length of EMA to compute

    Returns:
        dfCopy (pandas.DataFrame): outputted df with added EMA column
    """
    dfCopy = df.copy(deep=True)
    dfCopy[f'{numPeriods}_period_EMA'] = float('NaN')
    k = 2/(numPeriods+1)
    for i in range(numPeriods-1, len(dfCopy)):
        if i == (numPeriods - 1):
            # simple moving average (SMA) calc. for initial data pt.
            dfCopy[f'{numPeriods}_period_EMA'][i] = np.sum(dfCopy[closeCol][i-(numPeriods-1):i+1])/numPeriods
        else:
            # exponential moving average (EMA) calc. for remaining data pts.
            dfCopy[f'{numPeriods}_period_EMA'][i] = dfCopy[closeCol][i] * k + dfCopy[f'{numPeriods}_period_EMA'][i-1] * (1 - k)

    return dfCopy

def EMA_trading_strategy(df, emaCol1, emaCol2, emaCol3):
    """
    Function takes in dataframe and names of 3 EMA columns. Period length of 
    emaCol1 must be less than period length of emaCol2, which must also be 
    less than period length of emaCol3. Buy/sell signals are computed from 
    this trading strategy.

    Args:
        df (pandas.DataFrame): inputted df
        emaCol1 (str): name of column containing shortest period EMA data
        emaCol2 (str): name of column containing longer period EMA data
        emaCol3 (str): name of column containing longest period EMA data

    Returns (tup):
        dfCopy (pandas.DataFrame): outputted df with added Buy_Sell_Signal column
    """
    dfCopy = df.copy(deep=True)
    dfCopy['Buy_Sell_Signal'] = float('NaN')
    bought = False

    
    for i in range(len(dfCopy)):
        # assess 5-period EMA vs. 21-period EMA vs. 55-period EMA
        if np.isnan(dfCopy[emaCol1][i]) or np.isnan(dfCopy[emaCol2][i]) or np.isnan(dfCopy[emaCol3][i]):
            continue
        elif dfCopy[emaCol2][i] < dfCopy[emaCol1][i] and dfCopy[emaCol3][i] < dfCopy[emaCol2][i] and bought == False:
            dfCopy['Buy_Sell_Signal'][i] = 'BUY'
            bought = True
        elif dfCopy[emaCol2][i] > dfCopy[emaCol1][i] and dfCopy[emaCol3][i] > dfCopy[emaCol2][i] and bought == True:
            dfCopy['Buy_Sell_Signal'][i] = 'SELL'
            bought = False
        
    return dfCopy

def assessTradingStrategy(df, closeCol, buySellSignalCol, initialAmount=1000):
    """
    Function takes in dataframe, column name of Buy/Sell Signal data, column name containing Close Price data, 
    & initial investment amount (in USD). Function returns tuple of total profit made or losses incurred, 
    percent profit made or losses incurred, ending investment amount, number of successful trades, number of 
    unsuccessful trades, and success rate. Assume a 0.75% trading fee per buy or sell trade.

    Args:
        df (pandas.DataFrame): the input df
        buySellSignalCol (str): column name of Buy/Sell Signal data
        closeCol (str): column name of Close Price data
        initialAmount (float): initial investment amount (in USD)

    Returns (tup):
        totalProfit (float): total profit made (+) or loss incurred (-) over time period
        percentTotalProfit (str): percent total profit made or loss incurred over time period
        endingInvestmentAmount: ending investment amount with implementation of trading strategy
        numSuccess (int): number of successful trades, i.e. profitable/break-even trades
        numFailure (int): number of unsuccessful trades, i.e. non-profitable trades (losses incurred)
        successRate (str): percentage of trades that were successful trades (profitable/break-even)
    """
    investment = initialAmount
    buyPrice = 0
    sellPrice = 0
    bought = False
    numSuccess = 0
    numFailure = 0
    endingInvestmentAmount = 0
    
    for i in range(len(df)):
        if df[buySellSignalCol][i] == 'BUY' and bought == False:
            # 0.75% flat trading fee assumed (built into buy price)
            buyPrice = df[closeCol][i] * (1 + .0075)
            bought = True
        elif df[buySellSignalCol][i] == 'SELL' and bought == True:
            sellPrice = df[closeCol][i]
            investmentInitial = investment
            # 0.75% flat trading fee assumed
            investment *= (sellPrice/buyPrice - 0.0075)
            if investment >= investmentInitial:
                numSuccess += 1
            else:
                numFailure += 1
            bought = False
        if i == len(df) - 1:
            endingInvestmentAmount = round(investment, 2)

    totalProfit = round(investment - initialAmount, 2)
    percentTotalProfit = str(round((investment/initialAmount)*100 - 100, 2))  + '%'
    successRate = str(round((numSuccess/(numSuccess + numFailure))*100, 2)) + '%' 
    return (totalProfit, percentTotalProfit, endingInvestmentAmount, numSuccess, numFailure, successRate)


if __name__ == '__main__':
    pass