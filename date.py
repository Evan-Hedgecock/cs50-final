from datetime import date, timedelta

today = date.today()

for m in range(5):
    print(today + timedelta(weeks=+(m * 4)))