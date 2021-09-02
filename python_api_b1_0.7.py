#!/usr/bin/env python
import time
from datetime import datetime
import sys
import getopt
import os
import warnings
from binance import ThreadedWebsocketManager
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from beautifultable import BeautifulTable
from termcolor import colored

#api_key = os.environ.get('binance_api')
#api_secret = os.environ.get('binance_secret')
api_key = ''
api_secret = ''

def main(argv):
 # load client
 global client 
 client = Client(api_key, api_secret)
 # initialise and start the Websocket
 twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, testnet=False)
 try:
  a = ''
  c = ''
  for a in argv[1]:
   b = a.upper()
   c = c + b
  argv[1] = c
   
  opts, args = getopt.getopt(argv,'hs:o:i:wt:r',['symbol=','test='])
  #read out arguments
    
 except getopt.GetoptError:
  print ('try this: python_api_b1.py -h')
  #OnError print message: how to use
  sys.exit(2)
  #exit program
  
 for opt, arg in opts:  
 #the option switch -h shows help text
  if opt == '-h':
   print ('-s <symbol>   //Show Symbol info')
   print ('-s BTCUSDT')
   print ('-s ADABTC -t -w')
   print ()
   print ('-w   //Show Wallet info')
   print ('-t   //Show last 5 Trades')
   print ('-m <module>   //use module (not yet implemented)')
   print ('-i   //Show general info')

  # define the symbol to use
  elif opt == '-s':
   symbol_option(arg)

  # check open Order
  elif opt == '-o':
   open_order(arg)
   
  # check open Order
  elif opt == '-i':
   history_order(arg)
   
  # check all wallets over value 0.00 and prints a list of all
  elif opt == '-w':
   wallet_option()
  
  elif opt == '-t':
   test_order(arg)
  
  elif opt == '-r':
  # trailing_stop()
   replace_order()
  # finally, a trailing-stop for binance!!
  
  # for testing purpose
  elif opt == '--test':
   name = input('my personal input')
  
