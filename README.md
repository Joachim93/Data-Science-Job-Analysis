# 📊 Data Science Job Market Analysis – Germany 

In this project, over **3000 job offers** in the field of data science in Germany were automatically collected from a job exchange and then analyzed in order to gain more precise insights into the current job market. The results of the analysis are also available to other users within an **interactive web app**, which offers the following options:

- 🧠 **Skill Gap Analysis:** What skills and tools are most expected for my desired career?

- 🎯 **Job Recommendation System:** Which advertised jobs are best suited to my current skillset?

- 🗺️ **Regional Analysis:** Where in Germany are the most suitable jobs available?

- 💰 **Salary Estimate:** What is the approximate salary I can expect to earn in my desired job?




👉 [🔗 Link to Webapp](https://joachim93-data-science-job-analysis-deploymentwebapp-iaz63l.streamlitapp.com/)


## Table of Contents

- Data Collection
- Preprocessing
- Data Analysis
- Model Building
- Deployment
- Installation and Usage


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

Furthermore, the API of "https://positionstack.com/" was used to retrieve additional geographical information (e.g, federal state 
and geo-coordinates) for each location.


## Preprocessing

Subsequently, the raw data was cleaned, as well as new features were created from the existing information. The following steps were carried out:
- Filtering out the relevant work types and contract types.
- Classification of job titles into seven categories (Data Scientist, Data Analyst, Data Engineer, 
Machine Learning Engineer, Software Engineer, Data Science Consultant, Data Science Manager)
- Capture experience level from job titles (Junior, Senior)
- Conversion of salary ranges into average salaries
- Standardization of location information using regular expressions
- Join the additional geographical informations with the rest of the data
- Standardization and binning of company size information
- Capture of various requirements from the text description of the job ads using regular expressions 
    - Programming languages
    - Tools
    - Python libraries
    - Education
    - Degree
    - Knowledge
    - Soft skills
    - Professional experience
- Remove duplicate entries
    

## Data Analysis

An exploratory data analysis was then performed. The graphs were created with the help of the Seaborn and Plotly libraries. The aspects to which particular attention was paid here include:
- Analysis of the requirements for candidates
    - What skills (e.g., programming languages, tools or soft skills) are most often required? Are there differences between job titles?
    - What degrees and how much work experience are required?
- How does the size of the company affect the jobs and requirements needed?
- In which regions of Germany are there the most vacancies?
- Which attributes of the job influence the salary?

<table>
<tr>
  <td width="50%" valign="top">
    <img src="images/requirements.png" alt="Image 1" width="100%"/>
    <img src="images/salaries.png" alt="Image 2" width="100%"/>
  </td>
  <td width="50%">
    <img src="images/germany.png" alt="Image 3" width="100%"/>
  </td>
</tr>
</table>


## Model Building

Next, I tried to predict the salary of a job ad by the remaining variables. First, 20% of the data was split off as test data. The remaining data was used for cross validation. The Mean Absolute Error (MAE) was chosen as the optimization criterion, since large errors should not be penalized more than small ones. For categorical features One-Hot-Encoding and Target Encoding were tested. Missing values were replaced by a new category "missing_value". When using Target Encoding, the features where scaled afterwards. Then the following models were tested and tuned using Randomized Search:

<table>
<tr>
  <td width="50%">
    <img src="images/scores.png" alt="Model Scores" width="100%"/>
  </td>
  <td width="50%">
    <img src="images/importances.png" alt="Feature Importances" width="100%"/>
  </td>
</tr>
</table>

With the best model, an MAE of 6455 € was achieved, which represents an improvement of over 3000 € compared to the target mean, which was used as a naive baseline.
The drop column feature importanes were then calculated for the graph on the right in order to find out which features contributed most to reducing the error.



## Deployment

Finally, an interactive webapp was implemented using Streamlit, which allows users to perform certain analyses on the 
data themselves. The webapp was hosted via the Streamlit Cloud and can be accessed at 
https://joachim93-data-science-job-analysis-deploymentwebapp-iaz63l.streamlitapp.com/. It contains three standalone 
modules:
- Requirements Analysis.
    - This interface provides the ability to view and compare different requirements for different job titles.
- Geographic Analysis.
    - This interface provides an overview of the geographic distribution of desired job titles.
- Job Matching
    - This interface provides a ranked list of all jobs contained in the database, ordered by their similarity to the specified skills.

<table border="0" cellspacing="0">
<tr>
  <td width="50%" align="center">
    <h3>Requirements Analysis</h3>
  </td>
  <td width="50%" align="center">
    <h3>Geographical Analysis</h3>
  </td>
</tr>
<tr>
  <td width="50%" align="center">
    <img src="images/requirement_analysis.PNG" width="80%"/>
  </td>
  <td width="50%" align="center">
    <img src="images/geographical_analysis.PNG" width="80%"/>
  </td>
</tr>
<tr>
  <td width="50%">
    <p>Analysis of the most important skills and requirements across different job titles.</p>
  </td>
  <td width="50%">
    <p>Overview of job distribution across different regions in Germany.</p>
  </td>
</tr>
</table>


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
