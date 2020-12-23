import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import shutil

# create new output folder
shutil.rmtree('output')
os.makedirs('output')

# import violations dataset
Violations = pd.read_csv('input/Violations.csv')
Violations.info


# import active projects dataset
Active_Projects = pd.read_csv('input/cartodb-query.csv')
Active_Projects.info

# count the number of active projects per month
project_count = {f'{month}/{year}': 0 for year in (19, 20) for month in range(1, 13)}
for date in Active_Projects['permit_issuance_date']:
    month = date.split('/')[0]
    year = date.split('/')[2][2:]
    project_count[f'{month}/{year}'] += 1
# plot number of active projects per month
plt.plot(project_count.keys(), project_count.values())
plt.xticks(rotation=90)
plt.title('Number of Permits Granted Per Month')
plt.xlabel('Month')
plt.ylabel('Permits Granted')
plt.savefig('output/permits_granted.png')
plt.close()
    #The data for permits shows the number of construction permits granted over the past 2 years. The dip in March-May is explained by the NYS COVID shutdown 
    #The dip in August may be a return to normal due to the increase from May-July due to the shutdown (for permits)
    #The major dip after February for the violations can also be attributed to the NYS COVID shutdown.

# count the number of violations per month
project_count = {f'{month}/{year}': 0 for year in (19, 20) for month in range(1, 13)}
for date in Violations['ISSUE_DATE']:
    month = str(date)[4:6]
    if month[0] == '0':
        month = month[1]
    year = str(date)[2:4]
    project_count[f'{month}/{year}'] += 1
for key in project_count:
    if project_count[key] == 0: # remove all months with zero projects from plot
        project_count[key] = None
# plot violations per month
plt.plot(project_count.keys(), project_count.values())
plt.xticks(rotation=90)
plt.title('Violations Per Month')
plt.xlabel('Month')
plt.ylabel('Violations')
plt.savefig('output/violations.png')
plt.close()

# get date range from user
startDate = None
endDate = None
daterange = input('Enter date range in format MM/YYYY-MM/YYYY (or leave blank to skip): ')
if len(daterange.strip()) > 0:
    dates = daterange.split('-')
    if len(dates) == 2:
        startDateStr = dates[0]
        endDateStr = dates[1]
        try:
            startDate = datetime.datetime.strptime(startDateStr, '%m/%Y')
            endDate = datetime.datetime.strptime(endDateStr, '%m/%Y')
        except ValueError:
            pass

# map user input to actual borough name
boroughs = {
    '1': 'Manhattan',
    '2': 'The Bronx',
    '3': 'Brooklyn',
    '4': 'Queens',
    '5': 'Staten Island',
}

# get borough from user
borough = input('(1) Manhattan\n(2) The Bronx\n(3) Brooklyn\n(4) Queens\n(5) Staten Island\nEnter a borough (or leave blank to skip): ')
company_name = input('Enter company name (or leave blank to skip): ')

with open('output/violations.txt', 'a') as the_file: # output violations to a file
        for index in [i for i, item in enumerate(Active_Projects['applicant_business_name'].values) if company_name.lower() in str(item).lower()]:
            # if address matches, add  to violations output
            if Active_Projects['job_location_street_name'][index] in Violations['STREET'].values and Active_Projects['job_location_house_number'][index] in Violations['HOUSE_NUMBER'].values:
                violation_index = -1
                for i, (street, number) in enumerate(zip(Violations['STREET'].values, Violations['HOUSE_NUMBER'].values)):
                    if street == Active_Projects['job_location_street_name'][index]:
                        violation_index = i
                        break
                date = str(Violations['ISSUE_DATE'][violation_index])
                dateobj = datetime.datetime.strptime(date, '%Y%m%d')

                # if the user entered a valid date range, only output this project if it falls within the range
                if (startDate is None or endDate is None) or (dateobj > startDate and dateobj < endDate):
                    print(f'{Active_Projects["job_location_house_number"][index]} {Active_Projects["job_location_street_name"][index]}, {boroughs.get(borough)} NY ({Active_Projects["applicant_business_name"].values[index]}) (Issue Date: {date})')
                    the_file.write(f'{Active_Projects["job_location_house_number"][index]} {Active_Projects["job_location_street_name"][index]}, {boroughs.get(borough)} NY ({Active_Projects["applicant_business_name"].values[index]}) (Issue Date: {date})\n')

