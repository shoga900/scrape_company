"""Defined a robot model"""
import datetime
import IPython
import pandas as pd
import time

from models import handling
from models import function

class Scraping(object):
    def __init__(self): 
        pass

class ScrapingRobot(Scraping):
    """Scrape company information"""

    def read_company_list(self):
        self.list = [8316] # base: 9252, haishi: 5127, insure: 5843

        # reader = handling.Reader(
        #     'input/test.xlsx'
        #     # 'input/data_241129.xlsx'
        # )
        # self.list = reader.read_list()

    def scrape_company_information(self):
        l = len(self.list)
        for i,code in enumerate(self.list):
            print('------------------------------------------------------')
            print(f'code: {code}, {i+1}/{l}')
            self.code = code
            self.scrape_basic_info()
            if self.df_one.at[code, '株価(円)'] != '-':
                self.scrape_performance()
                self.scrape_stock_price()
            
            if i == 0:
                self.df = self.df_one
            else:
                self.df = pd.concat([self.df, self.df_one])

            # print(self.df)
            self.output_data()

    def scrape_basic_info(self):
        # 現在の株価と発行済株式数を抽出する
        code = self.code
        URL = 'https://kabutan.jp/stock/?code=' + str(code)

        try:
            # 現在の株価と発行済株式数を抽出する
            dfs = pd.read_html(URL, match='発行済株式')

            df = dfs[0]
            market_capitalization = float(
                df.iat[8, 1][:-2].replace(',', '').replace('兆', ''))
            temp_now_stocks = df.iat[9, 1]
            stocks = float(temp_now_stocks[:-2].replace(',', ''))
            stock_price = int(market_capitalization/ stocks * 1E+8)

        except ValueError:
            # テキストが含まれていない場合の処理
            print("'ページが見つかりませんでした。処理をスキップします。")
            stock_price = '-'
            market_capitalization = '-'
            stocks = '-'
            
        dict_result = {
                '株価(円)': stock_price,
                '時価総額(億円)': market_capitalization,
                '株式数(株)': stocks,
                }
        df_basic = pd.DataFrame([dict_result])
        df_basic.rename(index={0: code}, inplace=True)
        self.df_one = df_basic

        time.sleep(0.5)


    def scrape_performance(self):
        # 決算ページから業績データを取得する
        code = self.code
        URL = 'https://kabutan.jp/stock/finance?code=' \
            + str(code)

        # 過去の決算数値をスクレイピング
        dfs = pd.read_html(URL, match='決算期')

        if len(dfs[0]) < 4: # 1年前までの株価データがない場合はブレイクする
            print("'決算データが不足しています。処理をスキップします。")
            return {}

        df = dfs[0]
        df = df.drop(columns=['修正1株配', '発表日'])
        # IPython.embed()
        if len(df) >= 8:
            df = df.dropna(how='all')
            df = df.drop(len(df))
        else:
            df = df.drop(len(df)-1)
        df.index = range(len(df))
     
        values = df["決算期"]
        cleaned_values = values.str.replace(
            r"[連単変予*IU\s]", "", regex=True
        ).str.strip() # 不要な文字を削除
        date = pd.to_datetime(cleaned_values, format='%Y.%m') # datetime形式に変換

        df["決算期"] = date
        self.df_perfo = df
        # print(self.df_perfo)

        df_flatten = pd.DataFrame(df.values.flatten()).T
        df_flatten.columns = [
            f"{col}{i}" for i in range(len(df)) for col in df.columns
        ]

        df_flatten.rename(index={0: code}, inplace=True)
        self.df_one = self.df_one.join(df_flatten)

        time.sleep(0.5)


    def scrape_stock_price(self):
        # 株価を年足で取得し、倍率を出力する
        code = self.code
        URL = 'https://kabutan.jp/stock/kabuka?code=' \
            + str(code) + '&ashi=yar'

        # pandasで株たんページの表をスクレイピング
        dfs = pd.read_html(URL, match='始値')

        if (dfs[0].empty) or (len(dfs[1]) < 2):
            return {} # 2年前までの株価データがない場合はブレイクする

        # 今年の表と過去の表をmergeする
        dfs[0] = dfs[0].rename(columns={'今年': '日付'})
        df = pd.concat([dfs[0], dfs[1]], ignore_index=True)
        df = df.drop(columns=['前年比', '前年比％', '売買高(株)'])
        # print(df)

        # 上場年度の情報を抽出する
        pub_price = df.iat[len(df) - 1, 1]
        pub_date = df.iat[len(df) - 1, 0]  # 1996年以前は96年とする
        pub_year = int(pub_date[:2])
        pub_year = pub_year + 2000 if pub_year < 40 else pub_year + 1900

        n_years = 5  # ← 抽出する年数をここで指定する
        dict_result = {
            "上場年": pub_year,
            "上場株価": pub_price
        }

        for i in range(1, min(n_years + 1, len(df))):  # 1行目からn年分まで
            date = df.iat[i, 0]
            year = int(date[:2])
            year = year + 2000 if year < 40 else year + 1900
            op = df.iat[i, 1]
            cl = df.iat[i, 4]
            dict_result[f"株価{i}_年"] = year
            dict_result[f"年{i}_始値"] = op
            dict_result[f"年{i}_終値"] = cl

        print(dict_result)

        df_stock = pd.DataFrame([dict_result])
        df_stock.rename(index={0: code}, inplace=True)
        self.df_one = self.df_one.join(df_stock)

        # print(df_stock)
        time.sleep(0.5)


    def output_data(self):
        # 'output/company_info.csv'
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        now_time = now.strftime('%y%m%d')
        output_file_pass = 'output/output_' + now_time + '.csv'
        csv_writer = handling.CsvWriter(
            # 'output/company_info.csv'
            output_file_pass
        )
        csv_writer.write_dataframe(self.df)
