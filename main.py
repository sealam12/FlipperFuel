from calculator import TargetCalculator, LiveCalculator
from display import OverlayDisplay
from data import RaceData
import sys
import math
from PyQt5 import QtCore, QtGui, QtWidgets
import irsdk

race_data = RaceData("races/petit-lemans.ini")
lc = LiveCalculator(race_data)
tc = TargetCalculator(race_data)

fuel_use = []
last_fuel_level = 0
lap_times = []
last_lap_time = 0
in_pit_stall = False

def irsdk_update_all(sdk):
    global race_data, fuel_use, last_fuel_level, lap_times, last_lap_time, in_pit_stall

    current_fuel_level = sdk["FuelLevel"] * 0.264172  
    used_fuel = last_fuel_level - current_fuel_level

    pit_stall = sdk["PlayerCarInPitStall"]
    if in_pit_stall == True and pit_stall == False:
        race_data.live_data.completed_stints += 1
        pass
    
    in_pit_stall = pit_stall

    lap_time = sdk["LapLastLapTime"]
    if lap_time != last_lap_time:
        if abs(last_lap_time - lap_time) < (last_lap_time * 0.1):
            lap_times.append(lap_time)
        
        lap_times = lap_times[-5:]

        if used_fuel > 0:
            print(used_fuel)
            fuel_use.append(used_fuel)
            fuel_use = fuel_use[-5:]

        last_fuel_level = current_fuel_level
        last_lap_time = lap_time

    try:
        race_data.live_data.avg_lap_time = sum(lap_times) / len(lap_times)
        race_data.live_data.avg_lap_fuel = sum(fuel_use) / len(fuel_use)
    except:
        pass
    
    race_data.live_data.fuel_remaining = current_fuel_level 
    race_data.live_data.minutes_remaining = sdk["SessionTimeRemain"] / 60

if __name__ == "__main__":
    ir = irsdk.IRSDK()
    ir.startup()

    app = QtWidgets.QApplication(sys.argv)

    def tick():
        if (ir.is_initialized and ir.is_connected):
            irsdk_update_all(ir)

    updater = QtCore.QTimer()
    updater.timeout.connect(tick)
    updater.start(50)

    overlay = OverlayDisplay(race_data, lc, tc)
    overlay.show()
    sys.exit(app.exec_())
