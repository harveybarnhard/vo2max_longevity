library(data.table)
library(zoo)
library(gam)

# Parameters ===================================================================

# Prepare data =================================================================
df = fread("./data/vo2max.csv")

# Fill in dates
full_dates = data.table(
  date = as.IDate(seq.Date(from=df[1,]$date, to=df[nrow(df),]$date, by=1))
)
df = merge(df, full_dates, by="date", all=T)

# Vo2 Max ======================================================================

# Create rolling mean of vo2max
df[, vo2max := nafill(vo2max, type="locf")]
ma = function(x, w=60) {
  rollapply(
    x, width=w, FUN=function(y) mean(y, na.rm=T),
    by=1, by.column=T, partial=T, fill=NA, align="right"
  )
}
df_list = list()
wvec = seq(10, 100, by=10)
for(i in 1:length(wvec)) {
  df_list[[i]] = copy(df)[, (c("vo2max_m", "w")) := list(ma(vo2max, wvec[i]), wvec[i])]
}
df = rbindlist(df_list)

# Survival Curve ===============================================================

# For each estimated vo2max value, calculate survival curve
# 1. Estimate survival curve of American at median income
# 2. Suppose that this median American has median vo2max
# 3. Use hazard ratios to inflate/deflate this curve

# Estimate baseline mortality curve
mort = fread("./data/mort_data_2018_2021.csv")
setnames(mort, old="Single-Year Ages Code", new="age")
mort = mort[Gender=="Male" & age < 85 & age > 19,]
mort[, Population := as.numeric(Population)]
mort[, rate := Deaths/Population]
mod = gam(
  rate ~ s(age, 10), 
  family=binomial(link="logit"), weights=Population,
  data=mort, bs="cs", k=10
)

# Function that estimates HR relative to average based on vo2max
# Median vo2max taken from: https://www.kumc.edu/research/alzheimers-disease-research-center/fitness-ranking.html
vo2max_class = fread("./data/vo2max_classification.csv")
hr_class = fread("./data/HR_relative_to_low.csv")
vo2max_class = merge(vo2max_class, hr_class, by="group", all=T)

hr_est = Vectorize(function(x, base_age, gender="M", data=vo2max_class, med_vo2 = 43.7) {
  # Find age interval
  min_age = max(data[sex==gender & age_low <= base_age]$age_low)
  max_age = min(data[sex==gender & age_high >= base_age]$age_high)
  
  # For min and max age, estimate HR
  hr = rep(NA, 3)
  avgage = rep(NA, 3)
  ages = c(min_age, max_age)
  for(a in 1:3) {
    if(a==1){
      data_sub = data[sex==gender & age_high==min_age-1]
    }else if(a==2) {
      data_sub = data[sex==gender & age_low==min_age]
    }else {
      data_sub = data[sex==gender & age_low==max_age+1]
    }
    
    # Model the relationship between vo2max and HR relative to low group
    # Model separately for low and high vo2max interval
    mod_low = gam(
      HR ~ s(vo2max_low), family=gaussian,
      data=data_sub
    )
    mod_high = gam(
      HR ~ s(vo2max_high), family=gaussian,
      data=data_sub
    )
    
    # Predict HR for input vo2max estimate
    HR_pred_low  = predict(mod_low, newdata=data.table(vo2max_low=c(x, med_vo2)))
    HR_pred_high = predict(mod_high, newdata=data.table(vo2max_high=c(x, med_vo2)))
    
    # Convert HR so that it's relative to median vo2max, then take average
    # between low vo2max and high vo2max
    HR_pred_low = HR_pred_low[1]/HR_pred_low[2]
    HR_pred_high = HR_pred_high[1]/HR_pred_high[2]
    hr[a] = (HR_pred_low + HR_pred_high)/2
    avgage[a] = (data_sub$age_low[1] + data_sub$age_high[1])/2
  }
  
  # Take convex combination of hazard ratios over age bins
  hr_out = 1/approx(avgage, hr, xout=base_age)$y
  return(hr_out)
})

# Function to estimate life expectancy based on baseline mortality curve
# and a hazard ratio (assuming proportional hazards model)
le_est = Vectorize(function(hr, base_age, data=mort_base) {
  # Predict mortality rates starting at specific age
  ages = seq(base_age, 120, by=1)
  lrate_pred = predict.Gam(mod, newdata=data.table(age=ages))
  rate = exp(lrate_pred)/(1+exp(lrate_pred))
  rate[rate > 1] = 1
  
  # Multiply mortality curve by hazard ratio
  new_mort = rate * hr
  
  # Create survival curve
  surv = Vectorize(function(x) {
    curve = cumprod(1-new_mort[ages>=base_age & ages <= x])
    return(curve[length(curve)])
  })
  auc = integrate(surv, lower = min(ages), upper = max(ages), abs.tol=0.0001, subdivisions = 1000L)$value
  return(base_age + auc)
})

# Determine age in decmial points
df[, age_on_date := as.numeric(difftime(date, Sys.getenv("USER_BIRTHDATE"), units="days")/365)]

# Calculate LE for vo2max estimate
df[, hr_est := hr_est(vo2max_m, base_age=age_on_date)]
df[, le_est := le_est(hr_est, base_age=age_on_date)]
df[, le_est_m := ma(le_est, w=5)]
df[, le_diff := le_est - shift(le_est, n=1L, type="lag")]

fwrite(df, file="./data/le_estimates.csv")

# Assumptions:
# 1. Wrist-based accuracy: https://www.runnersworld.com/gear/a20856601/can-your-watch-estimate-your-vo2-max/ (within 5%!)
# 2. Causal relationship controlling for other factors
# 3. Extrapolation to higher levels of VO2
# 4. Extrapolation to younger age
# 5. Assuming proportional hazards model
# 6. Lots of interval based assumptions