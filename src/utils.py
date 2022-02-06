"""
Pos and Errors
"""


class Pos:
    def __init__(self, file_name, file_text, index, line_num, character_num):
        self.index = index
        self.file_name = file_name
        self.file_text = file_text
        self.line_num = line_num
        self.char_num = character_num
    
    def __repr__(self):
        return f"Pos(line {self.line_num}, char {self.char_num})"
    
    def advance(self, new_line=False):
        if new_line:
            self.char_num = 1
            self.line_num += 1
        else:
            self.char_num += 1
        self.index += 1
    
    def copy(self):
        return Pos(self.file_name, self.file_text, self.index, self.line_num, self.char_num)


def pos_highlight(text: str, pos_start: Pos, pos_end: Pos):
    result = ''
    
    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.line_num - pos_start.line_num + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.char_num if i == 0 else 0
        col_end = pos_end.char_num if i == line_count - 1 else len(line) - 1
        
        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '~' * (col_end - col_start)
        
        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)
    
    return result.replace('\t', '')


class Error:
    def __init__(self, name: str, pos_start: Pos, pos_end: Pos, info: str):
        self.name = name
        self.info = info
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.ecode = ''
    
    def set_ecode(self, ecode):
        self.ecode = ecode
        return self
    
    def set_pos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def __repr__(self):
        result = f'Traceback [{self.ecode}]: file "{self.pos_start.file_name}", line {self.pos_start.line_num + 1}.'
        result += '\n' + pos_highlight(self.pos_start.file_text, self.pos_start, self.pos_end)
        result += f'\n{self.name}: {self.info}'
        return result


class InvalidCharacterError(Error):
    def __init__(self, pos, info=''):
        super().__init__('InvalidCharacterError', pos, pos, info)
        # start and end pos are same because the error is with 1 character


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, info=''):
        super().__init__('SyntaxError', pos_start, pos_end, info)


class RTError(Error):
    def __init__(self, pos_start, pos_end, info, context):
        super().__init__('Runtime Error', pos_start, pos_end, info)
        self.context = context

    def __repr__(self):
        result = self.generate_traceback()
        result += pos_highlight(self.pos_start.file_text, self.pos_start, self.pos_end)
        result += f'\n{self.name}: {self.info}'
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context
    
        while ctx:
            result = f'  File {pos.file_name}, line {str(pos.line_num + 1)}, in {ctx.display_name}.\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        
        return 'Traceback:\n' + result