def symbol_option(arg):
 # load client
 status = client.get_system_status()
 # print('Status = ' , status)
 # show Symbol Info
 # get Symbol & variation name
 symbol_info = client.get_symbol_info(arg)
 symbol_a = symbol_info['quoteAsset']
 symbol_b = symbol_info['status']
 arg_symbol = arg.replace( symbol_a , '' )
 try:
  trades = client.get_recent_trades(symbol=arg)
 except TypeError:
  print( 'An Error occured!' )
  # get daytime
 except BinanceAPIException:
  print( 'Invalid Symbol used:' , arg )
 finally: 
  print('------------------------------------','\n')
  print ( '--- Time ---' , '\n' )
  current_time = time.strftime( '%d/%m/%Y, %H:%M:%S' )
  time_s = client.get_server_time()
  time_r = time_s['serverTime']
  time_d = datetime.fromtimestamp( time_r / 1000 )
  server_time = time_d.strftime( '%d/%m/%Y, %H:%M:%S' )
  print( 'Your current Local Time is ' , current_time )
  print( 'Your current Server Time is' , server_time , '\n' )
  # get Wallet balance
  asset_balance = client.get_asset_balance(asset=arg_symbol)
  free_balance = asset_balance['free']
  locked_balance = asset_balance['locked']
  free_balance_float = float(free_balance)
  locked_balance_float = float(locked_balance)
  total_wallet = free_balance_float + locked_balance_float
  total_wallet_rounded = round(total_wallet, 9)  
  price = client.get_symbol_ticker(symbol=arg)
  price_a = float(price['price'])
  price_f = float(asset_balance['free'])
  price_l = float(asset_balance['locked'])
  quote_value_a = price_f * price_a
  quote_value_l = price_l * price_a
  quote_value_t = total_wallet_rounded * price_a
  price_b = 1 / price_a
  
  ###
  print( '--- Symbol Info ---' , '\n' )
  # print Symbol Name
  print ( 'Symbol Code   =' , arg ) 
  # print Symbol Name shortened
  print( 'Symbol Name   =' , arg_symbol ) 
  # print quoteAsset
  print( 'Quote Asset   =' , symbol_a )
  # print Trading Status
  # print('Symbol Status =',symbol_b)
  print()
  ###
  # get live ticker price
  print( '--- Live Price ---' , '\n' )
  print( '1' , arg_symbol , ' = ' , "%.8f" % price_a , symbol_a )
  print( '1' , symbol_a , ' = ' , "%.8f" % price_b , arg_symbol , '\n' )
  ###
  # print Asset Wallet Spot
  print( '--- Asset Wallet: Spot ---' , '\n' )
  print( '-- as' , arg_symbol , '--' )
  
  print( 'Free Wallet   = ' , "%.8f" % free_balance_float , arg_symbol )
  print( 'Locked Wallet = ' , "%.8f" % locked_balance_float , arg_symbol )
  print ( 'Total Wallet  = ', "%.8f" % total_wallet_rounded , arg_symbol )
  print( '\n' , '-- as' , symbol_a , '--' )

  print( 'You have' , "%.8f" % quote_value_a , symbol_a , 'available' )
  print( 'You have' , "%.8f" % quote_value_l , symbol_a , 'locked' )
  print( 'You have' , "%.8f" % quote_value_t , symbol_a , 'total' )
  ###
  # print Asset Wallet Margin Cross
  ###
  # print Asset Wallet Margin Isolated
  ###
  # print Asset Wallet Futures
  ###
  '''
  print('--- Open Orders ---','\n')
  try:
   orders = client.get_open_orders(symbol=arg)
   if orders:
    table = BeautifulTable()
    table.clear(True)
    table.set_style(BeautifulTable.STYLE_MARKDOWN)
    table.maxwidht = 25
    table.precision = 8
    table.columns.header = ['Pos','Symbol','Price','Stop Price','Type','Quantity','Order ID']
    table.columns.width = [5,10,15,15,25,15,15]
    nr = 1
    for item in orders: 
     table.rows.append([ nr , item['symbol'] , float(item['price']), float(item['stopPrice']),item['type'],item['origQty'],item['orderId']])
     nr += 1
    print( table , '\n' )
   if not orders:
    print('-No open Orders-','\n')
  finally:
  # print('aktuelles Problem: Preis sollte als float angezeigt werden, bleibt aber immer bei 0.0 stehen...')
  # print('und die Farbe fehlt in der Tabelle')
  ###
  '''
  print()
  print('------------------------------------')

