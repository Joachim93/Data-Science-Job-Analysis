"""
Script to prepare the scraped data for later analysis.
"""

import os
import re
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

import config
import positionstack
from arguments import parse_preprocessing


def main():
    """Loads, transforms and saves the data.

    Two different dataframes are generated from the raw data:
    1. long format: contains one entry per location ==> needed for regional analysis
    2. wide format: contains one entry per job ad ==> needed for all further analysis
    """

    warnings.filterwarnings('ignore')
    args = parse_preprocessing()
    try:
        data = pd.read_csv(os.path.join(args.directory, "data_raw.csv"))
    except FileNotFoundError:
        print("Needed data was not found in directory.")
    else:
        data = filter_contract_types(data)
        data = convert_work_types(data)
        data = convert_title(data)
        data = extract_experience_level(data)
        data = convert_salary(data)
        data, data_long = extract_locations(data)
        data_long.to_csv(os.path.join(args.directory, "data_long.csv"), index=False)
        if args.geo_data:
            positionstack.main(args.directory)
            data_long = integrate_geo_data(data_long, args.directory)
            data_long.to_csv(os.path.join(args.directory, "data_long.csv"), index=False)
        data = create_location_features(data, args.directory, args.geo_data)
        data = convert_industries(data)
        data = convert_company_size(data)
        data = extract_requirements(data)
        data = extract_experience(data)
        data = remove_duplicates(data)
        data.to_csv(os.path.join(args.directory, "data_wide.csv"), index=False)
    return None


def filter_contract_types(df):
    """Filters out unwanted contract types (e.g. internship).

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("filter contract type")
    df["permanent_employment"] = df["contract_type"].str.contains("Feste Anstellung")
    df["trainee"] = df["contract_type"].str.contains("Trainee")
    df = df.loc[(df["permanent_employment"] == 1) | (df["trainee"] == 1)]
    df = df.drop("contract_type", axis=1)
    return df


def convert_work_types(df):
    """Extracts the individual information from the attribute 'work_type'.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("convert work type")
    df["full_time"] = df["work_type"].str.contains("Vollzeit")
    df["part_time"] = df["work_type"].str.contains("Teilzeit")
    df["home_office_possible"] = df["work_type"].str.contains("Home Office möglich")
    df = df.drop("work_type", axis=1)
    return df


def convert_title(df):
    """Classifies job titles into different categories.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("convert title")
    df["title_category"] = "Others"
    df.loc[df["title"].str.contains("Software|Developer|Entwickler", case=False, regex=True), "title_category"] = "Software Engineer"
    df.loc[df["title"].str.contains("Analyst|Business[- ]*Intelligence|Analytics|Reporting", case=False, regex=True), "title_category"] = "Data Analyst"
    df.loc[df["title"].str.contains("Data[ \S]*Scien|Research[ \S]*(Scientist|Engineer)|Statistik", case=False, regex=True), "title_category"] = "Data Scientist"
    df.loc[df["title"].str.contains("(Data|Cloud)[ \S]*(Engineer|Archite(c|k)t|Specialist)|Data Warehouse|Datenbank|Database", case=False, regex=True), "title_category"] = "Data Engineer"
    df.loc[df["title"].str.contains("Machine[- ]*Learning|Deep[- ]*Learning|(\W|^)(AI|KI|ML|DL)(\W|$)|Artificial[- ]*Intelligence|Künstliche[- ]*Intelligenz|MLOps", case=False, regex=True), "title_category"] = "Machine Learning Engineer"
    df.loc[df["title"].str.contains("Consultant|Berater|Consulting", case=False, regex=True), "title_category"] = "Data Science Consultant"
    df.loc[df["title"].str.contains("Manager|Head|Lead|Leiter|Leitung|Vorstand|Chief|Owner|Partner|Director", case=False, regex=True), "title_category"] = "Data Science Manager"
    return df


def extract_experience_level(df):
    """Captures the required experience level.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("extract experience level")
    df["experience_level"] = "No Information"
    df.loc[df["title"].str.contains("Junior|Jr.", case=False), "experience_level"] = "Junior"
    df.loc[df["title"].str.contains("Senior|Sr.", case=False), "experience_level"] = "Senior"
    return df


