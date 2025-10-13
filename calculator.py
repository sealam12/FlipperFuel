from data import RaceData
import math

class TargetCalculator:
    def __init__(self, race_data):
        self.data = race_data
    
    def total_race_laps(self):
        length_seconds = self.data.race_info.race_length * 60
        avg_lap_time = self.data.seed_data.avg_lap_time
        total_race_laps = math.ceil(length_seconds / avg_lap_time)
        
        return total_race_laps
    
    def total_race_fuel(self):
        total_race_laps = self.total_race_laps()
        lap_fuel = self.lap_fuel_required()
        total_race_fuel = lap_fuel * total_race_laps

        return total_race_fuel

    def stint_laps_required(self):
        total_laps = self.total_race_laps()
        stint_goal = self.data.targets.stint_target

        stint_laps_required = total_laps / stint_goal

        return stint_laps_required

    def stint_time_required(self):
        stint_laps = self.stint_laps_required()
        avg_lap_time = self.data.seed_data.avg_lap_time
        stint_time_required = (stint_laps * avg_lap_time) / 60

        return stint_time_required

    def lap_fuel_required(self):
        stint_laps = self.stint_laps_required()
        max_fuel = self.data.car_info.max_fuel

        lap_fuel_required = round(max_fuel / stint_laps, 3)

        return lap_fuel_required

class LiveCalculator:
    def __init__(self, race_data):
        self.data = race_data
    
    def total_race_laps(self):
        length_seconds = self.data.race_info.race_length * 60
        avg_lap_time = self.data.live_data.avg_lap_time
        total_race_laps = math.ceil(length_seconds / avg_lap_time)
        
        return total_race_laps

    def total_race_fuel(self):
        total_race_laps = self.total_race_laps()
        total_race_fuel = total_race_laps * self.data.live_data.avg_lap_fuel

        return total_race_fuel
        
    def remaining_race_laps(self):
        seconds_remaining = self.data.live_data.minutes_remaining*60
        avg_lap_time = self.data.live_data.avg_lap_time
        remaining_race_laps = math.ceil(seconds_remaining / avg_lap_time)

        return remaining_race_laps

    def remaining_race_fuel(self):
        remaining_race_laps = self.remaining_race_laps()
        remaining_race_fuel = remaining_race_laps * self.data.live_data.avg_lap_fuel

        return remaining_race_fuel

    def projected_stints_remaining(self):
        remaining_laps = self.remaining_race_laps()
        required_fuel = remaining_laps * self.data.live_data.avg_lap_fuel
        remaining_stints = required_fuel / self.data.car_info.max_fuel

        return math.ceil(remaining_stints)
    
    def projected_stints_total(self):
        return self.projected_stints_remaining() + self.data.live_data.completed_stints

    def current_stint_laps_remaining(self):
        remaining_fuel = self.data.live_data.fuel_remaining
        remaining_laps = remaining_fuel / self.data.live_data.avg_lap_fuel

        return remaining_laps
    
    def current_stint_time_remaining(self):
        remaining_laps = self.current_stint_laps_remaining()
        remaining_time = (remaining_laps * self.data.live_data.avg_lap_time) / 60

        return remaining_time
    
    def stint_laps_required(self):
        stints_remaining = self.data.targets.stint_target - self.data.live_data.completed_stints
        laps_remaining = self.remaining_race_laps()

        return laps_remaining / stints_remaining
    
    def lap_fuel_required(self):
        stints_remaining = self.data.targets.stint_target - self.data.live_data.completed_stints
        fuel_remaining = self.data.live_data.fuel_remaining + ( ( stints_remaining-1 ) * self.data.car_info.max_fuel )

        laps_remaining = self.remaining_race_laps()
        lap_fuel_required = round(fuel_remaining / laps_remaining, 3)

        return lap_fuel_required

    def stint_time_required(self):
        laps_required = self.stint_laps_required()
        time_required = (laps_required * self.data.live_data.avg_lap_time) / 60

        return time_required