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

import config


def get_cookies():
    """
    Function to login to stepstone.de and get cookies. These can be used later to extract salary information from job
    descriptions that are only visible to logged in users.
    :return:
        cookies: dict
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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
    r = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(r.content, "html.parser")
    posts = soup.find_all("article", class_="sc-oUcyK bjwYoi")
    results = {}
    links = []
    salaries = []
    for post in posts:
        link = post.find("a", class_="sc-pAZqv cyGFEN")["href"]
        links.append('https://www.stepstone.de' + link)
        try:
            salary = post.find("span", class_="sc-pjHjD jQRkla").text
        except AttributeError:
            salary = np.nan
        salaries.append(salary)
    results["link"] = links
    results["salary"] = salaries
    return results


def get_content(link):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
    jobs = {}
    try:
        r = requests.get(link, headers=headers, timeout=10)
    except:
        try:
            r = requests.get(link, headers=headers, timeout=10)
        except:
            jobs["link"] = link
            jobs["company"] = np.nan
            jobs["title"] = np.nan
            jobs["location"] = np.nan
            jobs["contract_type"] = np.nan
            jobs["work_type"] = np.nan
            jobs["content"] = np.nan
            jobs["industry"] = np.nan
            jobs["rating"] = np.nan
            jobs["num_ratings"] = np.nan
            jobs["release_date"] = np.nan
            print(link)
            return jobs
    jobs["link"] = link
    soup_job = BeautifulSoup(r.content, "html.parser")
    try:
        jobs["company"] = soup_job.find("h1", class_="sc-jWBwVP eMaqXl").text
    except AttributeError:
        jobs["company"] = np.nan
    try:
        jobs["title"] = soup_job.find("h1", class_="listing__job-title at-header-company-jobTitle sc-jDwBTQ fiXdfY").text
    except AttributeError:
        jobs["title"] = np.nan
    try:
        jobs["location"] = soup_job.find("li", class_="at-listing__list-icons_location js-map-offermetadata-link sc-chPdSV jStOTt").text
    except AttributeError:
        jobs["location"] = np.nan
    try:
        jobs["contract_type"] = soup_job.find("li", class_="at-listing__list-icons_contract-type sc-chPdSV jStOTt").text
    except AttributeError:
        jobs["contract_type"] = np.nan
    try:
        jobs["work_type"] = soup_job.find("li", class_="at-listing__list-icons_work-type sc-chPdSV jStOTt").text
    except AttributeError:
        jobs["work_type"] = np.nan
    try:
        jobs["content"] = soup_job.find("div", itemprop="description").text
    except AttributeError:
        jobs["content"] = np.nan
    try:
        industries = soup_job.find_all("li", class_="TokenItem-sc-18nyxil eyoowz")
        industries = [industry.text for industry in industries]
        jobs["industry"] = "|".join(industries)
    except AttributeError:
        jobs["industry"] = np.nan
    try:
        jobs["rating"] = soup_job.find("div", class_="styled__RatingValue-sc-1moxtx3-2 ljexEK").text
    except AttributeError:
        jobs["rating"] = np.nan
    try:
        jobs["num_ratings"] = soup_job.find("a", class_="styled__Link-hkoash-2 fkAStA").text
    except AttributeError:
        jobs["num_ratings"] = np.nan
    try:
        link = soup_job.find("a", class_="at-company-hub-link")
        if link:
            jobs["company_link"] = link["href"]
        else:
            jobs["company_link"] = np.nan
    except AttributeError:
        jobs["company_link"] = np.nan
    try:
        js_code = soup_job.find("script", id="js-section-preloaded-HeaderStepStoneBlock").text
        pattern = re.compile(r'"onlineDate":"(\d{4}-\d{2}-\d{2})')
        match = pattern.search(js_code)
        jobs["release_date"] = match.group(1)
    except AttributeError:
        jobs["release_date"] = np.nan

    return jobs


def get_company_info(link):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
    infos = {}
    infos["company_link"] = link
    try:
        r = requests.get(link, headers=headers, timeout=10)
    except:
        infos["company_size"] = np.nan
        print(link)
        return infos
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        elements = soup.find_all("li", re.compile("StyledMetaDataWrapper"))
        if len(elements) > 1 and ("http" not in elements[1].text):
            infos["company_size"] = elements[1].text
        else:
            infos["company_size"] = np.nan
    except AttributeError:
        infos["company_size"] = np.nan
    return infos


if __name__ == '__main__':
    cookies = get_cookies()
    os.makedirs("data2", exist_ok=True)
    keywords = ["Data%20Science", "Machine%20Learning", "Maschinelles%20Lernen", "Data%20Scientist", "Data%20Analyst",
                "Data%20Mining", "Data%20Engineer", "Deep%20Learning", "Künstliche%20Intelligenz",
                "Artificial%20Intelligence"]
    # keywords = ["Deep%20Learning"]

    links = []
    salaries = []
    keywords_result = []

    for keyword in keywords:

        # find the number of available jobs (includes similar jobs)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
        # url = f"https://www.stepstone.de/5/ergebnisliste.html?ke={keyword}&suid=da46ff49-bcee-4919-91aa-3ca166f5fbce" \
        #       f"&action=facet_selected%3BcontractTypes%3B222&ct=222"
        url = f"https://www.stepstone.de/5/ergebnisliste.html?what={keyword}&searchOrigin=Resultlist_top-search"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        num_jobs = soup.find("span", class_="at-facet-header-total-results").text
        num_jobs = int(num_jobs.replace(".", ""))

        # find the number of similar job to calculate the number of relevant jobs
        # url = f"https://www.stepstone.de/5/ergebnisliste.html?ke={keyword}&suid=da46ff49-bcee-4919-91aa-3ca166f5fbce" \
        #       f"&action=facet_selected%3BcontractTypes%3B222&ct=222&of={num_jobs - 1}"
        url = f"https://www.stepstone.de/5/ergebnisliste.html?what={keyword}&searchOrigin=Resultlist_top-search&of={num_jobs - 1}"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        similar_jobs = soup.find("h4", class_="SectionHeaderStyled-sc-fdk3rh-1 cnAJiQ").text
        num_similar_jobs = int(re.sub("[^0-9]", "", similar_jobs))
        num_relevant_jobs = num_jobs - num_similar_jobs

        urls = []
        for offset in range(0, num_relevant_jobs, 25):
            # url = f"https://www.stepstone.de/5/ergebnisliste.html?ke={keyword}&suid=da46ff49-bcee-4919-91aa" \
            #       f"-3ca166f5fbce&action=facet_selected%3BcontractTypes%3B222&ct=222&of={offset}"
            url = f"https://www.stepstone.de/5/ergebnisliste.html?what={keyword}&searchOrigin=Resultlist_top-search&of={offset}"
            urls.append(url)

        print(f"Get links for {num_relevant_jobs} job descriptions {keyword.replace('%20', '_')}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(tqdm(executor.map(lambda x: get_links(x, cookies), urls), total=len(urls)))

        for result in results:
            links.extend(result["link"])
            salaries.extend(result["salary"])
            keywords_result.extend(len(result["link"])*[keyword.replace('%20', '_')])

    if os.path.exists("data2/links.csv"):
        os.remove("data2/links.csv")

    links_df = pd.DataFrame({"link": links, "salary": salaries,
                             "keyword": keywords_result})
    links_df.to_csv("data2/links.csv", index=False)


    # links_df = pd.read_csv("data2/links.csv")
    links = links_df["link"].unique()

    print(f"Get content for {len(links)} job descriptions")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(get_content, links), total=len(links)))

    content_df = pd.DataFrame(results)
    content_df.to_csv("data2/jobs_unique.csv", index=False)
    results_df = pd.merge(content_df, links_df, on="link", how="left")
    results_df.to_csv("data2/jobs.csv", index=False)


    # results_df = pd.read_csv("data2/jobs.csv")
    company_links = results_df["company_link"].dropna().unique()

    print("Get additional company information")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(get_company_info, company_links), total=len(company_links)))

    company_df = pd.DataFrame(results)
    company_df.to_csv("data2/companies.csv", index=False)
    results_df = pd.merge(results_df, company_df, on="company_link", how="left")
    results_df.to_csv("data2/jobs2.csv", index=False)