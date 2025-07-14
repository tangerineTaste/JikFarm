import pandas as pd

file_path = r'C:\Users\Admin\Desktop\JikFarm\data\양파요약데이터_직팜정리.csv'
df = pd.read_csv(file_path, encoding='cp949', low_memory=False)

date_column_name = df.columns[0]

df[date_column_name] = pd.to_datetime(df[date_column_name], format='%Y-%m-%d')

print(df.info())
