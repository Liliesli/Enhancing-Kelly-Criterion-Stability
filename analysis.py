import pandas as pd

kelly_data = pd.read_csv('trix_result/kelly_result_2007-12-31~2024-05-31.csv')

def catch_collusion(df):
    # 수익률의 변화율 계산
    df['Return_Change'] = df['portfolio'].diff()
    df['Return_Change_3days'] = df['portfolio'].diff(3)

    # 급락 지점을 찾기 위한 임계값 설정
    threshold = -0.1 

    df['Is_Drop'] = df['Return_Change'] < threshold
    df['Is_Drop_3days'] = df['Return_Change_3days'] < threshold

    drops = df[df['Is_Drop']].sort_values('Return_Change')
    drops_3days = df[df['Is_Drop_3days']].sort_values('Return_Change_3days')
    drops.to_csv('data/drops.csv', index=False)
    drops_3days.to_csv('data/drops_3days.csv', index=False)
    return 

catch_collusion(kelly_data)