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
        # self.list = [8316] # base: 9252, haishi: 5127, insure: 5843

        reader = handling.Reader(
            # 'input/test.xlsx'
            'input/data_241129.xlsx'
        )
        self.list = reader.read_list()

    def scrape_company_information(self):
        l = len(self.list)
        for i,code in enumerate(self.list):
            print('-----------------------------------------------------')
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
        # 株価を月足で取得し、倍率を出力する
        code = self.code
        URL = 'https://kabutan.jp/stock/kabuka?code=' \
          + str(code) + '&ashi=mon'

        dfs = pd.read_html(URL, match='始値')
        if len(dfs[1]) < 5: # データが5周週間より少ない場合はスキップする
            print("'月足データが不足しています。処理をスキップします。")
            return {}
        df = dfs[1]
        df = df.drop(columns=['高値','安値','前月比', '前月比％'])

        # 日付をdatetime形式に変換して降順に並び替え
        df["日付"] = pd.to_datetime(df["日付"], format="%y/%m/%d")
        df.sort_values("日付", inplace=True)

        # 1．終値が最小の月から前方に探索
        min_close_row = df.loc[df["終値"].idxmin()]
        low1_date = min_close_row["日付"]
        low1_close = min_close_row["終値"]
        # 最小月以降のデータを取得
        high1_data = df[df["日付"] > low1_date]
        # 最小月以降の最大値とその日付
        if not high1_data.empty:
            high1_close_row = high1_data.loc[high1_data["終値"].idxmax()]
            high1_date = high1_close_row["日付"]
            high1_close = high1_close_row["終値"]
            # 日数と倍率を計算
            term1 = round((high1_date - low1_date).days / 365, 1)
            mult1 = round(high1_close / low1_close, 1)

        # 2．終値が最大の月から後方に探索
        high2_close_row = df.loc[df["終値"].idxmax()]
        high2_date = high2_close_row["日付"]
        high2_close = high2_close_row["終値"]
        # 最大月以前のデータを取得
        low2_data = df[df["日付"] < high2_date]
        # 後続月の最大値とその日付
        if not low2_data.empty:
            low2_close_row = low2_data.loc[low2_data["終値"].idxmin()]
            low2_date = low2_close_row["日付"]
            low2_close = low2_close_row["終値"]
            # 日数と倍率を計算
            term2 = round((high2_date - low2_date).days / 365, 1)
            mult2 = round(high2_close / low2_close, 1)

        if not high1_data.empty:
            bottom_date = low1_date
            bottom_close = low1_close
            peak_date = high1_date
            peak_close = high1_close
            term = term1
            multiplier = mult1
            
            if not low2_data.empty:
                if mult1 < mult2:
                    bottom_date = low2_date
                    bottom_close = low2_close
                    peak_date = high2_date
                    peak_close = high2_close
                    term = term2
                    multiplier = mult2

        elif not low2_data.empty:
            bottom_date = low2_date
            bottom_close = low2_close
            peak_date = high2_date
            peak_close = high2_close
            term = term2
            multiplier = mult2

        elif high1_data.empty and low2_data.empty:
            print("'株価が下がり続けているクソ株です。処理をスキップします。")
            return
        # ボトム日付近の決算データ
        dict_financials = function.get_closest_financials(bottom_date, self.df_perfo)
        # if dict_financials == 0:
        #     return


        stocks = self.df_one["株式数(株)"][code]
        sales = dict_financials["売上(百万円)"]
        eps = dict_financials["1株益(円)"]
        market_cap = round(stocks * bottom_close * 1E-6 , 1)
        per = round(bottom_close / eps, 1)
        psr = round(market_cap / sales, 2)

        dict_result = {
            "ボトム日": bottom_date,
            "B終値(円)": bottom_close,
            "B時価総額(百万円)": market_cap,
            "B_PER": per,
            "B_PSR": psr,
        }

        df_stock = pd.DataFrame([dict_result])
        
        df_stock[[
            "B決算期",
            "B売上(百万円)",
            "B営利(百万円)",
            "B_1株益(円)",
            "B営利率(%)",
            "B売上成長(%)",
            "B営利成長(%)"
            ]] = pd.DataFrame(dict_financials, index=df_stock.index)
        

        # ピーク日付近の決算データ
        dict_financials = function.get_closest_financials(peak_date, self.df_perfo)
        # if dict_financials == 0:
        #     return

        sales = dict_financials["売上(百万円)"]
        eps = dict_financials["1株益(円)"]
        market_cap = round(stocks * bottom_close * 1E-6 , 1)
        per = round(bottom_close / eps, 1)
        psr = round(market_cap / sales, 2)

        add_result = {
            "ピーク日": peak_date,
            "P終値(円)": peak_close,
            "P時価総額(百万円)": market_cap,
            "P_PER": per,
            "P_PSR": psr,
        }
        df_add = pd.DataFrame([add_result])
        df_stock = pd.concat([df_stock, df_add],axis=1)

        df_stock[[
            "P決算期",
            "P売上(百万円)",
            "P営利(百万円)",
            "P_1株益(円)",
            "P営利率(%)",
            "P売上成長(%)",
            "P営利成長(%)"
            ]] = pd.DataFrame(dict_financials, index=df_stock.index)
        
        hantei = 0
        if multiplier >= 2.0:
            hantei = 1
            print(f"2倍株!!!, 期間: {term}年")
        add_result = {
            "期間(年)": term,
            "倍率(倍)": multiplier,
            "2倍判定": hantei,
        }
        df_add = pd.DataFrame([add_result])
        df_stock = pd.concat([df_stock, df_add],axis=1)

        df_stock.rename(index={0: code}, inplace=True)
        self.df_one = self.df_one.join(df_stock)

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
