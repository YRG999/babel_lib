#!/usr/bin/env python3
"""
EST to Epoch Time Converter
Converts between 24-hour EST time (HHMM format) and Unix epoch time.
"""

from datetime import datetime
import pytz


def convert_time():
    """Convert between EST time and Unix epoch time."""
    
    print("\nEST ↔ Epoch Time Converter")
    print("=" * 45)
    print("Enter 24-hour time (HHMM format)")
    print("  - 1030 for 10:30 AM")
    print("  - 2030 for 10:30 PM")
    print("\nOr date+time (YYYYMMDD-HHMM format)")
    print("  - 20260204-1608 for Feb 4, 2026 at 4:08 PM")
    print("\nOr enter epoch time (Unix timestamp)")
    print()
    
    user_input = input("Enter time, date+time, or epoch: ").strip()
    
    if not user_input:
        print("No input provided.")
        return
    
    try:
        # Check if it's date+time format (contains hyphen)
        if '-' in user_input:
            parts = user_input.split('-')
            if len(parts) != 2:
                print("Invalid format. Use YYYYMMDD-HHMM")
                return
            
            date_str, time_str = parts
            
            if len(date_str) != 8 or len(time_str) != 4:
                print("Invalid format. Use YYYYMMDD-HHMM")
                return
            
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            hours = int(time_str[:2])
            minutes = int(time_str[2:4])
            
            # Validate date and time
            if month < 1 or month > 12 or day < 1 or day > 31:
                print("Invalid date. Check month (1-12) and day (1-31).")
                return
            if hours > 23 or minutes > 59:
                print("Invalid time. Hours must be 0-23, minutes 0-59.")
                return
            
            # Create datetime object in EST
            est = pytz.timezone('America/New_York')
            dt = est.localize(datetime(year, month, day, hours, minutes, 0))
            
            # Convert to epoch
            epoch = int(dt.timestamp())
            print(f"\n✓ Date+Time: {user_input} EST")
            print(f"✓ Epoch time: {epoch}")
            print(f"  Full: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            return
        
        value = int(user_input)
        
        # Determine if it's 24-hour time or epoch time
        # 24-hour time should be between 0 and 2359
        if 0 <= value <= 2359:
            # It's 24-hour time
            hours = value // 100
            minutes = value % 100
            
            # Validate time
            if hours > 23 or minutes > 59:
                print("Invalid time format. Hours must be 0-23, minutes 0-59.")
                return
            
            # Create datetime object for today in EST
            est = pytz.timezone('America/New_York')
            now = datetime.now(est)
            dt = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            # Convert to epoch
            epoch = int(dt.timestamp())
            print(f"\n✓ 24-hour time: {value:04d} EST (today)")
            print(f"✓ Epoch time: {epoch}")
            print(f"  Full: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        else:
            # It's epoch time
            dt = datetime.fromtimestamp(value, tz=pytz.timezone('America/New_York'))
            time_str = dt.strftime("%H%M")
            print(f"\n✓ Epoch time: {value}")
            print(f"✓ 24-hour time: {time_str} EST")
            print(f"  Full: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main entry point with loop for multiple conversions."""
    while True:
        convert_time()
        again = input("\nConvert another? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!\n")
            break


if __name__ == "__main__":
    main()
