"""
Script to scrape all job ads for specified keywords on 'https://www.stepstone.de/'.
"""

import requests
from bs4 import BeautifulSoup
import concurrent.futures
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from arguments import parse_arguments

import config


def main():
    """Runs the web scraper on 'https://www.stepstone.de/'.

    Steps:
    1. Finding the links to all job ads of the given keywords.
    2. Scraping the job information for all unique links.
    3. Scraping additional information about all unique companies.
    4. Combining the results and saving them as .csv file.
    """

    args = parse_arguments()
    cookies = get_cookies()
    os.makedirs(args.directory, exist_ok=True)
    # needed format of the url
    keywords = [keyword.replace("_", "%20") for keyword in args.keywords]
    links = []
    salaries = []
    for keyword in keywords:
        # find the number of available results (includes similar jobs)
        url = f"https://www.stepstone.de/5/ergebnisliste.html?what={keyword}&searchOrigin=Resultlist_top-search"
        r = requests.get(url, headers=config.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        num_jobs = soup.find("span", class_="at-facet-header-total-results").text
        num_jobs = int(num_jobs.replace(".", ""))

        # find the number of similar job to calculate the number of relevant jobs
        url = f"https://www.stepstone.de/5/ergebnisliste.html?what={keyword}&searchOrigin=Resultlist_top-search&of={num_jobs - 1}"
        r = requests.get(url, headers=config.headers)
        soup = BeautifulSoup(r.content, "html.parser")
        similar_jobs = soup.find("h4", class_="SectionHeaderStyled-sc-fdk3rh-1 cnAJiQ").text
        num_similar_jobs = int(re.sub("[^0-9]", "", similar_jobs))
        num_relevant_jobs = num_jobs - num_similar_jobs

        urls = []
        for offset in range(0, num_relevant_jobs, 25):
            url = f"https://www.stepstone.de/5/ergebnisliste.html?what={keyword}&searchOrigin=Resultlist_top-search&of={offset}"
            urls.append(url)

        print(f"Get links for {num_relevant_jobs} job descriptions {keyword.replace('%20', '_')}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(tqdm(executor.map(lambda x: get_links(x, cookies), urls[:1]), total=len(urls)))
        for result in results:
            links.extend(result["link"])
            salaries.extend(result["salary"])

    links_df = pd.DataFrame({"link": links, "salary": salaries})
    links_df.drop_duplicates(inplace=True, ignore_index=True)

    print(f"Get content for {len(links)} job descriptions")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(get_content, links_df["link"]), total=len(links_df["link"])))
    content_df = pd.DataFrame(results)
    results_df = pd.merge(content_df, links_df, on="link", how="left")
    company_links = results_df["company_link"].dropna().unique()

    print("Get additional company information")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(get_company_info, company_links), total=len(company_links)))
    company_df = pd.DataFrame(results)
    results_df = pd.merge(results_df, company_df, on="company_link", how="left")
    results_df.to_csv(os.path.join(args.directory, "data_raw.csv"), index=False)
    return None


def get_cookies():
    """Logs into a Stepstone account and saves the cookies.

    The cookies can be used in later requests to simulate a logged-in user and thus to obtain salary information,
    which is only visible when logged in.

    Returns
    -------
    cookies: dict
        contains all cookies of the session
    """

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(
        "https://www.stepstone.de/candidate/login?login_source=Homepage_top-login&intcid=Button_Homepage"
        "-navigation_login")
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='ccmgt_explicit_accept']")))
    element.click()
    element = driver.find_element(By.XPATH, "//input[@name='email']")
    element.send_keys(config.stepstone_email)
    element = driver.find_element(By.XPATH, "//input[@name='password']")
    element.send_keys(config.stepstone_password)
    element = driver.find_element(By.XPATH, "//input[@name='rememberMe']")
    element.click()
    element = driver.find_element(By.XPATH, "//button[@type='submit']")
    element.click()
    cookies_selenium = driver.get_cookies()
    driver.quit()
    cookies = {}
    for cookie in cookies_selenium:
        cookies[cookie['name']] = cookie['value']
    return cookies


