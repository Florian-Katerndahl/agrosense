import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setting the pandas option to enable future behavior mode
pd.set_option('future.no_silent_downcasting', True)

# File path
file_path = '99911-0006-STAAT1_$F.csv'

# Read the CSV file
full_data = pd.read_csv(file_path, encoding='iso-8859-1', delimiter=';', header=4)

# Clean data for specific data series
datasets = ["Primary Energy Consumption (Barrels of Oil Equivalent per Inhab.)", "Carbon Dioxide Emissions per Inhabitant"]
cleaned_data = full_data[full_data['Unnamed: 1'].isin(datasets)].copy()

# Convert data strings to numeric values and handle missing values
for year in range(1990, 2015):
    cleaned_data.loc[:, str(year)] = pd.to_numeric(cleaned_data[str(year)].str.replace(',', '.'), errors='coerce')

# Select data for the year 2014
data_2014 = cleaned_data.pivot(index='Unnamed: 0', columns='Unnamed: 1', values='2014').dropna()

# Calculate basic statistics
mean_values = data_2014.mean()
std_deviation = data_2014.std()

# Creating a table to display calculated statistics
stats_df = pd.DataFrame({'Mean': mean_values, 'Standard Deviation': std_deviation})
print(stats_df)

# Plotting histograms separately
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.histplot(data_2014['Primary Energy Consumption (Barrels of Oil Equivalent per Inhab.)'], kde=True, color='blue', log_scale=True)
plt.title('Distribution of Primary Energy Consumption 2014 (Log Scale)')
plt.xlabel('Primary Energy Consumption (Barrels of Oil Equivalent per Inhabitant)')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
sns.histplot(data_2014['Carbon Dioxide Emissions per Inhabitant'], kde=True, color='red', log_scale=True)
plt.title('Distribution of CO2 Emissions 2014 (Log Scale)')
plt.xlabel('CO2 Emissions per Inhabitant (Tons)')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

# Plotting boxplot separately
plt.figure(figsize=(12, 6))
sns.boxplot(data=data_2014, log_scale=True)
plt.title('Boxplot of Primary Energy Consumption and CO2 Emissions 2014 (Log Scale)')
plt.xlabel('Categories')
plt.ylabel('Values (Log Scale)')
plt.show()
