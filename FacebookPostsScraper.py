import requests
from bs4 import BeautifulSoup
import pickle
import os
from urllib.parse import urlparse, unquote
from urllib.parse import parse_qs
import json

#This code based on FacebookPostsScraper of ADEOY in GITHUB

class FacebookPostsScraper:

    def __init__(self, email, password, post_url_text='Full Story'):
        self.email = email
        self.password = password
        self.headers = {  # This is the important part: Nokia C3 User Agent
            'User-Agent': 'NokiaC3-00/5.0 (07.20) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+'
        }
        self.session = requests.session()  # Create the session for the next requests
        self.cookies_path = 'session_facebook.cki'  # Give a name to store the session in a cookie file.

        # At certain point, we need find the text in the Url to point the url post, in my case, my Facebook is in
        # English, this is why it says 'Full Story', so, you need to change this for your language.
        # Some translations:
        # - English: 'Full Story'
        # - Spanish: 'Historia completa'
        self.post_url_text = post_url_text

        # Evaluate if NOT exists a cookie file, if NOT exists the we make the Login request to Facebook,
        # else we just load the current cookie to maintain the older session.
        if self.new_session():
            self.login()

        self.posts = []  # Store the scraped posts

    # We need to check if we already have a session saved or need to log to Facebook
    def new_session(self):
        if not os.path.exists(self.cookies_path):
            return True

        f = open(self.cookies_path, 'rb')
        cookies = pickle.load(f)
        self.session.cookies = cookies
        return False

    # Utility function to make the requests and convert to soup object if necessary
    def make_request(self, url, method='GET', data=None, is_soup=True):
        if len(url) == 0:
            raise Exception(f'Empty Url')

        if method == 'GET':
            resp = self.session.get(url, headers=self.headers)
        elif method == 'POST':
            resp = self.session.post(url, headers=self.headers, data=data)
        else:
            raise Exception(f'Method [{method}] Not Supported')

        if resp.status_code != 200:
            raise Exception(f'Error [{resp.status_code}] > {url}')

        if is_soup:
            return BeautifulSoup(resp.text, 'lxml')
        return resp

    # The first time we login
    def login(self):
        # Get the content of HTML of mobile Login Facebook page
        url_home = "https://m.facebook.com/"
        soup = self.make_request(url_home)
        if soup is None:
            raise Exception("Couldn't load the Login Page")

        # Here we need to extract this tokens from the Login Page
        lsd = soup.find("input", {"name": "lsd"}).get("value")
        jazoest = soup.find("input", {"name": "jazoest"}).get("value")
        m_ts = soup.find("input", {"name": "m_ts"}).get("value")
        li = soup.find("input", {"name": "li"}).get("value")
        try_number = soup.find("input", {"name": "try_number"}).get("value")
        unrecognized_tries = soup.find("input", {"name": "unrecognized_tries"}).get("value")

        # This is the url to send the login params to Facebook
        url_login = "https://m.facebook.com/login/device-based/regular/login/?refsrc=https%3A%2F%2Fm.facebook.com%2F&lwv=100&refid=8"
        payload = {
            "lsd": lsd,
            "jazoest": jazoest,
            "m_ts": m_ts,
            "li": li,
            "try_number": try_number,
            "unrecognized_tries": unrecognized_tries,
            "email": self.email,
            "pass": self.password,
            "login": "Iniciar sesión",
            "prefill_contact_point": "",
            "prefill_source": "",
            "prefill_type": "",
            "first_prefill_source": "",
            "first_prefill_type": "",
            "had_cp_prefilled": "false",
            "had_password_prefilled": "false",
            "is_smart_lock": "false",
            "_fb_noscript": "true"
        }
        soup = self.make_request(url_login, method='POST', data=payload, is_soup=True)
        if soup is None:
            raise Exception(f"The login request couldn't be made: {url_login}")

        redirect = soup.select_one('a')
        if not redirect:
            raise Exception("Please log in desktop/mobile Facebook and change your password")

        url_redirect = redirect.get('href', '')
        resp = self.make_request(url_redirect)
        if resp is None:
            raise Exception(f"The login request couldn't be made: {url_redirect}")

        # Finally we get the cookies from the session and save it in a file for future usage
        cookies = self.session.cookies
        f = open(self.cookies_path, 'wb')
        pickle.dump(cookies, f)

        return {'code': 200}

    # Scrap a list of profiles
    def get_posts_from_list(self, profiles):
        data = []
        n = len(profiles)

        for idx in range(n):
            profile = profiles[idx]
            print(f'{idx + 1}/{n}. {profile}')

            posts = self.get_posts_from_profile(profile)
            data.append(posts)

        return data
    # This is the extraction point!
    def get_posts_from_profile(self, url_post):
        # Prepare the Url to point to the posts feed
        url = url_post;
        if "www." in url_post: url_post = url_post.replace('www.', 'm.')
        if 'v=timeline' not in url_post:
            if '?' in url_post:
                url_post = f'{url_post}&v=timeline'
            else:
                url_post = f'{url_post}?v=timeline'

        is_group = '/groups/' in url_post
        # Make a simple GET request
        soup = self.make_request(url_post)
        if soup is None:
            print(f"Couldn't load the Page: {url_post}")
            return []
        css_group = '#m_story_permalink_view > div > div'  # Select the posts from a Facebook group
        raw_data = soup.select_one(f'{css_group}')  # Now join and scrape it
        posts = []
        published = raw_data.select_one('abbr')  # Get the formatted datetime
        # Clean the publish date
        if published is not None:
            published = published.get_text()
        else:
            published = ''
        images = raw_data.select('a > img')  # Get list of all images
        # Get all the images links
        images = [image.get('src', '') for image in images]
        #Check content of post is p element or div element
        check_p = soup.find('p')
        if(check_p is not None ):
            description = raw_data.select('p')  # Get list of all p tag, they compose the description
            # Join all the text in p tags, else set empty string
            if len(description) > 0:
                    description = ' '.join([d.get_text() for d in description])
            else:
                description = '' 
            post = {'published': published, 'description': description, 'images': images,
                'post_url': url}
            posts.append(post)
            self.posts.append(post)
            return posts
        else:
            description = raw_data.find_all("div")[5].text# Get list of all div tag to text
            post = {'published': published, 'description': description, 'images': images,
            'post_url': url}
            posts.append(post)
            self.posts.append(post)
            return posts

    def posts_to_json(self, filename):
        if filename[:-5] != '.json':
            filename = f'{filename}.json'
        with open(filename, 'w', encoding='utf8') as f:
            json.dump(self.posts, f,ensure_ascii=False, sort_keys=True, indent=4)
