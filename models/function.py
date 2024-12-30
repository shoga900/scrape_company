import pandas as pd

def get_closest_financials(date, df_perfo):
    """
    指定された日付以降で一番近い決算期を検索し、
    以下のデータを計算して返す：
    - 決算期
    - 売上高(百万円)
    - 営業益(百万円)
    - 修正1株益(円)
    - 営業利益率(%)
    - 売上高成長率(%) (前年データが存在する場合)
    - 営業益成長率(%) (前年データが存在する場合)
    """

    fiscal_date = 9999
    sales = 9999
    op = 9999
    eps = 9999
    op_margin = 9999
    sales_growth_rate = 9999
    op_growth_rate = 9999

    try:
        # date以降で一番近い決算期のインデックス取得
        closest_index = df_perfo[df_perfo["決算期"] >= date].index[0]
    except IndexError:
        print("'対象の決算期がありません。")
        result =  {
            "決算期": fiscal_date,
            "売上(百万円)": sales,
            "営利(百万円)": op,
            "1株益(円)": eps,
            "営利率(%)": op_margin,
            "売上成長(%)": sales_growth_rate,
            "営利成長(%)": op_growth_rate,
        }
        return result

    # 該当するデータを取得
    try:
        fiscal_date = df_perfo["決算期"][closest_index]
        sales = float(df_perfo["売上高"][closest_index])
        # 営業益が存在しない場合は経常益を使用
        if df_perfo["営業益"][closest_index] == "－":
            rieki = "経常益"
        else:
            rieki = "営業益"
        op = float(df_perfo[rieki][closest_index])
        eps = float(df_perfo["修正1株益"][closest_index])
    except ValueError:
        # print("'対象期間の決算データがありません。")
        result =  {
            "決算期": fiscal_date,
            "売上(百万円)": sales,
            "営利(百万円)": op,
            "1株益(円)": eps,
            "営利率(%)": op_margin,
            "売上成長(%)": sales_growth_rate,
            "営利成長(%)": op_growth_rate,
        }
        return result

    # 営業利益率を計算
    op_margin = round((op / sales) * 100,1) if sales != 0 else None

    sales_growth_rate = '-'
    op_growth_rate = '-'

    # 売上高成長率と営業益成長率を計算
    if closest_index != 0:
        previous_sales = float(df_perfo["売上高"][closest_index - 1])
        previous_op = float(df_perfo[rieki][closest_index - 1])

        if previous_sales != 0:
            sales_growth_rate = round(((sales - previous_sales) / previous_sales) * 100, 1)

        if previous_op != 0:
            op_growth_rate = round(((op - previous_op) / previous_op) * 100, 1)

    # 結果を辞書形式で返す
    result =  {
        "決算期": fiscal_date,
        "売上(百万円)": sales,
        "営利(百万円)": op,
        "1株益(円)": eps,
        "営利率(%)": op_margin,
        "売上成長(%)": sales_growth_rate,
        "営利成長(%)": op_growth_rate,
    }
    return result
    # return pd.DataFrame([result])

