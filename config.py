import os
import configparser

class RaceCreator:
    def __init__(self):
        print("-> Create Race File <-")
        self.race_name = input("Race Name > ")
        self.car_file = input("Car File > ")
        self.track_file = input("Track File > ")

        self.car_config = configparser.ConfigParser()
        self.car_config.read(self.car_file)
        self.track_config = configparser.ConfigParser()
        self.track_config.read(self.track_file)

        self.create_file()
        self.create_race()
        self.write_file()
    
    def create_lap_data(self):
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

        self.create_lap_data()
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
    action = input("[c]reate : [m]odify $ ")
    if action == "c":
        race_creator = RaceCreator()