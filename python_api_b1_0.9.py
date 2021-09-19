#!/usr/bin/env python
import sys , os , time
from datetime import datetime
os.system( 'color' )
import math
import warnings
import argparse
import itertools
import traceback
import importlib
from config_w import *
from margin_w import *
from binance import ThreadedWebsocketManager
from binance import BinanceSocketManager
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from beautifultable import BeautifulTable
from termcolor import colored

client = Client( api_key , api_secret )

sl_hit = False #activates Trail Stop
trail_on = False #tells if trail was hit
trail_on_once = False #tells if trail was hit once
time_trigger_activated = False
is_first_run = True

symbol_true = False
wallet_true = False
orders_true = False
i_true = False
t_true = False
r_true = False

def main( arg ):
 parser = argparse.ArgumentParser( description='Binance Trailing S/L' )
 parser.add_argument( '-t' , '--trail' , type=str , help='Trailing value' )
 parser.add_argument( '-o' , '--orders' , type=str , help='Show open Orders for Symbol' )
 parser.add_argument( '-w' , '--wallet' , help='Show Wallet' , action='store_true')
 parser.add_argument( '-p' , '--pilz' , type=str , help='Ich hasse Pizza mit Pilzen!' )
 parser.add_argument( '-s' , '--symbol' , type=str , help='Specify Symbol to check by replacing SYMBOL by BTCUSDT or other Coin')
 arg = parser.parse_args()
 print(arg.wallet)
 try:
  if arg.trail: arg_symbol = arg.trail
  elif arg.orders: arg_symbol = arg.orders
  elif arg.wallet: arg_symbol = 'not specified'
  
  h_table = BeautifulTable()
  h_table.clear( True )
  h_table.set_style( BeautifulTable.STYLE_DOTTED )
  h_table.width = 100
  h_table.columns.alignment = BeautifulTable.ALIGN_CENTER
  
  h_table.rows.append ([ colored( 'No warranty taken at all! - Use at own Risk!' , 'red' )])
  h_table.rows.append ([''])
  h_table.columns.padding_left = 16
  h_table.columns.padding_right = 16
  h_table.rows.append ([ 'Please verify your Settings:' ])
  print( h_table , '\n' )
  
  sa_table = BeautifulTable()
  sa_table.clear( True )
  sa_table.set_style( BeautifulTable.STYLE_RST )
  sa_table.columns.header = [ 'Description' , 'Value' , 'Comment' ]
  sa_table.columns.header.alignment = BeautifulTable.ALIGN_CENTER
  sa_table.columns.alignment['Description'] = BeautifulTable.ALIGN_RIGHT
  sa_table.columns.alignment['Value'] = BeautifulTable.ALIGN_RIGHT
  sa_table.columns.alignment['Comment'] = BeautifulTable.ALIGN_CENTER

  sa_table.rows.append ([ 'Symbol:' , arg_symbol , '(Not needed to show wallets [-w])' ])
  sa_table.rows.append ([ 'Activate Price Trigger:' , price_trigger_on , '(0 = Always active)' ])
  sa_table.rows.append ([ 'Close Price Trigger:' , price_trigger_cl , '' ])
  sa_table.rows.append ([ 'Emergency Price Trigger:' , price_trigger_sl , '(0 = Disabled)' ])
  sa_table.rows.append ([ 'Order Limit Price:' , price , '(Only needed for LIMIT Order)' ])
  sa_table.rows.append ([ 'Amount:' , quantity , '' ])
  sa_table.rows.append ([ 'Order Type:' , sell_type , '(Uses MARKET or LIMIT)' ])
  sa_table.rows.append ([ 'SELL:' , side , '(Only SELL available, yet)' ])
  sa_table.rows.append ([ 'LONG/SHORT:' , direction_type , '' ])
  print(sa_table,'\n')
  
  sb_table = BeautifulTable()
  sb_table.clear( True )
  sb_table.set_style( BeautifulTable.STYLE_COMPACT )
  sb_table.columns.alignment = BeautifulTable.ALIGN_CENTER
  
  sb_table.rows.append ([ 'There is no user interaction asked, needed and possible beyond this point!' ]) 
  sb_table.rows.append ([ 'A Sell Order will be placed automatically (when Trigger Price is reached).' ])
  sb_table.rows.append ([ colored( 'On Error, the program will NOT place an Order.' , 'green' ) ])
  sb_table.rows.append ([ colored( 'Press CTRL+C to abort the program, at any time.' , 'blue' ) ])
  sb_table.rows.append ([ '(Hit multiple Times in a Row to be sure.)' ])
  sb_table.rows.append ([ colored( 'If you continue, you ackknowledge that you understand and accept the potential dangers and have been warned.' , 'red' ) ])
  sb_table.rows.append ([ '- No warranty taken at all! - Use at own Risk! -' ])
  sb_table.rows.append ([ 'Please answer with y or yes to continue (all other will abort)' ])
  print(sb_table,'\n')
  
  answer = input( str( 'Do you want to continue? ( y / n / hit Enter = no )' )  or 'n' ).lower()
  print()
  if not answer:
   answer = 'n'
  if answer == 'y' or answer == 'yes' :
   pass
  else:
   print ( '------------------------------------------------------------------------' )
   print ( '\n' , '- Always verify your settings before running the program -' )
   print ( ' - You MUST answer with "y" or "yes" to use the program -' , '\n' )
   sys.exit ( 'exiting... \n\n------------------------------------------------------------------------' ) 
 except Exception as exc:
  print ( 'Error:' , exc )
  sys.exit ( 'exiting...' )
 try:
  print ( '------------------------------------------------------------------------' , '\n' )
  if arg.trail:
   if arg.trail.isalpha():
    a , c = '' , ''
    for a in arg.trail:
     b = a.upper()
     c = c + b
    arg.trail = c
    try:
     check_order( loop_cl , arg.trail )
     if sl_hit == True:
      sell_order ( arg.trail )
      sys.exit( 'SELL is placed: exiting...' )
     if sl_hit == False:
      main( sys.argv[1:] )
    except Exception as ex:
     print ( 'Exception:' , ex )
     print ( 'Exception happened in here' )
     countdown(30)
   else: #if arg is not alpha
    print( '------------------------------------------------------------------------' , '\n' )
    print( '-Only alphabetic Letters allowed-' )
    print( '-Only alphabetic Letters allowed-' )
    print( '-Please verify Argument-' , '\n' )
    print( 'wrong Argument:' , arg.trail , '\n' )
    sys.exit( 'exiting...' )
  elif arg.orders:
   if arg.orders.isalpha():
    print( '------------------------------------------------------------------------' , '\n' )
    a , c = '' , ''
    for a in arg.orders:
     b = a.upper()
     c = c + b
    arg.orders = c
    try:
     open_order( arg.orders )
    except BinanceAPIException as be:
     print ( 'Exception:' , be )
    except Exception as ex:
     print ( 'Exception:' , ex )
     sys.exit( 'exiting...' )
   else: #if arg is not alpha
    print( '------------------------------------------------------------------------' , '\n' )
    print( '-Only alphabetic Letters allowed-' )
    print( '-Only alphabetic Letters allowed-' )
    print( '-Please verify Argument-' , '\n' )
    print( 'wrong Argument:' , arg.orders , '\n' )
    sys.exit( 'exiting...' )
  elif arg.wallet:
   print( '------------------------------------------------------------------------' , '\n' )
   try:
    show_wallet()
    # margin = filter_margin_symbol()
    # print ( 'margin:' , margin )
    print()
   except BinanceAPIException as be:
    print ( 'Exception:' , be )
   except Exception as ex:
    print ( 'Exception:' , ex )
    sys.exit( 'exiting...' )
  print()
 except Exception as ex:
  print( 'Exception:' , ex )
  sys.exit( 'exiting...' )
 print( '------------------------------------------------------------------------' , '\n' )
 print( '------------------------------------------------------------------------' , '\n' )

