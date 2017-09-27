import datetime
import numpy as np
from bs4 import BeautifulSoup 
from urllib.request import urlopen
from tabulate import tabulate

# Global constants 
sides = ("Buy", "Sell")
side_dict = {0: 1, 1: -1}
starting_cash = 10**7

# data = [portfolio, blotter, cash, user selection]

init_data = [np.array([["Ticker","Quantity","Price","WAP","UPL","RPL",
                        "Total P/L"],
                        ["AAPL", 0, 0, 0, 0, 0, 0],
                        ["AMZN", 0, 0, 0, 0, 0, 0],
                        ["INTC", 0, 0, 0, 0, 0, 0],
                        ["MSFT", 0, 0, 0, 0, 0, 0],
                        ["SNAP", 0, 0, 0, 0, 0, 0]], dtype = "O"),
        np.array([["Equity","Buy/Sell","Quantity","Price","Date & Time", 
                   "Cash After"]], 
                 dtype = "O"),
        starting_cash]

# Helper functions definitions

def welcome():
    print("Welcome to the Trading Floor", '\n', 
          "For this program, you will enter numbers to select menu options",
          '\n', sep ='')

def menu():
    print("\nPlease select an option \n",
          "1. Trade \n",
          "2. Show Blotter \n", 
          "3. Show P/L \n", 
          "4. Quit")
    
    selection = input()
    return selection

def trade_menu(data):    
    # User picks which stock to trade
    print("Please enter the ticker symbol of your desired equity \n", "\n",
          "Choices: \n",
          "AAPL \n",
          "AMZN\n",
          "INTC\n",
          "MSFT\n",
          "SNAP\n",)
    
    # k = the index of the equity, e.g. 0 = AAPL, 1 = AMZN, etc.
    ticker = input().upper()
        

    # User decides whether to buy or sell
    print("Would you like to: \n 1. Buy \n 2. Sell")
    side_index =  int(input())-1
    
    # Assign side, 1 if buying, -1 if selling
    side = side_dict[side_index]
    side_txt = sides[side_index]

    # User specifies trade quantity
    print("How many shares do you want to trade?")
    quantity = float(input())
    
    # Record trade price
    price = get_price(ticker)
    
    # Request user confirmation of trade
    print("Please type 1 to confirm the ", side_txt," of ", quantity, 
          " shares of ", ticker, " at the current market price of ", 
          "${:,.2f}".format(price), ", or press 0 to cancel.", sep ="")
    
    # Check if equity is already in portfolio
    # If it exists, obtain its index
    # If not, append it to the data frame
    if np.any(data[0][:, 0] == ticker):
        k = np.where(data[0][:,0] == ticker)[0][0]
    else:
        k = len(data[0][:,0])
        data[0] = np.concatenate((data[0], 
                np.array([[ticker, 0, price, price, 0, 0, 0]],dtype="O")))

    if input() == '0':
        print("Trade has been canceled")
    # Check that you have enough cash for the buy order
    elif data[2] < side * price * quantity:
        print("Buy cannot be executed, insufficient cash")
    # Check that you have enough shares for the sell order
    elif quantity < 0:
        print("Impossible trade quantity")
    elif side == -1 and quantity > data[0][k,1]:
        print("Sell cannot be executed, insufficient shares")    
    else: 
            #Update the portfolio dataframe
            data[0] = trading(ticker, side, quantity, price, k, data[0])
            
            # Record trade date
            date = str(datetime.datetime.now())[0:19]
            
            # Update cash on hand
            data[2] -= quantity * price * side
    
            # Update blotter aka trade history
            data[1] = np.concatenate((data[1], 
                [[ticker, side_txt, quantity, price, date, data[2]]]))
        
            print("Congratulations, you traded", quantity, "shares", 
                  "at $", "${:,.2f}".format(price))
    
    return data

def trading(ticker, side, quantity, price, k, data0):
    if side == 1: 
        # Update P/L Statistics: WAP
        # total_value = current quantity * WAP + current price*new quantity
        total_value = data0[k,1] * data0[k,3] + price * quantity
        
        # total quantity = existing quantity + new quantity
        total_quantity = data0[k, 1] + quantity
        
        # WAP = total value / total quantity
        data0[k,3] = total_value / total_quantity

    else:
        # Selling Stock
        # Realized change = quantity * (price - WAP)
        realized_change = quantity * (price - data0[k, 3])
        
        # RPL = quantity*(price - WAP)
        data0[k, 5] += realized_change
    
    #Total P/L
    data0[k, 6] = data0[k, 4] + data0[k,5]
    
    # Update quantity of stock on hand
    data0[k, 1] += side*quantity
    
    return data0

def get_price(ticker):
    
    url = "https://finance.yahoo.com/quote/" + ticker
    stock_page = urlopen(url)
    soup = BeautifulSoup(stock_page, 'lxml')
    stock_class = "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"
    price = float(soup.find('span', {'class': stock_class}).text)
    
    # For error-checking, allows rapid fluctuation of stock prices
    # price = round(random.random()*200,2) 
    
    return price

def get_prices(data00):
    # data00 = data[0][:,0], the list of ticker symbols
    prices = []
    
    # Get the ticker symbol of each stock, and then obtain its price
    for i in range(len(data00)):
        prices.append(get_price(data00[i]))
    return prices

def show_blotter(data1):
    
    if len(data1) > 1:
        
        # Sort by date, most recent trade on top
        flipped = data1[1:, :][::-1]
        
        # Create table
        table = np.vstack((data1[0,:], flipped))
    
        print(tabulate(table))
    else:
        print(tabulate(data1))
def show_PL(data0):

    # Making sure PL table is not empty
    if len(data0[:, 0]) > 1:
        
        # Assign prices for all stocks
        data0[1:,2] = get_prices(data0[1:,0])
        
        # Update UPL
        for i in range(1,len(data0[:,0])-1):
            # UPL = (current price - WAP) * Quantity Held
            data0[i, 4] = (data0[i, 2] - data0[i,3]) * data0[i,1]
            
            # Total P&L = UPL + RPL
            data0[i, 6] = data0[i, 4] + data0[i, 5]
    
    
    # Sort data by ticker name
    heading = data0[0,:]
    data0 = data0[1:,:]
    
    #Alphabetize by equity name
    data0sort = data0[data0[:,0].argsort()]
    table = np.vstack((heading, data0sort))

    print(tabulate(table))
    

def Execute():
    welcome()
    done = False
    data = np.copy(init_data)
    while not done:
        selection = menu()
        if selection == "1":
            data = trade_menu(data)
        if selection == "2":
            show_blotter(data[1])
        if selection == "3":
            show_PL(data[0])
            print ("Total cash on hand is: ${:,.2f}".format(data[2]))
        if selection == "4":
            done = True
            print("Thank you for trading with us!")

# Run Program!
Execute()
