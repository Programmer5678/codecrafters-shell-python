from app.command_invoc.models import CommandInvoc, CommandInvocArgs, CommandInvocSpec, LinePosition


class Line:

    def __init__(self, raw):
        self.raw = raw

    def invocs(self, shell_context):

        raw_invocs = self.raw.split("|")
        result = []

        for index, raw_invoc in enumerate( raw_invocs ):


            def create_invoc(raw_invoc, in_pipe, last_invoc, shell_context):
                return CommandInvoc.resolve(
                                            CommandInvocArgs(
                                                CommandInvocSpec( raw_invoc ),
                                                LinePosition( in_pipe, last_invoc ),
                                                shell_context,
                                            )
                            )

            in_pipe = len( raw_invocs) > 1
            last_invoc = (index == len( raw_invocs ) - 1)
            
            result.append(create_invoc(raw_invoc, in_pipe, last_invoc, shell_context))

        return result


def input_next_line():

    def empty_line(line):
        return line == None or len(line.split()) == 0

    raw_line = None
    while empty_line(raw_line):
        raw_line = input("$ ")

    return Line(raw_line)


def input_lines():
    while True:
        yield input_next_line()