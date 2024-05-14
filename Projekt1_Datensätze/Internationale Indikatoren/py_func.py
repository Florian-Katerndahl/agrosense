import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konstanten definieren
DATASET_PATH = '99911-0006-STAAT1_$F.csv'
ENCODING = 'iso-8859-1'
DELIMITER = ';'
DATA_COLUMNS = ["Primärenergieverbrauch (Rohöleinheiten je Einwoh.)", "Kohlendioxidemissionen je Einwohner"]
YEAR_RANGE = range(1990, 2015)
TREND_YEARS = ['1990', '2014']
SELECTED_COUNTRIES = ["Trinidad und Tobago", "Island", "Kuwait", "Katar", "Oman",
                      "Ukraine", "Moldau, Republik", "Luxemburg", "Litauen",
                      "Vereinigte Staaten", "China", "Indien", "Brasilien", "Deutschland",
                      "Ägypten", "Südafrika", "Australien", "Japan", "Saudi-Arabien"]
INDUSTRIAL_COUNTRIES = ["Vereinigte Staaten", "Deutschland", "Japan", "Frankreich", "Vereinigtes Königreich", "Südkorea"]
DEVELOPING_COUNTRIES = ["China", "Indien", "Bangladesch", "Vietnam", "Indonesien", "Brasilien", "Nigeria"]
COMBINED_COUNTRIES = INDUSTRIAL_COUNTRIES + DEVELOPING_COUNTRIES
WEST_EAST_COUNTRIES = {
    'West': [
        "USA", "Deutschland", "Frankreich", "Vereinigtes Königreich", "Brasilien",
        "Kanada", "Italien", "Spanien", "Mexiko", "Australien",
        "Niederlande", "Schweiz", "Argentinien", "Portugal", "Norwegen",
        "Schweden", "Finnland", "Dänemark", "Belgien", "Österreich",
        "Irland", "Griechenland", "Luxemburg", "Neuseeland", "Island",
        "Ungarn", "Tschechien", "Slowakei", "Slowenien", "Polen",
        "Lettland", "Litauen", "Estland", "Kroatien", "Bosnien und Herzegowina",
        "Montenegro", "Serbien", "Mazedonien", "Bulgarien", "Rumänien",
        "Albanien", "Malta", "Zypern", "Andorra", "Monaco",
        "Liechtenstein", "San Marino", "Vatikanstadt", "Uruguay", "Chile",
        "Paraguay", "Suriname", "Barbados", "Bahamas", "Antigua und Barbuda",
        "St. Kitts und Nevis", "St. Lucia", "St. Vincent und die Grenadinen", "Grenada", "Trinidad und Tobago"
    ],
    'Ost': [
        "China", "Indien", "Japan", "Südkorea", "Indonesien", "Bangladesch", "Vietnam", "Nigeria",
        "Philippinen", "Ägypten", "Thailand", "Pakistan", "Malaysia", "Saudi-Arabien", "Türkei",
        "Iran", "Irak", "Afghanistan", "Vereinigte Arabische Emirate", "Katar",
        "Oman", "Kuwait", "Bahrain", "Sri Lanka", "Nepal",
        "Bhutan", "Mongolei", "Kambodscha", "Laos", "Myanmar",
        "Brunei Darussalam", "Timor-Leste", "Russische Föderation", "Usbekistan", "Kasachstan",
        "Turkmenistan", "Tadschikistan", "Kirgisistan", "Armenien", "Aserbaidschan",
        "Georgien", "Syrien", "Libanon", "Jordanien", "Israel",
        "Palästina", "Jemen", "Sudan", "Libyen", "Marokko",
        "Algerien", "Tunesien", "Somalia", "Kenia", "Uganda",
        "Tansania", "Ruanda", "Burundi", "Demokratische Republik Kongo", "Angola",
        "Mosambik", "Madagaskar", "Simbabwe", "Namibia", "Südafrika",
        "Botswana", "Sambia", "Malawi", "Lesotho", "Eswatini"
    ]
}
CONTINENT_GROUPS = {
    'Europa': [
        "Albanien", "Andorra", "Belarus", "Belgien", "Bosnien und Herzegowina", "Bulgarien",
        "Dänemark", "Deutschland", "Estland", "Finnland", "Frankreich", "Griechenland",
        "Irland", "Island", "Italien", "Kroatien", "Lettland", "Liechtenstein", "Litauen",
        "Luxemburg", "Malta", "Moldau", "Monaco", "Montenegro", "Niederlande", "Nordmazedonien",
        "Norwegen", "Österreich", "Polen", "Portugal", "Rumänien", "Russische Föderation", "San Marino",
        "Schweden", "Schweiz", "Serbien", "Slowakei", "Slowenien", "Spanien", "Tschechien",
        "Türkei", "Ukraine", "Ungarn", "Vatikanstadt", "Vereinigtes Königreich", "Zypern"
    ],
    'Asien': [
        "Afghanistan", "Armenien", "Aserbaidschan", "Bahrain", "Bangladesch", "Bhutan",
        "Brunei Darussalam", "China", "Georgien", "Indien", "Indonesien", "Irak", "Iran",
        "Israel", "Japan", "Jemen", "Jordanien", "Kambodscha", "Kasachstan", "Katar",
        "Kirgisistan", "Korea, Demokratische Volksrepublik", "Korea, Republik", "Kuwait",
        "Laos", "Libanon", "Malaysia", "Malediven", "Mongolei", "Myanmar", "Nepal", "Oman",
        "Pakistan", "Philippinen", "Saudi-Arabien", "Singapur", "Sri Lanka", "Syrien",
        "Tadschikistan", "Thailand", "Timor-Leste", "Turkmenistan", "Usbekistan", "Vereinigte Arabische Emirate", "Vietnam"
    ],
    'Afrika': [
        "Ägypten", "Algerien", "Angola", "Äquatorialguinea", "Äthiopien", "Benin", "Botsuana",
        "Burkina Faso", "Burundi", "Cabo Verde", "Cote d'Ivoire", "Dschibuti", "Eritrea",
        "Eswatini", "Gabun", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kamerun", "Kenia",
        "Komoren", "Kongo, Demokratische Republik", "Kongo, Republik", "Lesotho", "Liberia",
        "Libyen", "Madagaskar", "Malawi", "Mali", "Marokko", "Mauretanien", "Mauritius", "Mosambik",
        "Namibia", "Niger", "Nigeria", "Ruanda", "Sambia", "Sao Tome und Principe", "Senegal",
        "Seychellen", "Sierra Leone", "Simbabwe", "Somalia", "Südafrika", "Südsudan", "Sudan",
        "Tansania", "Togo", "Tschad", "Tunesien", "Uganda", "Zentralafrikanische Republik"
    ],
    'Nordamerika': [
        "Antigua und Barbuda", "Bahamas", "Barbados", "Belize", "Dominica", "Dominikanische Republik",
        "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaika", "Kanada", "Kuba",
        "Mexiko", "Nicaragua", "Panama", "St. Kitts und Nevis", "St. Lucia", "St. Vincent und die Grenadinen",
        "Trinidad und Tobago", "Vereinigte Staaten"
    ],
    'Südamerika': [
        "Argentinien", "Bolivien", "Brasilien", "Chile", "Ecuador", "Guyana", "Kolumbien",
        "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"
    ],
    'Ozeanien': [
        "Australien", "Fidschi", "Kiribati", "Marshallinseln", "Mikronesien", "Nauru",
        "Neuseeland", "Palau", "Papua-Neuguinea", "Salomonen", "Samoa", "Tonga", "Tuvalu", "Vanuatu"
    ]
}