def open_order( arg ):
  print( '\n' , '--- All Open Orders for' , arg , '---'  , '\n' )
  # get open Margin Order
  print ('-- Cross Margin --' , '\n' )
  try:
   margin_cross_order_open = client.get_open_margin_orders( symbol=arg , limit=10 , isIsolated='FALSE' )
   if margin_cross_order_open: 
    print( 'Cross Orders:' , margin_cross_order_open )
   if not margin_cross_order_open: 
    print ( colored('No open Orders found for Cross Margin:' , 'yellow' ) , arg , '\n' )
  except BinanceAPIException:
   print ( colored('not available for Cross Margin:' , 'red' ) , arg , '\n' )
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
     table.rows.append([ nr , item['symbol'] , item['side'], '%.8f' % float(item['stopPrice']),item['type'], '%.8f' % float(item['origQty']),item['orderId']])
     nr += 1
    nrr = nr-1
    print( colored('Open Orders found:' , 'yellow' ) , nrr , '\n' )
    print( table , '\n' )  
   if not margin_iso_order_open: 
    print ( colored('No open Orders found for Isolated Margin:' , 'yellow' ) , arg , '\n' )
  except BinanceAPIException:
   print ( colored('Not available for Isolated Margin:' , 'red' ) , arg , '\n' )
  print ('-- Spot Market--' , '\n' )
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

