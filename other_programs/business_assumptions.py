# Assumptions
development_cost = 100000  # Total development cost
monthly_operating_cost = 5000  # Monthly operating costs
annual_operating_cost = development_cost + (monthly_operating_cost * 12)  # Total annual operating cost

# Subscription Model
subscription_price_per_month = 30
subscription_revenue_per_year = subscription_price_per_month * 12
break_even_subscribers = annual_operating_cost / subscription_revenue_per_year

# Commission Model with Ad Revenue
commission_rate = 0.05  # 5%
average_earnings_increase_per_driver = 500  # Monthly
commission_per_driver_per_month = commission_rate * average_earnings_increase_per_driver
commission_per_driver_per_year = commission_per_driver_per_month * 12
monthly_ad_revenue = 500
annual_ad_revenue = monthly_ad_revenue * 12
break_even_drivers = (annual_operating_cost - annual_ad_revenue) / commission_per_driver_per_year

print(break_even_subscribers, break_even_drivers)

