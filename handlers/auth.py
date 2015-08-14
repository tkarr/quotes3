import tornado
from handlers.base import Base
import utils.ad


class Login(Base):
    def get(self):
        if self.current_user:
            self.redirect(self.get_argument("next", "/"))
        else:
            self.render("login.html", next=self.get_argument("next", "/"))

    @tornado.gen.coroutine
    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        remember_me = bool(self.get_argument("remember_me", False))
        next = self.get_argument("next", "/")

        user = utils.ad.authenticate(username, password)
        if user:
            if remember_me:
                expires = None
            else:
                expires = 10
            self.set_secure_cookie("username",
                                   user['username'],
                                   expires_days=expires)
            self.set_secure_cookie("email",
                                   user['email'],
                                   expires_days=expires)
            self.set_secure_cookie("name",
                                   user['name'],
                                   expires_days=expires)
            self.set_secure_cookie("group",
                                   user['group'],
                                   expires_days=expires)
        else:
            self.set_message("danger", "Username or password is incorrect.")

        self.redirect("/login?next=" + tornado.escape.url_escape(next))

class Logout(Base):
    def get(self):
        self.clear_all_cookies()
        self.redirect("/")