def check_order( loop_cl , arg ):
 global trail_on
 global trail_on_once
 loop = 1 #starting value / dont change
 loop_total = 1 #starting value / dont change
 trail_stopPrice = price_trigger_cl
 if loop_cl == 0:
  loop_cl = math.inf
 while loop_total <= loop_cl:
  print( '------------------------------------------------------------------------' , '\n' )
  print( '-> Order verification activated:' , 'Check' , loop_total , '/' , loop_cl , '\n' )
  print( '// Timeframe:' , time_interval , '//' , 'Symbol:' , arg , '//' ) 
  print( '  ---------------  -----------------' , '\n' )
  print( 'Close Price Trigger:       ' , '%.8f' % float( price_trigger_cl ))
  print( 'Activate Price Trigger:    ' , '%.8f' % float( price_trigger_on ))
  if price_trigger_sl <= 0:
   print( 'Emergency Price Trigger:' , '    Not used' , '\n' )
  if price_trigger_sl > 0:
   print( 'Emergency Price Trigger:   ' , '%.8f' % float( price_trigger_sl ) , '\n' )
  try:
   result = check_klines( arg )
   if trail_on == False:
    try:
     close_price_now = result['close_price_now']
     if direction_type == 'LONG':
      trail_activated = activate_trail_long( close_price_now , arg )
     if direction_type == 'SHORT':
      trail_activated = activate_trail_short( close_price_now , arg )
     if trail_activated == False:
      if trail_on_once == False:
       countdown(time_sleep_cl_on)
     if trail_activated == True:
      if trail_on_once == False:
       trail_on_once_time = datetime.now()
       trail_on_once_time = trail_on_once_time.strftime( '%H:%M:%S on %d/%m/%Y' )
       print( colored( '- Trigger has been activated -' , 'green' ) , '@' , trail_on_once_time , '\n' )
       trail_on_once = True
       trail_on = True
      if trail_on_once == True:
       pass
    except Exception as ex:
     print ( 'Exception:' , Exception )
     print ( 'Error:' , ex )
   if trail_on == True:
    print( colored('- Trigger is activated -' , 'green' ) , '@' , trail_on_once_time , '\n' )
    result_loop = loopie_loop( arg , trail_stopPrice , result , loop )
    if result_loop == False:
     break
    if result_loop == True:
     countdown( time_sleep_cl )
     continue
  except KeyboardInterrupt as ek:
   print ( 'Operation got stopped by user' )
   break
  except ValueError as ev:
   print ( 'SL_Trigger_Hit:' , ev )
   break
  finally:
   loop_total += 1

