quantity = 10
price = '1.1' #Only used if sell_type is 'LIMIT'
side = 'SELL' #Must be 'SELL' // 'BUY' not yet implemented
time_force = 'TIME_IN_FORCE_GTC'
sell_type = 'MARKET' #choose between 'MARKET' or 'LIMIT' order type
stopPrice = 0 #only used for LIMIT Orders
sell_amount = 'half' #choose 'quarter'/'third'/'half'/'all' or own number

time_interval = '4h' #Timeframe to check ( 1m , 5m , 15m , 1h , 4h , 1d , ... )
trail = 0.08 #Trailing S/L Value (1.00 = 100% Throwback / 0.01 = 1% Throwback)

time_sleep_cl_on = 5 #Time in seconds to wait between each Price check (to activate S/L close-Trigger)
time_sleep_sl = 10 #Time in seconds to wait between each Price check 
time_sleep_cl = 15 #Time in seconds to wait between each Order check (once S/L is activated)

price_trigger_on = 1.20 #once this price is reached S/L close-Trigger will be enabled (on close) / 0 = S/L always active
price_trigger_cl = 1.24 #price to activate S/L close-Trigger / Must be lower than 'price_trigger_on' to work => triggers when last close price (last candle) is lower than this value (leave enough space or it will trigger too fast)
loop_cl = 0 #loop amount for price check / 0 = infinite
price_trigger_sl = 0 #price for S/L emergency-Trigger / 0 = deactivate emergency-Trigger
loop_sl = 10 #loop amount for S/L-Ticker check (emergency-Trigger) / not needed if price_trigger_sl = 0