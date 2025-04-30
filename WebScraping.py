# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---


# %% [markdown]
import streamlit as st
# Web Scraping (Loay)

# %%
import requests
import ast
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import csv



# %%
# Problem Encountered: HTTP Error 429, Too many requests
# Website blocks scraping and assumes we are a bot and immediately blocks us
# Use headers to trick website into thinking program is actually a browser, this effectively allows us to access the website and scrape it

url = "https://remoteok.com/remote-dev-jobs"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

src = requests.get(url, headers=headers)
soup = BeautifulSoup(src.content)


# %%
listed_jobs = soup.find_all("tr", {"class":"job"})
print(listed_jobs)


# %%
# Problem Encountered: Not all data loaded; must scroll to scrape it
# Install Selenium and use it to launch a Chrome instance of the website
# Script runs and scrolls to the end then all data is loaded and we can now scrape all/most 3ashan mankonsh kadabeen
# Store data in txt file to not run script every time, commented out for now

#from selenium import webdriver
#from selenium.webdriver.common.by import By

#path_to_file = "W:/Loay/Python Projects/ToolsProject/"

#driver = webdriver.Chrome()
#driver.maximize_window()

#driver.get(url)

#last_height = 0

#while True:
#    driver.execute_script('window.scrollBy(0, 5000)')
#    time.sleep(4)

#    new_height = driver.execute_script("return document.body.scrollHeight")

#    if(new_height == last_height):
#        break

#    else:
#        last_height = new_height

#page_source = driver.page_source

#f = open(path_to_file+"source.txt","w",encoding="utf-8")
#f.write(page_source)
#f.close()

#driver.close()


# %%
# Scrape html stored in txt file
import re
import numpy as np
from bs4 import BeautifulSoup

f = open(r"D:\GitHub\ToolsProject\source.txt",'r',encoding='utf-8')
page_source = f.read()
f.close()
soup = BeautifulSoup(page_source)

#TODO: Get Job details and store in dictionary and convert it to csv file

listed_jobs = soup.find_all("tr", {"class":"job"})
df_roles = []
df_organizations = []
df_locations = []
df_time_posted = []
df_tags = []
df_expected_salary = np.zeros(len(listed_jobs), dtype='object')
for i in range(0, len(listed_jobs)):
    role = listed_jobs[i].find("h2").text.strip()
    organization = listed_jobs[i].find("h3").text.strip()
    html_location = listed_jobs[i].find_all("div", {"class": "location"})
    locations = []
    for j in html_location:
        if (str(j.contents)[2] == '💰'):
            salary_str = str(j.contents)
            salary_str = salary_str[4:-2]  # Clean string to get only salary part
            matches = re.findall(r'[0-9]{2,3}', salary_str)
            if len(matches) == 2:
                min_salary, max_salary = int(matches[0]), int(matches[1])
                avg_salary = min_salary + max_salary / 2.0
                df_expected_salary[i] = avg_salary
            elif len(matches) == 1:
                df_expected_salary[i] = int(matches[0])
            else:
                df_expected_salary[i] = None
        else:
            locations += j.contents

    locations = re.sub(r'<.*?>', r"", str(locations))
    html_time = listed_jobs[i].find("time")
    time_posted = re.sub(r'<.*?>', r'', (str(re.sub(r"[\t\n]", r"", str(html_time)))))
    html_tags = listed_jobs[i].find("td", {"class": "tags"}).find_all('h3')
    tags = [re.sub(r'<.*?>', r'', re.sub(r'[\s\t\n]', r'', str(i))) for i in html_tags]
    
    df_roles.append(role)
    df_organizations.append(organization)
    df_locations.append(locations)
    df_time_posted.append(time_posted)
    df_tags.append(tags)

data = {'Role':df_roles, 'Organization':df_organizations, 'Locations':df_locations, 'Time_Posted':df_time_posted, 'Tags':df_tags, 'Expected_Salary (*1000$)':df_expected_salary}
# Scraped 1033 listed jobs

# %% [markdown]
#pressed = st.button("# Imported Scraped Data")

# %%
import pandas as pd
df = pd.DataFrame(data)
df.to_csv('Scraped Data.csv')
df = pd.read_csv("D:\GitHub\ToolsProject\Scraped Data.csv")
#if pressed :
#    st.dataframe(df) 



# %%
print(df.isnull().sum())

# %%
mean = df["Expected_Salary (*1000$)"].mean()
df["Expected_Salary (*1000$)"].fillna(mean, inplace = True)


# %%
print(df.isnull().sum())

# %%
df.head()


