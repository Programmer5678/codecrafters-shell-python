from abc import ABC, abstractmethod


class ShellContextUpdate:
    def __init__(self, value, is_update):
        self._value = value
        self._is_update = is_update

    @classmethod
    def no_update(cls):
        return cls(None, False)

    @classmethod
    def new(cls, value):
        return cls(value, True)

    def is_update(self):
        return self._is_update

    def value(self):
        return self._value


class InvocRunner(ABC):

    def __init__(self, spec, shell_context):
        self._spec = spec
        self._shell_context = shell_context
        self._updated_end_shell_context = ShellContextUpdate.no_update()

    @abstractmethod
    def run(self):
        pass


    def start(self):
        res = self.run()
        if res != None:
            self._updated_end_shell_context = ShellContextUpdate.new( res )

    def updated_end_shell_context(self):
        return self._updated_end_shell_context