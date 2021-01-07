class StudentLoginTable:
    def __init__(self):
        pass

    def load_from_file(self):
        pass


class StudentLogin:
    def __init__(self):
        pass


class SectionTable:
    def __init__(self):
        pass

    def load_from_file(self):
        pass


class Section:
    def __init__(self, activity_status):
        self._activity_status = activity_status

    @property
    def activity_status(self):  # new to me
        return self._activity_status

    @activity_status.setter
    def activity_status(self, new_value):
        pass

    @activity_status.getter
    def activity_status(self):
        return 'blah'
