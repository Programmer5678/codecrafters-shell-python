from app.command_invoc.models import CommandInvoc, CommandInvocArgs, CommandInvocSpec


class Line:

    def __init__(self, raw):
        self.raw = raw

    def split_redirect(self):
        def split_on(st, split_a, split_b):
            st_first_split = st.split(split_a)
            resplit_start = st_first_split[0].split(split_b)
            return resplit_start + st_first_split[1:]


        return split_on(self.raw, "1>", ">")

    def invocs_part(self):
        return self.split_redirect()[0]

    def redirect_part(self):

        split_red = self.split_redirect()

        if len(split_red) == 2:
            return split_red[1].strip()

        return None

    def invocs(self, shell_context):

        raw_invocs = self.invocs_part().split("|")
        result = []

        for index, raw_invoc in enumerate( raw_invocs ):


            def create_invoc(raw_invoc, in_pipe, last_invoc, shell_context, redirect_to):
                return CommandInvoc.resolve_subclass(
                                            CommandInvocArgs(
                                                CommandInvocSpec( raw_invoc ),
                                                in_pipe,
                                                last_invoc,
                                                shell_context,
                                                redirect_to
                                            )
                            )

            in_pipe = len( raw_invocs) > 1
            last_invoc = (index == len( raw_invocs ) - 1)
            redirect_to = self.redirect_part() if last_invoc else None # If not last invoc, we dont redirect the stdout anywhere
            result.append(create_invoc(raw_invoc, in_pipe, last_invoc, shell_context, redirect_to))

        return result


def input_next_line():

    def empty_line(line):
        return line == None or len(line.split()) == 0

    line = None
    while empty_line(line):
        line = input("$ ")

    return line


def input_lines():
    while True:
        yield input_next_line()