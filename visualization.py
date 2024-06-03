import matplotlib.pyplot as plt
import os

class Visualization:
    def __init__(self, original_dataset, var_dataset, date_range, confidence_interval,
                 folder_path):
        self.original_dataset = original_dataset
        self.var_dataset = var_dataset
        self.date_range_nm = date_range.replace('/', '_')
        self.confidence_interval = confidence_interval
        self.folder_path = folder_path
    
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    
    def plot_kelly_weight(self):
        plt.figure(figsize=(15,5))
        self.original_dataset['kelly'].plot()
        plt.title('Kelly Criterion over Time')
        plt.ylabel('Kelly Criterion')
        plt.xticks(rotation = 45)
        plt.savefig(f'{self.folder_path}/Kelly_date{self.date_range_nm}.png')
   
    def plot_capped_kelly_weight(self):
        plt.figure(figsize=(15,5))
        self.original_dataset['kelly_ratio'].plot()
        plt.title('Capped Kelly Criterion over Time')
        plt.ylabel('Kelly Criterion')
        plt.xticks(rotation=45)
        plt.savefig(f'{self.folder_path}/Capped_Kelly_date{self.date_range_nm}.png')
    
    def plot_two_returns(self):
        fig, ax = plt.subplots(ncols=2, figsize=(20, 4))
        self.original_dataset['portfolio'].plot(ax=ax[0])
        ax[0].set_ylabel('Portfolio Return')
        ax[0].tick_params(axis='x', rotation=45)
        ax[0].set_title(f'{str(self.confidence_interval)} - S&P500 Kelly Cumulative Return')
        self.var_dataset['portfolio'].plot(ax=ax[1])
        ax[1].set_ylabel('Portfolio Return')
        ax[1].tick_params(axis='x', rotation=45)
        ax[1].set_title('S&P500 VaR Kelly Cumulative Return')
        plt.savefig(f'{self.folder_path}/Returns_date_{str(self.date_range_nm)}, var_{str(self.confidence_interval)}.png')

    def plot_combined_returns(self):
        fig, ax = plt.subplots(figsize=(20, 6))
        self.original_dataset['portfolio'].plot(ax=ax, label='Kelly')
        self.var_dataset['portfolio'].plot(ax=ax, label='VaR Kelly')
        ax.set_ylabel('Portfolio Return')
        ax.set_title(f'{str(self.confidence_interval)} - S&P500 Zero vs VaR Kelly Cumulative Return')
        ax.legend()
        plt.savefig(f'{self.folder_path}/Combined_Returns_date_{str(self.date_range_nm)}, var_{str(self.confidence_interval)}.png')
    
    def plot_combined_all_returns(self):
        self.original_dataset['cumulative_return'] = (1+self.original_dataset['Change']).cumprod()
        fig, ax = plt.subplots(figsize=(20, 6))
        self.original_dataset['portfolio'].plot(ax=ax, label='Kelly')
        self.var_dataset['portfolio'].plot(ax=ax, label='VaR Kelly')
        self.original_dataset['cumulative_return'].plot(ax=ax, label='S&P500')
        ax.set_ylabel('Portfolio Return')
        ax.set_title(f'{str(self.confidence_interval)} - S&P500 Zero vs VaR Kelly Cumulative Return')
        ax.legend()
        plt.savefig(f'{self.folder_path}/Combined_All_Returns_date_{str(self.date_range_nm)}, var_{str(self.confidence_interval)}.png')
    
    def generate_all_plots(self):
        self.plot_kelly_weight()
        self.plot_capped_kelly_weight()
        self.plot_two_returns()
        self.plot_combined_returns()
        self.plot_combined_all_returns()