def wallet_option():
 # print Spot Wallet
 # get all balances
 info = client.get_account()
 # Get all Coins
 spot_balance = info['balances']
 # Filter out balances
 spot_list = list(spot_balance)
 spot_free = list()
 try: 
  for f in spot_list:
   if (f['free'] != '0.00000000') or (f['locked'] != '0.00000000'):
    if (f['free'] != '0.00') or (f['locked'] != '0.00'):
     spot_free.append(f)
 except TypeError:
  print(TypeError)
 ###
 # print Spot Wallet
 print('\n' , '--- Spot Wallet - Balance ---' , '\n')
 s_table = BeautifulTable()
 s_table.clear(True)
 s_table.set_style(BeautifulTable.STYLE_MARKDOWN)
 s_table.maxwidht = 25
 s_table.precision = 8
 s_table.columns.header = ['Asset Name' , 'Balance free' , 'Balance locked']
 s_table.columns.width = [17,29,29]
 for a in spot_free:
  s_table.rows.append([ a['asset'] , "%.8f" % float(a['free']) , "%.8f" % float(a['locked']) ])
 with warnings.catch_warnings():
  warnings.filterwarnings("ignore")
  try:
   s_table.sort('Balance free', True)
  finally:
   print(s_table,'\n')
   # print('Es fehlt ein TOTAL als USDT' , '\n' , '!aber! die Werte werden nicht in USDT umgerechnet, daher muss ich den Preis ziehen und selbst umrechnen')
 ###
 # print Futures Wallet
 print('\n' , '--- Futures Wallet - Balance ---' , '\n')
 futures_balance = client.futures_account_balance()
 f_table = BeautifulTable()
 f_table.clear(True)
 f_table.set_style(BeautifulTable.STYLE_MARKDOWN)
 f_table.maxwidht = 25
 f_table.precision = 8
 f_table.columns.header = ['Asset Name' , 'Balance' , 'Balance withdrawable']
 f_table.columns.width = [17,29,29]
 for a in futures_balance:
  f_table.rows.append([a['asset'] , "%.8f" % float(a['balance']) , "%.8f" % float(a['withdrawAvailable']) ])
 with warnings.catch_warnings():
  warnings.filterwarnings("ignore")
  try:
   f_table.sort('Balance', True)
  finally:
   print(f_table,'\n')
  # print('Es fehlt ein TOTAL als USDT')
  ###
  # print Margin Wallet
  print('\n' , '--- Margin Wallet - Balance ---' , '\n')
  # margin = margin_info()
  print('margin info comes in here')
  margin_all_assets = client.get_all_isolated_margin_symbols()
  margin_s = client.get_account_snapshot(type='SPOT')
  margin_all_assets_symbol = []
  # print('Margin:' , margin_s)
  # for m in margin_all_assets:
   # margin_all_assets_symbol.append(m['symbol'])
  ###
  print( '\n' , '------------------------------------')

def snapshot():
 # spot_sn = client.get_account_snapshot(type='SPOT')
 # margin_sn = client.get_account_snapshot(type='MARGIN')
 futures_sn = client.get_account_snapshot(type='FUTURES')
 # inf = client.get_exchange_info()
 print('qsfdsqgfsd:',inf)
 futures_open_trades = []
 # print('sn:' , futures_sn)
 if futures_sn:
  for fut in futures_sn:
   print('test: ' , fut)
   # if (fut['unRealizedProfit'] != '0'):
    # futures_open_trades.append(fut)
 if not futures_sn:
  print('Nothing found in Futures')
 print('futures' , futures_open_trades)
   

