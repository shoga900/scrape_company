"""Defined a robot model"""
import sys
import pandas as pd
import time

from models import handling

class Scraping(object):
    def __init__(self,code='9252'): 
        # base: 9252
        # haishi: 5127
        self.code = code

class ScrapingRobot(Scraping):
    """Scrape company information"""

    def scrape_company_information(self):
        self.scrape_basic_info()
        self.scrape_stock_price()
        self.scrape_sales()

    def read_company_list(self):
        print('------------------------')
        print(f'input list')
        print('------------------------')

    def scrape_basic_info(self):
        # 現在の株価と発行済株式数を抽出する
        URL = 'https://kabutan.jp/stock/?code=' + str(self.code)

        try:
            # 現在の株価と発行済株式数を抽出する
            dfs = pd.read_html(URL, match='発行済株式')

            df = dfs[0]
            market_capitalization = df.iat[8, 1][:-2]
            temp_now_stocks = df.iat[9, 1]
            now_stocks = int(temp_now_stocks[:-2].replace(',', ''))

            result = {
                '時価総額(億円)': market_capitalization,
                '株式数(株)': now_stocks,
                }
            
            result_df = pd.DataFrame([result])
            print(result_df)

            time.sleep(0.5)

            # return res_basic

        except ValueError:
            # テキストが含まれていない場合の処理
            print("'ページが見つかりませんでした。処理をスキップします。")
            return
    

    def scrape_stock_price(self):
        # 株価を月足で取得し、倍率を出力する
        URL = 'https://kabutan.jp/stock/kabuka?code=' \
          + str(self.code) + '&ashi=mon'

        dfs = pd.read_html(URL, match='始値')
        df = dfs[1]
        df = df.drop(columns=['高値','安値','前月比', '前月比％'])

        # 日付をdatetime形式に変換して降順に並び替え
        df["日付"] = pd.to_datetime(df["日付"], format="%y/%m/%d")
        df.sort_values("日付", inplace=True)

        # 終値が最小の月を特定
        min_close_row = df.loc[df["終値"].idxmin()]
        base_date = min_close_row["日付"]
        base_close = min_close_row["終値"]

        # 基準月以降のデータを取得
        later_data = df[df["日付"] > base_date]

        # 後続月の最大値とその日付
        if not later_data.empty:
            max_close_row = later_data.loc[later_data["終値"].idxmax()]
            max_date = max_close_row["日付"]
            max_close = max_close_row["終値"]
            
            # 日数と倍率を計算
            years_diff = round((max_date - base_date).days / 365, 1)
            multiplier = round(max_close / base_close, 1)
            
            # 結果を表示
            result = {
                "基準日": base_date,
                "基準終値(円)": base_close,
                "最大値日": max_date,
                "最大終値(円)": max_close,
                "期間(年)": years_diff,
                "倍率(倍)": multiplier,
            }

            result_df = pd.DataFrame([result])
            print(result_df)

        else:
            print("基準月以降にデータがありません。")
            result = {
                "基準日": base_date,
                "基準終値": base_close,
            }

        time.sleep(0.5)


    def scrape_sales(self):
        # 決算ページから業績データを取得する
        URL = 'https://kabutan.jp/stock/finance?code=' \
            + str(self.code)

        # 過去の決算数値をスクレイピング
        dfs = pd.read_html(URL, match='決算期')

        if len(dfs[0]) < 8: # 4年前までの株価データがない場合はブレイクする
            return {}

        df = dfs[0]
        df = df.drop(columns=['修正1株配', '発表日'])
        df = df.dropna(how='all')
        df = df.drop(len(df))
        df = df.iloc[::-1]  # 時系列降順に並び替え
        df.index = range(len(df))

        # 1年前の決算情報を抽出する
        past1_year = df.iat[1, 0]
        past1_sales = df.iat[1, 1]
        past1_OP = df.iat[1, 2]
        past1_EPS = df.iat[1, 5]

        # 2年前の決算情報を抽出する
        past2_year = df.iat[2, 0]
        past2_sales = df.iat[2, 1]
        past2_OP = df.iat[2, 2]
        past2_EPS = df.iat[2, 5]

        # 3年前の決算情報を抽出する
        past3_year = df.iat[3, 0]
        past3_sales = df.iat[3, 1]
        past3_OP = df.iat[3, 2]
        past3_EPS = df.iat[3, 5]

        result = {
            'sales3_year': past3_year,
            'sales3_sales': past3_sales,
            'sales3_OP': past3_OP,
            'sales3_EPS': past3_EPS,
            'sales2_year': past2_year,
            'sales2_sales': past2_sales,
            'sales2_OP': past2_OP,
            'sales2_EPS': past2_EPS,
            'sales1_year': past1_year,
            'sales1_sales': past1_sales,
            'sales1_OP': past1_OP,
            'sales1_EPS': past1_EPS,
        }

        print(result)

        time.sleep(0.5)

        # return res_sales



    def write_data(self):
        print('------------------------')
        print('write_data')
        print('------------------------')