def loopie_loop( arg , trail_stopPrice , result , loop=1 ):
 importlib.reload(margin)
 global sl_hit
 global time_trigger_activated
 try:
  close_price = result['close_price_last']
  if float(close_price) >= float( price_trigger_cl ):
   if time_trigger_activated == True:
    time_trigger = datetime.now()
    time_trigger = time_now.strftime( '%H:%M:%S on %d/%m/%Y' )
    print( colored('- Trade OK -' , 'green' ) , 'since' , time_trigger , '\n' )
    time_trigger_activated = False
  if float( close_price ) < float( price_trigger_cl ):
   now = datetime.now()
   now = now.strftime( '%H:%M:%S on %d/%m/%Y' )
   print( colored('- Trigger is lower than Stop Price -' , 'red' ) , '\n' )
   print( colored( '-> Trade closed' , 'red' ) , '@' , now , '//' , 'S/L hit:' , '%.8f' % float( price_trigger_cl ) , '\n' )
   sl_hit = True
   raise ValueError( 'S/L triggered' )
  if price_trigger_sl != 0:
   while loop <= loop_sl:
    loop_loopwalker (arg)
    loop += 1
  if price_trigger_sl == 0:
   print( colored( 'S/L Trigger skipped' , 'blue' ) )
  print()
  print( '------------------------------------------------------------------------' )
  print( '------------------------------------------------------------------------' , '\n' )
  return True
 except KeyboardInterrupt as ek:
  print ( 'Operation stopped by user' )
  sys.exit('exiting...') 
 except ValueError as ev:
  print ('S/L Trigger triggered:' , ev , '\n' )
  return False
 except TypeError as et:
  print ( 'invalid argument:' , et , '\n' )
  sys.exit('exiting...') 

def loop_loopwalker( arg ):
 list_of_tickers = client.get_symbol_ticker( symbol=arg )
 prev_symbolPrice = round( float( list_of_tickers['price'] ) , 8 )
 curr_time = time.strftime( '%H:%M:%S on %d/%m/%Y' )
 while True:
  trail_stopPrice = float( prev_symbolPrice ) - ( float( prev_symbolPrice ) * float( trail ) )
  break
 curr_symbolPrice = check_price( arg , prev_symbolPrice , curr_time , trail_stopPrice )
 print( 'curr_symbolPrice before:' , float( curr_symbolPrice ))
 if curr_symbolPrice < price_trigger_on: 
  print ( 'Minumum Price not yet reached...' )
 if curr_symbolPrice > price_trigger_on:
  if curr_symbolPrice < trail_stopPrice:
   print( colored( 'Trailing S/L hit at' , 'red' ) , '\b:' , current_time )
 if curr_symbolPrice <= prev_symbolPrice:
  pass
 if curr_symbolPrice > prev_symbolPrice:
  trail_stopPrice = float( curr_symbolPrice ) - ( float( curr_symbolPrice ) * float( trail ) )
  print( 'curr_symbolPrice after:' , '%.8f' % float( curr_symbolPrice ) , ', trail_stopPrice:' , '%.8f' % float( trail_stopPrice )) 
 print( 'last ts:' , trail_stopPrice )

def countdown( count ): #waits time and prints a countdown
 for remaining in range( count, 0, -1 ):
  sys.stdout.write( '\r' )
  sys.stdout.write( '-> Waiting {:2d} seconds'.format( remaining ))
  sys.stdout.flush()
  time.sleep( 1 )
 print( '\n' )

def activate_trail_long( close_price , arg ): #checks if T/S should be activated for LONG Trades
 if float( close_price ) > float( price_trigger_on ):
  print( colored('- Trail Trigger Price reached -' , 'red' ) )
  print( colored('- Trail Trigger Price reached -' , 'yellow' ) )
  print( colored('- Trail Trigger Price reached -' , 'blue' ) , '\n' )
  return True
 if float( close_price ) <= float( price_trigger_on ): 
  price = get_price_difference( arg )
  price_value = round( price[1] , 8 )
  price_perc = round( price[2] , 8 )
  print ( colored( '- Trail Trigger Price not yet reached -' , 'yellow' ) )
  print ( 'Difference to Activation Price:' , price_value , '=> %.3f%%' % price_perc , '\n' )
  return False

def activate_trail_short( close_price , arg ): #checks if T/S should be activated for SHORT Trades
 if float( close_price ) < float( price_trigger_on ):
  print( colored('- Trail Trigger Price reached -' , 'red' ) )
  print( colored('- Trail Trigger Price reached -' , 'yellow' ) )
  print( colored('- Trail Trigger Price reached -' , 'blue' ) , '\n' )
  return True
 if float( close_price ) >= float( price_trigger_on ):
  price = get_price_difference( arg )
  price_value = round( price[1] , 8 )
  price_perc = round( price[2] , 8 )
  print ( colored( '- Trail Trigger Price not yet reached -' , 'yellow' ) )
  print ( 'Difference to Activation Price:' , price_value , '=> %.3f%%' % price_perc , '\n' )
  return False