def open_order(arg):
 client = Client(api_key, api_secret)
 print( '\n' , '--- All Open Orders for' , arg , '---'  , '\n' )
 # get open Margin Order
 print ('-- Cross Margin --' , '\n' )
 try:
  margin_cross_order_open = client.get_open_margin_orders( symbol=arg , limit=10 , isIsolated='FALSE' )
  if margin_cross_order_open: 
   print( 'Cross Orders:' , margin_cross_order_open )
  if not margin_cross_order_open: 
   print ( 'No open Orders found for Cross Margin:' , arg , '\n' )
 except BinanceAPIException:
  print ( 'not available for Cross Margin:' , arg , '\n' )
 print ('-- Isolated Margin --' , '\n' )
 try:
  margin_iso_order_open = client.get_open_margin_orders( symbol=arg , limit=10 , isIsolated='TRUE' )
  if margin_iso_order_open: 
   table = BeautifulTable()
   table.clear(True)
   table.set_style(BeautifulTable.STYLE_MARKDOWN)
   table.maxwidht = 25
   table.precision = 8
   table.columns.header = ['Pos','Symbol','Long/Short','Stop Price','Type','Quantity','Order ID']
   table.columns.width = [5,10,15,15,20,15,15]
   nr = 1
   for item in margin_iso_order_open: 
    table.rows.append([ nr , item['symbol'] , item['side'], "%.8f" % float(item['stopPrice']),item['type'], "%.8f" % float(item['origQty']),item['orderId']])
    nr += 1
   nrr = nr-1
   print( 'Open Orders found:' , nrr , '\n' )
   print( table , '\n' )  
  if not margin_iso_order_open: 
   print ( 'No open Isolated Margin Orders found for:' , arg , '\n' )
 except BinanceAPIException:
  print ( 'Not available for Isolated Margin:' , arg , '\n' )
 print ('-- Spot Orders --' , '\n' )
 try:
  open_spot_order = client.get_open_orders( symbol=arg )
  if open_spot_order: 
   table = BeautifulTable()
   table.clear(True)
   table.set_style(BeautifulTable.STYLE_MARKDOWN)
   table.maxwidht = 25
   table.precision = 8
   table.columns.header = ['Pos','Symbol','Price','Stop Price','Type','Quantity','Order ID']
   table.columns.width = [5,10,15,15,20,15,15]
   nr = 1
   for item in open_spot_order: 
    table.rows.append([ nr , item['symbol'] , float(item['price']), float(item['stopPrice']),item['type'],item['origQty'],item['orderId']])
    nr += 1
   nrr = nr-1
   print( 'Open Orders found:' , nrr , '\n' )
   print( table , '\n' )
  if not open_spot_order: 
   print ( 'No open Spot Orders found for:' , arg , '\n' )
 except BinanceAPIException:
   print ( 'Not available for Spot' , arg , '\n' )
 print('-- Futures --' , '\n' )
 try:
  futures_open = client.futures_get_open_orders( symbol=arg )
  if futures_open:
   table = BeautifulTable()
   table.clear(True)
   table.set_style(BeautifulTable.STYLE_MARKDOWN)
   table.maxwidht = 25
   table.precision = 8
   table.columns.header = ['Pos','Symbol','Long/\nShort','Stop \nPrice','Entry \nPrice','Type','Quantity','Order \nID','Close \nPosition']
   table.columns.header.alignment = BeautifulTable.ALIGN_CENTER
   table.columns.alignment['Quantity'] = BeautifulTable.ALIGN_RIGHT
   table.columns.alignment['Symbol'] = BeautifulTable.ALIGN_RIGHT
   table.columns.width = [5,10,10,10,10,20,15,15,10]
   nr = 1
   for item in futures_open: 
    close_p = item['closePosition']
    close_po = ''
    if close_p == True:
     close_po = 'Yes'
    if close_p == False:
     close_po = 'No'
    symb = str(item['symbol'])
    side = str(item['side'])
    stop_p = float(item['stopPrice'])
    # stop_pr = str(stop_p)
    # stop_pm = "{0:10.8f}"
    # stop_prr = str(format(stop_pr, '<010'))
    price_e = float(item['price'])
    typ = str(item['type'])
    qty = float(item['origQty'])
    oid = int(item['orderId'])
    table.rows.append([ nr , symb , side , stop_p , "%.8f" % price_e , typ , "%.8f" % qty , oid , close_po])
    nr += 1
   nrr = nr-1
   print( 'Open Orders found:' , nrr , '\n' )
   print( table , '\n' )
  if not futures_open: 
   print('No open Future Orders found for:' , arg , '\n' )
 except BinanceAPIException:
  print( 'Not available for Futures:' , arg , '\n')
 # Error handling is not yet correct ?
 finally:
  # print('finally!!!')
  print()


