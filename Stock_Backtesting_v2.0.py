import pandas as pd
import datetime
import json


Stocks_Trans = json.load(open("Dictionary/Stocks_Trans_Dict"))


Date_limit = "2016-01-01"
starttime = datetime.datetime.now()

Break_Index_All_Total = []
P_Profit_Total = []
M_Profit_Total = []
Rate_of_Return_All_Total = []
Period_All_Total = []


def Buy(Stock_Dataframe, Index, Break_Index_All, BuyStop_num, TStop_num, StopP_num):
    Buy_price = Stock_Dataframe.iloc[Index]['Close']
    Buy_Date = datetime.datetime.strptime(Stock_Dataframe.iloc[Index]['Date'], '%Y-%m-%d')
    Close_High = Stock_Dataframe.iloc[Index]['Close']
    TrailingStop = round(Buy_price * TStop_num, 0)
    BuyStop = round(Buy_price *BuyStop_num, 0)                      # 暫時設很開(1000)所以不影響
    # BuyStop    = data.iloc[i]['20Low']                            # 用20日內最低點(支撐)當買進停損
    StopProfit = round(Buy_price * StopP_num, 0)

    print("Buy{:<7}{:<20}{:<24}{:<25}{:<26}{:<24}{:<25}{:<20}".format('',str(Index), Stock_Dataframe.iloc[Index]['Date'], Stock_Dataframe.iloc[Index]['Close'], Stock_Dataframe.iloc[Index]['20High'], Stock_Dataframe.iloc[Index]['60MA'], Stock_Dataframe.iloc[Index]['KD(K)'], Stock_Dataframe.iloc[Index]['KD(D)']))  # '%-12s' % str(StopProfit), '%-12s' % str(TrailingStop), '%-8s' % str(Close_High),'%-8s' % str(BuyStop)         , '%-10s' % data.iloc[i]['KD(K)'], '%-10s' % data.iloc[i]['KD(D)']     '%-10s' % data.iloc[i]['Bollinger(Btm)'], '%-10s' % data.iloc[i]['Bollinger(Tp)']

    Break_Index_All.append(Index)
    return Buy_price, Buy_Date, Close_High, TrailingStop, BuyStop, StopProfit, Break_Index_All, Index + 1


def Sell(Stock_Dataframe, Sell_Index, Buy_price, Buy_Date, Close_High, TrailingStop, BuyStop, StopProfit, TStop_num, Data_Num):

    while Stock_Dataframe.iloc[Sell_Index]['Close'] < StopProfit and Stock_Dataframe.iloc[Sell_Index]['Close'] > TrailingStop and Stock_Dataframe.iloc[Sell_Index]['Close'] > BuyStop and Sell_Index < (Data_Num - 1):  # 如果到最後都沒有跌破TS 則取現價為最後賣出價
        # while data.iloc[j]['Close'] > (data.iloc[j]['60MA']+0.001) and data.iloc[j-1]['Close'] < (data.iloc[j-1]['60MA']+0.001) and j < (Data_Num - 1):                                                               # 跌破季線賣出
        # while data.iloc[j]['KD(K)'] > (data.iloc[j]['KD(D)']) or (data.iloc[j]['KD(K)']> DeKD_value and data.iloc[j]['KD(D)']) > DeKD_value and j < (Data_Num - 1):                                                   # KD死亡交叉賣出   非常不怎麼樣的結果
        if Stock_Dataframe.iloc[Sell_Index]['Close'] > Close_High:
            Close_High = Stock_Dataframe.iloc[Sell_Index]['Close']
        else:
            Close_High = Close_High
        TrailingStop = round(Close_High * TStop_num, 2)
        Sell_Index += 1

    Sell_price = Stock_Dataframe.iloc[Sell_Index]['Close']
    Sell_Date = datetime.datetime.strptime(Stock_Dataframe.iloc[Sell_Index]['Date'], '%Y-%m-%d')
    Profit = round(Sell_price - Buy_price, 2)

    Period = Sell_Date - Buy_Date
    Rate_of_Return = round((Profit + 0.001) / (Buy_price + 0.1) * 100, 2)

    print("Sell{:<6}{:<20}{:<24}{:<25}{:<26}{:<24}{:<25}{:<20}".format('', str(Sell_Index), Stock_Dataframe.iloc[Sell_Index]['Date'], Stock_Dataframe.iloc[Sell_Index]['Close'], Stock_Dataframe.iloc[Sell_Index]['20High'], Stock_Dataframe.iloc[Sell_Index]['60MA'], Stock_Dataframe.iloc[Sell_Index]['KD(K)'], Stock_Dataframe.iloc[Sell_Index]['KD(D)']))
    print("Profit : ${:<6}({})".format(str(Profit), str(Rate_of_Return) + '%'))
    print("Period : {}".format(str(Period.days) + "days"))

    print('')

    return Sell_Index

