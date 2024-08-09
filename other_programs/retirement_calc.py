# retirement_calc3.py
# Optimized by codestral

def estimate_retirement_expenditures(current_savings, estimated_return_percent, yearly_expenses, years_until_retirement, 
safe_withdrawal_rate=0.04):
    """
    Estimate retirement expenditures based on current savings, estimated return percent,
    yearly expenses, and years until retirement. It also calculates the money needed at
    retirement to cover yearly expenses indefinitely and additional amount needed to reach
    the target retirement savings.

    :param current_savings: The amount currently saved for retirement
    :param estimated_return_percent: The estimated annual return percent
    :param yearly_expenses: The estimated yearly expenses during retirement
    :param years_until_retirement: The number of years until retirement
    :param safe_withdrawal_rate: The rate at which money can be withdrawn safely from the savings (default is 4%)
    :return: Future savings, money needed to cover yearly expenses indefinitely, and additional amount needed
    """
    # Convert percentage return to a decimal
    estimated_return = estimated_return_percent / 100

    # Calculate future value of current savings with compound interest
    future_savings = current_savings * (1 + estimated_return) ** years_until_retirement

    # Calculate the amount of money needed at retirement to cover yearly expenses indefinitely
    money_needed = yearly_expenses / safe_withdrawal_rate

    # Calculate additional amount needed to reach the target retirement savings
    additional_amount_needed = max(0, money_needed - future_savings)

    return future_savings, money_needed, additional_amount_needed

def calculate_years_until_retirement(current_savings, estimated_return_percent, yearly_expenses, safe_withdrawal_rate=0.04):
    """
    Calculate the number of years until retirement based on current savings,
    estimated return percent and yearly expenses during retirement.

    :param current_savings: The amount currently saved for retirement
    :param estimated_return_percent: The estimated annual return percent
    :param yearly_expenses: The estimated yearly expenses during retirement
    :param safe_withdrawal_rate: The rate at which money can be withdrawn safely from the savings (default is 4%)
    :return: The number of years until retirement based on current savings and estimated return
    """
    # Convert percentage return to a decimal
    estimated_return = estimated_return_percent / 100

    # Calculate the amount of money needed at retirement to cover yearly expenses indefinitely
    money_needed = yearly_expenses / safe_withdrawal_rate

    # Initialize years and future savings
    years = 0
    future_savings = current_savings

    # Loop to calculate how many years it will take to reach the target retirement savings
    while future_savings < money_needed:
        future_savings += future_savings * estimated_return
        years += 1

    return years

def main():
    print("Retirement Expenditures Estimator")
    current_savings = float(input("Enter the amount currently saved: "))
    estimated_return_percent = float(input("Enter the estimated annual return percent: "))
    yearly_expenses = float(input("Enter the estimated yearly expenses during retirement: "))
    years_until_retirement = int(input("Enter the number of years until retirement: "))

    # Validate user input
    if current_savings < 0 or estimated_return_percent < 0 or yearly_expenses < 0 or years_until_retirement < 0:
        print("Invalid input. All values must be non-negative.")
        return

    try:
        future_savings, money_needed, additional_amount_needed = estimate_retirement_expenditures(
            current_savings, estimated_return_percent, yearly_expenses, years_until_retirement
        )
        years_to_retire = calculate_years_until_retirement(
            current_savings, estimated_return_percent, yearly_expenses
        )

        print(f"Future savings: ${future_savings:,.2f}")
        print(f"Money needed to cover yearly expenses indefinitely: ${money_needed:,.2f}")
        print(f"Additional amount needed: ${additional_amount_needed:,.2f}")
        print("Number of years until retirement based on current savings and estimated return:", years_to_retire)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

main()