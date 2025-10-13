import configparser

class RaceInfo:
    def __init__(self, data):
        self.start_time = data.getint("start_time")
        self.race_length = data.getint("race_length")

class CarInfo:
    def __init__(self, data):
        self.max_fuel = data.getfloat("max_fuel")

class Targets:
    def __init__(self, data):
        self.stint_target = data.getint("stint_target")

class SeedData:
    def __init__(self, data):
        self.avg_lap_time = data.getfloat("avg_lap_time")
        self.avg_lap_fuel = data.getfloat("avg_lap_fuel")

class LiveData:
    def __init__(self, full_data):
        self.avg_lap_time = full_data["Data"].getfloat("avg_lap_time")
        self.avg_lap_fuel = full_data["Data"].getfloat("avg_lap_fuel")

        self.completed_stints = 0
        self.minutes_remaining = full_data["RaceInfo"].getint("race_length")
        self.fuel_remaining = full_data["CarInfo"].getfloat("max_fuel")

class RaceData:
    def __init__(self, race_file):
        filepath = race_file

        self.config = configparser.ConfigParser()
        self.config.read(filepath)

        self.race_info = RaceInfo(self.config["RaceInfo"])
        self.car_info = CarInfo(self.config["CarInfo"])
        self.targets = Targets(self.config["Targets"])
        self.seed_data = SeedData(self.config["Data"])
        self.live_data  = LiveData(self.config)