# Pandas Optionen setzen
pd.set_option('future.no_silent_downcasting', True)


def read_and_clean_data(filepath, encoding, delimiter):
    data = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter, header=4)
    data = data[data['Unnamed: 1'].isin(DATA_COLUMNS)]
    return data


def convert_to_numeric(data):
    for year in YEAR_RANGE:
        year_str = str(year)
        data[year_str] = pd.to_numeric(data[year_str].str.replace(',', '.').replace('-', float('nan')), errors='coerce')
    return data

def convert_years_to_numeric(data, years):
    for year in years:
        year_str = str(year)
        if data[year_str].dtype == 'object':
            data.loc[:, year_str] = data[year_str].str.replace(',', '.').replace('-', '')
        data.loc[:, year_str] = pd.to_numeric(data[year_str], errors='coerce')
    return data

def display_statistics(data, category):
    # Berechnet den Mittelwert und die Standardabweichung für die angegebene Kategorie
    mean_val = data[category].mean()
    std_dev = data[category].std()
    stats_df = pd.DataFrame({'Mean': mean_val, 'Standard Deviation': std_dev}, index=[0])
    print(f"Statistics for {category}:")
    print(stats_df)

def display_top_bottom(data, category):
    # Sortiert die Daten nach der angegebenen Kategorie und wählt die Top und Bottom 10
    top_10 = data.nlargest(10, category)
    bottom_10 = data.nsmallest(10, category)
    print(f"Top 10 countries for {category}:")
    print(top_10[['Unnamed: 0', category]])
    print(f"Bottom 10 countries for {category}:")
    print(bottom_10[['Unnamed: 0', category]])

