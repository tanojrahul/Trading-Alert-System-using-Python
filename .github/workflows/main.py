import requests
from twilio.rest import Client
import time

# Function to get live candlestick data
def get_candlestick_data(symbol, interval, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    time_series_key = 'Time Series ({})'.format(interval)
    if time_series_key in data:
        return data[time_series_key]
    else:
        print(f"Error: '{time_series_key}' key not found in API response.")
        return None

# Function to check moving average crossover
def check_crossover(data, short_period, long_period):
    # Extract closing prices and calculate moving averages
    closing_prices = [float(data[ts]['4. close']) for ts in sorted(data.keys(), reverse=True)]
    if len(closing_prices) < max(short_period, long_period):
        return 'HOLD'
    short_ma = sum(closing_prices[:short_period]) / short_period
    long_ma = sum(closing_prices[:long_period]) / long_period
    if short_ma > long_ma:
        return 'BUY'
    elif short_ma < long_ma:
        return 'SELL'
    else:
        return 'HOLD'

# Function to send WhatsApp message
def send_whatsapp_message(account_sid, auth_token, from_whatsapp_number, to_whatsapp_number, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_= from_whatsapp_number,
        to= to_whatsapp_number
    )
    print("WhatsApp message sent successfully!")

# Main function
def main():
    # Set up API keys and parameters
    symbol = '^NSEI'
    interval = '5min'
    api_key = 'Your Alpaca Vantage API key'
    short_period = 20
    long_period = 50

    # Twilio credentials
    account_sid = 'Your account sid'
    auth_token = 'Your account token'
    from_whatsapp_number = '+00000000000'  # Twilio sandbox number
    to_whatsapp_number = '+00000000000'  # Your WhatsApp number

    while True:
        # Get live candlestick data
        candlestick_data = get_candlestick_data(symbol, interval, api_key)
        if candlestick_data is None:
            time.sleep(60)
            continue

        # Check moving average crossover
        signal = check_crossover(candlestick_data, short_period, long_period)

        # Send WhatsApp notification if there's a BUY or SELL signal
        if signal in ['BUY', 'SELL']:
            message = (f"🚨 Trading Alert 🚨\nSymbol: {symbol}\nAction: {signal}\n"
                       f"Timeframe: {interval}\nDetails: Moving average crossover detected.")
            send_whatsapp_message(account_sid, auth_token, from_whatsapp_number, to_whatsapp_number, message)

        # Wait for some time before checking again (e.g., 1 minute)
        time.sleep(60)

if __name__ == "__main__":
    main()
