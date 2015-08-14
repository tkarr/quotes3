import config
import urls
import db
import tornado.web


class Application(tornado.web.Application):
    def __init__(self):
        app_urls = urls.handler_urls
        
        settings = {
            "template_path"     : config.TEMPLATE_PATH,
            "static_path"       : config.STATIC_PATH,
            "debug"             : config.DEBUG,
            "compress_response" : config.COMPRESS_RESPONSE,
            "cookie_secret"     : config.COOKIE_SECRET,
            "xsrf_cookies"      : config.XSRF_COOKIES,
            "login_url"         : config.LOGIN_URL
            }

        tornado.web.Application.__init__(self, app_urls, **settings)