def convert_salary(df):
    """Converts salary ranges into average salaries.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("convert salary")
    if df["salary"].dtype == "object":
        min_salaries = df["salary"].str.split(" ").str[0].str.replace(".", "", regex=False).astype("float")
        max_salaries = df["salary"].str.split(" ").str[2].str.replace(".", "", regex=False).astype("float")
        df["average_salary"] = (min_salaries + max_salaries) / 2
        df.drop("salary", axis=1, inplace=True)
        df.loc[df["average_salary"] < 25000, "average_salary"] = np.nan
    else:
        df.rename(columns={"salary": "average_salary"}, inplace=True)
    return df


def extract_locations(df):
    """Splits the lists of locations into individual locations.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    df_long: pandas.DataFrame
        transformed dataframe in long format (contains one entry per location)
    """

    print("extract_locations")
    locations = df["location"].str.strip(" ,")
    locations = locations.str.split(", ?").explode()
    locations = locations.str.split(" ?/ ?").explode()
    locations = locations.str.split(" oder ").explode()
    locations = locations.str.split(" und ").explode()
    locations = locations.str.split(" - ").explode()
    locations = locations.str.split("; ").explode()
    locations = locations.str.split(" ?\+ ?").explode()
    locations = locations.replace("^Raum ", "", regex=True)
    locations = locations.str.replace(" \(?(bei|b\.|an|am|a\.|ob|in|im|vor|v\.|\+|%|u\.a\.|Raum)[)\w\d .]+", "", regex=True)
    locations = locations.str.replace("[ \w-]*(Home|Office|Mobile|Remote|Bundes|Deutschland|Wahl|Standort|DACH|keine Angabe)[( \w-]*", "bundesweit", case=False, regex=True)
    locations = locations.str.replace(" ?(a\.M\.|Main|M\.|\.\.\.und weitere|Gutenbergquartier)$", "", regex=True)
    locations = locations.str.replace("(MBTI|bei|\d{5}|Metropolregion|Fürstentum|Großraum|100%) ?", "", regex=True)
    locations = locations.str.replace("St.", "Sankt", regex=False)
    locations = locations.str.replace(".", "", regex=False)
    locations = locations.str.split(" \(").explode()
    locations = locations.where(locations.str.contains("^(Bad|Sankt|Palma|New|Den|Schwäbisch|Lindau) ", regex=True), locations.str.split(" ")).explode()
    locations = locations.str.strip("[ )]")
    locations = locations.replace("^$", np.nan, regex=True)
    df_long = pd.merge(df, locations, left_index=True, right_index=True, how="left", suffixes=("_x", None))
    df_long = df_long.drop("location_x", axis=1)
    locations_list = df_long.groupby("link")["location"].apply(lambda x: x.tolist())
    df = pd.merge(df, locations_list, on="link", suffixes=("_x", None), how="left")
    df = df.drop("location_x", axis=1)
    return df, df_long


def integrate_geo_data(df_long, directory):
    """Integrates the geographic data of the Positionstack API.

    Parameters
    ----------
    df_long: pandas.DataFrame
        transformed dataframe in long format (contains one entry per location)
    directory: str
        needed to find the stored data of the Positionstack API

    Returns
    -------
    df_long: pandas.DataFrame
        transformed dataframe in long format (contains one entry per location) with additional geographic information
    """

    print("integrate geo data")
    geo_df = pd.read_csv(os.path.join(directory, "geo_data.csv"))
    geo_df = geo_df.loc[(geo_df["type"] == "locality") & (geo_df["confidence"] == 1)]
    df_long = pd.merge(df_long, geo_df[["latitude", "longitude", "location", "region"]], on="location", how="inner")
    return df_long


def create_location_features(df, directory, geo_flag):
    """Creates additional features from geographic information.

    Features:
    1. main_location ==> as first specified location within the lists
    2. multiple_locations ==> if multiple locations exist
    3. main_region ==> associated state to main_location

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe
    directory: str
        needed to find the stored data of the Positionstack API
    geo_flag: bool
        if geo_data is available to extract the region

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    # helper function
    def remove_element(x):
        x.remove("bundesweit")
        return x

    print("create location features")
    df.loc[(df["location"].apply(lambda x: "bundesweit" in x)) & (
                df["location"].apply(lambda x: len(x)) > 1), "location"].apply(remove_element)
    df.loc[(df["location"].apply(lambda x: "bundesweit" in x)) & (
                df["location"].apply(lambda x: len(x)) > 1), "location"].apply(remove_element)
    df["main_location"] = df["location"].str[0]
    df["multiple_locations"] = df["location"].apply(lambda x: len(x) > 1)
    if geo_flag:
        geo_df = pd.read_csv(os.path.join(directory, "geo_data.csv"))
        df = pd.merge(df, geo_df[["location", "region"]], left_on="main_location", right_on="location",
                      suffixes=(None, "_y"), how="left")
        df.drop("location_y", axis=1, inplace=True)
    df.drop("location", axis=1, inplace=True)
    df.rename({"region": "main_region"}, axis=1, inplace=True)
    return df


