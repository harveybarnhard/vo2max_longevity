# vo2max_longevity
Predict longevity changes based on changes in estimated vo2max.

<img src="https://github.com/harveybarnhard/vo2max_longevity/actions/workflows/vo2max_longevity.yml/badge.svg" height="20" />

<img src="https://img.shields.io/date/1721127651?color=007cc3&label=Last%20Updated&logo=garmin" height="20" />

<img src="[https://cdn.jamanetwork.com/ama/content_public/journal/jamanetworkopen/937561/zoi180168f2.png?Expires=1694543187&Signature=J09-L1zLDhNw7wiWb~iW0Qj11QaY~kNLg9Ved14RE~npRA251FHyUC8H0YzqP8Sbk314YZ1BD9A1J01VKpB7rOQQKUOg0G1LXsfb4R3EoZYTJAJTaDoK5rVx4UgOB15t13vaXXCXsSLJElyI0dTpdAD4MrHDVJLi3gRcKljGZjEQX1TL-nzsjkqJCvcgdc0RJUTy6S8F3OBJpnTDl62srEnaXiyV~giti0qdAXG6rCx-e-j4AYHMCxYgHiMd8V-vftDS0t-gGjCW68zTvbFua5YAH8doM-3dLnFnthy8NM1fQtZoV8-YzrvZIkq3HZlfUmVYSMxHQ7r9tiRulDgpGw__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA](https://cdn.jamanetwork.com/ama/content_public/journal/jamanetworkopen/937561/zoi180168f2.png?Expires=1723956891&Signature=wTAOJnX1dy7INY9OpbPwwVwRk8wy9nSmpIK3dqwv89o9zFSMlWMfOiN8SV7DLp6aJM4RCEOnmyBsd7Zg8TzbeDY~hxL~oIGsbQI69cbG6hfWp1uzQxliCR8OT4A7tLaVEsWeoYDFQjfnnIRsTCb0~TwWhlG9KbmL4IOxIk5NypWbIFjk8btM~65NZQldVT5Lxq0dd8cS-ZyA6Q~sic~hR2CeHnFVHX5QM8TZYbAytA4Xue~AZrc~Ic56uBUbIKX1LbNML~WszgOYNJAYwurRP-lQzIz1Kid9RpZiBqgA4zGl4jwBpDkobrv7~w7mLFIJQCwtqc0JGPRr63QCusctiA__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA)" height="600" class="center">

[Mandsager et al. (2018)](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2707428)

# Notes

1. Workflow is currently fragile in the sense that sometimes required packages do not download/install properly and entire workflow fails, but workflow works around 2/3 of the time. In particular, sometimes JQuery isn't loaded properly when pulling data from Garmin and sometimes `data.table` is not properly installed for the estimation procedure in R.
2. Current final output is a CSV of longevity estimates, but plots are the desired final output.

# Update July 29, 2023:
Workflow never runs anymore...apparently due to improved bot detection.

# Update August 11, 2023:
Here are the steps to manually obtain a range of Vo2 max data (and any other number of data) from Garmin Connect.

1. Log in to Garmin Connect using Google Chrome
2. Right click anywhere on the page and click "inspect"
3. Open the console and copy-and-paste the following code, perhaps changing the date range
``` javascript
response = jQuery.getJSON(
'https://connect.garmin.com/modern/proxy/metrics-service/metrics/maxmet/daily/2018-07-22/2023-08-10',
function(days)
    {
        days.forEach(
        function(day)
            {
                try {
                    d = day.generic;
                    console.dir(d.calendarDate, d.vo2MaxPreciseValue);
                } catch (e) {}
            }
        );
    } );
```
4. Wait a bit for the response, then right-click on the response in the console and click "copy object"
5. Paste the copied object into a plain text file with a `.json` extension.
6. Use `get_data_manual.py` to process the data instead of `get_data.py`