def check_klines( arg ): #gets last klines data (candel data)
 try:
  klines = client.get_klines( symbol=arg , interval=time_interval , limit = 3)
  klines_a = klines[0]
  close_time_a = klines_a[6] / 1000
  close_time_a = datetime.fromtimestamp( close_time_a )
  close_time_a = close_time_a.strftime( '%H:%M:%S on %d/%m/%Y' )
  close_price_a = klines_a[4]
  klines_b = klines[1]
  close_time_b = klines_b[6] / 1000
  close_time_b = datetime.fromtimestamp( close_time_b )
  close_time_b = close_time_b.strftime( '%H:%M:%S on %d/%m/%Y' )
  close_price_b = klines_b[4]
  klines_c = klines[2]
  close_time_c = klines_c[6] / 1000
  close_time_c = datetime.fromtimestamp( close_time_c )
  close_time_c = close_time_c.strftime( '%H:%M:%S on %d/%m/%Y' )
  close_price_c = klines_c[4]
  result = dict()
  result['close_price_prev'] = close_price_a
  result['close_time_prev'] = close_time_a
  result['close_price_last'] = close_price_b
  result['close_time_last'] = close_time_b
  result['close_price_now'] = close_price_c
  result['close_time_now'] = close_time_c
  print ( 'Previous Close:  ' , close_price_a , '@ Close Time:' , close_time_a )
  if close_price_b > close_price_a:
   print ( colored( 'Last Close Price:' ,'green' ) , close_price_b , '@ Close Time:' , close_time_b )
  if close_price_b < close_price_a:
   print ( colored( 'Last Close Price:' ,'red' ) , close_price_b , '@ Close Time:' , close_time_b )
  if close_price_b == close_price_a:
   print ( colored( 'Last Close Price:' ,'white' ) , close_price_b , '@ Close Time:' , close_time_b )
  if close_price_c > close_price_b:
   print ( colored( 'Current Price:   ' ,'green' ) , close_price_c , '@ Close Time:' , close_time_c )
  if close_price_c < close_price_b:
   print ( colored( 'Current Price:   ' ,'red' ) , close_price_c , '@ Close Time:' , close_time_c )
  if close_price_c == close_price_b:
   print ( colored( 'Current Price:   ' ,'white' ) , close_price_c , '@ Close Time:' , close_time_c )
  print()
  return ( result )
 except BinanceAPIException as eb:
  print ( 'Wrong Time interval used:' , time_interval )
  print ( '- Time_interval could be wrong -' )
  print ( 'Error:' , eb )
  sys.exit('invalid argument used')

def check_price( arg , prev_symbolPrice , curr_time , trail_stopPrice ): #prints price for Trailing Stop
 try:
  print()
  countdown( time_sleep_sl )
  list_of_tickers = client.get_symbol_ticker( symbol=arg )
  curr_symbolPrice = round( float( list_of_tickers['price'] ) , 8 )
  current_time = time.strftime( '%H:%M:%S on %d/%m/%Y' )
  price_difference = float( curr_symbolPrice ) - float( prev_symbolPrice )
  if not trail_stopPrice:
   trail_stopPrice = float( prev_symbolPrice ) - ( float( prev_symbolPrice ) * float( trail ) )
  price_difference_trail = float( curr_symbolPrice ) - float( trail_stopPrice )
  price_difference_trail_perc = (1.0 - ( trail_stopPrice / curr_symbolPrice )) * 100
  price_difference_trail_perc = round( float( price_difference_trail_perc ) , 5 )
  price_difference_perc = ( price_difference / prev_symbolPrice )
  price_difference_perc = round( float( price_difference_perc ) , 5 )
  print( '   Last Price:' , '%.8f' % float( prev_symbolPrice ) , '@' , curr_time )
  print( 'Current Price:' , '%.8f' % float( curr_symbolPrice ) , '@' , current_time )
  print( 'Trail Trigger:' , '%.8f' % float( trail_stopPrice ) )
  if price_difference < 0:
   print( 'Difference to Trail Stop: ' , '%.8f' % float( price_difference_trail ) , '=> %.3f%%' % price_difference_trail_perc )
   print( colored( 'Difference to last Price:' ,'magenta' ) , '%.8f' % float( price_difference ) , colored( 'down' ,'magenta' ) , '=> %.3f%%' % price_difference_perc )
  if price_difference > 0:
   print( 'Difference to Trail Stop: ' , '%.8f' % float( price_difference_trail ) , '=> %.3f%%' % price_difference_trail_perc )
   print( colored( 'Difference to last Price:' ,'yellow' ) , '%.8f' % float( price_difference ) , colored( 'up' ,'yellow' ) , '=> %.3f%%' % price_difference_perc )
  if price_difference == 0:
   print( 'Difference to Trail Stop: ' , '%.8f' % float( price_difference_trail ) , '=> %.3f%%' % price_difference_trail_perc )
   print( colored( 'Difference to last Price:' ,'cyan' ) , '%.8f' % float( price_difference ) , '(same Price)' )
 except Exception as ee:
  print( 'exception occured:' , e )
 finally:
  return curr_symbolPrice

