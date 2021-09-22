#!/usr/bin/env python
import time , sys , os
from datetime import datetime
os.system('color')
import math
import warnings
import argparse
sys.path.append('.')
from config import *
from binance import ThreadedWebsocketManager
from binance import BinanceSocketManager
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from beautifultable import BeautifulTable
from termcolor import colored

def main(arg):
 try:
  # load client
  global client 
  client = Client(api_key, api_secret)
  # initialise and start the Websocket
  parser = argparse.ArgumentParser(description='Binance Crypto-Trading Helper/Handler')
  parser.add_argument( '-s' , '--symbol' , type=str , help='Specify Symbol to check by replacing SYMBOL by BTCUSDT or other Coin')
  parser.add_argument( '-w' , '--wallet' , type=str , help='Show Wallet' )
  parser.add_argument( '-o' , '--orders' , type=str , help='Show open Orders for Symbol' )
  parser.add_argument( '-p' , '--pilz' , type=str , help='Ich hasse Pizza mit Pilzen!' )
  arg = parser.parse_args()
 finally:
  try:
   print('========================================================================','\n')
   if arg.orders:
    a , c = '' , ''
    for a in arg.orders:
     b = a.upper()
     c = c + b
    arg.orders = c
    get_open_order(arg.orders)
   if arg.symbol:
    a , c = '' , ''
    for a in arg.symbol:
     b = a.upper()
     c = c + b
    arg.symbol = c
    symbol_option(arg.symbol)
   if arg.wallet:
    wallet_option()
   if arg.pilz:
    if arg.pilz == 'Rene' :
     print( '\n' , 'Och nee,' , arg.pilz , '!' )
    if arg.pilz == 'René' :
     print( '\n' , 'Ik han pilt,' , arg.pilz , '!' )
    if arg.pilz != 'René' and arg.pilz != 'Rene' :
     print( '\n' , arg.pilz , ', Ik han Pilt?' )
  except BinanceAPIException as bai:
   print ( bai )
 print('========================================================================','\n')

def symbol_option(arg):
 if arg.isalpha():
  quote_typed = arg[-3]
  quote_typed = quote_typed + arg[-2]
  quote_typed = quote_typed + arg[-1]
  try:
   # show Symbol Info
   # get Symbol & variation name
   symbol_info = client.get_symbol_info(arg)
   symbol_a = symbol_info['quoteAsset'] # get asset name (USDT/BTC/BUSD...)
   symbol_b = symbol_info['status'] # get trading status
   arg_symbol = arg.replace( symbol_a , '' ) # get coin name (ADA/BTC/XRP/...)
   trades = client.get_recent_trades(symbol=arg)
   print ( '--------------------------------- Time ---------------------------------' , '\n' )
   current_time = time.strftime( '%d/%m/%Y, %H:%M:%S' )
   time_s = client.get_server_time()
   time_r = time_s['serverTime']
   time_d = datetime.fromtimestamp( time_r / 1000 )
   server_time = time_d.strftime( '%d/%m/%Y, %H:%M:%S' )
   print( 'Your current Local Time is ' , current_time )
   print( 'Your current Server Time is' , server_time , '\n' )
   # get Wallet balance
   asset_balance = client.get_asset_balance(asset=arg_symbol)
   arg_symbol = arg.replace( symbol_a , '' )
   trades = client.get_recent_trades(symbol=arg)
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
   print( '------------------------------ Symbol Info -----------------------------' , '\n' )
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
   print( '------------------------------ Live Price ------------------------------' , '\n' )
   print( '1' , arg_symbol , ' = ' , '%.8f' % price_a , symbol_a )
   print( '1' , symbol_a , ' = ' , '%.8f' % price_b , arg_symbol , '\n' )
   ###
   # print Asset Wallet Spot
   print( '-------------------------- Asset Wallet: Spot --------------------------' , '\n' )
   print( '-- in' , arg_symbol , '--' )
   print( 'Free Wallet   = ' , '%.8f' % free_balance_float , arg_symbol )
   print( 'Locked Wallet = ' , '%.8f' % locked_balance_float , arg_symbol )
   print ( 'Total Wallet  = ', '%.8f' % total_wallet_rounded , arg_symbol )
   print( '\n' , '-- in' , symbol_a , '--' )
   print( 'You have' , '%.8f' % quote_value_a , symbol_a , 'available' , '(as' , arg_symbol , '\b)' )
   print( 'You have' , '%.8f' % quote_value_l , symbol_a , 'locked' , '(as' , arg_symbol , '\b)' )
   print( 'You have' , '%.8f' % quote_value_t , symbol_a , 'total' , '(as' , arg_symbol , '\b)' )
   ###
   print()
  except TypeError:
   print( '-Please verify Argument-' , '\n' )
   print( 'Symbol Type Error:' , arg , '\n' )
   while quote_typed == 'USD':
    print('-USD is not supported by Binance-' , '\n' )
    break
  except BinanceAPIException:
   print( '-Please verify Argument-' , '\n' )
   print( '-Invalid Symbol used:' , arg , '\b-\n' )
 else:
  print('------------------------------------------------------------------------','\n')
  print( '-Only alphabetic Letters allowed-' )
  print( '-Please verify Argument-' , '\n' )
  print( 'wrong Argument:' , arg , '\n' )
  print('------------------------------------------------------------------------','\n')

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
 print( '--- Spot Wallet - Balance ---' , '\n' )
 s_table = BeautifulTable()
 s_table.clear(True)
 s_table.set_style(BeautifulTable.STYLE_MARKDOWN)
 s_table.maxwidht = 25
 s_table.precision = 8
 s_table.columns.header = ['Asset Name' , 'Balance free' , 'Balance locked']
 s_table.columns.width = [17,29,29]
 for a in spot_free:
  s_table.rows.append([ a['asset'] , '%.8f' % float(a['free']) , '%.8f' % float(a['locked']) ])
 with warnings.catch_warnings():
  warnings.filterwarnings('ignore')
  try:
   s_table.sort( 'Balance free' , True )
  finally:
   print( s_table , '\n' )
   # print('Es fehlt ein TOTAL als USDT' , '\n' , '!aber! die Werte werden nicht in USDT umgerechnet, daher muss ich den Preis ziehen und selbst umrechnen')
 ###
 # print Futures Wallet
 print( '\n' , '--- Futures Wallet - Balance ---' , '\n' )
 futures_balance = client.futures_account_balance()
 f_table = BeautifulTable()
 f_table.clear(True)
 f_table.set_style(BeautifulTable.STYLE_MARKDOWN)
 f_table.maxwidht = 25
 f_table.precision = 8
 f_table.columns.header = ['Asset Name' , 'Balance' , 'Balance withdrawable']
 f_table.columns.width = [17,29,29]
 for a in futures_balance:
  f_table.rows.append([a['asset'] , '%.8f' % float(a['balance']) , '%.8f' % float(a['withdrawAvailable']) ])
 with warnings.catch_warnings():
  warnings.filterwarnings( 'ignore' )
  try:
   f_table.sort( 'Balance' , True)
  finally:
   print( f_table , '\n' )

