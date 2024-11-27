import config
import streamlit as st
import pandas as pd
import datetime
import functions
import plotly.express as px
import matplotlib as plt

functions.set_page_definitition()
st.title("Petitabytes PoC")

df = pd.read_csv("data/2024-11-26T14-44_export_ezyVet_gardenVets.csv", low_memory=False)
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])
df['month_year'] = pd.to_datetime(df['Invoice Date']).dt.to_period('M')

df.info()

col1, col2 = st.columns([1, 1])

with col1:

    #insert user input for start and end date based on the dates in "Invoice Date"
    start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))

with col2:
    end_date = st.date_input("End Date", datetime.date(2024, 12, 31))

# Convert start_date and end_date to datetime64[ns] for comparison
start_date = pd.to_datetime(start_date)

end_date = pd.to_datetime(end_date)

# apply date filter
df = df[(df['Invoice Date'] >= start_date) & (df['Invoice Date'] <= end_date)]

# st.dataframe(df)

# create a streamlit box to show the total number of consults in the period
st.subheader('Consults')

# count unique values in 'Consult Number' column and put in variable 'consult_count'
consult_count = df['Consult Number'].nunique()
st.write('Total number of consults in this period:', consult_count)

# count of unique values in Consult Number column where at least one item in column 'Product Category' is 'Vaccination'
vaccination_consult_count = df[df['Product Category'].str.contains('Vaccination', na=False)]['Consult Number'].nunique()
st.write('Number of consults with at least one vaccination invoice line:', vaccination_consult_count)

# show vaccinations_by_species in % of consult_count    (vaccination_consult_count / consult_count) * 100
vaccination_percentage = (vaccination_consult_count / consult_count) * 100
st.write('Percentage of consults with at least one vaccination invoice line:', f"{vaccination_percentage:.2f}%")

st.write('---')

st.subheader('Vaccinations by Species')

col1, col2 = st.columns([1, 1])
with col1:
    st.write('Number of vaccinations by species')
    # create a new dataframe with only the 'Consult Number', 'Product Category', 'Species', 'Breed', 'month_year' columns
    vaccination_consults = df[['Consult Number', 'Product Category', 'Species', 'Breed', 'month_year']]
    # Only show rows where 'Product Category' contains 'Vaccination'
    vaccination_consults = vaccination_consults[vaccination_consults['Product Category'].str.contains('Vaccination', na=False)]
    # remove duplicates
    vaccination_consults = vaccination_consults.drop_duplicates()
    # create a new dataframe where each unique value in month_year is a column and each unique value in 'Species' is a row.  The cells should contain the count of 'Product Category' entries
    vaccination_consults = vaccination_consults.groupby(['month_year', 'Species']).size().reset_index(name='count')

    # Pivot the DataFrame
    vaccination_consults = vaccination_consults.pivot(index='Species', columns='month_year', values='count')

    # Fill NaN values with 0
    vaccination_consults = vaccination_consults.fillna(0)

    st.dataframe(vaccination_consults)

with col2:
    st.write('Percentage of vaccinations by species')
    percentage_df = (vaccination_consults / vaccination_consult_count) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)

# insert streamlit line
st.write('---')


col1, col2 = st.columns([1, 1])
with col1:

    # count of entries in 'Product Category' column where 'Product Category' is 'Vaccination'
    total_vaccination = df[df['Product Category'].str.contains('Vaccination', na=False)]['Product Category'].count()
    st.write('Total number of vaccinations administered in this period:', total_vaccination)

    # make a table showing one column per entry in 'year_month' column and one row per unique value in 'Species' column.  the cells should contain the respectie vaccination_count
    df_vaccination = df[df['Product Category'].str.contains('Vaccination', na=False)]   # filter for rows where 'Product Category' contains 'Vaccination'
    df_vaccination = df_vaccination.groupby(['month_year', 'Species']).size().reset_index(name='count')  # group by 'month_year' and 'Species' and count the number of rows in each group
    df_vaccination = df_vaccination.pivot(index='Species', columns='month_year', values='count')  # pivot the table so that the 'month_year' values become columns
    df_vaccination = df_vaccination.fillna(0)
    st.dataframe(df_vaccination)

with col2:
    st.write('Percentage of vaccinations by species')
    percentage_df = (df_vaccination / total_vaccination) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)

# make a bar chart showing the number of vaccinations by mont




# fig = px.bar(df_vaccination, x='month_year', y='count', title='Vaccinations by Month')
# st.plotly_chart(fig)



# df_grouped = df.groupby(['Animal Code'])
# st.dataframe(df_grouped)






#
# # add two streamlit columns
# col1, col2 = st.columns([1, 1])
#
# with col1:
# # group by 'Animal Code' and 'Species' and show a table of percentage of each Species
#     df_grouped = df.groupby(['Animal Code', 'Species']).size().reset_index(name='count')
#     df_grouped['percentage'] = (df_grouped['count'] / df_grouped['count'].sum()) * 100
#     st.write(df_grouped)
#
# with col2:
#     # group by 'Animal Code' and make an interactive pie chart showing species and breed
#     df_grouped = df.groupby(['Species']).size().reset_index(name='count')
#     df_grouped['percentage'] = (df_grouped['count'] / df_grouped['count'].sum()) * 100
#     fig = px.pie(df_grouped, values='count', names='Species', title='Distribution by Species',
#                  hover_data=['count', 'percentage'], labels={'count': 'Count', 'percentage': 'Percentage'})
#     fig.update_traces(textinfo='label+percent')
#     st.plotly_chart(fig)
#
# # make a sunburst chart showing the distribution of species and breed
# df_grouped = df.groupby(['Species', 'Breed']).size().reset_index(name='count')
# fig = px.sunburst(df_grouped, path=['Species', 'Breed'], values='count')
# st.plotly_chart(fig, use_container_width=True)
