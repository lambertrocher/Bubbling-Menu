from tkinter import *
from PIL import Image, ImageTk
from enum import Enum
from math import *

MENU_HEIGHT = 35
MENU_WIDTH = 159


class MenuAutomata(Enum):
    IDLE = 0
    BUBBLE = 1
    CLASSIC = 2
    CLASSIC_SUB = 3


all_menus = []


class Menu:
    def __init__(self, parent, items, x, y, first):
        self.x = x
        self.y = y
        self.first = first
        self.y_move = 0
        self.parent = parent
        self.canvas = Canvas(self.parent, borderwidth=1, background='white', bd=0,
                             highlightthickness=0)
        self.items = items
        self.item_views = []
        self.sub_menu = None
        self.sub_menu_view = None

        self.current_state = MenuAutomata.IDLE
        self.bubbled_item = None

        self.sub_classic_x = None
        self.sub_classic_y = None
        self.classic_sub_item = None

        self.canvas.place(height=500, width=MENU_WIDTH + 1, x=self.x, y=0)

        self.polygons = []

        self.all_items_y = []

        # draw menu items
        for i in range(len(items)):
            x1 = 0
            x2 = MENU_WIDTH
            y1 = i * MENU_HEIGHT
            y2 = (i + 1) * MENU_HEIGHT

            if items[i].important:
                item_view = ItemView(self.canvas.create_rectangle(x1, y1, x2, y2, outline="",
                                                                  fill="#99ccff", activefill="#9b8ff2"), i, x1, y1)
                self.all_items_y.append(item_view.tk_id)

            else:
                item_view = ItemView(self.canvas.create_rectangle(x1, y1, x2, y2, outline="",
                                                                  fill="white",
                                                                  activefill="gainsboro"), i, x1, y1)
                self.all_items_y.append(item_view.tk_id)

            if items[i].sub_menu is not None:
                polygon = self.canvas.create_polygon(
                    [(x2 - 10, y1 + MENU_HEIGHT / 2 - 5), (x2 - 10, y1 + MENU_HEIGHT / 2 + 5),
                     (x2 - 5, y1 + MENU_HEIGHT / 2)],
                    fill="black")
                self.all_items_y.append(polygon)

            self.canvas.tag_bind(item_view.tk_id, "<Enter>",
                                 lambda event, self=self, item_view=item_view: self.enter_handler(event, item_view),
                                 add=None)
            self.canvas.tag_bind(item_view.tk_id, "<Leave>",
                                 lambda event, self=self, item_view=item_view: self.leave_handler(event, item_view),
                                 add=None)

            self.item_views.append(item_view)
            text = self.canvas.create_text(0.2 * MENU_WIDTH, i * MENU_HEIGHT + 5, text=items[i].label,
                                           width=MENU_WIDTH - 10, anchor=NW,
                                           state=DISABLED)

            self.all_items_y.append(text)

        i = len(items)
        # draw menu outline
        rec1 = self.canvas.create_rectangle(0, 0, MENU_WIDTH, i * MENU_HEIGHT, outline="darkgrey")
        rec2 = self.canvas.create_rectangle(15, i * MENU_HEIGHT, MENU_WIDTH, i * MENU_HEIGHT + 1, outline="darkgrey")
        self.all_items_y.append(rec1)
        self.all_items_y.append(rec2)

        self.im = Image.open("deformation.png")
        self.img = ImageTk.PhotoImage(self.im)
        self.bubble = self.canvas.create_image(0, 0, image=self.img, anchor=NW, state=HIDDEN)

        self.im_rec = Image.new(size=(int(0.7 * MENU_WIDTH), (MENU_HEIGHT * 25)), mode="RGBA", color="#E4DAFC60")
        self.img_rec = ImageTk.PhotoImage(self.im_rec)
        self.rec = self.canvas.create_image(int(0.3 * MENU_WIDTH), 0, image=self.img_rec, anchor=NW, state=NORMAL)
        self.canvas.bind("<Motion>", self.motion_handler)
        self.canvas.bind("<Button-1>", self.click)

        self.move(self.x, self.y)

    def click(self, event):
        if self.current_state == MenuAutomata.BUBBLE:
            if self.items[self.bubbled_item.id].sub_menu is None:
                print(self.items[self.bubbled_item.id].label)
                label_selection["text"] = self.items[self.bubbled_item.id].label
        elif self.current_state == MenuAutomata.CLASSIC:
            print(self.items[self.get_item(event.x, event.y - self.y_move).id].label)
            label_selection["text"] = self.items[self.get_item(event.x, event.y - self.y_move).id].label

    def enter_handler(self, event, item_view):
        if self.sub_menu is not None:
            self.destroy(self.sub_menu.canvas)

        if self.items[item_view.id].sub_menu is not None:
            self.sub_menu = Menu(self.parent, self.items[item_view.id].sub_menu, self.x + MENU_WIDTH + 1, item_view.y,
                                 False)
            all_menus.append(self.sub_menu.canvas)
            self.current_state = MenuAutomata.CLASSIC_SUB
            self.sub_classic_x = item_view.x
            self.sub_classic_y = item_view.y_mid
            self.classic_sub_item = item_view

    def leave_handler(self, event, item_view):
        if self.classic_sub_item is not None:
            if self.items[self.classic_sub_item.id].important:
                self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="#99ccff")
            else:
                self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="white")
        if event.x < 3:
            if self.sub_menu is not None:
                self.destroy(self.sub_menu.canvas)

        if self.current_state == MenuAutomata.CLASSIC_SUB:
            if abs(self.sub_classic_y - event.y) > MENU_HEIGHT / 2:
                if self.sub_menu is not None:
                    self.destroy(self.sub_menu.canvas)

    def motion_handler(self, event):
        if self.current_state == MenuAutomata.IDLE:
            if event.x >= int(0.3 * MENU_WIDTH):
                self.current_state = MenuAutomata.BUBBLE
            else:
                self.bubbled_item = None
                self.current_state = MenuAutomata.CLASSIC
        elif self.current_state == MenuAutomata.BUBBLE:
            if event.x >= int(0.3 * MENU_WIDTH):
                if self.closest_item(event.x, event.y) != self.bubbled_item:

                    if self.bubbled_item is not None:
                        self.destroy(self.sub_menu.canvas)
                        self.canvas.itemconfig(self.bubbled_item.tk_id, fill="#99ccff")

                    self.bubbled_item = self.closest_item(event.x, event.y)
                    self.canvas.itemconfig(self.bubbled_item.tk_id, fill="#9b8ff2")
                    if self.items[self.bubbled_item.id].sub_menu is not None:
                        if self.sub_menu is not None:
                            self.destroy(self.sub_menu.canvas)
                        self.sub_menu = Menu(self.parent, self.items[self.bubbled_item.id].sub_menu,
                                             self.x + MENU_WIDTH + 1, event.y, False)
                        all_menus.append(self.sub_menu.canvas)
                else:
                    if self.sub_menu is not None:
                        self.sub_menu.move(x=self.x + MENU_WIDTH + 1, y=event.y)
                radius = self.closest_item_distance(event.x, event.y)
                if radius > 1:
                    state = DISABLED
                else:
                    state = HIDDEN
                if self.bubbled_item is not None:
                    if event.y > self.bubbled_item.y_mid:
                        rotate = True
                    else:
                        rotate = False
                    self.move_bubble(self.canvas, self.bubble, event.x, event.y, radius, state, rotate)
                    self.current_state = MenuAutomata.BUBBLE
            else:
                if self.bubbled_item is not None:
                    self.canvas.itemconfig(self.bubbled_item.tk_id, fill="#99ccff")
                self.bubbled_item = None
                radius = self.closest_item_distance(event.x, event.y)
                state = HIDDEN
                self.move_bubble(self.canvas, self.bubble, event.x, event.y, radius, state, rotate=False)
                self.current_state = MenuAutomata.CLASSIC
        elif self.current_state == MenuAutomata.CLASSIC:
            if self.sub_menu is not None:
                self.destroy(self.sub_menu.canvas)
            if event.x >= int(0.3 * MENU_WIDTH):
                self.current_state = MenuAutomata.BUBBLE
            else:
                self.bubbled_item = None
                self.current_state = MenuAutomata.CLASSIC
                if self.sub_classic_y is not None:
                    if abs(self.sub_classic_y - event.y) > MENU_HEIGHT / 2 + 1:
                        self.destroy(self.sub_menu.canvas)
                        self.current_state = MenuAutomata.CLASSIC
                        if self.items[self.classic_sub_item.id].important:
                            self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="#99ccff")
                        else:
                            self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="white")

        elif self.current_state == MenuAutomata.CLASSIC_SUB:
            if event.x >= int(0.3 * MENU_WIDTH):

                if self.sub_menu is None:
                    self.sub_menu = Menu(self.parent, self.items[self.closest_item(event.x, event.y).id],
                                         self.x + MENU_WIDTH + 1, self.closest_item(event.x, event.y).id.y, False)
                    all_menus.append(self.sub_menu.canvas)

                if self.angle(self.sub_classic_x, self.sub_classic_y, event.x, event.y) > 15:
                    self.current_state = MenuAutomata.BUBBLE
                    if self.items[self.classic_sub_item.id].important:
                        self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="#99ccff")
                    else:
                        self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="white")
                else:
                    if self.items[self.classic_sub_item.id].important:
                        self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="#9b8ff2")
                    else:
                        self.canvas.itemconfig(self.classic_sub_item.tk_id, fill="gainsboro")

            if event.x < int(0.3 * MENU_WIDTH):
                self.move_bubble(self.canvas, self.bubble, event.x, event.y, radius=1, state=HIDDEN, rotate=FALSE)

                if self.sub_classic_y is not None:

                    if abs(self.sub_classic_y - event.y) > MENU_HEIGHT / 2 + 1:
                        self.destroy(self.sub_menu.canvas)
                        self.current_state = MenuAutomata.CLASSIC
        else:
            print("Erreur automate")

    def destroy(self, canvas):
        rec = False
        for can in all_menus:
            if rec:
                can.destroy()
                del can
            elif can == canvas:
                can.destroy()
                del can
                rec = True
            else:
                pass

    def angle(self, x1, y1, x2, y2):
        norm = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        if norm != 0:
            res = acos((x2 - x1) / norm) * 180 / pi
            return res
        else:
            return 0

    def move_bubble(self, parent, bubble, center_x, center_y, radius, state, rotate):
        self.im = Image.open("deformation.png")
        if rotate:
            self.im = self.im.rotate(180)

        if radius > 10 ** 6:
            radius = 10 ** 6
        self.im = self.im.resize((int(radius * 2), int(radius * 1.2)))
        self.img = ImageTk.PhotoImage(self.im)
        if not rotate:
            self.bubble = self.canvas.create_image(center_x, center_y - 0.19 * radius, image=self.img, anchor=N,
                                                   state=state)
        else:
            self.bubble = self.canvas.create_image(center_x, center_y + 0.19 * radius, image=self.img, anchor=S,
                                                   state=state)

    def closest_item_distance(self, x, y):
        min_distance = sys.float_info.max
        for item_view in self.item_views:
            if self.items[item_view.id].important:
                distance = abs(y - item_view.y_mid)
                if distance <= min_distance:
                    min_distance = distance
        return max(1, min_distance - MENU_HEIGHT / 2)

    def closest_item(self, x, y):
        min_distance = sys.float_info.max
        item = None
        for item_view in self.item_views:
            if self.items[item_view.id].important:
                distance = abs(y - item_view.y_mid)
                if distance <= min_distance:
                    min_distance = distance
                    item = item_view
        return item

    def get_item(self, x, y):
        return self.item_views[min(int(y / MENU_HEIGHT), len(self.items) - 1)]

    def move(self, x, y):
        for item in self.all_items_y:
            self.canvas.move(item, 0, y - self.y_move)
        if not self.first:
            for item_view in self.item_views:
                item_view.y = item_view.y + y - self.y_move
                item_view.y_mid = item_view.y_mid + y - self.y_move

        self.y_move = y


