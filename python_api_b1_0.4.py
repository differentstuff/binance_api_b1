#!/usr/bin/env python
import time
import datetime
import sys
import getopt
import os
from binance import ThreadedWebsocketManager
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from texttable import Texttable

#api_key = os.environ.get('binance_api')
#api_secret = os.environ.get('binance_secret')
api_key = 'Insert_your_Key_here'
api_secret = 'Insert_your_Secret_here'

def main(argv):
 # load client
 client = Client(api_key, api_secret)
 # initialise and start the Websocket
 twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, testnet=False)
 
 try:
  opts, args = getopt.getopt(argv,'hiwts:','symbol=, test')
  #read out arguments "s" (mandatory) or "h"
  
 except getopt.GetoptError:
  print ('python_api_b1.py -s <Symbol>')
  #OnError print message: how to use
  sys.exit(2)
  #exit program
  
 for opt, arg in opts:  
  if opt == '-h':
   print ('-s <symbol>   //Show Symbol info')
   print ('-s BTCUSDT')
   print ('-s ADABTC -t -w')
   print ()
   print ('-w   //Show Wallet info')
   print ('-t   //Show last 5 Trades')
   print ('-m <module>   //use module (not yet implemented)')
   print ('-i   //Show general info')
     #the option switch -h shows help text
   
  elif opt == '-i':
   print('------i-i-i------')
   
  elif opt == '-s':
   symbol_option(arg)
   # the option switch -s looks for the symbol to use (and initialize connection to API)
   
   
  elif opt == '-w':
  # the option switch -w looks for all wallets over value 0.00 and prints a list of all
   wallet_option()

  
  elif opt == '--test':
   #for testing purpose
   name = input('my personal input')

  elif opt == '-t':
   # get specific trade
   print('---Last Trades---')
   trades = client.get_recent_trades(symbol=arg)
   trades_l = trades.pop()
   trades_list = list(trades)
   print(type(trades))
   print(trades)
   print('\n'.join(trades[5].values()))

def symbol_option(arg):
 # load client
 client = Client(api_key, api_secret)
 status = client.get_system_status()
 # print('Status = ' , status)
 # show Symbol Info
 # get Symbol & variation name
 symbol_info = client.get_symbol_info(arg)
 symbol_a = symbol_info['quoteAsset']
 symbol_b = symbol_info['status']
 arg_symbol = arg.replace(symbol_a,'')
 try:
  trades = client.get_recent_trades(symbol=arg)
 except TypeError:
  print('An Error occured!')
  # get daytime
 finally: 
  print('------------------------------------')
  print ('--- Local Time ---')
  t = time.localtime()
  current_time = time.strftime('%T', t)
  print('Your current local Time is',current_time)
  # get Wallet balance
  asset_balance = client.get_asset_balance(asset=arg_symbol)
  print()
  ###
  print('--- Symbol Info ---')
  # print Symbol Name
  print ('Symbol Code   =' , arg) 
  # print Symbol Name shortened
  print('Symbol Name   =' , arg_symbol) 
  # print quoteAsset
  print('Quote Asset   =',symbol_a)
  print('Symbol Status =',symbol_b)
  print()
  ###
  # print Asset Wallet Spot
  print('--- Asset Wallet: Spot ---')
  free_balance = asset_balance['free']
  locked_balance = asset_balance['locked']
  free_balance_float = float(free_balance)
  locked_balance_float = float(locked_balance)
  total_wallet = free_balance_float + locked_balance_float
  total_wallet_rounded = round(total_wallet, 9)  
  print('Free Wallet   = ' , "%.8f" % free_balance_float , arg_symbol , '(exact)')
  print('Locked Wallet = ' , "%.8f" % locked_balance_float , arg_symbol , '(exact)')
  print ('Total Wallet  = ', "%.8f" % total_wallet_rounded , arg_symbol , '(rounded)')
  price = client.get_symbol_ticker(symbol=arg)
  price_a = float(price['price'])
  price_f = float(asset_balance['free'])
  price_l = float(asset_balance['locked'])
  quote_value_a = price_f * price_a
  quote_value_l = price_l * price_a
  quote_value_t = total_wallet_rounded * price_a
  print('You have', int(quote_value_a), symbol_a , 'available (rounded)')
  print('You have', int(quote_value_l), symbol_a , 'locked (rounded)')
  print('You have', int(quote_value_t), symbol_a , 'total (rounded)')
  print()
  ###
  # print Asset Wallet Margin Cross
  # print Asset Wallet Margin Isolated
  # print Asset Wallet Futures
  # print Open Orders
  print('--- Open Orders ---')
  orders = client.get_open_orders(symbol=arg)
  print(orders)
  print()
  ###
  # get live ticker price
  print('--- Live Price ---')
  print('1' , arg_symbol , ' = ' , float(price_a) , symbol_a)
  print('------------------------------------')

def sort(list):
 for e in list:
  #
  #
  #
  return e

def wallet_option():
 # print Spot Wallet
 # load client
 client = Client(api_key, api_secret)
 # get all balances
 info = client.get_account()
 # Get all Coins
 spot_balance = info['balances']
 print('\n' , '--- Spot Balance ---')
 print()
 # Filter out balances
 spot_list = list(spot_balance)
 spot_free = list()
 try: 
   for k in spot_list:
    if (k['free'] != '0.00000000'):
     if (k['free'] != '0.00'):
      spot_free.append(k)
 except TypeError:
   print('An Error occured!')
###
 # print Spot Wallet
 st = Texttable()
 st.set_cols_align(['l','l','l'])
 st.set_cols_dtype(['t','f','f'])
 st.set_max_width(800)
 st_header = ['Asset Name' , 'Balance free' , 'Balance locked']
 st.header(st_header)
 for a in spot_free:
  row = [a['asset'] , a['free'] , a['locked']]
  st.add_row(row)
 print(st.draw())
 ###
 # print Futures Wallet
 print('\n' , '--- Futures ---')
 print()
 futures_balance = client.futures_account_balance()
 ft = Texttable()
 ft.set_cols_align(['l','l','l'])
 ft.set_cols_dtype(['t','f','f'])
 ft.set_max_width(800)
 ft_header = ['Asset Name' , 'Balance' , 'Balance withdrawable']
 ft.header(ft_header)
 for a in futures_balance:
  row = [a['asset'] , a['balance'] , a['withdrawAvailable']]
  ft.add_row(row)
 print(ft.draw())
 print('------------------------------------')

if __name__ == "__main__":
 main(sys.argv[1:])
