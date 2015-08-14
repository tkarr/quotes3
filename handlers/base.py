
import config
import tornado.web
import functools
import utils.mailer


class Base(tornado.web.RequestHandler):
    '''
        methods that apply to all other page handlers.
    '''
    
    @property
    def sara_mode(self):
        return self.get_secure_cookie("sara_mode")

    @sara_mode.setter
    def sara_mode(self, value):
        if value:
            self.set_secure_cookie("sara_mode", "True")
        else:
            self.clear_cookie("sara_mode")
        return value
    
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        ''' returns username from cookie. '''
        return self.get_secure_cookie("username")


    def get_user_group(self):
        try:
            return self.get_secure_cookie("group").decode("utf-8")
        except:
            return None

    @property
    def user_group(self):
        if not hasattr(self, "_user_group"):
            self._user_group = self.get_user_group()
        return self._user_group

    @user_group.setter
    def user_group(self, value):
        self._user_group = value

    def get_user_name(self):
        ''' returns user's real name from cookie '''
        try:
            return self.get_secure_cookie("name").decode('utf-8')
        except:
            return None

    @property
    def user_name(self):
        ''' cached version of get_user_name() '''
        if not hasattr(self, "_user_name"):
            self._user_name = self.get_user_name()
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        self._user_name = value

    def get_user_email(self):
        ''' returns user's email from cookie '''
        try:
            return self.get_secure_cookie("email").decode('utf-8')
        except:
            return None

    @property
    def user_email(self):
        ''' cached version of get_user_email() '''
        if not hasattr(self, "_user_email"):
            self._user_email = self.get_user_email()
        return self._user_email

    @user_email.setter
    def user_email(self, value):
        self._user_email = value

    def check_admin(self):
        ''' implementation depends on site setup. '''
        return False

    def render(self, template, **kwargs):
        ''' overrides the render function to add variables to all templates '''
        kwargs['config'] = config
        kwargs['sara_mode'] = self.sara_mode
        kwargs['user_group'] = self.user_group
        kwargs['user_name'] = self.user_name
        kwargs['user_email'] = self.user_email
        kwargs['has_message'] = self.has_message
        kwargs['get_message'] = self.get_message
        super(Base, self).render(template, **kwargs)

    @classmethod
    def admin_required(self, method):
        '''
            decorates handler methods to allow only admin access.
        '''
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.check_admin():
                return method(self, *args, **kwargs)
            else:
                self.write("Access denied")
        return wrapper

    def set_message(self, message_type, message):
        self.set_secure_cookie("message", tornado.escape.url_escape(message))
        self.set_secure_cookie("message_type", message_type)

    def has_message(self):
        message = self.get_secure_cookie("message")
        return True if message else False

    def get_message(self):
        if self.has_message():
            message_type = self.get_secure_cookie("message_type")
            message = tornado.escape.url_unescape(
                self.get_secure_cookie("message"))
            self.clear_cookie("message_type")
            self.clear_cookie("message")
        else:
            message = None
        return (message_type, message)

    def email(self, to, subject, template, **kwargs):
        '''
        adds mailer.send function to ioloop
        and calls it after 10 seconds
        '''
        loop = tornado.ioloop.IOLoop.current()
        loop.call_later(10,
                        utils.mailer.send,
                        to=to,
                        subject=subject,
                        template=template,
                        **kwargs)

    @tornado.gen.coroutine
    def which_rep(self, zip_code):
        zip_code = int(zip_code)
        cursor = yield self.db.execute("""
            SELECT rep_no, zip_codes FROM reps;""")
        reps = cursor.fetchall()
        for rep in reps:
            for zip_range in rep['zip_codes']:
                if zip_code in range(int(zip_range[0]), int(zip_range[1]) + 1):
                    return rep['rep_no']

        return None
