import pandas as pd
import re




if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)

    data_from = pd.read_csv("./his/6_13/analyzed_result.csv")
    data_to = pd.read_csv("./his/7_4/analyzed_result.csv")

    data_to = data_to[["id","listprice"]]
    data = data_from.merge(data_to,how="outer",on="id")

    data_sold = data.loc[data['listprice_y'].isna()]
    print("sold houses")
    print(data_sold.shape)

    data_new = data.loc[data['listprice_x'].isna()]
    print("new houses")
    print(data_new.shape)

    data_both = data.loc[data['listprice_y'].notna()]
    data_both = data.loc[data['listprice_x'].notna()]
    print("comparing houses prices change")
    print(data_both.shape)

    data_both['delta'] = data_both['listprice_y'] - data_both['listprice_x']

    area_price_diff = data_both.groupby(['area'])['delta','listprice_x'].sum() # new line added.
    area_price_diff['rate'] = area_price_diff['delta'] / area_price_diff['listprice_x']
    area_price_diff['rate'] = area_price_diff['rate'].apply(lambda o: '{:.2%}'.format(o))
    print("change per area")
    print(area_price_diff)

    villa = data_both.groupby(['isvilla'])['delta', 'listprice_x'].sum()
    print("change per house type")
    print(villa)

    top = data_both.groupby(['istopfloor'])['delta', 'listprice_x'].sum()
    print(top)

    all = '{:.2%}'.format(data_both['delta'].sum() / data_both['listprice_x'].sum())
    print("overall changes")
    print(all)

    print("increase most")
    final_df = data_both.sort_values(by=['delta'], ascending=False)
    print(final_df.head(n=3)[['name','delta']])

    print("decrease most")
    final_df = data_both.sort_values(by=['delta'], ascending=True)
    print(final_df.head(n=5)[['name', 'delta', 'listprice_y', 'bottomprice']])