import pandas as pd
from utils import *
from visualization import Visualization

def generate_date_range(date, years):
    # 년도와 월로 나누기
    whole_years = int(years)
    additional_months = int((years - whole_years) * 12)

    start_date = pd.to_datetime(date) - pd.DateOffset(years=whole_years, months=additional_months)
    end_date = pd.to_datetime(date) + pd.DateOffset(years=whole_years, months=additional_months)
    
    if start_date < pd.to_datetime('2007-12-31'):
        start_date = pd.to_datetime('2007-12-31')

    if end_date > pd.to_datetime('2024-05-31'):
        end_date = pd.to_datetime('2024-05-31')

    return f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"



def generate_result(confidence_interval, date_range):
    dataset = pd.read_csv('data/total_dataset.csv')
    start, end = date_range.split('~')

    dataset['trix'] = calculate_trix(dataset['Close'], n=5)
    dataset = set_signal(dataset)
    dataset = get_historical_var(dataset, 400, confidence_interval)
    dataset['kelly'] = get_rolling_kelly(dataset)
    dataset['kelly_ratio'] = dataset['kelly'].apply(lambda x: calculate_capped_kelly(x, 3))
    dataset.set_index('Date', inplace=True)
    try:
        index_location = dataset.index.get_loc(start)
    except:
        updated_start = start.split('-')
        updated_start =  start.split('-')[0] + '-' + start.split('-')[1] + '-' + str(int(start.split('-')[2]) + 2).zfill(2)
        print(f'Updated Start date from {start} to {updated_start}')
        index_location = dataset.index.get_loc(updated_start)
    try:
        index_end_location = dataset.index.get_loc(end)
    except:
        updated_end = end.split('-')[0] + '-' + end.split('-')[1] + '-' + str(int(end.split('-')[2]) + 2).zfill(2)
        print(f'Updated End date from {end} to {updated_end}')
        index_end_location = dataset.index.get_loc(updated_end)

    target_dataset = dataset.iloc[index_location:index_end_location+1]

    # kelly VS VaR 적용 kelly로 나누기
    var_dataset = target_dataset.copy()
    var_dataset['kelly_ratio'] = var_dataset.apply(lambda row: update_var_kelly(row), axis=1)

    kelly_result = get_cumulative_trix_returns(target_dataset)
    var_result = get_cumulative_trix_returns(var_dataset)

    kelly_result.to_csv(f'trix_result/kelly_result_{date_range}.csv')
    var_result.to_csv(f'trix_result/var_result_{date_range}_{confidence_interval}.csv')

    visualization = Visualization(
        original_dataset = kelly_result,
        var_dataset = var_result,
        date_range = date_range,
        confidence_interval = confidence_interval,
        folder_path = 'trix_result'
    )
    visualization.generate_all_plots()
    return var_result

if __name__ == '__main__':
    for confidence in [0.01, 0.03, 0.05, 0.1]:
        for date_range in [generate_date_range('2020-03-09', 3),
                           generate_date_range('2020-03-09', 2), 
                           generate_date_range('2020-03-09', 1.5),

                           generate_date_range('2015-08-24', 3),
                           generate_date_range('2015-08-24', 2),
                           generate_date_range('2015-08-24', 1.5),

                           generate_date_range('2018-10-11', 3),
                           generate_date_range('2018-10-11', 2),
                           generate_date_range('2018-10-11', 1.5),

                           generate_date_range('2022-05-09', 3),
                           generate_date_range('2022-05-09', 2),
                           generate_date_range('2022-05-09', 1.5),

                           '2007-12-31~2024-05-31', # 전체 데이터 기간
                           ]:
            generate_result(confidence, date_range)