class ItemView:
    def __init__(self, tk_id, identifier, x, y):
        self.tk_id = tk_id
        self.id = identifier
        self.x = x
        self.y = y
        self.y_mid = y + MENU_HEIGHT / 2
        self.x_mid = x + MENU_WIDTH / 2


class Item:
    def __init__(self, label: str, important: bool, sub_menu):
        self.label = label
        self.important = important
        self.sub_menu = sub_menu


root = Tk()
frame = Frame(root, width=900, height=675, background="white")
frame.pack()
items = [Item("Item 1", False,
              [Item("Item 1.1", True, [Item("Item 1.1.1", True, None), Item("Item 1.1.2", False, None)]),
               Item("Item 1.2", False, None)]), Item("Item 2", False, None),
         Item("Item 3", True,
              [Item("Item 3.1", True, [Item("Item 3.1.1", True, None), Item("Item 3.1.2", False, None)]),
               Item("Item 3.2", False, None), Item("Item 3.3", False, None),
               Item("Item 3.4", True, [Item("Item 3.4.1", False, None), Item("Item 3.4.2", True, [
                   Item("Item 3.4.2.1", True, [Item("Item 3.4.2.1.1", False, None)]),
                   Item("Item 3.4.2.2", False, None)]), Item("Item 3.4.3", False, None)])]),
         Item("Item 4", False, None), Item("Item 5", False, None),
         Item("Item 6", False,
              [Item("Item 6.1", True, [Item("Item 6.1.1", True, None), Item("Item 6.1.2", False, None)]),
               Item("Item 6.2", False, None)]),
         Item("Item 7", False, None), Item("Item 8", True, [Item("Item 8.1", True, None), Item("Item 8.2", False, None)]),
         Item("Item 9", False, None),
         Item("Item 10", False, [Item("Item 10.1", True, None), Item("Item 10.2", False, None)]),
         Item("Item 11", True, [Item("Item 11.1", True, None), Item("Item 11.2", False, None)])]

menu = Menu(frame, items, 20, 0, True)

canvas_text = Canvas(root, borderwidth=1, background='#f0f0f5', bd=0,
                     highlightthickness=0)

canvas_text.place(height=40, width=200, x=250, y=550)

label_selection = Label(canvas_text, text="", background="#f0f0f5")
text = Label(canvas_text, text="Item activé : ", background="#f0f0f5")
canvas_text.create_window(60, 17, window=text, width=80)
canvas_text.create_window(140, 17, window=label_selection, width=80)

root.mainloop()
