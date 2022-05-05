import pygame

ALIGNMENT_NEAR = 0
ALIGNMENT_FAR = 2
ALIGNMENT_CENTER = 1

ALIGNMENT_LEFT = ALIGNMENT_NEAR
ALIGNMENT_TOP = ALIGNMENT_NEAR
ALIGNMENT_RIGHT = ALIGNMENT_FAR
ALIGNMENT_BOTTOM = ALIGNMENT_FAR


# string format class, used to set the alignment of the draw_string function
class StringFormat:
    def __init__(self, _align=ALIGNMENT_NEAR, _line_align=ALIGNMENT_NEAR):
        self._align = _align
        self._line_align = _line_align

    @property
    def align(self):
        return self._align

    @property
    def line_align(self):
        return self._line_align

    @align.setter
    def align(self, _align):
        self._align = _align

    @line_align.setter
    def line_align(self, _line_align):
        self._line_align = _line_align


def draw_string(surface, string, rect, font, format, color):
    if rect.width == -1 or rect.height == -1:
        display_info = pygame.display.Info()
        if rect.width == -1:
            rect.width = display_info.current_w - rect.x
        if rect.height == -1:
            rect.height = display_info.current_h - rect.y

    font_height = font.get_height()
    lines_of_string = format_string(string, font, rect).splitlines()
    i = 0
    y = 0

    if not lines_of_string:
        return False

    if format.line_align == ALIGNMENT_NEAR:
        y = rect.y
    elif format.line_align == ALIGNMENT_CENTER:
        # get the number of lines that will fit in the area
        while i < len(lines_of_string):
            if i * font_height < rect.height:
                i += 1
            else:
                break
        # calculate the starting position of y
        # will center the number of lines it can draw
        y = rect.y + (rect.height / 2) - ((i * font_height) / 2)
        # y is going to start above the actual start position of y, re-adjust
        if y < rect.y:
            y = rect.y
    elif format.line_align == ALIGNMENT_FAR:
        lines_of_string = reversed(lines_of_string)
        y = rect.bottom - font_height
        font_height *= -1

    for line in lines_of_string:
        # if the line alignment is far
        if format.line_align == ALIGNMENT_FAR:
            # check that the y value is not above the top of the rect
            if y < rect.top:
                break
        # if the y value + the current height needed to draw this line goes below the bottom
        elif y + font_height > rect.bottom:
            break

        # create a new surface with the drawn string of this line
        string_surface = font.render(line, True, color)

        # get the width of this line
        width = font.size(line)[0]

        # draw on the left side
        if format.align == ALIGNMENT_NEAR:
            surface.blit(string_surface, (rect.left, y))
        # draw in the center
        elif format.align == ALIGNMENT_CENTER:
            surface.blit(string_surface, (rect.left + ((rect.width / 2) - (width / 2)), y))
        # draw on the right side
        elif format.align == ALIGNMENT_FAR:
            surface.blit(string_surface, (rect.right - width, y))
        # adjust the y position
        y += font_height
    return True


# returns a list formatted to fit the rect provided
# font needed to measure each line
def format_string(string, font, rect):
    if not isinstance(string, str):
        string = str(string)

    lines_of_string = string.splitlines()

    # string that will hold the newly formatted string
    new_string = ''

    for line in lines_of_string:
        if line == '':
            new_string += "\n"
        else:
            while line:
                i = 0

                # start building this line
                while font.size(line[:i])[0] < rect.width and i < len(line):
                    i += 1

                # i is less than the length of this line
                if i < len(line):
                    # find the last word in this line up until the i position
                    i = line.rfind(' ', 0, i) + 1

                    # no words found, this string is way too long to be drawn in this area
                    if i == 0:
                        return ''
                    else:
                        # append the fitted line to new_string, trimming the trailing ' ' character and add the linefeed
                        new_string += line[:i - 1] + '\n'
                # this whole line fits
                else:
                    i = len(line)
                    new_string += line[:i] + '\n'

                # trim the string we took out of this line
                line = line[i:]
    # return the properly formatted string, complete with newlines
    return new_string