# %%
def parse_duration(x):
    if pd.isna(x):
        return np.nan #NaN
    num = int(''.join(filter(str.isdigit, x)))  
    unit = ''.join(filter(str.isalpha, x)).lower()  
    
    if unit == 'h':
        return pd.Timedelta(hours=num)
    elif unit == 'd':
        return pd.Timedelta(days=num)
    elif unit == 'mo':
        return pd.Timedelta(minutes=num)
    elif unit == 'yr':  
        return pd.Timedelta(days=num * 365)  
    else:
        return np.nan 

df['Time_Posted_parsed'] = df['Time_Posted'].apply(parse_duration)


now = pd.Timestamp.now()


df['Actual_Time'] = now - df['Time_Posted_parsed']


df['Actual_Time'] = df['Actual_Time'].dt.date





# %%
df = df.drop("Time_Posted_parsed" , axis = 1)
df = df.drop("Time_Posted" , axis = 1)

# %%
df.rename(columns={'Actual_Time': 'Date_Posted'}, inplace=True)



# %%


df['Locations'] = df['Locations'].apply(
    lambda x: '['+ re.sub(r'[^\w\s,]', '', str(x).lstrip('[').rstrip(']')) + ']'
)
df['Locations'] = df['Locations'].str.replace(r'\s+', ' ', regex=True).str.strip()





# %%
print(df.duplicated().sum())

# %%
df.info()

# %%
df['Role'].unique()

# %%
df['Role'].nunique()

# %%
df['Role'].value_counts()

# %%
import ast

