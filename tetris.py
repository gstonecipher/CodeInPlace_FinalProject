'''
This program allows the user to play a simplified version of the game Tetris.
By pressing the left and right arrow keys, the user can move pieces left and right.
If a row is completed, it was disappear and all other pieces will shift downwards.
The user gets one point for each completed row.
Once the pieces hit the top of the board, the game will end, and the user will be shown their score.
To close the board, press Q.

Future components to add:
-ability to rotate pieces
-ability to pause and restart the game
-ability to preview the next piece
-ability to start a new game once the game is over
-ability to show the score on the screen
'''

import tkinter
import time
import random

CANVAS_WIDTH = 400  # Width of drawing canvas in pixels
CANVAS_HEIGHT = 800  # Height of drawing canvas in pixels
N_ROW = 20
N_COL = 10

SIZE = CANVAS_WIDTH/10


def main():
    canvas = make_canvas(CANVAS_WIDTH, CANVAS_HEIGHT, 'Tetris')
    canvas.bind("<Key>", lambda event: key_pressed(event, canvas, tag_num))
    canvas.focus_set()
    points = 0
    draw_background(canvas)

    x = 4
    y = -1
    tag_num = 0

    while True:
        tag_num = draw_piece(canvas, x, y, random.randint(1, 7), tag_num)
        piece_falling(canvas, tag_num)
        piece_settled(canvas, tag_num)
        points = update_board(canvas, points)

        if check_if_done(canvas):
            break

    # create rectangle and display the score
    canvas.create_rectangle(CANVAS_WIDTH/2 - 5 * SIZE, CANVAS_HEIGHT/2 - 3 * SIZE, CANVAS_WIDTH/2 + 5 * SIZE,
                            CANVAS_HEIGHT/2 + 3*SIZE, fill = "white")
    canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, justify=tkinter.CENTER, font='Courier 20',
                       text="GAME OVER\nYour score was\n" + str(points))

    canvas.mainloop()


# checks to see if a piece is in the top row
def check_if_done(canvas):
    full_cells = canvas.find_withtag("full")
    for cell in full_cells:
        if get_top_coord(canvas, cell) -2 < SIZE :
            return True


# reads in key presses from the user and acts accordingly
def key_pressed(event, canvas, tag_num):
    sym = event.keysym.lower()
    tag = "tag" + str(tag_num - 1)
    if is_not_blocked(canvas, tag):
        if sym == "left" and get_left_coord(canvas, tag) > 0:
           canvas.move("tag" + str(tag_num - 1), -SIZE, 0)
        if sym == "right" and get_right_coord(canvas, tag) < CANVAS_WIDTH:
            canvas.move("tag" + str(tag_num - 1), SIZE, 0)
        if sym == "down" and get_bottom_coord(canvas, tag) <= CANVAS_HEIGHT:
            if is_not_blocked(canvas, tag):
                canvas.move("tag" + str(tag_num - 1), 0, SIZE)
    if sym == "q":
        canvas.destroy()


# animates a piece moving down the screen
def piece_falling(canvas, tag_num):
    dx = 0
    dy = SIZE
    tag = "tag" + str(tag_num - 1)
    while is_not_blocked(canvas, tag):
        canvas.move(tag, dx, dy)
        canvas.update()
        time.sleep(1/3.)


# adds the tag "full" to a piece once it's moved as far down as it can
def piece_settled(canvas, tag_num):
    tag = "tag" + str(tag_num - 1)
    canvas.addtag_withtag("full", tag)


# checks the board to see if any rows are full, deletes those rows, and moves all pieces down that were above those rows
def update_board(canvas, points):
    rows_to_delete = check_if_row_full(canvas)
    for row in rows_to_delete:
        points = delete_row(canvas, row, points)

    move_pieces_down(canvas,rows_to_delete)
    return points


# deletes a row of pieces, adds one point for each row deleted
def delete_row(canvas, row, points):
    full_cells = canvas.find_withtag("full")
    boxes = canvas.find_overlapping(2, row * SIZE + 2, CANVAS_WIDTH - 2, row * SIZE + SIZE - 2)

    for item in boxes:
        if item in full_cells:
            canvas.delete(item)
    points += 1
    return points


# reads in the index of a deleted row, and moves all pieces down that were above a deleted row
def move_pieces_down(canvas, rows):
    full_cells = canvas.find_withtag("full")
    for row in rows:
        top = row * SIZE
        for cell in full_cells:
            if get_bottom_coord(canvas, cell) -2 < top:
                canvas.move(cell, 0, SIZE)


# checks to see if a row is full of pieces, returns index of that row
def check_if_row_full(canvas):
    rows = []
    for row in range(N_ROW):
        objects_in_row = canvas.find_overlapping(2, row * SIZE + 2, CANVAS_WIDTH -2, row * SIZE + SIZE - 2)
        full_cells = canvas.find_withtag("full")
        count = 0
        for item in objects_in_row:
            if item in full_cells:
                count += 1
        if count == 10:
            rows.append(row)
    return rows


