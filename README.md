# OnsiteHotelBookingSystem

## Overview

### This is a simple model of a real-life hotel booking system designed to simulate the process of booking customers into hotel rooms. Unlike real-life booking systems, this version is optimized for speed, allowing users to explore its features faster:

1. Customers are automatically evicted after 1 minute and 25 seconds using the AutomateCustomerLeave function.
2. The system supports 5 rooms only for simplicity.
3. The booking system does not offer 24/7 service. It only runs while the script is active, but the system saves the previous state so you can resume the booking process later.
4. Time is based on the local machine’s clock (e.g., laptop or phone), not the database.


## Features and Functions
1. Add Customer: Book customers into rooms. Note that there are only 5 rooms available at once.
2. Delete Customer: Remove customers and their bookings.
3. Queueing System: Automatically queue customers when no rooms are available and assign them once rooms are vacated.
4. Automatic Room Eviction: Customers are removed from their room after 1 minute and 25 seconds, freeing the room for new customers.
5. Trigger Notifications: Track the history of room bookings and see the past appointments.


## Prerequisites
1. Python version **3.10 or higher**.
2. MySQL server (local or cloud-based).
3. MySQL Connector for Python: **mysql-python-connector** package for Python.

**Note:**
- Enter **pip install mysql-python-connector** on a terminal just in case the package does not exist in your local machine. 

## How to use
1. Run the main script **MyHotel_BookingSystem.py** on a terminal.

2. Enter your MySQL server credentials. 

**Example:**

![Example Image](https://uc07eb1c75dd6d6f77e6002ab6a8.previews.dropboxusercontent.com/p/thumb/ACayKe3fZKGIPMT8QDZpwaYefcBEJLkWMCDjnz7m8FLBZmlFA6T0P_Qri8zjwcnU3NBntg4nP1DhHmAn2rfAmeaOdVOIgZe7oewDAXeBFib1jM-0AAoNocTnGowDGFeGsPsOLxNx-AjbhK0hYN_PDVGrxuSVGZXZv7qu6EPDJGBnqAePUWANc9xNoE2jDuHCEZ1jkdtlSFWma3_Ibki8wWR2rbhd0QSpBNgmXDXGgHJB3U_FTQemMe5SAYfutv5CeQ2wEmUrzPQLoXWm47dRoe5-FNJU9DEUglsxTjXQBuYvQsErxmkliDpylrD1MkCgJ0WUOdrb-tqSue0XuJr7At4XWEQis8Aw05JcrqirIiF75s_QDW0os-wptLdxvmyneg8/p.png?is_prewarmed=true)

3. Once the connection to the database is established and initialized, you will see the main menu.

**Example:**

![Example Image](https://uc8010a8bcb5d626c7cb106c8625.previews.dropboxusercontent.com/p/thumb/ACaRkCqC8RyZL_WCI2qL6Nm5mzRIFQbVpyGCIhVlz6ElG0QfjwUs_-vl2sJ2rS-TIwynGA20tiVzyu639o0uKYW2S6GLrrTZF4dj8eGJe6UIiFj_Txiy_PzjKHfegEf-CFKK8O_ebPcHC6jYqnPVCLWa4wS7BqFaEM0nP9IVpB4ku0Tvm_vuCx4jDrpZOppupE36qhf6QbJ0SrCaoWMr6Ml7Av8bpEUX9o_FE4BH08brpStiM8RamnSMAM8cDlyPH9BTp3gVTlcVP09Ds5auWrSDG3Lz33XX7_fgr5IqoLdISdgFueP2HBQp94cCK9vLpDrSSoGsJKZBNxS1JQm_mkcw-gYoQeB_KKXxYXYYoj0QCc-neef70bqVb5Mcp_fXqnE/p.png?is_prewarmed=true)

**Note**: You will be prompted for an input. In this case, only input integers from 1 to 5.

## What each function in the menu does
1. **Add Customer**
- This adds a customer to the database and then appoints it to a vacant room. If there are no vacant rooms, the customer is queued until a room becomes available and is automatically appointed a room.

2. **Delete Customer**
- This removes every record of a customer in the database associated with the inputted name. This also includes a customer who occupies a room.

3. **Show All Past Room Appointements**
- This displays the history of customers who occupied the rooms (and their customer IDs).

4. **Refresh**
- Does nothing.

5. **Exit**
- This terminates the running program.

## Important Notes
- This hotel booking system does not run 24/7. It only functions when the script is running. However, it does save the system's current state to a MySQL database. When you restart the script, it resumes from the saved state.
- The system is designed to work faster than a real hotel booking system to allow users to see its features more quickly. Each customer can only stay in a room for 1 minute and 25 seconds before being evicted.
- The system operates on local machine time, not on the time set in the MySQL database.
