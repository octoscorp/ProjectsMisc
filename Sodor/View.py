"""
Create an interface for the SODOR project.
Author: G Hampton
Last Edited: 26/07/23
"""
import tkinter as tk
from tkinter import (Button, Canvas, DISABLED, Entry, Frame, Label, LEFT, Message, NORMAL, NW,
                     OptionMenu, RIGHT, StringVar, Tk, TOP, Toplevel, X, Y)
from functools import partial
from threading import Thread
from time import sleep


# Constants
S_SIZE = 10     # MUST be even
T_WIDTH = 3
SCALE_FACTOR = 0.9
NUM_PLAYERS = 5
TV_OFFSET = 1540
# TV_OFFSET = 0

# Colours
BACKGROUND = "#303030"
STATION = "#08c408"
TRACK = "#04a004"
SELECTED = "#e4e4e4"
BROKEN = "#c40808"
BUTTON = "#aaaaaa"


class View:
    def __init__(self, controller, stations, tracks):
        self.controller = controller
        self.selected_station_1 = None
        self.selected_station_2 = None
        self.station_ids = []       # Maps the tk id to the station object
        self.stations = stations

        self.selected_tracks = []
        self.track_ids = []     # Maps the tk id to the track object
        self.tracks = tracks
        self.deactivated_tracks = []

        self.pathset = []
        self.path_index = 0

        self.cooldown = False

        # GUI Stuff
        self.train_labels = []
        self.root = Tk()
        self.root.title('Sodor Railway Management System - Map')
        self.root.geometry(f"{int(1340*SCALE_FACTOR)}x{int(750*SCALE_FACTOR)}+{TV_OFFSET}+0")

        map_frame = Frame(self.root, bg=BACKGROUND)
        map_frame.pack(side=LEFT, anchor=NW)

        dialog_frame = Frame(self.root, bg=TRACK)
        dialog_frame.pack(side=LEFT, fill=Y)

        self.create_dialog_area(dialog_frame)

        self.canvas = Canvas(map_frame, width=int(1000*SCALE_FACTOR), height=int(750*SCALE_FACTOR),
                             highlightthickness=0, bg=BACKGROUND)
        self.canvas.pack()

        # Draw stations over tracks
        self.create_tracks(tracks)
        self.create_stations(stations)

        self.dm = DMWindow(self.root, self.controller, self)

    def create_dialog_area(self, frm):
        # First station
        s1_frm = Frame(frm, bg=BACKGROUND, pady=5, padx=5)
        s1_frm.pack(side=TOP, padx=(int(3*SCALE_FACTOR), 0))

        title_1_label = Label(s1_frm, text="Station 1", bd=0, bg=BACKGROUND, fg=SELECTED,
                              font=("Arial", 15))
        title_1_label.pack(side=TOP, anchor=NW)

        self.station_1_label = Label(s1_frm, text="-", pady=5, width=26, bd=0, bg=BACKGROUND,
                                     fg=SELECTED, font=("Arial", 20))
        self.station_1_label.pack(side=TOP)

        # Second station
        s2_frm = Frame(frm, bg=BACKGROUND, pady=5, padx=5)
        s2_frm.pack(side=TOP, padx=(int(3*SCALE_FACTOR), 0), pady=(int(1*SCALE_FACTOR), 0))

        title_2_label = Label(s2_frm, text="Station 2", bd=0, bg=BACKGROUND, fg=SELECTED,
                              font=("Arial", 15))
        title_2_label.pack(side=TOP, anchor=NW)

        self.station_2_label = Label(s2_frm, text="-", pady=5, width=26, bd=0, bg=BACKGROUND,
                                     fg=SELECTED, font=("Arial", 20))
        self.station_2_label.pack(side=TOP)

        self.all_routes_btn = Button(s2_frm, bg=BUTTON, text="Get most routes",
                                     command=self.all_routes, state=DISABLED)
        self.all_routes_btn.pack(side=LEFT)

        self.shortest_route_btn = Button(s2_frm, bg=BUTTON, text="Get shortest route",
                                         command=self.shortest_route, state=DISABLED)
        self.shortest_route_btn.pack(side=RIGHT)

        # Routes
        r_frm = Frame(frm, bg=BACKGROUND, pady=5, padx=5)
        r_frm.pack(side=TOP, padx=(int(3*SCALE_FACTOR), 0), fill=X, pady=(int(1*SCALE_FACTOR), 0))

        tracks_lbl = Label(r_frm, text="Route Selected", bd=0, bg=BACKGROUND, fg=SELECTED,
                           font=("Arial", 14))
        tracks_lbl.pack(side=TOP, anchor=NW)

        self.tracks_num_lbl = Label(r_frm, text="-", pady=5, bd=0, bg=BACKGROUND, fg=SELECTED,
                                    font=("Arial", 12))
        self.tracks_num_lbl.pack(side=TOP)

        self.tracks_dist_lbl = Label(r_frm, text="-", pady=5, bd=0, bg=BACKGROUND, fg=SELECTED,
                                     font=("Arial", 12))
        self.tracks_dist_lbl.pack(side=TOP)

        self.prev_path_btn = Button(r_frm, bg=BUTTON, text="Previous", command=self.prev_path,
                                    state=DISABLED)
        self.prev_path_btn.pack(side=LEFT)

        self.deselect_all_btn = Button(r_frm, bg=BUTTON, text="Deselect tracks",
                                       command=self.deselect_all, state=DISABLED)
        self.deselect_all_btn.pack(side=LEFT)

        self.next_path_btn = Button(r_frm, bg=BUTTON, text="Next", command=self.next_path,
                                    state=DISABLED)
        self.next_path_btn.pack(side=RIGHT)

        # Step
        s_frm = Frame(frm, bg=BACKGROUND, pady=5, padx=5)
        s_frm.pack(side=TOP, padx=(int(3*SCALE_FACTOR), 0), fill=X, pady=(int(1*SCALE_FACTOR), 0))

        self.msg_lbl = Label(s_frm, text="-", pady=5, bd=0, bg=BACKGROUND, fg=BROKEN,
                             font=("Arial", 12))
        self.msg_lbl.pack(side=TOP)

        self.step_btn = Button(s_frm, bg=BUTTON, text="Step", command=self.step)
        self.step_btn.pack(side=RIGHT)

        # WHat it says on the tin
        filler = Frame(frm, bg=BACKGROUND, height=600)
        filler.pack(side=TOP, padx=(int(3*SCALE_FACTOR), 0), fill=X)

    def create_stations(self, station_list):
        """ Generate all the stations """
        for station in station_list:
            station_id = self.canvas.create_oval(int((station.position.x-(S_SIZE/2))*SCALE_FACTOR),
                                                 int((station.position.y-(S_SIZE/2))*SCALE_FACTOR),
                                                 int((station.position.x+1+(S_SIZE/2)) *
                                                     SCALE_FACTOR),
                                                 int((station.position.y+1+(S_SIZE/2)) *
                                                     SCALE_FACTOR),
                                                 width=0,
                                                 fill=STATION)
            self.canvas.tag_bind(station_id, '<Button-1>',
                                 partial(self.on_station_l_click, station_id))
            self.canvas.tag_bind(station_id, '<Button-3>',
                                 partial(self.on_station_r_click, station_id))
            self.station_ids.append(station_id)

    def create_tracks(self, track_list):
        """ Join all the stations """
        express_ends = [53, 57]
        for track in track_list:
            if track[0].id in express_ends and track[1].id in express_ends:
                # This hacky workaround is to make a curve, as this one track makes the map look
                #  much worse when it goes straight.
                track_id = self.canvas.create_line(int(track[0].position.x*SCALE_FACTOR),
                                                   int(track[0].position.y*SCALE_FACTOR),
                                                   int(600*SCALE_FACTOR),
                                                   int(920*SCALE_FACTOR),
                                                   int(track[1].position.x*SCALE_FACTOR),
                                                   int(track[1].position.y*SCALE_FACTOR),
                                                   width=int(T_WIDTH*SCALE_FACTOR),
                                                   dash=(10, 3),
                                                   fill=TRACK,
                                                   smooth=1)
            else:
                track_id = self.canvas.create_line(int(track[0].position.x*SCALE_FACTOR),
                                                   int(track[0].position.y*SCALE_FACTOR),
                                                   int(track[1].position.x*SCALE_FACTOR),
                                                   int(track[1].position.y*SCALE_FACTOR),
                                                   width=int(T_WIDTH*SCALE_FACTOR),
                                                   dash=(10, 3),
                                                   fill=TRACK)
            self.canvas.tag_bind(track_id, '<Button-1>',
                                 partial(self.on_track_l_click, track_id))
            self.canvas.tag_bind(track_id, '<Button-3>',
                                 partial(self.on_track_r_click, track_id))
            self.track_ids.append(track_id)

    def start(self):
        """ Runs the loop """
        self.root.mainloop()

    # Action
    def redraw(self):
        # Stations
        lbl_contents = "-" if self.selected_station_1 is None else \
                       self.stations[self.station_ids.index(self.selected_station_1)].name
        self.station_1_label.config(text=lbl_contents)

        lbl_contents = "-" if self.selected_station_2 is None else \
                       self.stations[self.station_ids.index(self.selected_station_2)].name
        self.station_2_label.config(text=lbl_contents)

        btn_state = DISABLED if self.selected_station_1 is None or self.selected_station_2 is None \
                    else NORMAL  # noqa
        self.all_routes_btn.config(state=btn_state)
        self.shortest_route_btn.config(state=btn_state)

        # Routes
        lbl_contents = "-" if len(self.selected_tracks) == 0 else \
                       f"{len(self.selected_tracks)} selected"
        self.tracks_num_lbl.config(text=lbl_contents)

        selected_length = sum([self.tracks[self.track_ids.index(tk_id)][2] for tk_id in
                               self.selected_tracks])
        lbl_contents = "-" if len(self.selected_tracks) == 0 else f"{selected_length}km"
        self.tracks_dist_lbl.config(text=lbl_contents)

        self.next_path_btn.config(state=DISABLED)
        self.prev_path_btn.config(state=DISABLED)
        if len(self.pathset) > 1 and not self.cooldown:
            if self.path_index < len(self.pathset) - 1:
                self.next_path_btn.config(state=NORMAL)
            if self.path_index > 0:
                self.prev_path_btn.config(state=NORMAL)

        btn_state = DISABLED if len(self.selected_tracks) == 0 else NORMAL
        self.deselect_all_btn.config(state=btn_state)

        self.root.update_idletasks()

    def deselect_all(self, redraw=True):
        for sel in self.selected_tracks:
            self.canvas.itemconfig(sel, fill=TRACK)
        self.selected_tracks = []
        if redraw:
            self.redraw()

    def next_path(self):
        if self.path_index < len(self.pathset)-1:
            self.path_index += 1
            self.deselect_all(redraw=False)
            for tr_ind in self.pathset[self.path_index]:
                self.selected_tracks.append(self.track_ids[tr_ind])
                self.canvas.itemconfig(self.track_ids[tr_ind], fill=SELECTED)
            self.cooldown = True
            t = Thread(target=self.end_cooldown, args=())
            t.start()
            self.redraw()

    def prev_path(self):
        if self.path_index > 0:
            self.path_index -= 1
            self.deselect_all(redraw=False)
            for tr_ind in self.pathset[self.path_index]:
                self.selected_tracks.append(self.track_ids[tr_ind])
                self.canvas.itemconfig(self.track_ids[tr_ind], fill=SELECTED)
            self.cooldown = True
            t = Thread(target=self.end_cooldown, args=())
            t.start()
            self.redraw()

    def on_station_l_click(self, station_id, _):
        self.pathset = []
        if self.selected_station_1:
            self.canvas.itemconfig(self.selected_station_1, fill=STATION)
            if self.selected_station_1 == station_id:
                self.selected_station_1 = None
                self.redraw()
                return
            if self.selected_station_2 == station_id:
                self.selected_station_2 = None
        self.selected_station_1 = station_id
        self.canvas.itemconfig(station_id, fill=SELECTED)
        self.redraw()

    def on_station_r_click(self, station_id, _):
        self.pathset = []
        if self.selected_station_2:
            self.canvas.itemconfig(self.selected_station_2, fill=STATION)
            if self.selected_station_2 == station_id:
                self.selected_station_2 = None
                self.redraw()
                return
            if self.selected_station_1 == station_id:
                self.selected_station_1 = None
        self.selected_station_2 = station_id
        self.canvas.itemconfig(station_id, fill=SELECTED)
        self.redraw()

    def on_track_l_click(self, track_id, _):
        if track_id in self.selected_tracks:
            # Deselect
            self.selected_tracks.remove(track_id)
            self.canvas.itemconfig(track_id, fill=TRACK)
        elif track_id not in self.deactivated_tracks:
            # Select
            self.selected_tracks.append(track_id)
            self.canvas.itemconfig(track_id, fill=SELECTED)
        self.redraw()

    def on_track_r_click(self, track_id, _):
        if track_id in self.selected_tracks:
            # Deselect
            self.selected_tracks.remove(track_id)
            self.canvas.itemconfig(track_id, fill=TRACK)
        if track_id in self.deactivated_tracks:
            t = Thread(target=self.controller.activate_track,
                       args=(self.track_ids.index(track_id),
                             self.track_reactivated))
        else:
            t = Thread(target=self.controller.deactivate_track,
                       args=(self.track_ids.index(track_id),
                             self.track_deactivated))
        t.start()

    def all_routes(self):
        t = Thread(target=self.controller.all_paths_between,
                   args=(self.station_ids.index(self.selected_station_1),
                         self.station_ids.index(self.selected_station_2),
                         self.pathset_returned))
        t.start()

    def shortest_route(self):
        t = Thread(target=self.controller.shortest_path_between,
                   args=(self.station_ids.index(self.selected_station_1),
                         self.station_ids.index(self.selected_station_2),
                         self.pathset_returned))
        t.start()

    def step(self):
        """ Step the trains forward """
        events = self.controller.step(self.show_error)
        if events is not None:
            for timestamp, type, train, item in events:
                if type == "STATION":
                    self.station_prompt(timestamp, train, item)
                else:
                    self.talk_prompt(timestamp, train, item)
                self.update_trains()

    def station_prompt(self, timestamp, train, station):
        new_window = Toplevel(self.root)
        new_window.title(timestamp)

        message = f'{self.controller.trains[train].name} is going through \
                    {self.stations[station].name}. Would you like to stop?'
        Label(new_window, text=message).pack()
        Button(new_window, text="No", command=lambda:
               self.pass_station(train, station, new_window)).pack()
        Button(new_window, text="Yes", command=lambda:
               self.stop_at_station(train, station, new_window)).pack()

    def pass_station(self, train, station, window):
        self.controller.train_pass_station(train, station, False)
        window.destroy()

    def talk_prompt(self, timestamp, train, item):
        new_window = Toplevel(self.root)
        new_window.title(timestamp)

        message = f'{self.controller.trains[train].name} and {self.controller.trains[item].name} \
                    have a chance to talk as they pass.'
        Label(new_window, text=message).pack()

        sleep(10)
        new_window.destroy()

    def stop_at_station(self, train, station, window):
        self.controller.train_pass_station(train, station, True)
        window.destroy()

    def update_trains(self):
        """ Update their locations """
        # Remove old
        for txt, box in self.train_labels:
            self.canvas.delete(txt)
            self.canvas.delete(box)

        self.train_labels = []
        count = {}
        for train in self.controller.get_active_trains():
            station = self.stations[train.last_station]
            if station not in count:
                count[station] = 0
            count[station] += 1

            x_val = int((station.position.x + 10*count[station])*SCALE_FACTOR)
            y_val = int((station.position.y)*SCALE_FACTOR)
            t_label = self.canvas.create_text(x_val, y_val, text=train.number)
            bgbox = self.canvas.create_rectangle(self.canvas.bbox(t_label), fill=train.colour)
            self.canvas.tag_lower(bgbox, t_label)
            self.train_labels.append((t_label, bgbox))

        self.dm.rerender()

    # Callbacks
    def show_error(self, message):
        """ Called by controller """
        self.msg_lbl.config(text=message)
        self.root.update_idletasks()

    def pathset_returned(self, paths):
        """ Called by the controller """
        self.path_index = 0
        self.pathset = paths
        self.deselect_all(redraw=False)
        for tr_ind in self.pathset[self.path_index]:
            self.selected_tracks.append(self.track_ids[tr_ind])
            self.canvas.itemconfig(self.track_ids[tr_ind], fill=SELECTED)
        self.redraw()

    def track_deactivated(self, track_id):
        self.deactivated_tracks.append(self.track_ids[track_id])
        self.canvas.itemconfig(self.track_ids[track_id], fill=BROKEN)
        self.redraw()

    def track_reactivated(self, track_id):
        self.deactivated_tracks.remove(self.track_ids[track_id])
        self.canvas.itemconfig(self.track_ids[track_id], fill=TRACK)
        self.redraw()

    def end_cooldown(self):
        sleep(0.3)
        self.cooldown = False
        self.redraw()


