
class TagGroup:
    def __init__(self, name: str, fact_sheet_type: str = None, tags=None):
        self.name = name
        self.fact_sheet_type = fact_sheet_type
        self.tags = tags