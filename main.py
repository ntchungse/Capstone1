from FacebookPostsScraper import FacebookPostsScraper as Fps
from pprint import pprint as pp
from config import EMAIL, PASSWORD
from crawlposts import getPostsURL as getURLs
def main():
    getURLs()
    urls = []
    with open('output.txt') as f:
        for line in f:
            urls.append(line.replace("\n",""))

    # Instantiate an object
    fps = Fps(EMAIL, PASSWORD, post_url_text='Full Story')

    fps.get_posts_from_list(urls)
    fps.posts_to_json('my_posts')  #export the posts as JSON document


if __name__ == '__main__':
    main()