def history_order(arg):
 client = Client(api_key, api_secret)
 print( '\n' , '--- History Order ---' , '\n' )
 # get historical margin order and print if found
 try:
  margin_trades_iso = client.get_margin_trades(symbol=arg , limit=20 , isIsolated='TRUE' )
  margin_trades_cross = client.get_margin_trades(symbol=arg , limit=20 , isIsolated='FALSE' )
  if not margin_trades_iso and margin_trades_cross: 
   print ('No History for:' , arg , '\n' )
  if margin_trades_iso or margin_trades_cross:
   # Margin Isolated
   mi_table = BeautifulTable()
   mi_table.clear(True)
   mi_table.set_style(BeautifulTable.STYLE_MARKDOWN)
   mi_table.maxwidht = 30
   mi_table.precision = 8
   mi_table.columns.header = [ 'Pos' , 'Asset Name' , 'Price' , 'Quantity' , 'Order ID' , 'Time' ]
   mi_table.columns.width = [5,15,20,15,15,30]
   nr = 1
   for item in margin_trades_iso:
    d_time_a = item['time'] / 1000
    d_time_b = datetime.fromtimestamp((item['time'])/1000)
    d_time_c = d_time_b.strftime('%d. %b %Y %H:%M:%S')
    d_time = datetime.fromtimestamp(d_time_a)
    mi_table.rows.append([ nr , item['symbol'] , "%.8f" % float(item['price']) , "%.8f" % float(item['qty']) , item['orderId'] , d_time_c ])
    nr += 1
   with warnings.catch_warnings():
    warnings.filterwarnings("ignore") 
    try:
     mi_table.sort('Time', True)
    finally:
     print(mi_table , '\n' )
   # Margin Cross
   mc_table = BeautifulTable()
   mc_table.clear(True)
   mc_table.set_style(BeautifulTable.STYLE_MARKDOWN)
   mc_table.maxwidht = 30
   mc_table.precision = 8
   mc_table.columns.header = [ 'Pos' , 'Asset Name' , 'Price' , 'Quantity' , 'Order ID' , 'Time' ]
   mc_table.columns.width = [5,15,20,15,15,30]
   nr = 1
   for item in margin_trades_cross:
    d_time_a = item['time'] / 1000
    d_time_b = datetime.fromtimestamp((item['time'])/1000)
    d_time_c = d_time_b.strftime('%d. %b %Y %H:%M:%S')
    d_time = datetime.fromtimestamp(d_time_a)
    mi_table.rows.append([ nr , item['symbol'] , "%.8f" % float(item['price']) , "%.8f" % float(item['qty']) , item['orderId'] , d_time_c ])
    nr += 1
   with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    try:
     mc_table.sort('Time', True)
    finally:
     print(mc_table , '\n' )
 except BinanceAPIException:
  print ( '- No Margin Orders found for:' , arg , '-' , '\n' )
 
def replace_order():
 print('under construction')
 '''
 get all orders from arg
  ask user for specific trade
 check its stop price
  modify stop price 

 orders = client.get_open_orders(symbol=arg)
 print (orders)
 print(type(orders)) 
 
 table = BeautifulTable()
 table.set_style(BeautifulTable.STYLE_MARKDOWN)
 table.columns.header = ['Symbol','Price','Stop Price','Type','Quantity','Order ID']
 for item in orders:
  table.rows.append([item[key_a] ,"%.8f" % float(item[key_c]),item[key_d],item[key_e],item[key_f],item[key_b]])
  print(table,'\n')
'''

def get_USDT_price():
 
 return usdt_price

def test_order(arg):
 client = Client(api_key, api_secret)
 orders_a = client.futures_get_open_orders()
 print(orders_a)
 # futures_get_order()
 # futures_position_information()
# futures_recent_trades(**params)
# futures_time() '''check time with server''' 


if __name__ == "__main__":
 main(sys.argv[1:])


'''
To do:
---
 -w option: 
  Print Total [all symbols (Spot && Futures)]
   formatted in table with color?
  
'''


'''
 ###

   # print(datetime.datetime.fromtimestamp(1518308894652/1000))
   # print(trades)
   # print('Trade with ID 993...8 : ' , trades['id' == '993996378'])
   # trades_b = trades['id' == '993996378']
   # filter out price value
   # trades_c = float(trades_b['price'])
   # print('Last trade value was = ' , trades_c)
   # find all assets that have any value
   
   
    # for all_assets do: get open orders 
 # margin_all_assets = client.get_all_isolated_margin_symbols()
 # margin_all_assets_symbol = []
 # for m in margin_all_assets:
  # margin_all_assets_symbol.append(m['symbol'])
 '''
