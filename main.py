from calculator import TargetCalculator, LiveCalculator
from display import Display
from data import RaceData

race_data = RaceData("races/gt-endurance-barcelona.ini")
lc = LiveCalculator(race_data)
tc = TargetCalculator(race_data)

display = Display(race_data, lc, tc)
display.display_all()