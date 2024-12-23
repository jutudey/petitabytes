import pandas as pd
import datetime
import functions
import hmac
import streamlit as st
# from streamlit_scroll_navigation import scroll_navbar
import config
import plotly.express as px
import matplotlib as plt


if not functions.check_password():
    st.stop()  # Do not continue if check_password is not True.

functions.set_page_definitition()
st.title("📊  Petitabytes")

df = pd.read_csv("data/2024-11-26T14-44_export_ezyVet_gardenVets.csv", low_memory=False)
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])
df['month_year'] = pd.to_datetime(df['Invoice Date']).dt.to_period('M')
# remove rows where 'Species' is NaN
df = df.dropna(subset=['Species'])

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
st.subheader('🩺   Consults')

# count unique values in 'Consult Number' column and put in variable 'consult_count'
consult_count = df['Consult Number'].nunique()
st.write('Total number of consults in this period:', consult_count)

st.write("")
st.write("")
st.write("")

# ------------------------------
# Vaccinations
# ------------------------------


st.subheader('💉   Vaccinations')


# count of unique values in Consult Number column where at least one item in column 'Product Category' is 'Vaccination'
vaccination_consult_count = df[df['Product Category'].str.contains('Vaccination', na=False)]['Consult Number'].nunique()
st.write('Number of consults with at least one vaccination administered:', vaccination_consult_count)

# show vaccinations_by_species in % of consult_count    (vaccination_consult_count / consult_count) * 100
vaccination_percentage = (vaccination_consult_count / consult_count) * 100
st.write('Percentage of total number of consults with at least one vaccination:', f"{vaccination_percentage:.2f}%")

# count of entries in 'Product Category' column where 'Product Category' is 'Vaccination'
total_vaccination = df[df['Product Category'].str.contains('Vaccination', na=False)]['Product Category'].count()
st.write('Total number of vaccinations administered in this period:', total_vaccination)


st.write('---')


col1, col2 = st.columns([1, 1])
with col1:
    st.write('Number of vaccination consults by species')
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
    st.write('Percentage by species')
    percentage_df = (vaccination_consults / vaccination_consult_count) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)

# insert streamlit line
st.write('---')


col1, col2 = st.columns([1, 1])
with col1:

    st.write('Total number of vaccinations administered by species')

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


st.write("")
st.write("")
st.write("")

# ------------------------------
# Neuters
# ------------------------------
subject = 'Neuters'
st.subheader('✂️   Neuters')

# count of unique values in Consult Number column where at least one item in column 'Product Category' is 'Vaccination'
subject_consults = df[df['Product Name'].isin(['Bitch Spay',
                                              'Cat Spay',
                                              'Dog Castration',
                                              'Cat Castration',
                                              'Dog Castration (retained/scrotal ablation)',
                                              'Repro - Rabbit Castration'])]
# st.write('Number of neuters:', neuter_count)
# st.dataframe(subject_consults)

subject_consults_count = subject_consults.shape[0]
st.write('Total number of ' + subject + ' in this period:', subject_consults_count)

# show vaccinations_by_species in % of consult_count    (neuter_count / consult_count) * 100
subject_percentage = (subject_consults_count / consult_count) * 100
st.write(subject + ' in percentage of total number of consults:', f"{subject_percentage:.2f}%")

st.write('---')

col1, col2 = st.columns([1, 1])
with col1:
    st.write('Number of ' + subject + ' by species')
    # create a new dataframe with only the 'Consult Number', 'Product Category', 'Species', 'Breed', 'month_year' columns
    subject_consults = subject_consults[['Consult Number', 'Product Category', 'Species', 'Breed', 'month_year']]
    # remove duplicates
    subject_consults = subject_consults.drop_duplicates()
    # create a new dataframe where each unique value in month_year is a column and each unique value in 'Species' is a row.  The cells should contain the count of 'Product Category' entries
    subject_consults = subject_consults.groupby(['month_year', 'Species']).size().reset_index(name='count')

    # Pivot the DataFrame
    subject_consults = subject_consults.pivot(index='Species', columns='month_year', values='count')

    # Fill NaN values with 0
    subject_consults = subject_consults.fillna(0)

    st.dataframe(subject_consults)

with col2:
    st.write('Percentage of ' + subject + ' by species')
    percentage_df = (subject_consults / vaccination_consult_count) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)


st.write("")
st.write("")
st.write("")

# ------------------------------
# Diagnotics
# ------------------------------
subject = 'Diagnostics'
st.subheader('🩻️   ' + subject)

# count of unique values in Consult Number column where at least one item in column 'Product Category' is 'Vaccination'
subject_consults = df[df['Product Category'] == 'Diagnostic']

# st.dataframe(subject_consults)

subject_consults_count = subject_consults.shape[0]
st.write('Total number of ' + subject + ' in this period:', subject_consults_count)

