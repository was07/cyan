from cyan.utils import Pos, pos_highlight


class Error:
    def __init__(self, name: str, pos_start: Pos, pos_end: Pos, info: str):
        self.name = name
        self.info = info
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.ecode = ""

    def set_ecode(self, ecode):
        self.ecode = ecode
        return self

    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def __repr__(self):
        result = f'Traceback [{self.ecode}]: file "{self.pos_start.file_name}", line {self.pos_start.line_num + 1}.'
        result += "\n" + pos_highlight(
            self.pos_start.file_text, self.pos_start, self.pos_end
        )
        result += f"\n{self.name}: {self.info}"
        return result


class InvalidCharacterError(Error):
    def __init__(self, pos, info=""):
        super().__init__("InvalidCharacterError", pos, pos, info)
        # start and end pos are same because the error is with 1 character


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, info=""):
        super().__init__("SyntaxError", pos_start, pos_end, info)


class RTError(Error):
    def __init__(self, pos_start, pos_end, info, context):
        super().__init__("Runtime Error", pos_start, pos_end, info)
        self.context = context

    def __repr__(self):
        result = self.generate_traceback()
        result += pos_highlight(self.pos_start.file_text, self.pos_start, self.pos_end)
        result += f"\n{self.name}: {self.info}"
        return result

    def generate_traceback(self):
        result = ""
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = (
                f"  File {pos.file_name}, line {str(pos.line_num + 1)}, in {ctx.display_name}.\n"
                + result
            )
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return "Traceback:\n" + result
