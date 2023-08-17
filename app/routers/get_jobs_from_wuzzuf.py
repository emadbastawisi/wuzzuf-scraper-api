from datetime import datetime, timedelta
import json
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
from fastapi import Depends ,status
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models ,schemas 


# import schedule

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# add user agent to avoid 403 error *optional*
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}

url='https://wuzzuf.net/search/jobs/?filters%5Bpost_date%5D%5B0%5D=within_1_week&start=0'

# method to create the search url
def create_search_url(search_keyword, time_range='none'):
    if time_range == 'past_24_hours':
        search_url = 'https://wuzzuf.net/search/jobs/?a=navbl%7Cspbl&filters%5Bpost_date%5D%5B0%5D=within_24_hours&q={}&start=0'.format(search_keyword.replace(' ', '+'))
    else:
        search_url = 'https://wuzzuf.net/search/jobs/?a=navbl%7Cspbl&q={}&start=0'.format(search_keyword.replace(' ', '+'))
    return search_url

# method to get the html from the search url
def get_html(url: str) -> str:
    req = urllib.request.Request(url=url, headers=headers)
    return urllib.request.urlopen(req, context=ctx).read()


# method to parse the html
def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'lxml')


# method to get the jobs in each page
def get_jobs(soup: BeautifulSoup) -> list:
    return soup.find_all('div', class_='css-1gatmva e1v1l3u10')


# get jobs number to find the number of pages   
def get_pages_number(url: str) -> int:
    html = get_html(url)
    soup = parse_html(html)
    try:
        jobs_number = soup.find('span', class_="css-xkh9ud").find('strong').text
        pages_number = round(int(jobs_number)/15)
        return int(pages_number)
    except:
        return None

# method to replace the last number in the url with the new page number
def replace_page_number(url: str, new_number: int) -> str:
    pattern = r'start=\d+'
    return re.sub(pattern, 'start={}'.format(new_number), url)


# method to got the number in a post date string
def get_hours(string: str) -> int:
    return int(re.findall('\d+', string)[0])


# method to get the post date then genrate the created_at date
def get_created_at(string: str) -> str:
    hours = get_hours(string)
    now = datetime.now() - timedelta(hours=hours)
    return now


# method to get the expired_at date by adding 7 days to the created_at date
def get_expired_at(created_at: datetime) -> datetime:
    now = created_at + timedelta(days= 7)
    return now

# method to get the job info
def get_job_info(job: BeautifulSoup) -> schemas.JobCreate:
    # try:
        job_title = job.find('h2', class_='css-m604qf').text
        job_company = job.find('a', class_='css-17s97q8').text.rstrip(' -')
        job_location = job.find('span', class_='css-5wys0k').text
        job_type = job.find('div', class_='css-1lh32fc').text
        job_skills = job.find('div', class_='css-y4udm8').text.lstrip(job_type)
        job_link = job.find('a', class_='css-o171kl')['href']
        # some jobs have a different class name for the posted date
        try:
            created_at = get_created_at(job.find('div', class_='css-4c4ojb').text)
        except:
            created_at = get_created_at(job.find('div', class_='css-do6t5g').text)
        expired_at = get_expired_at(created_at)

        result = {'title': job_title, 'company': job_company, 'location': job_location,'type': job_type, 'skills': job_skills,  'link': 'https://wuzzuf.net'+job_link ,'created_at': created_at, 'expired_at': expired_at}
        return result
    # except:
        return None

# method to write the job info to the database
def write_to_db(job_info: schemas.JobCreate ,db: Session = Depends(get_db)):
    # Connect to the database
    query = db.query(models.Job).filter(models.Job.link == job_info['link']).first()
    if query == None:
        new_job = models.Job(**job_info)
        db.add(new_job)
        db.commit()




def get_jobs_from_wuzzuf_toDb(url:str ,db: Session = Depends(get_db)):
    all_jobs = []
    search_url = url
    # get the right number of pages
    pages_number = get_pages_number(search_url)
    if pages_number == None:
        return None
    # loop through all the pages
    for i in range(0, int(pages_number)):

        # replace the page number in the url with the new page number
        search_url = replace_page_number(search_url, i)

        # get the html from the url
        html = get_html(search_url)

        # parse the html
        soup = parse_html(html)

        # get the jobs in each page
        jobs = get_jobs(soup)

        # loop through all the jobs in a page
        for job in jobs:

            # get the job info
            job_info = get_job_info(job)

            # write the job info to a txt file
            if job_info:
                write_to_db(job_info,db)
                all_jobs.append(job_info)
    return  all_jobs