def get_price_difference( arg ): #compares price for Trailing Stop // gets a list
 list_of_tickers = client.get_symbol_ticker( symbol=arg )
 curr_symbolPrice = round( float( list_of_tickers['price'] ) , 8 )
 price_difference = float( price_trigger_on ) - float( curr_symbolPrice )
 price_difference_perc = ( 1.0 - ( curr_symbolPrice / price_trigger_on ) )
 price_difference_perc = round( float( price_difference_perc ) , 5 )
 price = dict()
 price[1] = price_difference
 price[2] = price_difference_perc
 return price

def sell_order( arg ): #places a SELL Order
 if sell_amount == 'quarter':
  pass
 if sell_amount == 'third':
  pass
 if sell_amount == 'half':
  pass
 if sell_amount == 'all':
  pass
 if sell_type == 'MARKET':
  try:
   print ( 'A Market Sell Order will be placed now...' , '\n' )
   print ( 'Symbol:     ' , arg )
   print ( 'Order Price: ' , price )
   print ( 'Amount:     ' , quantity )
   print ( 'Order Type: ' , sell_type )
   print ( 'BUY/SELL:   ' , side )
   order = client.create_test_order( symbol=arg , side=side , type=sell_type , quantity=quantity )
  except BinanceAPIException as ba:
   print ( 'Binance API Error:' , ba )
  except BinanceOrderMinTotalException as bo:
   print ( 'Binance API Error:' , bo )
  print ( '\n' , 'Order placed:' , order )
  pass
 if sell_type == 'LIMIT':
  try:
   print ( 'A Limit Sell Order will be placed now...' , '\n' )
   print ( 'Symbol:     ' , arg )
   print ( 'Order Price: ' , price )
   print ( 'Amount:     ' , quantity )
   print ( 'Order Type: ' , sell_type )
   print ( 'BUY/SELL:   ' , side )
   pass
  except BinanceAPIException as ba:
   print ( 'Binance API Error:' , ba )
  except BinanceOrderMinTotalException as bo:
   print ( 'Binance API Error:' , bo )
  print ( '\n' , 'Order placed:' , order )
 
