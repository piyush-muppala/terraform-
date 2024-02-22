import pandas as pd
import world_trade_data as wits
pd.set_option('display.max_rows', 6)

data = wits.get_indicator('MPRT-TRD-VL', reporter='usa', year='2017', name_or_id='id')
print(data)