import os
import pandas as pd
import time
import json

f = open('./data/garmin_response.json')

response = json.load(f)

d = []
for x in response:
    try:
        d.append(
            {
                'date': x['generic']['calendarDate'],
                'vo2max': x['generic']['vo2MaxPreciseValue']
            }
        )
    except:
        pass

df = pd.DataFrame(d)
df.to_csv('./data/vo2max.csv', index=False)
