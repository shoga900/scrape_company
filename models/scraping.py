"""Defined a robot model"""
import sys
import pandas as pd
import time

from models import handling

class Robot(object):
    """Base model for Robot."""
    def __init__(self,speak_color='green'):
        self.speak_color = speak_color

class ScrapingRobot(Robot):
    """Scrape company information"""

    def read_company_list(self):
        print('------------------------')
        print(f'input list')
        print('------------------------')
    

    def scrape_company(self):

        code = '9252' # Temp


        # 現在の株価と発行済株式数を抽出する
        URL = 'https://kabutan.jp/stock/?code=' + str(code)

        try:
            # 現在の株価と発行済株式数を抽出する
            dfs = pd.read_html(URL, match='発行済株式')

            df = dfs[0]
            temp = df.iat[9, 1]
            now_stocks = int(temp[:-2].replace(',', ''))
            time.sleep(0.2)

            dfs = pd.read_html(URL, match='始値')
            df = dfs[0]
            now_price = df.iat[3, 1]

            # for df in dfs:
            #     print(df)
            #     print("---------------")

            res_basic = {
                'now_stocks': now_stocks,
                'now_price': now_price,
                }
            time.sleep(0.5)

            # return res_basic

        except ValueError:
            # テキストが含まれていない場合の処理
            print("'ページが見つかりませんでした。処理をスキップします。")
            return


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
            result_df = pd.DataFrame([result])
            print(result_df)
        else:
            print("基準月以降にデータがありません。")
            result = {
                "基準日": base_date,
                "基準終値": base_close,
            }


        # 年単位の業績を取得する


        # aaa




    def write_data(self):
        print('------------------------')
        print('write_data')
        print('------------------------')