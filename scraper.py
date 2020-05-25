import re
import time
import pandas as pd
import urllib.parse
from dateutil import utils, parser, relativedelta
from selenium import webdriver

start_time = time.perf_counter()

def load_parse_save():
    start = time.perf_counter()
    print('>launching driver...')
    driver = webdriver.Chrome()
    driver.set_window_size(500,900)
    print(' driver running.\n>loading page...')
    driver.get('https://m.facebook.com/groups/••{group ID}••/')
    print(' page loaded.')

    # click load more button until page fully loaded (+ close mobile popup)
    print('>loading more content...')
    while True:
        try:
            driver.find_element_by_id('popup_xout').click()
            print('>closed mobile popup.')
        except: pass
        try:
            print(' ...')
            driver.find_element_by_class_name('fullwidthMore').click()
            time.sleep(2.5)
        except: break # if no more show more button

    # create iterable container of posts
    articles = driver.find_element_by_id('m_group_stories_container'
                        ).find_elements_by_class_name("story_body_container")
    print(f" additional content loaded: {len(articles)} total posts")
    print(">scraping post data...")
    posts = []

    for a in articles:
        a_data = {} # temporary post data store
        try: link_box = a.find_element_by_class_name('_32l5')
        except: continue # end iteration if no link box

        a_data['post_text'] = a.find_element_by_class_name('_5rgt').text

        # elements in link box (href thumbnail)
        a_data['title'] = link_box.find_element_by_class_name('_52jh').text
        try: a_data['description'] = link_box.find_element('class','_2rbw').text
        except: pass # some posts have no description, but still scrape
        try: a_data['source'] = link_box.find_element('class', '_52jc').text
        except: continue

        a_data['posted'] = a.find_element_by_css_selector(
                                "[data-sigil='m-feed-voice-subtitle']").text
        a_data['url'] = a.find_element_by_css_selector("[target='_blank']"
                                ).get_attribute('href')
        if '?u=' in a_data['url']: # if url is encoded:
            a_data['url'] = a_data['url'].split('?u=')[1] # remove FB rel prefix
            a_data['url'] = urllib.parse.unquote(a_data['url'] # decode url
                                            ).split('&h=')[0] # remove client ID
        posts.append(a_data)

    print(f' data scraped: {len(posts)} posts')
    print(' quitting driver.\n>parsing...')
    driver.quit()
    data = pd.DataFrame(posts)

    # parsing (specific to Justice Jobs 2.0)
    data['post_text'] = data.post_text.str.replace('JTM', '').apply(
        lambda x: re.sub('^[^a-zA-Z]*', '', x))
    data['location'] = data.post_text.apply(
        lambda x: x.split('-')[0] if ' ' in x and '-' in x and len(
            re.findall('[A-Z]{3,}', x[:20]))>0 else "-")
    data['message'] = data.post_text.apply(
        lambda x: '-'.join(x.split('-')[1:]) if ' ' in x and '-' in x and len(
            re.findall('[A-Z]{3,}', x[:20]))>0 else x)

    def parse_datetime(x):
        x = x.split('at')[0].replace(' ·', '')
        if 'Yesterday' in x:
            return utils.today() - relativedelta.relativedelta(days=1)
        if 'hr' in x or 'mins' in x:
            return utils.today()
        else: return parser.parse(x+" "+str(utils.today().year))

    # standardize timestamps and sort by most recent first
    data.posted = data.posted.apply(parse_datetime)
    data = data.sort_values('posted', ascending=False)
    data.posted = data.posted.apply(lambda x: x.strftime('%B %d'))

    # reorder columns and save as xls
    data = data[["title", "description", "message", "posted",
                 "location", "url", "source"]]
    print(' parsed.')
    data.to_excel("scraped_listings.xls")
    print(f">scraped in {round(time.perf_counter()-start, 2)} seconds\n saved.")
    return data

data = load_parse_save() # trigger scrape function

# ——————————————————————————————
# Email generator - adapted from:
# https://www.geeksforgeeks.org/send-mail-attachment-gmail-account-using-python/

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
print('>generating message...')
fromaddr = "••••@abc.com"
toaddr = "••••••@def.org"
# generate message
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Justice Jobs 2.0"
body = "Good luck!"
msg.attach(MIMEText(body, 'plain'))
# attach file
print('>attaching file...')
filename = "scraped_listings.xls"
attachment = open("scraped_listings.xls", "rb")
# instance of MIMEBase and named as p
p = MIMEBase('application', 'octet-stream')
# To change the payload into encoded form
p.set_payload((attachment).read())
# encode into base64
encoders.encode_base64(p)
p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
# attach the instance 'p' to instance 'msg'
msg.attach(p)
print(' attached.')
# Converts the Multipart msg into a string
text = msg.as_string()
print(' message generated.\n>launching smtp server...')
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
s.starttls()
# authentication
s.login(fromaddr, "••••••••") # email password goes here
print(' authenticated')
# sending the mail
print('>sending...')
s.sendmail(fromaddr, toaddr, text)
s.quit()
print(' message sent.')
print(f'>completed in {round(time.perf_counter()-start_time, 2)} seconds')
