import requests
from bs4 import BeautifulSoup
import time
import csv
import os
from unidecode import unidecode

job_positions = [
    "Data Scientist",
    "Software Engineer",
    "Product Manager",
    "UX Designer",
    "Business Analyst",
    "Marketing Manager",
    "Financial Analyst",
    "Project Manager",
    "HR Manager",
    "Sales Representative"
]

base_url = "https://www.glassdoor.co.in"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
position_data = {}

# Scrape data from GlassDoor
for i, position in enumerate(job_positions):
    urlPosition = position.lower().replace(' ', '-')

    avgSalaryURL = f"{base_url}/Salaries/india-{urlPosition}-salary-SRCH_IL.0,5_IN115_KO6,{len(position)+6}.htm"
    avgSalaryResponse = requests.get(avgSalaryURL, headers=headers)

    url = f"{base_url}/Job/{urlPosition}-jobs-SRCH_IL.0,5_IN115_KO0,{len(position)}.htm"
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and avgSalaryResponse.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        avgSalarySoup = BeautifulSoup(avgSalaryResponse.content, "html.parser")

        salary_elements = soup.find_all(class_="salary-estimate", limit=20)
        avgSalary = avgSalarySoup.find(attrs={"data-test": "occ-median-average-pay"})

        if salary_elements:
            print(position)
            position_data[position] = []
            for salary_element in salary_elements:
                salary = salary_element.contents[0].strip()
                location = unidecode(salary_element.previous_sibling.contents[0].strip())
                position_data[position].append({"salary": salary, "location": location, "avg": avgSalary.text})
                print("Salary: ", salary, "Location: ", location, "Average Pay: ", avgSalary.text)
            print()
            time.sleep(2)
        else:
            print("Salary information not found on this page. ", url)
    else:
        print("Failed to retrieve the webpage.")

# Get user input for generating CSV
job_positions_lower = [position.lower() for position in job_positions]
while True:
    selected_position = input("Enter a position to filter by (or type 'All'): ").lower()
    if selected_position == "all" or selected_position in job_positions_lower:
        break
    else:
        print("Invalid position. Please try again.")
selected_location = input("Enter a location to filter by (or type 'All'): ").lower()

# Filter data based on input
filtered_data = []
for position, data_list in position_data.items():
    if selected_position == "all" or position.lower() == selected_position:
        for data in data_list:
            if selected_location == "all" or data["location"].lower() == selected_location:
                filtered_data.append({"position": position, **data})

# Generate CSV
csv_filename = "job_data.csv"
print("Current Working Directory:", os.getcwd())

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    
    # Write header
    header = ["Position", "Location", "Salary", "Average Salary"]
    csv_writer.writerow(header)

    for data in filtered_data:
        position = data["position"]
        location = data["location"]
        salary = data["salary"]
        averageSalary = data["avg"]
            
        # Write data to CSV
        data_row = [position, location, salary, averageSalary]
        csv_writer.writerow(data_row)