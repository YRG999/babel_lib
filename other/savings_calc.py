# savings_calc.py
# This script calculates the interest earned on a savings account over 12 months
# based on the provided annual percentage yield (APY) and principal amount.
# It generates a table showing the interest earned each month, total interest,
# and the balance at the end of each month. The table is then exported to a CSV file.

import pandas as pd

def generate_interest_table(principal, apy):
    monthly_rate = apy / 12
    months = 12
    data = []
    balance = principal
    total_interest = 0

    for month in range(1, months + 1):
        interest = balance * monthly_rate
        balance += interest
        total_interest += interest
        data.append({
            "Month": month,
            "Interest Earned": round(interest, 2),
            "Total Interest": round(total_interest, 2),
            "Balance": round(balance, 2)
        })

    df = pd.DataFrame(data)
    print(df)

    # Export to CSV
    csv_filename = "interest_table.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Table has been saved to {csv_filename}")

if __name__ == "__main__":
    try:
        principal = float(input("Enter the current balance: $"))
        apy = float(input("Enter the APY (e.g., 3.60 for 3.60%): ")) / 100
        generate_interest_table(principal, apy)
    except ValueError:
        print("Please enter valid numeric inputs.")
