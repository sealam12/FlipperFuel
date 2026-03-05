import os, blessed, configparser

term = blessed.Terminal()

class RaceCreator:
    def select(self, heading, items):
        last_key = ""
        selection_index = 0
        while last_key != "KEY_ENTER":
            print(term.home + term.clear, end="")
            print(term.on_color_rgb(60,60,60) + term.center(heading) + term.normal)
            for indx, item in enumerate(items):
                clr = (indx == selection_index) and term.on_color_rgb(50,255,50) or term.on_color_rgb(60,60,60)
                print(term.center(clr + item + term.normal))

            val = term.inkey()

            if val.is_sequence:
                last_key = val.name
            else:
                last_key = val
            
            if last_key == "KEY_UP":
                selection_index -= 1
            elif last_key == "KEY_DOWN":
                selection_index += 1
            
            if selection_index < 0:
                selection_index = len(items)-1
            elif selection_index > (len(items)-1):
                selection_index = 0
        
        return items[selection_index]

    def centered_input(self, prompt):
        last_key = ""
        txt = ""
        while last_key != "KEY_ENTER":
            print(term.home + term.clear, end="")
            print(term.on_color_rgb(60,60,60) + term.center(prompt) + term.normal)
            print(term.center("> " + txt))

            val = term.inkey()

            if val.is_sequence:
                last_key = val.name

                if val.name == "KEY_BACKSPACE":
                    txt = txt[:-1]
            else:
                last_key = val
                txt += last_key
        
        return txt

    def __init__(self):
        print(term.home + term.normal + term.clear, end="")
        print(term.on_color_rgb(60,60,60) + term.center("Create Race File") + term.normal)
        print(term.move_xy(0, round(term.height/2)) + term.center("Press any key to begin."))

        with term.cbreak():
            term.inkey()

            self.race_name = self.centered_input("Enter Race Name")

            self.car_file = "cars/" + self.select("Select Car File", os.listdir("cars"))
            self.track_file = "tracks/" + self.select("Select Track File", os.listdir("tracks"))

        self.car_config = configparser.ConfigParser()
        self.car_config.read(self.car_file)
        self.track_config = configparser.ConfigParser()
        self.track_config.read(self.track_file)

        self.create_file()
        self.create_race()
        self.write_file()
    
    def create_seed_data(self):
        car_class = self.car_config["CarInfo"]["car_class"].split("\"")[1].lower()

        lap_fuel = 0
        lap_time = 0
        
        if self.track_config["LapFuel"].get(car_class) != None:
            lap_fuel = self.track_config["LapFuel"].getfloat(car_class)
            print(f"Used existing lap fuel data [{lap_fuel}]")
        else:
            lap_fuel = float(input("Avg Lap Fuel > "))
        
        if self.track_config["LapTimes"].get(car_class) != None:
            lap_time = self.track_config["LapTimes"].getfloat(car_class)
            print(f"Used existing lap time data [{lap_time}]")
        else:
            lap_time = float(input("Avg Lap Time > "))

        self.race_config.set("Data", "avg_lap_fuel", str(lap_fuel))
        self.race_config.set("Data", "avg_lap_time", str(lap_time))
    
    def create_race(self):
        self.race_config.set("RaceInfo", "race_name", self.race_name)

        self.create_seed_data()
        self.race_config.set("CarInfo", "max_fuel", self.car_config["Fuel"]["max_fuel"])

        self.race_config.set("RaceInfo", "track_file", f"\"{self.track_file}\"")
        self.race_config.set("CarInfo", "car_file", f"\"{self.car_file}\"")

        race_length = int(input("Race Length > "))
        self.race_config.set("RaceInfo", "race_length", str(race_length))

        stint_target = int(input("Stint Target > "))
        self.race_config.set("Targets", "stint_target", str(stint_target))
    
    def create_file(self):
        self.race_config = configparser.ConfigParser()
        self.race_config.add_section("RaceInfo")
        self.race_config.add_section("CarInfo")
        self.race_config.add_section("Targets")
        self.race_config.add_section("Data")
    
    def write_file(self):
        file_name = self.race_name.replace(" ", "-").lower() + ".ini"
        file_path = "races/" + file_name

        with open(file_path, "w") as file:
            self.race_config.write(file)

if __name__ == "__main__":
    race_creator = RaceCreator()