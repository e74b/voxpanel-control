from piccolo.table import Table
from piccolo.columns import Varchar, ForeignKey, Text

class User(Table):
    username = Varchar(null=False, unique=True)
    password = Text(null=False, help_text="password hash")

class Scope(Table):
    user = ForeignKey(references=User)
    scope = Varchar(null=True)

