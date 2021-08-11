from newsapi import NewsApiClient
from validator import error_window

# globals
categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
countries = ['gb', 'ie', 'us', 'ar', 'br', 've', 'ca', 'fr', 'it', 'ae', 'at', 'au', 'be', 'bg', 'ch', 'cn', 'co', 'cu', 'cz', 'de', 'eg', 'gr', 'hk', 'hu', 'id', 'il', 'in', 'jp', 'kr', 'lt', 'lv', 'ma', 'mx', 'my', 'ng', 'nl', 'no', 'nz', 'ph', 'pl', 'pt', 'ro', 'rs', 'ru', 'sa', 'se', 'sg', 'si', 'sk', 'th', 'tr', 'tw', 'ua', 'za']
languages = ['en', 'es', 'fr', 'pt', 'ar', 'de', 'he', 'it', 'nl', 'no', 'ru', 'se', 'ud', 'zh']

__api_keys = ['69575f0b2ce948aeb55478afe19e5498', 'f4e229f94aad4abf931d09f2fb04b3f3']

# returns a list of dictionaries from API
def get_news(country, category, language, keyword=''):
    global __api_keys

    # for loop between API keys in case there is a problem with the first one
    for i, key in enumerate(__api_keys):
        try:
            # instantiating the client
            news_api = NewsApiClient(api_key=key)

            # if there is no keyword, search by settings
            if keyword == '':
                top_headlines = news_api.get_top_headlines(category=category, language=language, country=country, page_size=100)
            # otherwise, search by the keyword
            else:
                top_headlines = news_api.get_top_headlines(q=keyword)

            return top_headlines['articles']
        except:
            if i != len(__api_keys) - 1: print('API error. Trying different API key...')
            else: error_window('API ERROR', 'There has been a problem with the API connection.\r\nPlease check your connection and try again.')

    # if neither key works, allows user to insert their own key
    new_key = input('API error. Try typing another NewsAPI key (type "cancel" to exit)')
    if new_key == 'cancel': return None
    __api_keys.append(new_key)
    return get_news(country, category, language, keyword)
