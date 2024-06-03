# Enhancing Kelly Criterion Stability: A VaR-Centric Approach
Value at Risk 개념을 활용한 Kelly Criterion 투자전략 재해석

## 환경 설정
이 레포지토리는 파이썬 3.11.4 기준으로 설정되었습니다.
```bash
python --version
3.11.4
```

```bash
pip install -r requirements.txt
```

## 데이터 설명
1. 무위험 이자율: 장기 국채 이자율
2. 대출 이자율:
3. 수시입출금 계좌 이자율:
4. S&P 500 데이터

## 각 파일 설명
1. preprocess_data: 데이터 1, 2, 3, 4 를 통합한 total_dataset 도출
2. utils: 전략 구현에 필요한 함수 
3. visualization: 결과 시각화 파일
4. main: 전략 실행 파일