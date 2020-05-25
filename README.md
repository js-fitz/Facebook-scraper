# Facebook Scraper
### A tool for collecting post data from public Facebook Groups without a Facebook account

Job-searching without Facebook can be hard. So using python, selenium, and an automated emailing script, I created a tool to anonymously collect data from posts in a Facebook group, remove Facebook’s link tracking system, and email myself the results in an Excel spreadsheet.

<a href="https://medium.com/@3joemail/job-hunting-without-social-media-152ada0639db?source=friends_link&sk=97e4d6132f26663748a4a4474b17b598"
>See my article on Medium for more details (no paywall)</a> or check out the script for yourself at `/scraper.py`

To implement the script on your own, edit the {group_id} in Selenium's inital driver launch, rewrite my parsing code to fit your needs, and set up a low-security gmail account to take care of the sending. Happy scraping!
