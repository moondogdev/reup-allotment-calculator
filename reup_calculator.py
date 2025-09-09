"""
ReUp: Medical Marijuana Allotment Calculator

This script provides the core logic for calculating weekly purchase recommendations
based on a 35-day allotment.
"""
import datetime

# Constants for conversion
OUNCES_TO_GRAMS = 28.35
DISPENSARY_INCREMENT_GRAMS = 3.5  # Standard "eighth" in grams
ALLOTMENT_PERIOD_WEEKS = 5
DAYS_IN_WEEK = 7

def calculate_purchase_for_cycle(total_allotment_oz: float, start_date_str: str) -> dict:
    """
    Calculates a 5-week purchasing plan and identifies the current week's recommendation.

    Args:
        total_allotment_oz: The user's total 35-day allotment in ounces.
        start_date_str: The start date of the 35-day cycle in 'YYYY-MM-DD' format.

    Returns:
        A dictionary containing the detailed 5-week plan and the current week's action.
    """
    if total_allotment_oz <= 0:
        return {
            "error": "Allotment must be a positive number."
        }
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Invalid date format. Please use YYYY-MM-DD."}

    # 1. Convert total allotment from ounces to grams.
    total_allotment_grams = total_allotment_oz * OUNCES_TO_GRAMS

    # 2. Calculate the total number of 3.5g units that can be purchased over 35 days.
    # We use integer division to ensure we don't exceed the allotment.
    total_units_in_cycle = int(total_allotment_grams // DISPENSARY_INCREMENT_GRAMS)

    # 3. Distribute these units across the 5-week cycle.
    base_weekly_units = total_units_in_cycle // ALLOTMENT_PERIOD_WEEKS
    extra_units_to_distribute = total_units_in_cycle % ALLOTMENT_PERIOD_WEEKS

    # 4. Create the full 5-week plan.
    weekly_plan = []
    for week_num in range(1, ALLOTMENT_PERIOD_WEEKS + 1):
        units_for_this_week = base_weekly_units
        if extra_units_to_distribute > 0:
            units_for_this_week += 1
            extra_units_to_distribute -= 1
        
        weekly_plan.append({
            "week": week_num,
            "units_to_buy": units_for_this_week,
            "grams_to_buy": units_for_this_week * DISPENSARY_INCREMENT_GRAMS
        })

    # 5. Determine the current week and the recommendation for it.
    today = datetime.date.today()
    days_into_cycle = (today - start_date).days
    current_week_num = (days_into_cycle // DAYS_IN_WEEK) + 1
    
    current_week_recommendation = None
    if 1 <= current_week_num <= 5:
        current_week_recommendation = weekly_plan[current_week_num - 1]

    total_grams_purchased = total_units_in_cycle * DISPENSARY_INCREMENT_GRAMS
    grams_leftover = total_allotment_grams - total_grams_purchased

    return {
        "total_allotment_oz": total_allotment_oz,
        "total_allotment_grams": round(total_allotment_grams, 2),
        "total_purchasable_units": total_units_in_cycle,
        "total_grams_purchased_in_cycle": round(total_grams_purchased, 2),
        "grams_leftover_at_end_of_cycle": round(grams_leftover, 2),
        "current_week_recommendation": current_week_recommendation,
        "full_5_week_plan": weekly_plan
    }

# Example Usage:
if __name__ == "__main__":
    # This block now serves as a simple test case for the function.
    # The main application logic is in reup_app.py
    print("--- Testing reup_calculator.py ---")
    
    # Example: Cycle started 8 days ago
    test_start_date = (datetime.date.today() - datetime.timedelta(days=8)).strftime('%Y-%m-%d')
    recommendation = calculate_purchase_for_cycle(3.25, test_start_date)

    if "error" in recommendation:
        print(f"Error: {recommendation['error']}")
    else:
        current_rec = recommendation.get("current_week_recommendation")
        print(f"Test Start Date: {test_start_date}")
        print(f"Current Recommendation: {current_rec}")
        print("\nFull Plan:")
        print(recommendation.get("full_5_week_plan"))
