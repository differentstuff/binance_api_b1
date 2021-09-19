api_key = 'your API Key'
api_secret = 'your API Secret'
spot_min = 0.01 #assets in wallet while amount less than this will not be showed
spot_skip = 'NFT' #assets with that name will not be showed / use Comma Separated List
spot_quote = 'USDT' #use 'USDT', 'BUSD', 'USDC' or 'EUR' // 'USD' is not supported by Binance and will be calculated as 'USDT' (of not found 'USDC' or 'BUSD' is used)
direction_type = 'LONG' #use 'LONG' or 'SHORT' // 'SHORT' is not yet implemented