# show vaccinations_by_species in % of consult_count    (neuter_count / consult_count) * 100
subject_percentage = (subject_consults_count / consult_count) * 100
st.write(subject + ' in percentage of total number of consults:', f"{subject_percentage:.2f}%")

st.write('---')

col1, col2 = st.columns([1, 1])
with col1:
    st.write('Number of ' + subject + ' by species')
    # create a new dataframe with only the 'Consult Number', 'Product Category', 'Species', 'Breed', 'month_year' columns
    subject_consults = subject_consults[['Consult Number', 'Product Category', 'Product Group', 'Product Name', 'Species', 'Breed', 'month_year']]
    # remove duplicates
    subject_consults = subject_consults.drop_duplicates()
    # create a new dataframe where each unique value in month_year is a column and each unique value in 'Species' is a row.  The cells should contain the count of 'Product Category' entries
    subject_consults = subject_consults.groupby(['month_year', 'Species']).size().reset_index(name='count')

    # Pivot the DataFrame
    subject_consults = subject_consults.pivot(index='Species', columns='month_year', values='count')

    # Fill NaN values with 0
    subject_consults = subject_consults.fillna(0)

    st.dataframe(subject_consults)


with col2:
    st.write('Percentage of ' + subject + ' by species')
    percentage_df = (subject_consults / vaccination_consult_count) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)

col1, col2 = st.columns([1, 1])

with col1:
# add a sunburst chart from plotly.express to show the breakdown of diagnostics by species. the hierarchy should be Species -> Product Category -> Product group -> Product Name

    subject_consults = df[df['Product Category'] == 'Diagnostic']
    subject_consults = subject_consults[['Species', 'Product Group', 'Product Name']]

    fig1 = px.sunburst(subject_consults, path=['Species', 'Product Group', 'Product Name'], title='Diagnostics by Species')
    st.plotly_chart(fig1, use_container_width=True)
    st.write('Make the chart interactive by clicking on the slices to show/hide data')
    st.markdown("Click on the :material/Fullscreen: button to view the chart in full screen")

with col2:
    fig2 = px.sunburst(subject_consults, path=['Product Group', 'Species', 'Product Name'], title='Diagnostics by Diagnostic Group')
    st.plotly_chart(fig2, use_container_width=True)


st.write("")
st.write("")
st.write("")


# ------------------------------
# Surgeries
# ------------------------------
subject = 'Surgeries'
st.subheader('🏥   ' + subject)

# count of unique values in Consult Number column where at least one item in column 'Product Category' is 'Vaccination'
subject_consults = df[df['Product Group'] == 'Surgery']
subject_consults = subject_consults[~subject_consults['Product Name'].isin(['Bitch Spay',
                                              'Cat Spay',
                                              'Dog Castration',
                                              'Cat Castration',
                                              'Dog Castration (retained/scrotal ablation)',
                                              'Repro - Rabbit Castration'])]


# st.dataframe(subject_consults)

subject_consults_count = subject_consults.shape[0]
st.write('Total number of ' + subject + ' in this period:', subject_consults_count)

# show vaccinations_by_species in % of consult_count    (neuter_count / consult_count) * 100
subject_percentage = (subject_consults_count / consult_count) * 100
st.write(subject + ' in percentage of total number of consults:', f"{subject_percentage:.2f}%")

st.write('---')

col1, col2 = st.columns([1, 1])
with col1:
    st.write('Number of ' + subject + ' by species')
    # create a new dataframe with only the 'Consult Number', 'Product Category', 'Species', 'Breed', 'month_year' columns
    subject_consults = subject_consults[['Consult Number', 'Product Category', 'Product Group', 'Product Name', 'Species', 'Breed', 'month_year']]
    # remove duplicates
    subject_consults = subject_consults.drop_duplicates()
    # create a new dataframe where each unique value in month_year is a column and each unique value in 'Species' is a row.  The cells should contain the count of 'Product Category' entries
    subject_consults = subject_consults.groupby(['month_year', 'Species']).size().reset_index(name='count')

    # Pivot the DataFrame
    subject_consults = subject_consults.pivot(index='Species', columns='month_year', values='count')

    # Fill NaN values with 0
    subject_consults = subject_consults.fillna(0)

    st.dataframe(subject_consults)


with col2:
    st.write('Percentage of ' + subject + ' by species')
    percentage_df = (subject_consults / vaccination_consult_count) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)

col1, col2 = st.columns([1, 1])