def safe_parse(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except:
            return [x]  
    return [x]

df['Tags'] = df['Tags'].apply(safe_parse)


# %%
# separates every single tag in the array 
#df = df.explode('Tags')
print(df.explode('Tags'))


# %%
df.explode('Tags')['Tags'].unique()


# %%
df.explode('Tags')['Tags'].nunique()


# %%
df.explode('Tags')['Tags'].value_counts()


# %%
def add_quotes_to_list_string(cell):
    if isinstance(cell, str):
        # Remove the brackets first
        cell = cell.strip('[]')
        # Split by comma
        items = [item.strip() for item in cell.split(',') if item.strip()]
        # Add quotes
        quoted_items = [f'"{item}"' for item in items]
        # Rebuild the string with brackets
        return '[' + ', '.join(quoted_items) + ']'
    else:
        return cell

df['Locations'] = df['Locations'].apply(add_quotes_to_list_string)


# %%
import ast

def safe_parse(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except:
            return [x]  
    return [x]

df['Locations'] = df['Locations'].apply(safe_parse)

# %%
# separates every single tag in the array 
#df = df.explode('Locations')
print(df.explode('Locations'))


# %%
df.explode('Locations')['Locations'].unique()


# %%
df.explode('Locations')['Locations'].nunique()


# %%
df.explode('Locations')['Locations'].value_counts()




# %%
df.drop(columns='Unnamed: 0', inplace=True)


# %%
import matplotlib.pyplot as plt

#plt.figure(figsize=(40, 10))  # ⬅️ Make it very wide
#plt.bar(df['Role'], df['Expected_Salary (*1000$)'], width=0.8)  # Optional: width=bar thickness
#plt.xlabel('Role')
#plt.ylabel('Expected Salary (*1000$)')

#plt.xticks(rotation=90)
#plt.tight_layout()
#plt.show()



# %%
role_salary_df = df[['Role', 'Expected_Salary (*1000$)']]
print(role_salary_df.sample(10))

# %%
df.to_csv('Scraped Data.csv') # Update csv file with our formatted data, this same data will be stored in MongoDB
df['Organization'].value_counts()

#%%
#geting the value counts of locations
locations_count = df.explode('Locations')['Locations'].value_counts()

#gets top 5 locations and their counts and put any thing else in others
sizes = locations_count.head().values
labels = locations_count.head().index.tolist()

#adding a category named "others" if there are more locations (more the first than 5)
if len(locations_count) > 5:
    others_count = locations_count[6:].sum()
    sizes = np.append(sizes, others_count)
    labels.append('Others')

colors = ['purple','#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'][:len(labels)]

#pie chart
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.axis('equal')
plt.show()


# %%
ax = plt.gca()
ax.hist(df['Expected_Salary (*1000$)'],color='purple')
plt.title('Distribution of the expected salary')
plt.xlabel('Salary')
plt.ylabel('Frequency')
plt.show()

# %%
Year = pd.DatetimeIndex(df['Date_Posted']).year
mean_salary = df.groupby(Year)['Expected_Salary (*1000$)'].mean().reset_index()

plt.plot(mean_salary['Date_Posted'],mean_salary['Expected_Salary (*1000$)'],color='purple',marker='o')
plt.title('Salary VS Time')
plt.xlabel('Time')
plt.ylabel('Salary')
plt.show()


# %%
tag_count = df['Tags'].explode().value_counts().reset_index()

plt.figure(figsize=(69, 10))
plt.bar(tag_count['Tags'], tag_count['count'], color = 'purple')
plt.title('Tags and their frequency')
plt.xlabel('Tags')
plt.ylabel('Frequencies')
plt.xticks(rotation=90)
plt.show()


#%%
#get top 5 most frequent tags
top_tags = df['Tags'].explode().value_counts().head(5).index

#filtering df to just include the top tags
df_top_tags = df[df['Tags'].apply(lambda x: any(tag in x for tag in top_tags))]

#calculating the salary mean by tag (explode first to handle list-type tags)
mean_salaries = df_top_tags.explode('Tags').groupby('Tags')['Expected_Salary (*1000$)'].mean().loc[top_tags]

#create bar plot
plt.figure(figsize=(10, 6))
mean_salaries.plot(kind='bar', color='purple')
plt.title('Mean Salary by Top 5 Most Frequent Tags')
plt.xlabel('Tags')
plt.ylabel('Mean Salary (in thousands)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# Data Storage Using MongoDB (Loay)

# %%

#from pymongo import MongoClient
#import datetime
#client = MongoClient("mongodb://localhost:27017/")
#mydb = client['RemoteOk']
#for organ in df['Organization'].unique():
#    while organ[-1] ==  '.':
#        organ = organ[0:-1] # organization has a . at the end of its name causes error with driver
#    col = mydb[organ]
#    for job in df.index:
#        d = datetime.datetime.strptime(str(df.loc[job, 'Date_Posted']), "%Y-%m-%d")
#        if df.loc[job, 'Organization'] == organ:
#            item = {
#                "Role":df.loc[job, 'Role'],
#                "Locations":df.loc[job, 'Locations'],
#                "Tags":df.loc[job,'Tags'],
#                "Expected_Salary in $1,000":df.loc[job, 'Expected_Salary (*1000$)'],
#                "Date_posted":d
#            }
#            col.insert_one(item)


# %% [markdown]
import plotly.express as px
st.header(" Data after cleaning")

st.dataframe(df)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total rows",value = len(df))
with col2:
    st.metric(label="Total columns",value= len(df.columns))

st.header('Charts :')
#pie chart
pie = px.pie(
    values=sizes,
    names=labels,
    color_discrete_sequence=['purple', '#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'],
    title='Distribution of Locations'
)
st.plotly_chart(pie)

#hist
hist = px.histogram(
    df,
    x='Expected_Salary (*1000$)',
    color_discrete_sequence=['#be2ed6'], 
    title='Distribution of the Expected Salary',
    labels={'Expected_Salary (*1000$)': 'Salary (in thousands $)'}
)
hist.update_layout(
    xaxis_title='Salary (in thousands $)',
    yaxis_title='Frequency',
    bargap=0.1, 
)
st.plotly_chart(hist)

#line
line = px.line(
    mean_salary,
    x='Date_Posted', 
    y='Expected_Salary (*1000$)',
    title='Salary Trends Over Time',
    labels={
        'Date_Posted': 'Year',
        'Expected_Salary (*1000$)': 'Average Salary (in thousands $)'
    },
    markers=True 
)
line.update_traces(
    line_color='#be2ed6',
    line_width=2,
    marker=dict(
        size=8,
        color='#e8bcf0',
        line=dict(width=1, color='white')
    )
)
line.update_layout(
    xaxis_title='Year',
    yaxis_title='Average Salary (in thousands $)',
    hovermode='x unified' 
)
st.plotly_chart(line)
    
#bar
tag_count.columns = ['Tags', 'Count']
bar = px.bar(
    tag_count,
    x='Tags',
    y='Count',
    title='Tags and Their Frequencies',
    labels={'Count': 'Frequency', 'Tags': 'Tags'},
    color_discrete_sequence=['#be2ed6'] 
)
bar.update_layout(
    xaxis_title='Tags',
    yaxis_title='Frequency',
    xaxis_tickangle=-90, 
    height=600,
    width=1200, 
    margin=dict(l=20, r=20, t=60, b=200)
)
st.plotly_chart(bar, use_container_width=True)


#streamlit run "The file directory without quotes"