def convert_industries(df):
    """Extracts the main industry from a list of industries.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("convert industries")
    try:
        df["main_industry"] = df["industry"].str.split("|").str[0]
    except AttributeError:
        df["main_industry"] = np.nan
    df.drop("industry", axis=1, inplace=True)
    return df


def convert_company_size(df):
    """Unifies the company sizes.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("convert company size")
    df["company_size"] = df["company_size"].replace({"11-50": "0-50", "1-10": "0-50", ">15": "0-50",
                                                     "1000+": "1001-2500", "130": "51-250", "approx. 250": "251-500",
                                                     "201-500 Mitarbeiter": "251-500", "120": "251-500"})
    return df


def extract_requirements(df):
    """Extracts various requirements from the job ad contents.

    Categories of extracted skills:
    1. programming languages
    2. tools
    3. python libraries
    4. education
    5. degrees
    6. knowledge
    7. soft skills

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    print("extract skills")
    # programming languages (18)
    df["python"] = df["content"].str.contains("Python", case=False)
    df["r"] = df["content"].str.contains("\WR(\W|Studio)", case=False, regex=True)
    df["sql"] = df["content"].str.contains("(?<!No)SQL", case=False)
    df["java"] = df["content"].str.contains("Java ", case=False)
    df["javascript"] = df["content"].str.contains("Javascript", case=False)
    df["c"] = df["content"].str.contains("\WC ", case=False, regex=True)
    df["c++"] = df["content"].str.contains("C\+\+", case=False, regex=True)
    df["c#"] = df["content"].str.contains("C#", case=False, regex=True)
    df["scala"] = df["content"].str.contains("Scala ", case=False)
    df["julia"] = df["content"].str.contains("Julia", case=False)
    df["matlab"] = df["content"].str.contains("Matlab", case=False)
    df["swift"] = df["content"].str.contains("Swift", case=False)
    df["go"] = df["content"].str.contains("\WGo |Golang", case=True)
    df["perl"] = df["content"].str.contains("Perl", case=False)
    df["php"] = df["content"].str.contains("Php", case=False)
    df["html"] = df["content"].str.contains("HTML", case=False)
    df["css"] = df["content"].str.contains("CSS", case=False)
    df["rust"] = df["content"].str.contains("\WRust\W", case=False, regex=True)
    # tools (31)
    df["excel"] = df["content"].str.contains("Excel", case=True)
    df["tableau"] = df["content"].str.contains("Tableau", case=False)
    df["power_bi"] = df["content"].str.contains("Power ?BI|PBI", case=False, regex=True)
    df["spark"] = df["content"].str.contains("Spark", case=False)
    df["hadoop"] = df["content"].str.contains("Hadoop", case=False)
    df["hive"] = df["content"].str.contains("Hive", case=False)
    df["aws"] = df["content"].str.contains("AWS|Amazon ?Web ?Services|Redshift", case=False, regex=True)
    df["kafka"] = df["content"].str.contains("Kafka", case=False)
    df["azure"] = df["content"].str.contains("Azure|Synapse", case=False)
    df["google_cloud"] = df["content"].str.contains("Google ?Cloud|GCP|Big ?query", case=False)
    df["docker"] = df["content"].str.contains("Docker", case=False)
    df["git"] = df["content"].str.contains("\WGit", case=False, regex=True)
    df["linux"] = df["content"].str.contains("Linux|Unix|Bash|Shell", case=False, regex=True)
    df["kubernetes"] = df["content"].str.contains("Kubernetes", case=False)
    df["jenkins"] = df["content"].str.contains("Jenkins", case=False)
    df["airflow"] = df["content"].str.contains("Airflow", case=False)
    df["databricks"] = df["content"].str.contains("Databricks", case=False)
    df["sas"] = df["content"].str.contains("\WSas\W", case=False, regex=True)
    df["spss"] = df["content"].str.contains("Spss", case=False, regex=True)
    df["terraform"] = df["content"].str.contains("Terraform", case=False, regex=True)
    df["ansible"] = df["content"].str.contains("Ansible", case=False, regex=True)
    df["puppet"] = df["content"].str.contains("Puppet", case=False, regex=True)
    df["mlflow"] = df["content"].str.contains("Mlflow", case=False, regex=True)
    df["kubeflow"] = df["content"].str.contains("Kubeflow", case=False, regex=True)
    df["splunk"] = df["content"].str.contains("Splunk", case=False, regex=True)
    df["talend"] = df["content"].str.contains("Talend", case=False, regex=True)
    df["prometheus"] = df["content"].str.contains("Prometheus", case=False, regex=True)
    df["grafana"] = df["content"].str.contains("Grafana", case=False, regex=True)
    df["flink"] = df["content"].str.contains("Flink", case=False, regex=True)
    df["storm"] = df["content"].str.contains("Storm", case=False, regex=True)
    df["looker"] = df["content"].str.contains("Looker", case=False, regex=True)
    # databases / data warehouses (21)
    df["mysql"] = df["content"].str.contains("My ?SQL", case=False, regex=True)
    df["postgresql"] = df["content"].str.contains("Postgre", case=False, regex=True)
    df["oracle"] = df["content"].str.contains("Oracle", case=False, regex=True)
    df["sql_server"] = df["content"].str.contains("SQL ?Server", case=False, regex=True)
    df["maria_db"] = df["content"].str.contains("Maria ?DB", case=False, regex=True)
    df["sqlite"] = df["content"].str.contains("Sqlite", case=False, regex=True)
    df["ibm_db2"] = df["content"].str.contains("DB2", case=False, regex=True)
    df["amazon_redshift"] = df["content"].str.contains("Redshift", case=False, regex=True)
    df["google_bigquery"] = df["content"].str.contains("Big ?Query", case=False, regex=True)
    df["azure_synapse"] = df["content"].str.contains("Synapse", case=False, regex=True)
    df["snowflake"] = df["content"].str.contains("Snowflake", case=False, regex=True)
    df["redis"] = df["content"].str.contains("Redis", case=False, regex=True)
    df["dynamo_db"] = df["content"].str.contains("Dynamo ?DB", case=False, regex=True)
    df["mongo_db"] = df["content"].str.contains("Mongo ?DB", case=False, regex=True)
    df["firebase"] = df["content"].str.contains("Firebase", case=False, regex=True)
    df["couch_db"] = df["content"].str.contains("Couch ?DB|Couchbase", case=False, regex=True)
    df["cassandra"] = df["content"].str.contains("Cassandra", case=False, regex=True)
    df["hbase"] = df["content"].str.contains("H ?Base", case=False, regex=True)
    df["neo4j"] = df["content"].str.contains("Neo4j", case=False, regex=True)
    df["amazon_neptune"] = df["content"].str.contains("Amazon ?Neptune", case=False, regex=True)
    df["elastic_search"] = df["content"].str.contains("Elastic ?Search", case=False, regex=True)
    # python libraries (18)
    df["pandas"] = df["content"].str.contains("Pandas", case=False)
    df["numpy"] = df["content"].str.contains("Numpy", case=False)
    df["tensorflow/keras"] = df["content"].str.contains("Tensorflow|Keras", case=False)
    df["pytorch"] = df["content"].str.contains("Pytorch", case=False)
    df["matplotlib"] = df["content"].str.contains("Matplotlib", case=False)
    df["seaborn"] = df["content"].str.contains("Seaborn", case=False)
    df["scikit-learn"] = df["content"].str.contains("(scikit[ -]?learn|sklearn)", case=False, regex=True)
    df["plotly"] = df["content"].str.contains("plotly", case=False)
    df["streamlit"] = df["content"].str.contains("stream[ -]lit", case=False)
    df["spacy"] = df["content"].str.contains("spacy", case=False)
    df["nltk"] = df["content"].str.contains("nltk", case=False)
    df["scipy"] = df["content"].str.contains("scipy", case=False)
    df["statsmodels"] = df["content"].str.contains("statsmodels", case=False)
    df["flask"] = df["content"].str.contains("flask", case=False)
    df["fastapi"] = df["content"].str.contains("fast ?api", case=False)
    df["dask"] = df["content"].str.contains("dask", case=False)
    df["xgboost"] = df["content"].str.contains("xg ?boost|light ?gbm", case=False)
    df["pyspark"] = df["content"].str.contains("pyspark", case=False)
    # degrees (4)
    df["master"] = df["content"].str.contains("(master|diplom)", case=False, regex=True)
    df["phd"] = df["content"].str.contains("(doktor|phd|promotion)", case=False, regex=True)
    df["bachelor"] = (df["content"].str.contains("(Studium|degree|Hochschulabschluss|studiert|Studienabschluss|studies|bachelor)", case=False, regex=True)) & ~df["master"]
    df["no_degree_info"] = ~df["bachelor"] & ~df["master"] & ~df["phd"]
    # majors (5)
    df["computer_science"] = df["content"].str.contains("(computer science|informatik|informatics)", case=False, regex=True)
    df["math/statistics"] = df["content"].str.contains("(math|Statistik|statistics|stats)", case=False, regex=True)
    df["natural_science"] = df["content"].str.contains("(Physik|physics|Naturwissenschaft|natural science|Chemie|chemistry|Biologie|biology|natur-)", case=False, regex=True)
    df["engineering"] = df["content"].str.contains("(Ingenieurwesen|Ingenieurwissenschaft|Engineering)", case=False, regex=True)
    df["business"] = df["content"].str.contains("(bwl|Betriebswirtschaft|vwl|Volkswirtschaft|Wirtschaftswissenschaft)", case=False, regex=True)
    # knowledge (13)
    df["machine_learning"] = df["content"].str.contains("(Machine Learning|Machinelle[sn]? Lern)", case=False, regex=True)
    df["deep_learning"] = df["content"].str.contains("Deep Learning|Neural|Neuronal", case=False, regex=True)
    df["computer_vision"] = df["content"].str.contains("computer vision|convolution|cnn|image processing|Bildverarbeitung", case=False, regex=True)
    df["natural_language_processing"] = df["content"].str.contains("nlp|natural language|speech recognition|Spracherkennung", case=False, regex=True)
    df["autonomous_driving"] = df["content"].str.contains("autonomous driving|autonomes fahren", case=False, regex=True)
    df["robotics"] = df["content"].str.contains("roboti", case=False, regex=True)
    df["reinforcement_learning"] = df["content"].str.contains("reinforcement", case=False, regex=True)
    df["regression"] = df["content"].str.contains("regression", case=False, regex=True)
    df["classification"] = df["content"].str.contains("classification|Klassifikation|Klassifizierung", case=False, regex=True)
    df["clustering"] = df["content"].str.contains("cluster", case=False, regex=True)
    df["forecasting"] = df["content"].str.contains("forecast|time ?series|Zeitreihe", case=False, regex=True)
    df["recommender_systems"] = df["content"].str.contains("recommender system|recommendation system|Empfehlungssystem", case=False, regex=True)
    df["anomaly_detection"] = df["content"].str.contains("anomaly|Anomalie", case=False, regex=True)
    # soft skills (10)
    df["communication"] = df["content"].str.contains("communication| Kommunikation|storytelling", case=False, regex=True)
    df["teamwork"] = df["content"].str.contains("teamfähig|teamplay|teamwork|teamorient|interpersonal|zwischenmenschlich", case=False, regex=True)
    df["motivation"] = df["content"].str.contains("motivation |Neugier|curiosity|lernbereit|to learn|persönlich[\S]* weiterentwick|Engagement|Leidenschaft|passion", case=False, regex=True)
    df["critical_thinking"] = df["content"].str.contains("(analytisch|struktur|logisch|kritisch)[\S]* denk|(analytic|structur|logic|critical)[\S]* think|Auffassungsgabe|problemlös|problem solv", case=False, regex=True)
    df["creativity"] = df["content"].str.contains("kreativität|creativity", case=False, regex=True)
    df["leadership"] = df["content"].str.contains("Führungs(kraft|stärke|kompetenz)|leadership skill|verantwortungsbereit", case=False, regex=True)
    df["flexibility"] = df["content"].str.contains("belastbarkeit|flexibilit|anpassungsfähig", case=False, regex=True)
    df["business_focus"] = df["content"].str.contains("unternehmerisch|Geschäftssinn", case=False, regex=True)
    df["initiative"] = df["content"].str.contains("(selbst|eigen)ständig|eigen(initiative|verantwortung)", case=False, regex=True)
    df["structured_working"] = df["content"].str.contains("(struktur|strategi|orientiert)[\S]* Arbeit|sorgfalt|sorgfältig|(slebst|Zeit|time )manage", case=False, regex=True)
    return df


def extract_experience(df):
    """Extracts the required professional experience.

    To avoid infrequent categories, the individual categories are then grouped into three overarching categories.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    # helper Functions
    def drop_outliers(x):
        try:
            int_value = int(x)
            if int_value > 10:
                return np.nan
            else:
                return x
        except ValueError:
            return x

    def convert_ranges(x):
        try:
            splits = x.split("-")
        except AttributeError:
            return x
        try:
            if len(splits) > 1:
                return str(int((int(splits[0]) + int(splits[1])) / 2))
            else:
                return x
        except ValueError:
            return x

    def unify_words(x):
        try:
            x = x.lower()
            return x
        except AttributeError:
            return x

    def drop_useless(x):
        try:
            int(x)
            return x
        except ValueError:
            if x == "much":
                return x
            else:
                return np.nan

    def convert_keywords(x):
        if type(x) == float:
            return x
        else:
            if x in ("erste", "first", "initial"):
                return "little"
            else:
                return "some"

    print("extract experience")
    # first pattern
    pattern = df["content"].str.extract(r"(\S+) ?Jahre?n? ?(Beruf|\S*erfahrung|relevant|praktisch|einschlägig|fundiert|Expertise)", flags=re.IGNORECASE)[0]
    pattern = pattern.apply(drop_outliers)
    pattern = pattern.apply(convert_ranges)
    pattern = pattern.replace({"ein": "1", "zwei": "2", "drei": "3", "vier": "4", "fünf": "5", "sechs": "6",
                               "sieben": "7", "acht": "8", "neun": "9", "zehn": "10"})
    pattern = pattern.apply(unify_words)
    pattern = pattern.replace({"einigen": "much", "einige": "much", "mehr": "much", "mehrere": "much"})
    pattern = pattern.fillna("")
    digits = pattern.str.extract(r"\D*(\d+)\D*")[0]
    pattern = digits.combine_first(pattern)
    experience = pattern.apply(drop_useless)
    # second pattern
    pattern = df["content"].str.extract(r"(\S+) ?jährige[rn]? ?(Beruf|\S*erfahrung|,? praktisch|,? relevant|,? einschlägig|,? fundiert|Expertise)", flags=re.IGNORECASE)[0]
    pattern = pattern.where(~(pattern.str.contains("mehr|lang", case=False, regex=True, na=False)), "much")
    pattern = pattern.str.strip("- ")
    pattern = pattern.apply(drop_outliers)
    pattern = pattern.apply(unify_words)
    pattern = pattern.replace({"ein": "1", "zwei": "2", "drei": "3", "vier": "4", "fünf": "5", "sechs": "6",
                               "sieben": "7", "acht": "8", "neun": "9", "zehn": "10"})
    pattern = pattern.apply(drop_useless)
    experience = experience.combine_first(pattern)
    # third pattern
    pattern = df["content"].str.extract(r"(\S+) ?years?( of)? ?(\S* ?experience|professional|relevant|work|employment|proven|practical)", flags=re.IGNORECASE)[0]
    pattern = pattern.apply(convert_ranges)
    pattern = pattern.fillna("")
    digits = pattern.str.extract(r"\D*(\d+)\D*")[0]
    pattern = digits.combine_first(pattern)
    pattern = pattern.apply(unify_words)
    pattern = pattern.where(~(pattern.str.contains("several|multiple", case=False, regex=True, na=False)), "much")
    pattern = pattern.replace({"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
                               "seven": "7", "eight": "8", "nine": "9", "ten": "10"})
    pattern = pattern.apply(drop_outliers)
    pattern = pattern.apply(drop_useless)
    experience = experience.combine_first(pattern)
    # fourth pattern
    pattern = df["content"].str.extract(r"(\S+) ?Berufserfahrung", flags=re.IGNORECASE)[0]
    pattern = pattern.apply(unify_words)
    pattern = pattern.apply(convert_keywords)
    experience = experience.combine_first(pattern)
    # fifth pattern
    pattern = df["content"].str.extract(r"(\S+) ?(professional|work|working|practical) experience", flags=re.IGNORECASE)[0]
    pattern = pattern.apply(unify_words)
    pattern = pattern.apply(convert_keywords)
    experience = experience.combine_first(pattern)
    # sixth pattern
    pattern = df["content"].str.extract("(Berufseinstieg|Berufseinsteiger)", flags=re.IGNORECASE)[0]
    pattern = pattern.replace({"Berufseinstieg": "little", "Berufseinsteiger": "little"})
    experience = experience.combine_first(pattern)
    # seventh pattern
    pattern = df["experience_level"].str.extract("(Junior|Senior)", flags=re.IGNORECASE)[0]
    pattern = pattern.replace({"Junior": "little", "Senior": "much"})
    experience = experience.combine_first(pattern)
    # eighth pattern
    pattern = df["trainee"]
    pattern = pattern.replace({True: "little", False: np.nan})
    experience = experience.combine_first(pattern)

    experience_bins = experience.replace({"1": "<=2_years_experience", "2": "<=2_years_experience", "3": "3-4_years_experience", "4": "3-4_years_experience", 
                                      "5": ">=5_years_experience", "6": ">=5_years_experience", "7": ">=5_years_experience", "8": ">=5_years_experience",
                                      "9": ">=5_years_experience", "10": ">=5_years_experience", "little": "<=2_years_experience", "some": "3-4_years_experience",
                                      "much": ">=5_years_experience"})
    experience_bins.fillna("no_experience_information", inplace=True)
    categories = ["<=2_years_experience", "3-4_years_experience", ">=5_years_experience", "no_experience_information"]
    # pd.get_dummies() would only generate one feature for new data points
    experience_dummies = OneHotEncoder(categories=[categories], sparse_output=False, dtype="bool").fit_transform(experience_bins.to_frame())
    experience_dummies = pd.DataFrame(experience_dummies, columns=categories)

    df = pd.merge(df, experience_dummies, left_index=True, right_index=True)
    return df


