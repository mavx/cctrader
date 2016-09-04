import time
import pandas as pd
import numpy as np
import sys
import logging

logging.basicConfig(filename='simulation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

def simulate(buyPercent, sellPercent, buy_mult, sell_mult):
    
    # Display prices in 8 decimals and disables scientific notation
    pd.set_option('precision', 8)
    np.set_printoptions(precision=8, suppress=True)

    # Import market trade history file
    raw_df = pd.read_csv("tradehistory/xem.csv")
    df = raw_df.sort_index(ascending=False, axis=0)

    # Return rows of data
    data_length = len(df.index) #112860
    logging.info('Loaded {} rows.'.format(data_length))

    # Select first 200 rows of data
    init_row = 200
    dataRange = 200 # define range of past data used to generate buyAt or sellAt price
    row = init_row
    init_data = df[init_row:]

    def newBuyPrice(pastData, buyPercent):
        p = np.percentile(pastData['rate'], buyPercent)
        return p

    def newSellPrice(pastData, sellPercent):
        p = np.percentile(pastData['rate'], sellPercent)
        return p

    # Define starting row_index to loop from ==> 112660
    row_index = data_length - row

    #Starting Profit
    profit = 0
    totalProfit = 0
    tx_num = 0
    ROI = 0
    tx_type = ''
    last_price = 0

    try:
        while (row_index > 0):
            # BUY LOOP

            # Define past data to calculate intended buy price, take Range(T-200) for now
            pastData = df[-(row_index+dataRange):-row_index] #112860 to 112660
            
            # Define future data to match our buy price
            loopData = df[-(row_index):] #112660 to 0
            sell_list = loopData[loopData['type'] == 'sell']
            
            # Calculate intended buy price
            buyAt = newBuyPrice(pastData, buyPercent) * buy_mult

            logging.debug('''
                ===========================================
                Buying at {:.8f}'''.format(buyAt)
                )
           
            # Return first row index that is below our intended buy price
            row_index = sell_list[sell_list['rate'] <= buyAt].index.tolist()[0]

            saleRow = loopData.loc[[row_index]] # Return selected row with row_index
            sale = loopData.loc[row_index]['rate'] # Return sale price at row_index (aka bought at)

            logging.debug(saleRow)
            logging.debug('Bought XEM at {:.8f}.'.format(sale))
            
            tx_num = tx_num + 1
            logging.debug('''
                Transaction #{}
                '''.format(tx_num)
                )
            
            # Transaction type
            tx_type = 'buy'
            last_price = sale

            # SELL LOOP
            # Define past data to calculate intended sell price, take Range(T-200) for now
            newData = df[-(row_index+dataRange):-row_index] #112859 to 112659
            
            # Define future data to match our sell price, from #112659 onwards
            newLoopData = df[-row_index:]
            buy_list = newLoopData[newLoopData['type'] == 'buy']

            # Calculate intended sell price
            sellAt = newSellPrice(newData, sellPercent) * sell_mult
            logging.debug('Selling at {:.8f}.'.format(sellAt))
            
            # Return first row index that is above our intended sell price
            row_index = buy_list[buy_list['rate'] >= sellAt].index.tolist()[0]

            buyRow = newLoopData.loc[[row_index]]
            purchase = newLoopData.loc[row_index]['rate'] # Return purchase price at row_index (aka sold at)
            
            logging.debug(buyRow)
            logging.debug('Sold XEM at {:.8f}.'.format(purchase))

            tx_num = tx_num + 1
            logging.debug('''
                Transaction #{}
                ------------------------------------------'''.format(tx_num)
                )
            
            profit = 0.1 * ((purchase/sale)-1)
            profit_perc = profit/0.1*100
            logging.debug('Profit on 0.1 BTC transacted: {:.8f} BTC'.format(profit))
            logging.debug('Gained {:.8f}%% this round'.format(profit_perc))

            totalProfit = totalProfit + profit
            ROI = (totalProfit/0.1)*100
            logging.debug('Total profit so far: {:.8f} BTC'.format(totalProfit))
            logging.debug('Overall ROI: {:.2f}%%'.format(ROI))
            
            # Transaction type
            tx_type = 'sell'
            last_price = purchase

    except IndexError:
        logging.debug('Last transaction: {}'.format(tx_type))
        logging.debug('Transaction price: {:.8f}'.format(last_price))

    except:
        logging.warning('Something is wrong')

    logging.debug('Congratulations! Your accumulated profit is roughly {:.8f} BTC.'.format(totalProfit))
    logging.debug('Overall ROI: {:.2f}%%'.format(ROI))
    
    return float('{:.2f}'.format(ROI))

def progressBar(array):
    """ Shows simulation progress """
    sys.stdout.write('\r')
    # the exact output you're looking for:
    num = len(array)
    sys.stdout.write("Iterating: [%-*s] %d%%" % (num, '='*i, (100*i/num)))
    sys.stdout.flush()

def profit_stats(sim_profit, calc):
    """ Provide summary statistics on simulated strategies
    :sim_profit -> simulated profit dict
    :calc -> min, max, mean
    rtype: float
    """

    # First define array of profits associated to each buy strategy
    buyStrat_profits = []

    if (calc == 'mean'):
        for buyPerc in sim_profit:
            meanBuy = np.mean(sim_profit[buyPerc])
            # Append mean ROI for each buy strategy
            buyStrat_profits.append(meanBuy)
        # Calculate overall mean ROI
        return '{:.2f}'.format(np.mean(buyStrat_profits))

    elif (calc == 'max'):
        for buyPerc in sim_profit:
            maxBuy = max(sim_profit[buyPerc])
            buyStrat_profits.append(maxBuy)
        return '{:.2f}'.format(max(buyStrat_profits))

    elif (calc == 'min'):
        for buyPerc in sim_profit:
            minBuy = min(sim_profit[buyPerc])
            buyStrat_profits.append(minBuy)
        return min(buyStrat_profits)

    return float('{:.2f}'.format(ROIstat))

# List of percentile strategy to test
sim_buyPerc = [75, 80, 85]
sim_sellPerc = [90, 95, 100]
sim_profit = {}

# Define multiplier to calculated price to cater for high growth
buy_mult = [1]
sell_mult = [1.1]
mult_dict = {}

print "\nTo cater for XEM's high growth, a multiplier on the calculated target buy/sell price is used:"
print 'Buy multiplier: %r' % buy_mult
print 'Sell multiplier: %r \n' % sell_mult
print 'There will be %d iteration(s)..' % (len(buy_mult) * len(sell_mult))
print 'Calculating %r x %r = %r combinations..' % (len(sim_buyPerc), len(sim_sellPerc), len(sim_buyPerc)*len(sim_sellPerc))

# Runs simulate function for each percentile strategy combination
# And inserts profit into sim_profit dictionary
# Format: sim_profit = {buyPerc1: [profit1, profit2, profit3], buyPerc2: [profit1, profit2, profit3]}

# Iterate over our chosen multipliers
for b_mult in buy_mult:
    # Add a column to our dictionary for each buy multiplier
    mult_dict[b_mult] = []
    for s_mult in sell_mult:

        # Iterate over our chosen buy/sell strategies
        i=0
        for buy in sim_buyPerc:
            sim_profit[buy] = []
            for sell in sim_sellPerc:
                prof_calc = simulate(buy, sell, b_mult, s_mult)
                # Add each profit into sim_profit dict
                sim_profit[buy].append(prof_calc)
            # Add progress bar
            i = i + 1
            progressBar(sim_buyPerc)

#print sim_profit

        # Putting buy vs sell percentile matrix into Pandas Dataframe:
        df3 = pd.DataFrame(data=sim_profit, index=sim_sellPerc)

        # Print final summary
        print '\n'
        print '===================================================='
        print 'Profit Summary Matrix'
        print '===================================================='
        print 'Multipliers: %r (Buy), %r (Sell)' % (b_mult, s_mult)
        print 'col headers: buy percentile'
        print 'row headers: sell percentile'
        print 'table values: ROI (%)\n'
        print df3

        # Print out profit for buy/sell multiplier combo
        mean_ROI = profit_stats(sim_profit, 'mean')
        max_ROI = profit_stats(sim_profit, 'max')
        min_ROI = profit_stats(sim_profit, 'min')
        print '\n'
        print 'Max ROI: %r%%' % max_ROI
        print 'Min ROI: %r%%' % min_ROI
        print 'Mean ROI: %r%%' % mean_ROI
        print '----------------------------------------------------\n'
        
'''
        mult_dict[b_mult].append(m_ROI)

df4 = pd.DataFrame(data=mult_dict, index=sell_mult)
print 'AND FINALLY, the ROI table for each buy/sell multiplier:'
print df4
'''