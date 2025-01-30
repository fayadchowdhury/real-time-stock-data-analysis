from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import logging

last_fetched = None

def fetch_hourly_ticker_data(symbols: list) -> pd.DataFrame:
    logger = logging.getLogger("pull")
    try:
        data = yf.download(symbols, period="1d", interval="1h")
        
        df_flattened = pd.DataFrame()

        for ticker in data.columns.get_level_values(1).unique():
            ticker_df = data.xs(ticker, axis=1, level=1)
            ticker_df["Symbol"] = ticker
            df_flattened = pd.concat([df_flattened, ticker_df])

        df_flattened.reset_index(inplace=True)
        df_flattened.rename(columns={"Datetime": "Timestamp"}, inplace=True)
        df_flattened["Timestamp"] = df_flattened["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_flattened.columns.name = None
        logger.debug(f"Data fetched and transformed successfully")
        return df_flattened
    except Exception as e:
        logger.error(e)
        return None

def filter_stock_data(symbols: list) -> pd.DataFrame:
    logger = logging.getLogger("pull")
    global last_fetched
    try:
        data = fetch_hourly_ticker_data(symbols)
        if last_fetched:
            data = data[data["Timestamp"] > last_fetched]

        if data is not None and not data.empty:
            last_fetched = data["Timestamp"].max()
            logger.debug(f"Data last fetched at {last_fetched}")
            return data
        else:
            logger.debug(f"No new data to pull")
    except Exception as e:
        logger.error(e)
        return None