with col1:
# add a sunburst chart from plotly.express to show the breakdown of diagnostics by species. the hierarchy should be Species -> Product Category -> Product group -> Product Name

    subject_consults = df[df['Product Group'] == 'Surgery']
    subject_consults = subject_consults[~subject_consults['Product Name'].isin(['Bitch Spay',
                                                                            'Cat Spay',
                                                                            'Dog Castration',
                                                                            'Cat Castration',
                                                                            'Dog Castration (retained/scrotal ablation)',
                                                                            'Repro - Rabbit Castration'])]

    fig4 = px.sunburst(subject_consults, path=['Species', 'Product Name'], title=f"{subject} by Species")
    st.plotly_chart(fig4, use_container_width=True,  key="Surgeries1")
    st.write('Make the chart interactive by clicking on the slices to show/hide data')
    st.markdown("Click on the :material/Fullscreen: button to view the chart in full screen")
#
# with col2:
#     fig3 = px.sunburst(subject_consults, path=['Product Group', 'Species', 'Product Name'], title='Diagnostics by Diagnostic Group')
#     st.plotly_chart(fig3, use_container_width=True, key='Surgeries2')


st.write("")
st.write("")
st.write("")

# ------------------------------
# Dental
# ------------------------------
subject = 'Dentals'
st.subheader('🦷   ' + subject)

# count of unique values in Consult Number column where at least one item in column 'Product Category' is 'Vaccination'
subject_consults = df[df['Product Group'] == 'Dental']

# st.dataframe(subject_consults)

subject_consults_count = subject_consults.shape[0]
st.write('Total number of ' + subject + ' in this period:', subject_consults_count)

# show vaccinations_by_species in % of consult_count    (neuter_count / consult_count) * 100
subject_percentage = (subject_consults_count / consult_count) * 100
st.write(subject + ' in percentage of total number of consults:', f"{subject_percentage:.2f}%")

st.write('---')

col1, col2 = st.columns([1, 1])
with col1:
    st.write('Number of ' + subject + ' by species')
    # create a new dataframe with only the 'Consult Number', 'Product Category', 'Species', 'Breed', 'month_year' columns
    subject_consults = subject_consults[['Consult Number', 'Product Category', 'Product Group', 'Product Name', 'Species', 'Breed', 'month_year']]
    # remove duplicates
    subject_consults = subject_consults.drop_duplicates()
    # create a new dataframe where each unique value in month_year is a column and each unique value in 'Species' is a row.  The cells should contain the count of 'Product Category' entries
    subject_consults = subject_consults.groupby(['month_year', 'Species']).size().reset_index(name='count')

    # Pivot the DataFrame
    subject_consults = subject_consults.pivot(index='Species', columns='month_year', values='count')

    # Fill NaN values with 0
    subject_consults = subject_consults.fillna(0)

    st.dataframe(subject_consults)


with col2:
    st.write('Percentage of ' + subject + ' by species')
    percentage_df = (subject_consults / vaccination_consult_count) * 100
    percentage_df = percentage_df.applymap(lambda x: f"{x:.2f}%")

    st.dataframe(percentage_df)

col1, col2 = st.columns([1, 1])

with col1:
# add a sunburst chart from plotly.express to show the breakdown of diagnostics by species. the hierarchy should be Species -> Product Category -> Product group -> Product Name

    subject_consults = df[df['Product Group'] == 'Dental']

    fig4 = px.sunburst(subject_consults, path=['Species', 'Product Name'], title=f"{subject} by Species")
    st.plotly_chart(fig4, use_container_width=True,  key="Dental")
    st.write('Make the chart interactive by clicking on the slices to show/hide data')
    st.markdown("Click on the :material/Fullscreen: button to view the chart in full screen")
#
# with col2:
#     fig3 = px.sunburst(subject_consults, path=['Product Group', 'Species', 'Product Name'], title='Diagnostics by Diagnostic Group')
#     st.plotly_chart(fig3, use_container_width=True, key='Surgeries2')

# insert an icicle chart to show the breakdown of diagnostics by species. the hierarchy should be Species -> Product Category -> Product group -> Product Name
# st.dataframe(df)
st.write("")
st.write("")
st.write("")

st.subheader(':cat: :dog:   Visualisation of all clinical components of all consults for cats and dogs')
# remove all rows from df where Product Name contains 'Fee'
df = df[~df['Product Name'].str.contains('Fee', na=False)]


# only where Species is Canine and Feline
icicle_df = df[df['Species'].isin(['Canine', 'Feline'])]

fig = px.icicle(icicle_df, path=['Species', 'Product Category', 'Product Group', 'Product Name'])
st.plotly_chart(fig, use_container_width=True, height=1200)

st.subheader(':mouse: :rabbit: :rat:   Visualisation of all clinical components of all consults for small furries')
# remove all rows from df where Product Name contains 'Fee'

# only where Species is Canine and Feline
icicle_df = df[~df['Species'].isin(['Canine', 'Feline'])]

fig = px.icicle(icicle_df, path=['Species', 'Product Category', 'Product Group', 'Product Name'])
st.plotly_chart(fig, use_container_width=True, height=1200)