def remove_duplicates(df):
    """Removes duplicate job ads.

    Parameters
    ----------
    df: pandas.DataFrame
        original dataframe

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe
    """

    df = df[~df.drop(["link", "title", "content", "release_date"], axis=1).duplicated()]
    return df


def preprocess_data(df):
    """Preprocesses the input data for the prediction model.
    
    Parameters
    ----------
    df: pandas.DataFrame
        input data

    Returns
    -------
    df: pandas.DataFrame
        transformed dataframe 
    """

    df = pd.DataFrame(df, index=[0])

    df = filter_contract_types(df)
    if len(df) == 0:
        print("The model can only predict salaries for permanent employment or trainee positions.")
        return None
    df = convert_work_types(df)
    df = convert_title(df)
    df = extract_experience_level(df)
    df, _ = extract_locations(df)
    df = create_location_features(df, None, None)
    geo_df = pd.read_csv("data/geo_data.csv")
    query = df["main_location"].iloc[0]
    response = geo_df.loc[(geo_df["name"] == query) & (geo_df["type"] == "locality") & (geo_df["confidence"] == 1)]
    # the code in the comments can be used to get the location data from the Positionstack API when executed locally
    # when used in the published streamlit app I decided to only use the data from the Positionstack API that I already saved in the data folder
    if response.empty:
        # response = positionstack.get_location(query, config.positionstack_key)
        # if "region" in response.columns:
        #     if (response["type"].iloc[0] == "locality") & response["confidence"].iloc[0] == 1:
        #         df["main_region"] = response["region"].iloc[0]
        # else:
        #     df["main_region"] = np.nan
        df["main_region"] = np.nan
    else:
        df["main_region"] = response["region"].iloc[0]
    df = convert_industries(df)
    df = convert_company_size(df)
    df = extract_requirements(df)
    df = extract_experience(df)
    return df


if __name__ == "__main__":
    main()
