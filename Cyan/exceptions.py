from cyan.utils import Pos, pos_highlight


class Error:
    __slots__ = ("name", "info", "start_pos", "end_pos", "ecode")

    def __init__(self, name: str, pos_start: Pos, pos_end: Pos, info: str):
        self.name = name
        self.info = info
        self.start_pos = pos_start
        self.end_pos = pos_end
        self.ecode = ""

    def set_ecode(self, ecode):
        self.ecode = ecode
        return self

    def set_pos(self, pos_start, pos_end):
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def __repr__(self):
        result = (
            f'Traceback [{self.ecode}]: file "{self.start_pos.filename}", line {self.start_pos.line_num + 1}.\n'
            + pos_highlight(self.start_pos.file_text, self.start_pos, self.end_pos)
            + f"\n{self.name}: {self.info}"
        )

        return result


class RTError(Error):
    __slots__ = (*Error.__slots__, "context")  # extends base slots with self.context

    def __init__(self, pos_start, pos_end, info, context):
        super().__init__("Runtime Error", pos_start, pos_end, info)

        self.context = context

    def __repr__(self):
        result = (
            self.get_traceback()
            + pos_highlight(self.start_pos.file_text, self.start_pos, self.end_pos)
            + f"\n{self.name}: {self.info}"
        )

        return result

    def get_traceback(self):
        result = ""
        pos = self.start_pos
        ctx = self.context

        while ctx:
            result = f"  File {pos.filename}, line {str(pos.line_num + 1)}, in {ctx.name}.\n{result}"
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return f"Traceback:\n{result}"


class InvalidCharacterError(Error):
    def __init__(self, pos, info=""):
        # start and end pos are same because the error is with 1 character
        super().__init__("InvalidCharacterError", pos, pos, info)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, info=""):
        super().__init__("SyntaxError", pos_start, pos_end, info)
