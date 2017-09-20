"""
Below follows my code. Initially, it was a bit more elegant as it used global variables, 
which let me refer to various lists by name, such as UPL, RPL, WAP, equities, etc. Now,
those have all been subsumed into a list of lists to avoid the use of global variables.

Note that k is an index of equities, with k = 0 being Apple, k = 1, Amazon, etc.
"""
# Install Python package tabulate
# !pip install tabulate
# !pip install texttable

import time
from datetime import datetime
from pytz import timezone
import texttable as tt
from urllib.request import urlopen
from bs4 import BeautifulSoup
# import random

# Global constants

# The stocks available
tickers = ("AAPL", "AMZN", "MSFT", "INTC", "SNAP")
count = len(tickers)

# Trade Options: Buy & Sell
sides = ("Buy", "Sell")
side_dict = {0: 1, 1: -1}

# Blotter and P/L Headings
blot_headers = ("Ticker", "Side", "Quantity", "Executed Price", "Date / Time")
PL_headers = ("Ticker", "Position", "Market", "WAP", "UPL", "RPL")

date_format = "%m/%d/%y %H:%M:%S" # EST is used

# Initial user selection
init_selection = 0

# Initial portfolio of $10m and 0 shares;
# Cash is last element in list
init_portfolio = [0]*count + [10**7]

# Initial history of past trades (i.e. nothing)
init_history = [[], # Equity names
                [], # Buy or Sell designation
                [], # Quantities traded
                [], # Equity Prices
                []]  # Date of trades

# Initial P/L Figures (i.e. nothing)
init_PL = [[0] * count, # WAP
           [0] * count, # UPL
           [0] * count] # RPL

new_ledger = [init_selection, init_portfolio, init_history, init_PL]

# Functions

def welcome():
    print("Welcome to the Trading Floor")
    print("For this program, you will enter numbers to select menu options")
    time.sleep(1)

def menu(data):
    print()
    print("Please select an option")
    print("1. Trade")
    print("2. Show Blotter")
    print("3. Show P/L")
    print("4. Quit")
    
    data[0] = input()
    return data
    
def get_price(ticker):
    
    url = "https://finance.yahoo.com/quote/" + ticker
    stock_page = urlopen(url)
    soup = BeautifulSoup(stock_page, 'lxml')
    price = float(soup.find('span', {'class': 
        "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text)
    
    # For error-checking, allows rapid fluctuation of stock prices
    # price = round(random.random()*200,2) 
    
    return price


def get_prices():
    prices = []
    for i in range(count):
        prices.append(get_price(tickers[i]))
    return prices

# Trade menu
def trade_menu(data):    
    # User picks which stock to trade
    print("Which equity would you like to trade?")
    for i in range(count):
        print(i+1,". ", tickers[i], sep = "")
    
    # k = the index of the equity, e.g. 0 = AAPL, 1 = AMZN, etc.
    k = int(input()) - 1

    # User decides whether to buy or sell
    print("Would you like to:")
    print("1. Buy")
    print("2. Sell")
    side_index =  int(input())-1
    
    # Assign side, 1 if buying, -1 if selling
    side = side_dict[side_index]

    # User specifies trade quantity
    print("How many shares do you want to trade?")
    quantity = float(input())
    
    # Record trade price
    price = get_price(tickers[k])
    
    # Check that you have enough cash for the buy order
    if data[1][count] < side * price * quantity:
        print("Buy cannot be executed, insufficient cash")
    # Check that you have enough shares for the sell order
    elif side == -1 and quantity > data[1][k]:
        print("Sell cannot be executed, insufficient shares")
    elif quantity < 0:
        print("Impossible trade quantity")
    else: 
        data = trading(side, price, quantity, k, data)
        data = update_blotter(side_index, price, quantity, k, data)    
        print("Congratulations, you traded", quantity, "shares", 
              "at $", price)
    
    return data


def trading(buying, price, quantity, k, data):
    if buying == 1: 
        # Update P/L Statistics: WAP
        total_value = data[3][0][k] * data[1][k] + price * quantity
        total_quantity = data[1][k] + quantity
        data[3][0][k] = total_value / total_quantity

    else:
        # Selling Stock
        # Update P/L Statistics: RPL
        data[3][2][k] += quantity * (price - data[3][0][k])
        data[3][1][k] -= data[3][2][k]
    
    # Update cash on hand    
    data[1][count] -= buying*quantity * price
    
    # Update quantity of stock on hand
    data[1][k] += buying*quantity
    
    return data


def update_blotter(side_index, price, quantity, k, data):
    # Record trade date
    now_time = datetime.now(timezone('US/Eastern'))
    date = now_time.strftime(date_format)

    # Update trade history
    data[2][0].append(tickers[k]) 
    data[2][1].append(sides[side_index])    
    data[2][2].append(quantity)
    data[2][3].append(price)    
    data[2][4].append(date) 
    
    return data

    
def show_blotter(data):
    # Create empty table
    tab = tt.Texttable()
    
    headings = blot_headers    
    tab.header(headings)
    for row in zip(data[2][0][::-1], data[2][1][::-1],  data[2][2][::-1],
                   data[2][3][::-1], data[2][4][::-1]):
        tab.add_row(row)

    s = tab.draw()
    print (s)
    return data

def show_PL(data):
    tab = tt.Texttable()
    
    headings = PL_headers
    tab.header(headings)
    current_prices = get_prices()
    for i in range(count):
        data[3][1][i] = (current_prices[i] - data[3][0][i]) * data[1][i]
    for row in zip(tickers, data[1][:-1], current_prices,
                   data[3][0], data[3][1], data[3][2]):
        tab.add_row(row)

    s = tab.draw()
    print (s)
    return data   

# Function to run program
def Execute():
    data = new_ledger
    welcome()
    done = False
    while not done:
        data = menu(data)
        if data[0] == "1":
            data = trade_menu(data)
        if data[0] == "2":
            show_blotter(data)
        if data[0] == "3":
            show_PL(data)
            print ("Total cash on hand is: ${:,.2f}".format(data[1][count]))
        if data[0] == "4":
            done = True
            print("Thank you for trading with us!")

# Run Program!
Execute()