class DMWindow:
    # Setup
    def __init__(self, root, controller, true_root):
        # Attributes
        self.true_root = true_root
        self.root = root
        self.controller = controller
        self.window = Toplevel(self.root)
        self.subwindows = []

        # Create this window
        self.window.title("Sodor Railway Management System - Information")
        self.window.attributes("-fullscreen", True)

        self.populate_window()

    def populate_window(self):
        locations = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1)]
        for i in range(NUM_PLAYERS):
            train_frame = Frame(self.window, highlightbackground="#888", highlightthickness="1")
            self.subwindows.append(TrainWindow(train_frame, self.controller, self.true_root))
            train_frame.grid(row=locations[i][0], column=locations[i][1], sticky="ns")

        puzzle_frame = Frame(self.window,  highlightbackground="#888", highlightthickness="1")
        puzzle_frame.grid(row=2, column=2, sticky="we", ipady=10, ipadx=10)

        PuzzleWindow(puzzle_frame, self.controller)

    # Action

    # Callbacks
    def rerender(self):
        for win in self.subwindows:
            win.rerender()


class TrainWindow:
    # Setup
    def __init__(self, window, controller, true_root):
        self.true_root = true_root
        self.window = window
        self.controller = controller
        self.train_names = self.controller.get_train_names()
        self.train_object = None
        self.previous_train = None

        self.train_selected = StringVar()
        dropdown = OptionMenu(self.window, self.train_selected, *self.train_names)
        dropdown.config(width=40)
        dropdown.grid(row=0, column=0, columnspan=3)
        self.train_selected.trace("w", self.update)

        self.num_label = Label(self.window)
        self.num_label.grid(row=1, column=1)

        Label(self.window, text="Last station: ").grid(row=2, column=0, columnspan=2)
        self.station_label = Label(self.window, text="-")
        self.station_label.grid(row=2, column=2)

        Label(self.window, text="Dist. since station: ").grid(row=3, column=0, columnspan=2)
        self.distance_label = Label(self.window, text="-")
        self.distance_label.grid(row=3, column=2)

        self.facing = StringVar()
        Label(self.window, text="Facing station: ").grid(row=4, column=0, columnspan=2)
        self.facing_select = OptionMenu(self.window, self.facing, *[''])
        self.facing_select.grid(row=4, column=2)
        self.facing.trace("w", self.change_facing)

        Label(self.window, text="Remaining range: ").grid(row=5, column=0, columnspan=2)
        self.range_label = Label(self.window, text="-")
        self.range_label.grid(row=5, column=2)

    # Callbacks
    def change_facing(self, *args):
        value = self.facing.get()
        if value != '' and self.train_object is not None:
            ident = None
            for i in range(len(self.true_root.stations)):
                if self.true_root.stations[i].name == value:
                    ident = i

            if ident is not None:
                self.train_object.facing = ident

    def update(self, *args):
        self.previous_train = self.train_object
        self.train_object = self.controller.get_train_by_name(self.train_selected.get())
        if self.train_object is not None:
            self.num_label.config(text=self.train_object.number,
                                  background=self.train_object.colour)
            self.train_object.played = True

        if self.previous_train is not None:
            self.previous_train.played = False

        self.true_root.update_trains()
        self.window.update_idletasks()

    def rerender(self):
        if self.train_object is not None:
            self.station_label.config(text=self.train_object.last_station)
            self.distance_label.config(text=self.train_object.distance_from_last_station)
            self.range_label.config(text=self.train_object.remaining_range)
            self.facing.set('')
            self.facing_select['menu'].delete(0, 'end')
            new_choices = [self.controller.model.nodes[stat].name for stat in
                           self.controller.get_adjacent_nodes(self.train_object.last_station)]
            for choice in new_choices:
                self.facing_select['menu'].add_command(label=choice,
                                                       command=tk._setit(self.facing, choice))
            if self.train_object.facing is not None:
                self.facing.set(f'{self.controller.model.nodes[self.train_object.facing].name}')


