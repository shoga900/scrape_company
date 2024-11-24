"""Defined a robot model"""
import sys
import pandas as pd
import time

from models import handling

class Scraping(object):
    def __init__(self): 
        pass
        # self.df = pd.DataFrame()
        # base: 9252
        # haishi: 5127

class ScrapingRobot(Scraping):
    """Scrape company information"""

    def read_company_list(self):
        self.list = [9252]
        self.df = pd.DataFrame(0, index=self.list, columns=[])
        print(f'list={self.list}')

    def scrape_company_information(self):
        for code in self.list:
            self.scrape_basic_info(code)
            self.scrape_stock_price(code)
            self.scrape_performance(code)

    def output_data(self):
        print(self.df)


    def scrape_basic_info(self, code):
        # 現在の株価と発行済株式数を抽出する
        URL = 'https://kabutan.jp/stock/?code=' + str(code)

        try:
            # 現在の株価と発行済株式数を抽出する
            dfs = pd.read_html(URL, match='発行済株式')

            df = dfs[0]
            stock_price = 100
            market_capitalization = float(df.iat[8, 1][:-2])
            temp_now_stocks = df.iat[9, 1]
            stocks = int(temp_now_stocks[:-2].replace(',', ''))
            stock_price = int(market_capitalization/ float(stocks) * 1E+8)

            result = {
                '株価(円)': stock_price,
                '時価総額(億円)': market_capitalization,
                '株式数(株)': stocks,
                }
            
            df_basic = pd.DataFrame([result])
            df_basic.rename(index={0: code}, inplace=True)
            self.df = pd.concat([self.df, df_basic], axis=1)
            # print(self.df)

            time.sleep(0.5)

            # return res_basic

        except ValueError:
            # テキストが含まれていない場合の処理
            print("'ページが見つかりませんでした。処理をスキップします。")
            return
    

    def scrape_stock_price(self, code):
        # 株価を月足で取得し、倍率を出力する
        URL = 'https://kabutan.jp/stock/kabuka?code=' \
          + str(code) + '&ashi=mon'

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

        else:
            print("基準月以降にデータがありません。")
            result = {
                "基準日": base_date,
                "基準終値": base_close,
            }

        df_price = pd.DataFrame([result])
        df_price.rename(index={0: code}, inplace=True)
        self.df = pd.concat([self.df, df_price], axis=1)
        # print(result_df)

        time.sleep(0.5)

    def scrape_performance(self, code):
        # 決算ページから業績データを取得する
        URL = 'https://kabutan.jp/stock/finance?code=' \
            + str(code)

        # 過去の決算数値をスクレイピング
        dfs = pd.read_html(URL, match='決算期')

        if len(dfs[0]) < 4: # 1年前までの株価データがない場合はブレイクする
            return {}

        df = dfs[0]
        df = df.drop(columns=['修正1株配', '発表日'])
        df = df.dropna(how='all')
        df = df.drop(len(df))
        # df = df.iloc[::-1]  # 時系列降順に並び替え
        df.index = range(len(df))
     
        values = df["決算期"]
        year_month = pd.Series(0, index=range(len(values)))
        for i, value in enumerate(values):
            year_month[i] = value[-7:]
            # "予"が含まれている場合に(E)を追加
            if "予" in value:
                year_month[i] = "(E)" + year_month[i]
        df["決算期"] = year_month

        # print(df)

        df_flatten = pd.DataFrame(df.values.flatten()).T
        df_flatten.columns = [
            f"{col}{i}" for i in range(len(df)) for col in df.columns
        ]

        # print(df_flatten)

        df_flatten.rename(index={0: code}, inplace=True)
        self.df = pd.concat([self.df, df_flatten], axis=1)
        # print(result_df)

        time.sleep(0.5)

        # return res_sales