def show_wallet(): #prints a list of each asset in wallet (for Spot, Futures and Margin Isolated) //Margin Cross not yet implemented
 # show Spot Wallet
 global spot_quote
 spot_free = get_spot_balance()
 print( '\n' , '--- Spot Wallet - Balance ---' , '\n' )
 if not spot_free:
  print( 'No assets found' , '\n' , 'This could be an Error' , '\n' , 'Please check manually'  )
 if spot_free:
  # print Spot Wallet
  header_value = 'Value in ' + spot_quote
  s_table = BeautifulTable()
  s_table.clear(True)
  s_table.set_style(BeautifulTable.STYLE_MARKDOWN)
  s_table.maxwidht = 25
  s_table.precision = 8
  s_table.columns.header = [ 'Asset Name' , 'Balance free' , 'Balance locked' , header_value ]
  s_table.columns.width = [ 17 , 25 , 25 , 25 ]
  if spot_quote == 'USD':
   spot_quote = 'USDT'
  for a in spot_free:
   try: 
    if a[ 'asset' ] == 'USDT' or a[ 'asset' ] == 'USDC' or a[ 'asset' ] == 'BUSD':
     quotePrice = 1.00
    else:
     try:
      quote = a[ 'asset' ] + spot_quote
      quoteValue = client.get_symbol_ticker( symbol = quote )
      quotePrice = quoteValue[ 'price' ]
     except BinanceAPIException as bae:
      if spot_quote == 'USDT':
       try:
        quote = a[ 'asset' ] + 'BUSD'
        quoteValue = client.get_symbol_ticker( symbol = quote )
        quotePrice = quoteValue[ 'price' ]
       except BinanceAPIException as bae:
        try:
         quote = a[ 'asset' ] + 'USDC'
         quoteValue = client.get_symbol_ticker( symbol = quote )
         quotePrice = quoteValue[ 'price' ]
        except BinanceAPIException as bae:
         quotePrice = 0
      if spot_quote == 'USDC':
       try:
        quote = a[ 'asset' ] + 'BUSD'
        quoteValue = client.get_symbol_ticker( symbol = quote )
        quotePrice = quoteValue[ 'price' ]
       except BinanceAPIException as bae:
        try:
         quote = a[ 'asset' ] + 'USDT'
         quoteValue = client.get_symbol_ticker( symbol = quote )
         quotePrice = quoteValue[ 'price' ]
        except BinanceAPIException as bae:
         quotePrice = 0
      if spot_quote == 'BUSD':
       try:
        quote = a[ 'asset' ] + 'USDC'
        quoteValue = client.get_symbol_ticker( symbol = quote )
        quotePrice = quoteValue[ 'price' ]
       except BinanceAPIException as bae:
        try:
         quote = a[ 'asset' ] + 'USDT'
         quoteValue = client.get_symbol_ticker( symbol = quote )
         quotePrice = quoteValue[ 'price' ]
        except BinanceAPIException as bae:
         quotePrice = 0
   except BinanceAPIException as bae:
    quotePrice = 0
   a[ 'free' ] = float( a[ 'free' ] )
   a[ 'locked' ] = float( a[ 'locked' ] ) 
   if float(quotePrice) > 0:
    quotePrice = (float(quotePrice) * ( a[ 'free' ] + a[ 'locked' ] ))
   s_table.rows.append( [ a[ 'asset' ] , '%.8f' % a[ 'free' ] , '%.8f' % a[ 'locked' ] , float(quotePrice) ] )
  with warnings.catch_warnings():
   warnings.filterwarnings( 'ignore' )
   try:
    s_table.sort( header_value , True )
    spot_total = float()
    spot_total_all = s_table.columns[header_value]
    for spot in spot_total_all:
     spot_total = spot_total + spot
   finally:
    s_row = 'Total ' + spot_quote
    s_table.rows.append( [ '' , '' , '' , '' ] )
    s_table.rows.append( [ s_row , '' , '' , float(spot_total) ] )
    print( s_table , '\n' )
 # show Futures Wallet
 print( '\n' , '\n' , '--- Futures Wallet - Balance ---' , '\n' )
 futures_balance = client.futures_account_balance()
 if not futures_balance:
  print( 'No assets found' , '\n' , 'This could be an Error' , '\n' , 'Please check manually'  )
 if futures_balance:
  f_table = BeautifulTable()
  f_table.clear( True )
  f_table.set_style( BeautifulTable.STYLE_MARKDOWN )
  f_table.maxwidht = 25
  f_table.precision = 8
  f_table.columns.header = [ 'Asset Name' , 'Balance' , 'Balance withdrawable' ]
  f_table.columns.width = [ 17 , 25 , 25 ]
  for a in futures_balance:
   f_table.rows.append( [ a[ 'asset' ] , '%.8f' % float( a[ 'balance' ] ) , '%.8f' % float( a[ 'withdrawAvailable' ] ) ] )
  with warnings.catch_warnings():
   warnings.filterwarnings( 'ignore' )
   try:
    f_table.sort( 'Balance' , True )
   finally:
    print( f_table , '\n' )
    # print( 'Es fehlt ein TOTAL als USDT' )
 # show Margin Wallet
 print( '\n' , '\n' , '--- Margin Wallet - Balance ---' , '\n' )
 margin_symbol = filter_margin_symbol()
 if not margin_symbol:
  print( 'No assets found' , '\n' , 'This could be an Error' , '\n' , 'Please check manually'  )
 if margin_symbol:
  totalBTC_free = float(0)
  totalBTC_total = float(0)
  totalUSD_free = float(0)
  totalUSD_total = float(0)
  m_table = BeautifulTable()
  m_table.clear( True )
  m_table.set_style( BeautifulTable.STYLE_MARKDOWN )
  m_table.maxwidht = 25
  m_table.precision = 8
  m_table.columns.header = [ 'Asset Name' , 'Balance free' , 'Balance total' ]
  m_table.columns.width = [ 17 , 25 , 25 ]
  for margin_s in margin_symbol:
   base , quote = get_margin_balance( margin_s )
   if base and quote:
    m_table.rows.append([ base[ 'asset' ] , base[ 'free' ] , base[ 'totalAsset' ] ])
    m_table.rows.append([ quote[ 'asset' ] , quote[ 'free' ] , quote[ 'totalAsset' ] ])
    m_table.rows.append([ '' , '' , '' ])
    if quote[ 'asset' ] == 'BTC':
     totalBTC_free = totalBTC_free + float(quote[ 'free' ])
     totalBTC_total = totalBTC_total + float(quote[ 'totalAsset' ])
    if quote[ 'asset' ] == 'USDT' or quote[ 'asset' ] == 'BUSD' or quote[ 'asset' ] == 'USDC':
     totalUSD_free = totalUSD_free + float(quote[ 'free' ])
     totalUSD_total = totalUSD_total + float(quote[ 'totalAsset' ])
   else:
    print ( 'Not found for asset:' , margin_s , '\n' )
    return None
  m_table.rows.append([ '' , '' , '' ])
  m_table.rows.append([ 'Total *USD*' , totalUSD_free , totalUSD_total ])
  m_table.rows.append([ 'Total BTC' , totalBTC_free , totalBTC_total ])
  print( m_table )
 
