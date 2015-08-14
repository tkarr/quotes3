from handlers.base import Base

class SaraMode(Base):
    def get(self):
        if self.sara_mode:
            self.sara_mode = False
        else:
            self.sara_mode = True
        self.redirect("/")
