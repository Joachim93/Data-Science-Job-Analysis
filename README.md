# Data-Science-Job-Analysis

This repository contains the code I implemented to collect and analyze job offers from the field of Data Science in 
Germany. The goal of this project was for me to answer the following questions:
- What are the requirements for the different job titles? What are the skills in which I need to improve as a 
prospective employee in this field?
- What attributes affect the salary of a job and how well can the salary be predicted using machine learning on the 
features available?
- Which job opportunities best fit my current skill set?

As part of this analysis, the following steps were performed, which will be discussed in more detail below.
- Scraping over 3000 different job openings in the Data Science field.
- Cleaning the data and engineering new features.
- Exploratory analysis of the data to get information about the job market
- Design and analysis of a model to predict the salary of a job (MAE ~ 6000 €)
- Publication of the results as an interactive webapp using Streamlit ==> 
Link: https://joachim93-data-science-job-analysis-webappwebapp-l9dmku.streamlitapp.com/

A description for using this code can be found [here](#usage).


## Data Collection

A web scraper was implemented that searches job listings on the website "https://www.stepstone.de" and saves various 
attributes of each of the jobs offered in a .csv file. The extracted information includes:
- Job title
- Company
- Text description
- Location
- Industry
- Job rating
- Salary projection
- Company size
- Contract type
- Work type

Furthermore, the API of "https://positionstack.com/" was used to retrieve additional geographical information (state 
and geo-coordinates) for each location.


## Preprocessing

Subsequently, the raw data was cleaned, as well as new features were created from the existing information. 
These include:
- Filtering out the relevant work types and contract types.
- Classification of job titles into seven categories (Data Scientist, Data Analyst, Data Engineer, 
Machine Learning Engineer, Software Engineer, Data Science Consultant, Data Science Manager)
- Capture experience level from job titles (Junior, Senior)
- Conversion of salary ranges into average salaries
- Standardization of location information using regular expressions
- Unification and binning of company size information
- Capture of various requirements from the text description of the job ads using regular expressions 
    - Programming languages
    - Tools
    - Python libraries
    - Education
    - Degree
    - Knowledge
    - Soft skills
    - Professional experience
    

## Data Analysis

TODO


## Model Building

TODO


## Deployment

TODO


## Usage

1. Clone repository: 
    ````
    git clone https://github.com/Joachim93/Data-Science-Job-Analysis.git
    ````
   
2. Install dependecies:
    ````
    pip install -r requirements.txt
    ````
   
3. Create a ``config.py``:

    To collect the data, some personal data is needed, which is stored in the file ``config.py`` and should not be 
    published in this repository. So this file has to be created by a new user and stored in the folder 
    ``data_collection``. The following variables are defined there:
    
    - ``header = {"User-Agent": "..."}``
        - the user agent helps to disguise that the requests are automatic queries
        - your own user agent can be easily googled via "my user agent" and inserted into the template above

    - ``stepstone_email`` und ``stepstone_password``
        - is only needed if the salary forecasts of all jobs, which are only visible when logged in, are to be 
        retrieved as well
        
    - ``positionstack_key``:
        - is only required if additional geographic information about the locations is to be retrieved as well
        - the required key can be read directly on the start page after creating an account and logging in
        
4. Using the web scraper (example):
    ````
    python data_collection/webscraper.py --directory data --keywords data_science machine_learning --salary
    ````
    - in this case the webscraper searches all job offers under the search terms "data science" and "machine learning 
    and stores the information in the folder "data
    - the ``--salary`` flag indicates that salary information should also be scraped
    
5. Preprocessing of the data (example):
    ````
    python data_collection/preprocessing.py --directory data --geo_data
    ````
    - the script transforms the raw data in the specified folder into a format suitable for the analysis and stores 
    them in the same folder
    - the ``--geo_data`` flag indicates that geographic information should also be retrieved from the Positionstack-API
    should be retrieved
    
6. Running the webapp:
    ````
    streamlit run deployment/webapp.py
    ````
    - if during data collection another name than "data" was chosen for the folder with data, it must be changed 
    manually in the code of the function "load_data" in the file ``deployment/webapp.py`` manually.