def filter_margin_symbol(): #gets a list of the names of all margin assets over zero
 margin = get_all_margin()
 margin_symbol = []
 for asset in margin:
  symbol = asset[ 'symbol' ]
  margin_symbol.append(symbol)
 return margin_symbol
 
def get_all_margin(): #gets a list of dicts of all margin assets info over zero
 info = client.get_isolated_margin_account()
 assets = info [ 'assets' ]
 margin = []
 for asset in assets:
  base = asset[ 'baseAsset' ]
  quote = asset[ 'quoteAsset' ]
  base_total = base[ 'totalAsset' ]
  quote_total = quote[ 'totalAsset' ]
  if float(base_total) > 0 or float(quote_total) > 0:
   margin.append(asset)
 return margin

def get_margin_balance( arg ): #gets 2 dict of margin balance base & quote over zero
 account_info = client.get_isolated_margin_account( symbols= arg )
 assets = account_info[ 'assets' ]
 if assets:
  assets = assets[0]
  baseAsset = ()
  quoteAsset = ()
  base = assets[ 'baseAsset' ]
  quote = assets[ 'quoteAsset' ]
  trash = base.pop( 'borrowEnabled' )
  trash = base.pop( 'netAssetOfBtc' )
  trash = base.pop( 'repayEnabled' )
  trash = quote.pop( 'borrowEnabled' )
  trash = quote.pop( 'netAssetOfBtc' )
  trash = quote.pop( 'repayEnabled' )
 if not assets:
  base , quote =  None  , None
  return base , quote
 if base[ 'totalAsset' ] == '0' and quote[ 'totalAsset' ] == '0':
  base , quote =  None  , None
 return base , quote

def get_spot_balance(): #gets a dict of spot balance over zero
 balance = client.get_account()
 spot_balance = balance[ 'balances' ]
 spot =  []
 try:
  for asset in spot_balance:
   if ( asset[ 'free' ] > '0.00000000' ) or ( asset[ 'locked' ] > '0.00000000' ):
    if ( asset[ 'free' ] != '0.00' ) or ( asset[ 'locked' ] != '0.00' ):
     if ( float(asset[ 'free' ]) >= float( spot_min )) or ( float(asset[ 'locked' ]) >= float( spot_min )):
      if ( asset[ 'asset' ] in spot_skip ):
       pass
      else:
       spot.append( asset )
     else:
      pass
  return spot
 except TypeError as te: 
  print( 'Error:' , te )
  return None

if __name__ == '__main__':
 main( sys.argv[1:] )