def get_links(url, cookies):
    """Searches the url for links to all included job ads.

    If salary information is provided for an advertisement, it will be requested at this point.

    Parameters
    ----------
    url: str
        url of an overview page with several job ads
    cookies: dict
        previously saved cookies to simulate a session with logged in user

    Returns
    -------
    results: dict
        contains a list with links and another with salary information
    """

    r = requests.get(url, headers=config.headers, cookies=cookies)
    soup = BeautifulSoup(r.content, "html.parser")
    posts = soup.find_all("article", class_="resultlist-1pa5tff")
    results = {}
    links = []
    salaries = []
    for post in posts:
        link = post.find("a", class_="resultlist-12iu5pk")["href"]
        links.append('https://www.stepstone.de' + link)
        try:
            salary = post.find("strong", class_="resultlist-izsl9y").text
        except AttributeError:
            salary = np.nan
        salaries.append(salary)
    results["link"] = links
    results["salary"] = salaries
    return results


def get_content(link):
    """Extracts various information from a job ad.

    Parameters
    ----------
    link: str
        link to job ad

    Returns
    -------
    results: dict
        contains extracted information from the job ad
    """
    
    results = {}
    # sometimes the content of a url cannot be retrieved the first time due to various reasons
    try:
        r = requests.get(link, headers=config.headers, timeout=10)
    except requests.exceptions.RequestException:
        try:
            r = requests.get(link, headers=config.headers, timeout=10)
        except requests.exceptions.RequestException:
            results["link"] = link
            results["company"] = np.nan
            results["title"] = np.nan
            results["location"] = np.nan
            results["contract_type"] = np.nan
            results["work_type"] = np.nan
            results["content"] = np.nan
            results["industry"] = np.nan
            results["rating"] = np.nan
            results["num_ratings"] = np.nan
            results["release_date"] = np.nan
            print(link)
            return results
    results["link"] = link
    soup_job = BeautifulSoup(r.content, "html.parser")
    try:
        results["company"] = soup_job.find("h1", class_="sc-brqgnP exEzGX").text
    except AttributeError:
        results["company"] = np.nan
    try:
        results["title"] = soup_job.find("h1", class_="listing__job-title at-header-company-jobTitle sc-gPEVay czGyJS").text
    except AttributeError:
        results["title"] = np.nan
    try:
        results["location"] = soup_job.find("li", class_="at-listing__list-icons_location js-map-offermetadata-link sc-kgoBCf dyHDRg").text
    except AttributeError:
        results["location"] = np.nan
    try:
        results["contract_type"] = soup_job.find("li", class_="at-listing__list-icons_contract-type sc-kgoBCf dyHDRg").text
    except AttributeError:
        results["contract_type"] = np.nan
    try:
        results["work_type"] = soup_job.find("li", class_="at-listing__list-icons_work-type sc-kgoBCf dyHDRg").text
    except AttributeError:
        results["work_type"] = np.nan
    try:
        results["content"] = soup_job.find("div", class_="listing-content-provider-jcjzuc").text
    except AttributeError:
        results["content"] = np.nan
    try:
        industries = soup_job.find_all("li", class_="TokenItem-sc-18nyxil eyoowz")
        industries = [industry.text for industry in industries]
        results["industry"] = "|".join(industries)
    except AttributeError:
        results["industry"] = np.nan
    try:
        results["rating"] = soup_job.find("div", class_="styled__RatingValue-sc-1moxtx3-2 ljexEK").text
    except AttributeError:
        results["rating"] = np.nan
    try:
        results["num_ratings"] = soup_job.find("a", class_="styled__Link-hkoash-2 fkAStA").text
    except AttributeError:
        results["num_ratings"] = np.nan
    try:
        link = soup_job.find("a", class_="at-company-hub-link")
        if link:
            results["company_link"] = link["href"]
        else:
            results["company_link"] = np.nan
    except AttributeError:
        results["company_link"] = np.nan
    try:
        js_code = soup_job.find("script", id="js-section-preloaded-HeaderStepStoneBlock").text
        pattern = re.compile(r'"onlineDate":"(\d{4}-\d{2}-\d{2})')
        match = pattern.search(js_code)
        results["release_date"] = match.group(1)
    except AttributeError:
        results["release_date"] = np.nan
    return results


def get_company_info(link):
    """Gathers additional information about a company.

    Parameters
    ----------
    link: str
        link to company site on Stepstone

    Returns
    -------
    results: dict
        contains a link and the corresponding company sizes
    """

    results = {"company_link": link}
    try:
        r = requests.get(link, headers=config.headers, timeout=10)
    except requests.exceptions.RequestException:
        results["company_size"] = np.nan
        return results
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        elements = soup.find_all("li", re.compile("StyledMetaDataWrapper"))
        if len(elements) > 1 and ("http" not in elements[1].text):
            results["company_size"] = elements[1].text
        else:
            results["company_size"] = np.nan
    except AttributeError:
        results["company_size"] = np.nan
    return results


if __name__ == "__main__":
    main()
