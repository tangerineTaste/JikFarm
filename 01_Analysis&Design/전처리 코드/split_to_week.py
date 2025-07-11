import pandas as pd
import numpy as np

def get_week_of_year(date):
    year = date.year
    week_number = date.isocalendar().week
    return f"{year}년 {week_number}째주"

def split_to_week(df):
    df['등급이름'] = df['등급이름'].apply(lambda x: x if x in ['특', '상', '보통'] else '하')
    
    df['단가'] = round(df['총가격(원)'] / df['단위총물량(kg)'])
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=['단가'], inplace=True)

    df['날짜(YYYY-MM-DD)'] = pd.to_datetime(df['날짜(YYYY-MM-DD)'])
    df.set_index('날짜(YYYY-MM-DD)', inplace=True)
    weekly_df = df.groupby(['상품 중분류 이름', '등급이름']).resample('W').agg({'단가': 'mean'}).reset_index()
    weekly_df['단가'] = weekly_df['단가'].astype(int)
    weekly_df.rename(columns={'날짜(YYYY-MM-DD)': '날짜'}, inplace=True)

    grade_order = ['특', '상', '보통', '하']
    weekly_df['등급이름'] = pd.Categorical(weekly_df['등급이름'], categories=grade_order, ordered=True)
    weekly_df = weekly_df.sort_values(['날짜','등급이름']).reset_index(drop=True)

    weekly_df['날짜'] = weekly_df['날짜'].apply(get_week_of_year)

    return weekly_df