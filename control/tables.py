from piccolo.table import Table
from piccolo.columns import UUID, Text 

class Agent(Table):
    name = Text()
    uuid = UUID()
    token = Text()