# checks to see if the movement of a piece is blocked
def is_not_blocked(canvas, tag):
    if get_bottom_coord(canvas, tag) >= CANVAS_HEIGHT: # pieces is blocked by the bottom of the board
        return False

    full_cells = canvas.find_withtag("full") # get id of all cells that have a piece in them
    this_piece = canvas.find_withtag(tag) # get id of cells that make up current piece

    overlap_piece = [] # create list to store cells that overlap the piece
    for item in this_piece:
        bbox = canvas.bbox(item) # get bounding box of all squares that make up the piece
        # get ids of all items that overlap the squares of the current piece - returns a tuple: background id + piece id
        new_overlap = canvas.find_overlapping(bbox[0] + 2, bbox[1] + 2 + SIZE, bbox[2] - 2, bbox[3] - 2 + SIZE)
        # pull out id of only the background square, add to overlapping piece list
        overlap_piece.append(new_overlap[0])

    overlap_full = []
    for item in full_cells:
        bbox = canvas.bbox(item) # get bounding box of every full square
        # get ids of all items that overlap with full squares
        new_overlap = canvas.find_overlapping(bbox[0] + 2, bbox[1] + 2, bbox[2] - 2, bbox[3] - 2)
        # add id of only background square to full list
        overlap_full.append(new_overlap[0])

    # check to see if squares are in both lists - overlap with current piece and full squares
    # if the item is in both lists, the piece will overlap with a full square, and shoudn't move further - return False
    for item in overlap_piece:
        if item in overlap_full:
            return False

    else:
        return True


# draws the background of the game
def draw_background(canvas):
    for row in range(N_ROW):
        for col in range(N_COL):
            draw_square(canvas, col, row, "white", "lightgray", "empty")


# gets the bottom coordinate of an object
def get_bottom_coord(canvas, tag):
    return canvas.bbox(tag)[3]


# gets the left coordinate of an object
def get_left_coord(canvas, tag):
    return canvas.bbox(tag)[0]


# gets the right coordinate of an object
def get_right_coord(canvas, tag):
    return canvas.bbox(tag)[2]


# gets the top coordinate of an object
def get_top_coord(canvas, tag):
    return canvas.bbox(tag)[1]


# draws a new piece given a certain piece type, returns a tag number for that piece
def draw_piece(canvas, col, row, shape, tag_num):
    if shape == 1:
        draw_shape1(canvas, col, row, shape, tag_num)
    if shape == 2:
        draw_shape2(canvas, col, row, shape, tag_num)
    if shape == 3:
        draw_shape3(canvas, col, row, shape, tag_num)
    if shape == 4:
        draw_shape4(canvas, col, row, shape, tag_num)
    if shape == 5:
        draw_shape5(canvas, col, row, shape, tag_num)
    if shape == 6:
        draw_shape6(canvas, col, row, shape, tag_num)
    if shape == 7:
        draw_shape7(canvas, col, row, shape, tag_num)
    tag_num += 1
    return tag_num


# draw the seven pieces
# each piece is composed of four squares, which are all assigned the same tag number
# this tag number is unique to that piece, and thus all components can be moved together
def draw_shape1(canvas, col, row, shape, tag_num):
    draw_square(canvas, col, row, "red", "black", tag_num)
    draw_square(canvas, col + 1, row, "red", "black", tag_num)
    draw_square(canvas, col + 1, row + 1, "red", "black", tag_num)
    draw_square(canvas, col + 2, row + 1, "red", "black", tag_num)


def draw_shape2(canvas, col, row, shape, tag_num):
    draw_square(canvas, col + 1, row, "green", "black", tag_num)
    draw_square(canvas, col + 2, row, "green", "black", tag_num)
    draw_square(canvas, col, row + 1, "green", "black", tag_num)
    draw_square(canvas, col + 1, row + 1, "green", "black", tag_num)


def draw_shape3(canvas, col, row, shape, tag_num):
    draw_square(canvas, col + 1, row, "purple", "black", tag_num)
    draw_square(canvas, col, row + 1, "purple", "black", tag_num)
    draw_square(canvas, col + 1, row + 1, "purple", "black", tag_num)
    draw_square(canvas, col + 2, row + 1, "purple", "black", tag_num)


def draw_shape4(canvas, col, row, shape, tag_num):
    draw_square(canvas, col -1, row, "lightblue", "black", tag_num)
    draw_square(canvas, col, row, "lightblue", "black", tag_num)
    draw_square(canvas, col + 1, row, "lightblue", "black", tag_num)
    draw_square(canvas, col + 2, row, "lightblue", "black", tag_num)


def draw_shape5(canvas, col, row, shape, tag_num):
    draw_square(canvas, col, row, "yellow", "black", tag_num)
    draw_square(canvas, col + 1, row, "yellow", "black", tag_num)
    draw_square(canvas, col, row + 1, "yellow", "black", tag_num)
    draw_square(canvas, col + 1, row + 1, "yellow", "black", tag_num)


def draw_shape6(canvas, col, row, shape, tag_num):
    draw_square(canvas, col, row, "orange", "black", tag_num)
    draw_square(canvas, col + 1, row, "orange", "black", tag_num)
    draw_square(canvas, col + 2, row, "orange", "black", tag_num)
    draw_square(canvas, col, row + 1, "orange", "black", tag_num)


def draw_shape7(canvas, col, row, shape, tag_num):
    draw_square(canvas, col, row, "darkblue", "black", tag_num)
    draw_square(canvas, col, row + 1, "darkblue", "black", tag_num)
    draw_square(canvas, col + 1, row + 1, "darkblue", "black", tag_num)
    draw_square(canvas, col + 2, row + 1, "darkblue", "black", tag_num)


# draws a square and assigns a tag number to it
def draw_square(canvas, col, row, fill, outline, tag_num):
    x = col * SIZE
    y = row * SIZE
    tags = "tag" + str(tag_num)
    canvas.create_rectangle(x, y, x + SIZE, y + SIZE, tags = tags, fill = fill, outline= outline)


def make_canvas(width, height, title=None):
    """
    DO NOT MODIFY
    Creates and returns a drawing canvas
    of the given int size with a blue border,
    ready for drawing.
    """
    objects = {}
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    if title:
        top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)
    canvas.pack()
    canvas.xview_scroll(8, 'units')  # add this so (0, 0) works correctly
    canvas.yview_scroll(8, 'units')  # otherwise it's clipped off

    return canvas



if __name__ == '__main__':
    main()


