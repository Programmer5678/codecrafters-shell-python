import copy

class Tokens:

    def __init__(self):
        self._data = []
        self._new_word = True

    def __iter__(self):
        return self._data.__iter__()

    def add_char(self, c):
        if self._new_word:
            self._new_word = False
            self._data.append("")

        self._data[-1] += c

    def new_word(self):
        self._new_word = True


class TokenizeState:

    def __init__(self):
        # -------------------- private state --------------------
        self._inside_single_quotes = False
        self._inside_double_quotes = False
        self._in_escape_seq = False
        self._tokens = Tokens()  # the backing object for accumulated words/tokens

    # -------------------- public getter --------------------
    def tokens(self):
        """Read-only access to the underlying Tokens object"""
        return self._tokens

    # -------------------- predicates / helpers --------------------
    def _outer_space(self, c):
        return c.isspace() and not self._inside_single_quotes and not self._inside_double_quotes and not self._in_escape_seq

    def _is_closing_single_quote(self, c):
        return c == "'" and self._inside_single_quotes

    def _is_closing_double_quote(self, c):
        return c == '"' and self._inside_double_quotes and not self._in_escape_seq

    def _is_opening_single_quote(self, c):
        return c == "'" and not self._inside_single_quotes and not self._inside_double_quotes and not self._in_escape_seq

    def _is_opening_double_quote(self, c):
        return c == '"' and not self._inside_single_quotes and not self._inside_double_quotes and not self._in_escape_seq

    def _open_single_quote(self):
        self._inside_single_quotes = True

    def _close_single_quote(self):
        self._inside_single_quotes = False

    def _open_double_quote(self):
        self._inside_double_quotes = True

    def _close_double_quote(self):
        self._inside_double_quotes = False

    def _is_start_escape_seq(self, cur, next_chr):
        if cur != "\\":
            return False
        elif self._in_escape_seq:
            return False
        elif self._inside_single_quotes:
            return False
        elif self._inside_double_quotes:
            escaped = ['"', '\\', '$', '`']
            return next_chr in escaped
        else:
            return True

    def _is_end_escape_seq(self, started_escape_seq):
        return self._in_escape_seq and not started_escape_seq

    def _end_escape_seq(self):
        self._in_escape_seq = False

    # -------------------- transition --------------------
    def next_state(self, chr, next_chr):
        """Compute the next state based on the current char and next char, returns a new TokenizeState"""
        result = copy.deepcopy(self)
        started_escape_seq = False

        def _start_escape_seq():
            result._in_escape_seq = True
            nonlocal started_escape_seq
            started_escape_seq = True

        # -------------------- transitions --------------------
        if result._outer_space(chr):
            result._tokens.new_word()

        elif result._is_closing_single_quote(chr):
            result._close_single_quote()

        elif result._is_closing_double_quote(chr):
            result._close_double_quote()

        elif result._is_opening_single_quote(chr):
            result._open_single_quote()

        elif result._is_opening_double_quote(chr):
            result._open_double_quote()

        elif result._is_start_escape_seq(chr, next_chr):
            _start_escape_seq()

        else:
            result._tokens.add_char(chr)

        if result._is_end_escape_seq(started_escape_seq):
            result._end_escape_seq()

        return result


# -------------------- Main tokenizer --------------------
def tokenize(st):

    tokenize_state = TokenizeState()

    for index in range(len(st)):
        chr = st[index]
        next_chr = st[index + 1] if index + 1 < len(st) else None

        tokenize_state = tokenize_state.next_state(chr, next_chr)


    return list(tokenize_state.tokens() )