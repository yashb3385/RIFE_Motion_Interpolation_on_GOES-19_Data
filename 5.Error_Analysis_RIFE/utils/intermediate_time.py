from datetime import datetime

def inter_time(year1, day1, hr1, min1, year2, day2, hr2, min2):
    # Convert inputs to datetime objects using day-of-year (%j)
    dt1 = datetime.strptime(f"{year1} {day1:03d} {hr1:02d} {min1:02d}", "%Y %j %H %M")
    dt2 = datetime.strptime(f"{year2} {day2:03d} {hr2:02d} {min2:02d}", "%Y %j %H %M")

    # Calculate the intermediate (midpoint) time
    dt_inter = dt1 + (dt2 - dt1) / 2

    # Extract back to year, day of year, hour, and minute
    year_inter = dt_inter.year
    day_inter = int(dt_inter.strftime("%j"))
    hr_inter = dt_inter.hour
    min_inter = dt_inter.minute
    return year_inter, day_inter, hr_inter, min_inter
