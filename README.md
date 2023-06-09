# vo2max_longevity
Predict longevity changes based on changes in estimated vo2max.

<img src="https://github.com/harveybarnhard/vo2max_longevity/actions/workflows/vo2max_longevity.yml/badge.svg" height="20" />

<img src="https://img.shields.io/date/1687821647?color=007cc3&label=Last%20Updated&logo=garmin" height="20" />

<img src="https://cdn.jamanetwork.com/ama/content_public/journal/jamanetworkopen/937561/zoi180168f2.png?Expires=1685562302&Signature=EyuW4Pb-nMV22EnXVgVTUAf9glpQQjJ7DoCjX4QHqnZo1toveLGcddJ0q~dlqdiTRkAzeBPulTTEOGHh~Xftm7VfK0lCjUPlRw2V-cFZZpcg8oV0szFRHaK6FLV9RLRBQa1jnVATJaZroc7~DdVPfwl5TFmjskwknU0jTnaQMpiA9PfYRQ2ivJYcJIaMiZOfU4gcc3FrFM7HPY7cg3LP-z3~99DvuFa3BkTihFxQp4G5r1JaDHwMSNHNe1qOwb4MVfIIVAPGQi1tfVVowEtRnrk8x1kHaTORsmfxhRZf~S0MxXFPz6p1S1LTh-4SXrphw5cgLziiW4RKQ5jKC-WeEw__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA" height="600" class="center">

[Mandsager et al. (2018)](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2707428)

# Notes

1. Workflow is currently fragile in the sense that sometimes required packages do not download/install properly and entire workflow fails, but workflow works around 2/3 of the time. In particular, sometimes JQuery isn't loaded properly when pulling data from Garmin and sometimes `data.table` is not properly installed for the estimation procedure in R.
2. Current final output is a CSV of longevity estimates, but plots are the desired final output.
