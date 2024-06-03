import pandas as pd
import numpy as np
import yfinance as yf
from utils import calculate_daily_rate

class AssetProcessor:
    def __init__(self, ticker, start_date):
        self.asset_data = yf.download(ticker, start_date)
    
    def get_pct_change(self):
        self.asset_data['Change'] = self.asset_data['Close'].pct_change()
    
    def process_date(self):
        self.asset_data = self.asset_data.reset_index()
        self.asset_data['Date'] = self.asset_data['Date'].dt.strftime('%m/%d/%Y')
        self.asset_data.set_index('Date')
    
    def save_result(self, result_file_nm):
        self.get_pct_change()
        self.process_date()
        self.asset_data[['Date', 'Close', 'Change']].to_csv(f'data/{result_file_nm}.csv')
        return self.asset_data[['Date', 'Close', 'Change']]
    
class RateProcessor:
    def __init__(self, loan_rate_file, asset_dataset, deposit_rate_file, output_file, rf_file,
                loan_rate_date_col='DATE', loan_rate_col='DPRIME', 
                deposit_rate_date_col='Record Date', deposit_rate_col='Annualized Effective Rate', 
                asset_date_format='%m/%d/%Y', loan_date_format='%Y-%m-%d', deposit_date_format='%Y-%m-%d', rf_date_format='%m/%d/%Y'):
        
        self.loan_rate_file = loan_rate_file
        self.asset_dataset = asset_dataset
        self.deposit_rate_file = deposit_rate_file
        self.rf_file = rf_file
        self.output_file = output_file
        
        self.loan_rate_date_col = loan_rate_date_col
        self.loan_rate_col = loan_rate_col
        self.deposit_rate_date_col = deposit_rate_date_col
        self.deposit_rate_col = deposit_rate_col
        
        self.asset_date_format = asset_date_format
        self.loan_date_format = loan_date_format
        self.deposit_date_format = deposit_date_format
        self.rf_date_format = rf_date_format

    def handle_loan_rate(self):
        loan_rf = pd.read_csv(self.loan_rate_file)
        loan_rf = loan_rf[[self.loan_rate_date_col, self.loan_rate_col]]
        loan_rf.columns = ['Date', 'loan_rate']
        loan_rf['loan_rate'] = loan_rf['loan_rate'].replace('.', np.nan).astype(float)
        loan_rf['loan_rate'] = loan_rf['loan_rate'].apply(lambda x: calculate_daily_rate(x,250))
        return loan_rf
    
    def handle_deposit_rate(self):
        deposit_rf = pd.read_csv(self.deposit_rate_file)
        deposit_rf = deposit_rf[[self.deposit_rate_date_col, self.deposit_rate_col]]
        deposit_rf.columns = ['Date', 'deposit_rate']
        deposit_rf['deposit_rate'] = deposit_rf['deposit_rate'].apply(lambda x: calculate_daily_rate(x, 250))
        return deposit_rf
    
    def handle_rf(self):
        rf = pd.read_csv(self.rf_file)
        rf.columns = ['Date', 'rf']
        rf['rf'] = rf['rf'].apply(lambda x: calculate_daily_rate(x, 250))
        return rf
    
    def merge_data(self, loan_rf, asset, deposit_rf, rf):
        asset['Date'] = pd.to_datetime(asset['Date'], format=self.asset_date_format)
        loan_rf['Date'] = pd.to_datetime(loan_rf['Date'], format=self.loan_date_format)
        deposit_rf['Date'] = pd.to_datetime(deposit_rf['Date'], format=self.deposit_date_format)
        rf['Date'] = pd.to_datetime(rf['Date'], format=self.rf_date_format)

        joined = pd.merge(asset, loan_rf, how='left')
        joined = pd.merge(joined, deposit_rf, how='left')
        joined = pd.merge(joined, rf, how='left')
        return joined
    
    def fill_na(self, joined):
        print(joined)
        joined['loan_rate'] = joined['loan_rate'].ffill()
        joined['deposit_rate'] = joined['deposit_rate'].ffill()
        joined['rf'] = joined['rf'].ffill()
        return joined
    
    def process_rates(self, file_nm):
        loan_rf = self.handle_loan_rate()
        deposit_rf = self.handle_deposit_rate()
        rf = self.handle_rf()

        merged_data = self.merge_data(loan_rf, self.asset_dataset, deposit_rf, rf)
        merged_data = self.fill_na(merged_data)
        merged_data['Date'] = merged_data['Date'].dt.strftime('%Y-%m-%d')
        merged_data.to_csv(f'data/{file_nm}.csv', index=False)
        
        return merged_data


if __name__ == "__main__":
    # SP500 데이터 생성
    asset_processor = AssetProcessor(
        ticker = "^GSPC",
        start_date = "2004-01-02"
    )
    sp500 = asset_processor.save_result('sp500')

    # 금리 관련 data 정리
    rate_processor = RateProcessor(
        loan_rate_file='data/loan_rate_before.csv',
        asset_dataset=sp500,
        deposit_rate_file='data/deposit_rate_before.csv',
        rf_file='data/rf_data.csv',
        output_file='data/deposit_and_loan_rate.csv'
    )
    rate = rate_processor.process_rates('loan_deposit_rf_rate')

    rate.to_csv('data/total_dataset.csv', index=False)