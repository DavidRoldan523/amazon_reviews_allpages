from lxml import html
from json import dump, loads
from requests import get
import json
from re import sub
from dateutil import parser as dateparser_to_html
from time import sleep
import urllib3
from ast import literal_eval

import random


def get_random_user_agent():
    user_agent_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
                        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
    ]
    return random.choice(user_agent_list)
def get_header(asin):
    try:
        ratings_dict = {}
        amazon_url = 'https://www.amazon.com/product-reviews/' + asin + '/ref=cm_cr_arp_d_paging_btm_next_1?pageNumber=1'
        urllib3.disable_warnings()
        headers = {'User-Agent': get_random_user_agent()}
        print(headers)
        response2 = get(amazon_url, headers=headers, verify=False, timeout=30)
        # Removing the null bytes from the response.
        cleaned_response = response2.text.replace('\x00', '')
        parser_to_html = html.fromstring(cleaned_response)
        number_reviews = ''.join(parser_to_html.xpath('.//span[@data-hook="total-review-count"]//text()')).replace(',', '')
        product_price = ''.join(parser_to_html.xpath('.//span[contains(@class,"a-color-price arp-price")]//text()')).strip()
        product_name = ''.join(parser_to_html.xpath('.//a[@data-hook="product-link"]//text()')).strip()
        total_ratings = parser_to_html.xpath('//table[@id="histogramTable"]//tr')
        for ratings in total_ratings:
            extracted_rating = ratings.xpath('./td//a//text()')
            if extracted_rating:
                rating_key = extracted_rating[0]
                raw_raing_value = extracted_rating[1]
                rating_value = raw_raing_value
                if rating_key:
                    ratings_dict.update({rating_key: rating_value})
        number_page_reviews = int(int(number_reviews) / 10)
        if number_page_reviews % 2 == 0:
            number_page_reviews += 1
        else:
            number_page_reviews += 2
        return product_price, product_name, number_reviews, ratings_dict, number_page_reviews
    except Exception as e:
        return {"url": amazon_url, "error": e}


def get_all_reviews(asin):
    review_total_pages = []
    product_price, product_name, number_reviews, ratings_dict, stop_loop_for = get_header(asin)
    user_agent = get_random_user_agent()
    print(user_agent)
    for page_number in range(1, stop_loop_for):
        print(f"Reviews of Page #: {page_number}")
        try:
            amazon_url = 'https://www.amazon.com/product-reviews/' + asin + '/ref=cm_cr_arp_d_paging_btm_next_' \
                         + str(page_number) + '?pageNumber=' + str(page_number)
            urllib3.disable_warnings()
            headers = {'User-Agent': user_agent}
            response2 = get(amazon_url, headers=headers, verify=False, timeout=30)

            # Removing the null bytes from the response.
            cleaned_response = response2.text.replace('\x00', '')
            parser_to_html = html.fromstring(cleaned_response)
        except Exception as e:
            return {"url": amazon_url, "error": e}
        reviews = parser_to_html.xpath('//div[contains(@id,"reviews-summary")]')

        if not reviews:
            reviews = parser_to_html.xpath('//div[@data-hook="review"]')

        for review in reviews:
            raw_review_author = review.xpath('.//span[contains(@class,"profile-name")]//text()')
            raw_review_rating = review.xpath('.//i[@data-hook="review-star-rating"]//text()')
            raw_review_header = review.xpath('.//a[@data-hook="review-title"]//text()')
            raw_review_posted_date = review.xpath('.//span[@data-hook="review-date"]//text()')
            raw_review_text1 = review.xpath('.//span[@data-hook="review-body"]//text()')
            raw_review_text2 = review.xpath('.//div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview')
            raw_review_text3 = review.xpath('.//div[contains(@id,"dpReviews")]/div/text()')

            # Cleaning data
            author = ' '.join(' '.join(raw_review_author).split())
            review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
            review_header = ' '.join(' '.join(raw_review_header).split())
            try:
                review_posted_date = dateparser_to_html.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
            except:
                review_posted_date = None
            review_text = ' '.join(' '.join(raw_review_text1).split())

            # Grabbing hidden comments if present
            if raw_review_text2:
                json_loaded_review_data = loads(raw_review_text2[0])
                json_loaded_review_data_text = json_loaded_review_data['rest']
                cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
                full_review_text = review_text + cleaned_json_loaded_review_data_text
            else:
                full_review_text = review_text
            if not raw_review_text1:
                full_review_text = ' '.join(' '.join(raw_review_text3).split())

            review_dict = {
                'review_text': full_review_text,
                'review_posted_date': review_posted_date,
                'review_header': review_header,
                'review_rating': review_rating,
                'review_author': author
            }
            review_total_pages.append(review_dict)
    data = {
        'product_name': product_name,
        'product_price': product_price,
        'number_reviews': number_reviews,
        'ratings': ratings_dict,
        'reviews': review_total_pages,
    }
    return data

if __name__ == '__main__':
    try:
        response_list = []
        asin_list = ["B00JD242MS"]
        for asin in asin_list:
            temp = get_all_reviews(asin)
            response_list.append(temp)
        print(response_list)
    except Exception as e:
        print("Asin error")