def Buy_Sell(Stock_Dataframe, Buy_Index, Break_Index_All, BuyStop_num, TStop_num, StopP_num, Data_Num):
    Buy_price, Buy_Date, Close_High, TrailingStop, BuyStop, StopProfit, Break_Index_All, Sell_Index = Buy(Stock_Dataframe, Buy_Index, Break_Index_All, BuyStop_num, TStop_num, StopP_num)
    Sell_Index = Sell(Stock_Dataframe, Sell_Index, Buy_price, Buy_Date, Close_High, TrailingStop, BuyStop, StopProfit, TStop_num, Data_Num)
    return Sell_Index


def Stock_Backtesting(Stock_Code, Buying_Rule, Sell_Rule):

    Stock_Dataframe = pd.read_csv(".\DataBase\AdvanceData_" + Stock_Code + ".csv")     #,index_col = 'Date'
    Start_Num= 0                                                      # 若要更新資料就不用全部重跑 可以重特定位置開始
    data_mask = Stock_Dataframe["Date"] > Date_limit                  # 篩選日期
    Stock_Dataframe = Stock_Dataframe[data_mask]                      # 刪除掉特定日期之前的數據
    Stock_Dataframe = Stock_Dataframe.reset_index()                   # 重新做排序 但目前多跑出index 因此移除index
    del Stock_Dataframe['index']                                      # print(data.index)
    Start_Num = Stock_Dataframe.index.start
    Data_Num = Stock_Dataframe.index.stop


    # 定義一組全部的策略整合成函式
    #  買進策略: 1.季線 2.KD金叉(<20) 3.KD金叉(<80) + 60MA上 3.KD金叉後過季線 4.隨機買入 5.鳥嘴 6.半身 7.PPP 逆勢進場:   1.跌破季線進場 2.反鳥嘴 3.抄底
    #  停損(利)策略: 1.TrailingStop 30% 目前完全找不到更好的出場策略 其他出場策略目前抓不到超級績效

    Break_Index_All =[]             #計算總共有幾組突破資訊 且記錄Index
    StopP_num = 1000                #1000倍報酬理論上 不太可能被觸發
    TStop_num = 1 - Sell_Rule       #TrailingStop的參數
    BuyStop = 0                     #設定買入價停損
    BuyStop_num = 0.7               #買入價停損參數


    #  買進策略: 1.季線 2.KD金叉(<20) 3.KD金叉(<80) + 60MA上 3.KD金叉後過季線 4.隨機買入 5.鳥嘴 6.半身 7.PPP 逆勢進場:   1.跌破季線進場 2.反鳥嘴 3.抄底
    #  停損(利)策略: 1.TrailingStop 30% 目前完全找不到更好的出場策略 其他出場策略目前抓不到超級績效

    #從第十天開始避開很多Bug
    print('{:<10}Index{:<15}Date{:<20}Close{:<20}20High{:<20}60MA{:<20}KD(K){:<20}KD(D){:<20}'.format('', '', '', '', '',  '', '', ''))


    # for day_index in range(Data_Num-1):
    day_index = Start_Num + 10
    while day_index < Data_Num:
    ##順勢進場 #關鍵價位突破
        if Stock_Dataframe.iloc[day_index]['Close'] > (Stock_Dataframe.iloc[day_index - 1][Buying_Rule] + 0.001) and Stock_Dataframe.iloc[day_index - 1]['Close'] < (Stock_Dataframe.iloc[day_index - 2][Buying_Rule] + 0.001):           # 突破20日高點買入策略
            day_index = Buy_Sell(Stock_Dataframe, day_index, Break_Index_All, BuyStop_num, TStop_num, StopP_num, Data_Num)
        day_index += 1

def main():
    Stocks50 = ['2330.TW', '2317.TW', '2454.TW', '2308.TW', '2382.TW', '2891.TW', '2303.TW', '2881.TW', '3711.TW', '2882.TW', '2412.TW', '2886.TW', '2884.TW', '1216.TW', '2885.TW', '2357.TW', '3034.TW', '3231.TW', '2892.TW', '2345.TW', '2890.TW', '2327.TW', '3008.TW', '2002.TW', '5880.TW', '2880.TW', '1303.TW', '2379.TW', '3037.TW', '2883.TW', '6669.TW', '1101.TW', '2887.TW', ' 2301.TW', '3017.TW', '4938.TW', '1301.TW', '2207.TW', '2603.TW', '3661.TW', '1326.TW', '5876.TW', '2395.TW', '3045.TW', '2912.TW', '4904.TW', '1590.TW', '5871.TW', '6505.TW', '2408.TW']
    for s_index, Stock_Code in enumerate(Stocks50):
        try:
            print("股票代號:{} ({})".format(Stock_Code, Stocks_Trans[Stock_Code]))
            Stock_Backtesting(Stock_Code, Buying_Rule='20High', Sell_Rule=0.3)                # 代表突破20日高點當作進場訊號, 賣出訊豪為30% Trailing Stop
            print('')
            print('===================================================================================================================================================================================================')
        except:
            print(Stock_Code , 'error...')

if __name__ == "__main__":
    main()