def plot_distribution(data, column, color, title, xlabel):
    plt.figure(figsize=(12, 6))
    sns.histplot(data[column], kde=True, color=color, log_scale=True)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Frequency')
    plt.show()


def plot_trends(data, years, countries, category, title):
    plt.figure(figsize=(14, 8))
    colors = plt.get_cmap('tab20')
    for idx, country in enumerate(countries):
        country_data = data[(data['Unnamed: 0'] == country) & (data['Unnamed: 1'] == category)]
        if not country_data.empty:
            plt.plot(years, country_data.iloc[0][years], label=country, color=colors(idx))
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(category)
    plt.legend()
    plt.show()

def calculate_trend(data, category):
    category_data = data[data['Unnamed: 1'] == category]
    trend_data = category_data[['Unnamed: 0', '1990', '2014']].dropna(subset=['1990', '2014'], how='any')
    trend_data['trend'] = trend_data['2014'] - trend_data['1990']
    return trend_data

def plot_trends_indi(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(14, 8))
    data = data.sort_values(by='trend', key=abs, ascending=False)
    colors = ['green' if x > 0 else 'red' for x in data['trend']]
    data.plot(kind='bar', x='Unnamed: 0', y='trend', ax=ax, color=colors, legend=None)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    plt.show()

def plot_data_with_styles(data, category, title):
    fig, ax = plt.subplots(figsize=(14, 8))
    for country in COMBINED_COUNTRIES:
        country_data = data[(data['Unnamed: 0'] == country) & (data['Unnamed: 1'] == category)]
        if not country_data.empty:
            linestyle = '-' if country in INDUSTRIAL_COUNTRIES else '--'
            marker = 'o' if country in INDUSTRIAL_COUNTRIES else 'x'
            ax.plot(list(map(str, YEAR_RANGE)), country_data.iloc[0][list(map(str, YEAR_RANGE))], linestyle=linestyle, marker=marker, label=country)
    ax.set_title(f'{title} (1990-2014)')
    ax.set_xlabel('Jahr')
    ax.set_ylabel('Menge pro Einwohner')
    ax.legend()
    plt.show()

def plot_grouped_data(data, category, title, group_labels):
    fig, ax = plt.subplots(figsize=(14, 8))
    years_list = list(map(str, YEAR_RANGE))  # Konvertieren Sie die Jahre in eine Liste von Strings
    for label, countries in group_labels.items():
        group_data = data[(data['Unnamed: 0'].isin(countries)) & (data['Unnamed: 1'] == category)]
        mean_values = group_data[years_list].mean(axis=0)  # Verwenden Sie years_list statt map direkt
        ax.plot(years_list, mean_values, label=f'{label} Länder')  # Verwenden Sie years_list für die x-Achse

    ax.set_title(f'{title} nach geografischer Gruppierung (1990-2014)')
    ax.set_xlabel('Jahr')
    ax.set_ylabel('Menge pro Einwohner')
    ax.legend(title="Gruppen:")
    plt.show()

def plot_grouped_trends(data, category, title, groups):
    fig, ax = plt.subplots(figsize=(14, 8))
    years = list(map(str, YEAR_RANGE))
    for label, countries in groups.items():
        group_data = data[(data['Unnamed: 0'].isin(countries)) & (data['Unnamed: 1'] == category)]
        mean_values = group_data[years].mean(axis=0)
        ax.plot(years, mean_values, label=f'{label} Länder')
    ax.set_title(f'{title} (1990-2014)')
    ax.set_xlabel('Jahr')
    ax.set_ylabel('Menge pro Einwohner')
    ax.legend(title="Gruppen:")
    plt.show()