def get_open_order(arg):
 if arg.isalpha():
  print( '--- All Open Orders for' , arg , '---'  , '\n' )
  # get open Margin Order
  print ( '-- Cross Margin --' , '\n' )
  try:
   margin_cross_order_open = client.get_open_margin_orders( symbol=arg , limit=10 , isIsolated='FALSE' )
   if margin_cross_order_open: 
    print( 'Cross Orders:' , margin_cross_order_open )
   if not margin_cross_order_open: 
    print ( colored( 'No open Orders found for Cross Margin:' , 'yellow' ) , arg , '\n' )
  except BinanceAPIException:
   print ( colored( 'not available for Cross Margin:' , 'red' ) , arg , '\n' )
  print ( '-- Isolated Margin --' , '\n' )
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
     table.rows.append([ nr , item['symbol'] , item['side'], '%.8f' % float(item['stopPrice']),item['type'], '%.8f' % float(item['origQty']),item['orderId']])
     nr += 1
    nrr = nr-1
    print( colored( 'Open Orders found:' , 'yellow' ) , nrr , '\n' )
    print( table , '\n' )  
   if not margin_iso_order_open: 
    print ( colored( 'No open Orders found for Isolated Margin:' , 'yellow' ) , arg , '\n' )
  except BinanceAPIException:
   print ( colored( 'Not available for Isolated Margin:' , 'red' ) , arg , '\n' )
  print ( '-- Spot Market--' , '\n' )
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
    print( colored( 'Open Orders found:' , 'green' ) , nrr  , '\n' )
    print( table , '\n' )
   if not open_spot_order: 
    print ( colored( 'No open Orders found for Spot:' , 'yellow' ) , arg , '\n' )
  except BinanceAPIException:
    print ( colored( 'Not available for Spot' , 'red' ) , arg , '\n' )
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
     # stop_pm = '{0:10.8f}'
     # stop_prr = str(format(stop_pr, '<010'))
     price_e = float(item['price'])
     typ = str(item['type'])
     qty = float(item['origQty'])
     oid = int(item['orderId'])
     table.rows.append([ nr , symb , side , stop_p , '%.8f' % price_e , typ , '%.8f' % qty , oid , close_po])
     nr += 1
    nrr = nr-1
    print( colored( 'Open Orders found:' , 'green' ) , nrr , '\n' )
    print( table , '\n' )
   if not futures_open: 
    print( colored( 'No open Orders found for Future:' , 'yellow' ) , arg , '\n' )
  except BinanceAPIException:
   print( colored( 'Not available for Futures:' , 'red' ) , arg , '\n')
  # Error handling is not yet correct ?
  except TypeError:
   print( '-Please verify Argument-' , '\n' )
   print( 'Symbol Type Error:' , arg , '\n' )
   while quote_typed == 'USD':
    print('-USD is not supported by Binance-' , '\n' )
    break
  except BinanceAPIException:
   print( '-Please verify Argument-' , '\n' )
   print( '-Invalid Symbol used:' , arg , '\b-\n' )
 else:
  print('------------------------------------------------------------------------','\n')
  print( '-Only alphabetic Letters allowed-' )
  print( '-Please verify Argument-' , '\n' )
  print( 'wrong Argument:' , arg , '\n' )
  print('------------------------------------------------------------------------','\n')
  print('------------------------------------------------------------------------','\n')
  # print('finally!!!')
  print()

if __name__ == '__main__':
 main(sys.argv[1:])
 