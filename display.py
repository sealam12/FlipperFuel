from blessed import Terminal
import time, math

term = Terminal()
bgcolor = term.on_color_rgb(60,56,54)

def fill(x1, y1, x2, y2, char):
    for y in range(y1, y2):
        for x in range(x1, x2):
            if y > y1:
                print("\n", end="")
            print(term.move_xy(x, y) + char + term.normal, end="")

def outline_sides(x, y, txt):
    print(term.move_xy(x, y) + bgcolor + "  " + term.normal + " " + txt + " " +  bgcolor + "  " + term.normal, end="")

class Display:
    def __init__(self, race_data, live_calculator, target_calculator):
        self.rd = race_data
        self.lc = live_calculator
        self.tc = target_calculator

        self.on_track = True

    def display_target_race(self):
        print(term.move_xy(0, 0) + bgcolor + "       TARGET RACE        " + term.normal, end="")
        outline_sides(0, 1, f"STINTS            {self.rd.targets.stint_target:02d}")
        outline_sides(0, 2, f"LAPS             {self.lc.total_race_laps():03d}")
        outline_sides(0, 3, f"FUEL          {self.lc.total_race_fuel():06.2f}")

    def display_target_stint(self):
        print(term.move_xy(26, 0) + bgcolor + "      TARGET STINT      " + term.normal, end="")
        outline_sides(24, 1, f"LAP FUEL        {self.tc.lap_fuel_required():04.2f}" + term.normal)
        outline_sides(24, 2, f"LAPS           {self.tc.stint_laps_required():05.2f}" + term.normal)
        outline_sides(24, 3, f"TIME           {self.tc.stint_time_required():05.2f}" + term.normal)

    def display_live_race(self):
        color = self.lc.projected_stints_total() > self.rd.seed_data.avg_lap_fuel and term.on_red or ""

        print(term.move_xy(0, 4) + bgcolor + "        LIVE RACE         " + term.normal, end="")
        outline_sides(0, 5, f"FUEL R        {self.lc.remaining_race_fuel():06.2f}")
        outline_sides(0, 6, f"LAPS R           {self.lc.remaining_race_laps():03d}")
        outline_sides(0, 7, color + f"STINTS PROJ       {self.lc.projected_stints_total():02d}" + term.normal)
        outline_sides(0, 8, color + f"STINTS REMN       {self.lc.projected_stints_remaining():02d}" + term.normal)

    def display_live_stint(self):
        print(term.move_xy(26, 4) + bgcolor + "       LIVE STINT       " + term.normal, end="")

        color = ""
        if self.rd.live_data.avg_lap_fuel > self.tc.lap_fuel_required():
            color = term.on_yellow
        if self.rd.live_data.avg_lap_fuel > self.lc.lap_fuel_required():
            color = term.on_red

        outline_sides(24, 5, color + f"AVG FUEL        {self.rd.live_data.avg_lap_fuel:04.2f}" + term.normal)
        outline_sides(24, 6, f"AVG TIME      {self.rd.live_data.avg_lap_time:06.2f}")
        outline_sides(24, 7, f"LAPS R         {self.lc.current_stint_laps_remaining():05.2f}")
        outline_sides(24, 8, f"TIME R         {self.lc.current_stint_time_remaining():05.2f}")
    
    def display_live_minimum(self):
        lf_color = self.lc.lap_fuel_required() < self.tc.lap_fuel_required() and term.on_yellow or ""
        l_color = self.lc.stint_laps_required() > self.tc.stint_laps_required() and term.on_yellow or ""
        t_color = self.lc.stint_time_required() > self.tc.stint_time_required() and term.on_yellow or ""

        print(term.move_xy(0, 9) + bgcolor + "                   LIVE MINIMUM                   " + term.normal, end="")
        outline_sides(12, 10, lf_color + f"LAP FUEL        {self.lc.lap_fuel_required():04.2f}" + term.normal)
        outline_sides(12, 11, l_color + f"LAPS           {self.lc.stint_laps_required():05.2f}" + term.normal)
        outline_sides(12, 12, t_color + f"TIME           {self.lc.stint_time_required():05.2f}" + term.normal)
        print(term.move_xy(0, 13) + (" " * 12) + bgcolor + (" " * 26) + term.normal, end="")

    def display_all(self):
        global bgcolor 

        while True:
            print(term.home + term.clear, end="")

            self.on_track = self.lc.projected_stints_total() <= self.rd.targets.stint_target

            self.display_target_race()
            self.display_target_stint()

            self.display_live_race()
            self.display_live_stint()

            self.display_live_minimum()

            print(term.move_xy(0, term.height-1), end="")

            print(end="", flush=True)
            time.sleep(1)