def main():
    # Daten einlesen und bereinigen
    data = read_and_clean_data(DATASET_PATH, ENCODING, DELIMITER)

    # Konvertieren von Daten zu numerischen Typen
    data = convert_to_numeric(data)

    # Spezifische Analyse für das Jahr 2014
    data_2014 = data.pivot(index='Unnamed: 0', columns='Unnamed: 1', values='2014').reset_index()

    # Statistiken und Top/Bottom für Primärenergieverbrauch
    display_statistics(data_2014, 'Primärenergieverbrauch (Rohöleinheiten je Einwoh.)')
    display_top_bottom(data_2014, 'Primärenergieverbrauch (Rohöleinheiten je Einwoh.)')

    # Statistiken und Top/Bottom für Kohlendioxidemissionen
    display_statistics(data_2014, 'Kohlendioxidemissionen je Einwohner')
    display_top_bottom(data_2014, 'Kohlendioxidemissionen je Einwohner')

    plot_distribution(data_2014, 'Primärenergieverbrauch (Rohöleinheiten je Einwoh.)', 'blue',
                      'Distribution of Primary Energy Consumption 2014 (log scale)',
                      'Primary Energy Consumption (Oil Units per Capita)')

    plot_distribution(data_2014, 'Kohlendioxidemissionen je Einwohner', 'red',
                      'Distribution of CO2 Emissions 2014 (log scale)',
                      'CO2 Emissions per Capita (Tons)')

    # Trendanalyse für ausgewählte Länder
    plot_trends(data, list(map(str, YEAR_RANGE)), SELECTED_COUNTRIES,
                "Primärenergieverbrauch (Rohöleinheiten je Einwoh.)",
                "Trend in Primary Energy Consumption of Selected Countries")

    plot_trends(data, list(map(str, YEAR_RANGE)), SELECTED_COUNTRIES,
                "Kohlendioxidemissionen je Einwohner",
                "Trend in Carbon Dioxide Emissions of Selected Countries")

    # Konvertieren von Daten zu numerischen Typen für ausgewählte Jahre + Trends
    selected_data = data[(data['Unnamed: 1'].isin(DATA_COLUMNS)) & (data['Unnamed: 0'].isin(SELECTED_COUNTRIES))]
    selected_data = convert_years_to_numeric(selected_data, TREND_YEARS)
    consumption_trend = calculate_trend(selected_data, "Primärenergieverbrauch (Rohöleinheiten je Einwoh.)")
    emission_trend = calculate_trend(selected_data, "Kohlendioxidemissionen je Einwohner")
    plot_trends_indi(consumption_trend, 'Change in Primary Energy Consumption (1990 to 2014)',
                     'Country', 'Change in crude oil units (kg) per capita')
    plot_trends_indi(emission_trend, 'Change in Carbon Dioxide Emissions (1990 to 2014)',
                     'Country', 'Change in tons per capita')

    # Daten für Industrie- und Entwicklungsländer filtern und analysieren
    industrial_developing_data = data[
        (data['Unnamed: 1'].isin(DATA_COLUMNS)) & (data['Unnamed: 0'].isin(COMBINED_COUNTRIES))]
    industrial_developing_data = convert_years_to_numeric(industrial_developing_data, list(map(str, YEAR_RANGE)))
    plot_data_with_styles(industrial_developing_data, "Primärenergieverbrauch (Rohöleinheiten je Einwoh.)",
                          "Primärenergieverbrauch der ausgewählten Länder")
    plot_data_with_styles(industrial_developing_data, "Kohlendioxidemissionen je Einwohner",
                          "Kohlendioxidemissionen der ausgewählten Länder")

    # Hinzufügen der neuen Plots für West vs. Ost
    west_east_data = data[(data['Unnamed: 1'].isin(DATA_COLUMNS)) & (
        data['Unnamed: 0'].isin(WEST_EAST_COUNTRIES['West'] + WEST_EAST_COUNTRIES['Ost']))]
    west_east_data = convert_years_to_numeric(west_east_data, list(map(str, YEAR_RANGE)))
    plot_grouped_data(west_east_data, "Primärenergieverbrauch (Rohöleinheiten je Einwoh.)",
                             "Primärenergieverbrauch: West vs. Ost", WEST_EAST_COUNTRIES)
    plot_grouped_data(west_east_data, "Kohlendioxidemissionen je Einwohner",
                             "Kohlendioxidemissionen: West vs. Ost", WEST_EAST_COUNTRIES)

    # Kontinentale Trends plotten
    continent_data = data[
        (data['Unnamed: 0'].isin([country for sublist in CONTINENT_GROUPS.values() for country in sublist]))]
    plot_grouped_trends(continent_data, "Primärenergieverbrauch (Rohöleinheiten je Einwoh.)",
                        "Primärenergieverbrauch nach Kontinenten", CONTINENT_GROUPS)
    plot_grouped_trends(continent_data, "Kohlendioxidemissionen je Einwohner",
                        "Kohlendioxidemissionen nach Kontinenten", CONTINENT_GROUPS)


if __name__ == '__main__':
    main()