class PuzzleWindow:
    # Setup
    def __init__(self, window, controller):
        self.controller = controller
        self.window = window
        Label(self.window, text="Crane Puzzle Generator").grid(row=0, column=0, columnspan=3)

        Label(self.window, text="Starting point:").grid(row=1, column=0)
        self.start = Entry(self.window)
        self.start.grid(row=1, column=1)

        Label(self.window, text="Anti-Cl. Step:").grid(row=2, column=0)
        self.left_step = Entry(self.window)
        self.left_step.grid(row=2, column=1)

        Label(self.window, text="Clockwise Step:").grid(row=3, column=0)
        self.right_step = Entry(self.window)
        self.right_step.grid(row=3, column=1)

        self.submit_btn = Button(self.window, bg=BUTTON, text="Submit", command=self.generate)
        self.submit_btn.grid(row=4, column=2)

        Label(self.window, text="-"*35).grid(row=5, column=0, columnspan=3)

        self.output_lbl = Message(self.window, text="\n\n\n")
        self.output_lbl.grid(row=6, column=0, columnspan=3)

    # Action
    def generate(self):
        strt = self.start.get()
        ls = self.left_step.get()
        rs = self.right_step.get()
        if strt != '' and ls != '' and rs != '':
            t = Thread(target=self.controller.crane_puzzle_numbers, args=(int(strt), int(ls),
                       int(rs), self.update))
            t.start()

    # Callbacks
    def update(self, description=None):
        if description is not None:
            self.output_lbl.config(text=description)
        self.window.update_idletasks()


def test():
    from Model import Model
    g = Model("./data/stations.txt", "./data/tracks.txt")

    v = View(None, g.nodes, g.get_all_edges())
    v.start()

    # Test response to path information
    v.pathset_returned([[0, 1, 2, 3, 4], [5, 6, 7, 8]])

    # Let user know of our success!
    print("All tests passed with flying scotsman!")


# Only run tests if this is not imported
if __name__ == "__main__":
    test()
