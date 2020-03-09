'''
DP3 Code 
Team 33
@Author Ishan Vermani
@Author Owen Johnstone

If the monitor reads "Sensor not responding, please press button":
- Press the blue button on the bottom right of the breadboard twice (once to depress, once to repress)
- This restarts the sensor by momentarily breaking its power supply
'''

import time
from gpiozero import LED, Button

while True:
    try:
        from sensor_library import *
        break
    except OSError:
        print("Import Error. Check Wiring of sensor")
import pygame

pygame.init()
danger_zone = pygame.mixer.Sound('/home/pi/Desktop/DP3/danger_zone_sound_wav.wav')

green1LED = LED(1)
green2LED = LED(7)
green3LED = LED(8)
yellow1LED = LED(25)
yellow2LED = LED(24)
yellow3LED = LED(23)
red1LED = LED(18)
red2LED = LED(15)
red3LED = LED(14)
coLED = LED(26)
h2LED = LED(17)
propaneLED = LED(27)
butaneLED = LED(22)
methaneLED = LED(10)
ethanolLED = LED(9)
statusLED = LED(12)
buttonLED = LED(13)
sensor = Gas_Sensor()
button = Button(6)

# A tier list for each gas that relates the PPM value to the number of LEDs to turn on
CO_values = [5,10,15,20,250,300,350,400,450]
H2_values = [0, 1, 2, 3, 4, 500, 600, 700, 800]
propane_values = [7500, 15000, 30000, 60000, 80000, 500000, 600000, 700000, 800000]
butane_values = [1000, 2000, 3000, 4000, 100000, 160000, 170000, 180000, 190000]
methane_values = [1, 2, 3, 4, 6, 600000000, 800000000, 10000000000, 12000000000]
ethanol_values = [1, 3, 5, 7, 8, 8.1, 8.2, 8.3, 8.4]

gas_list = ["CO", "H2", "propane", "butane", "methane", "ethanol"]
CO_list = []
H2_list = []
propane_list = []
butane_list = []
methane_list = []
ethanol_list = []
total_gas_list = [CO_list, H2_list, propane_list, butane_list, methane_list, ethanol_list]
average_gas_list = []
dangerous_gases_indexes = []
all_gas_tier_list = [CO_values, H2_values, propane_values, butane_values, methane_values, ethanol_values]
meter_LED = [green1LED, green2LED, green3LED, yellow1LED, yellow2LED, yellow3LED, red1LED, red2LED, red3LED]
gas_LED = [coLED, h2LED, propaneLED, butaneLED, methaneLED, ethanolLED]

''' danger = 0 - Normal function. Button LED is on, active danger mode is automatically activated if a dangerous gas concentration is reached.
    danger = 1 - Active danger. Button LED flashes, corresponding gas indicator flashes, speaker turns on, a single button press selects the most dangerous gas and activates passive danger mode.
    danger = 2 - Passive danger. Button LED flashes, corresponding gas indicator flashes. The speaker turns off, and a button press does not automatically select the most dangerous gas. To enter back into normal function, press and hold the button for a minimum of 2 seconds.'''
danger = 0
danger_threshold = 6 # Index value of the lowest LED considered to be dangerous
sleep = False
count = 0 # Counter variable used to toggle the gas LEDs of the corresponding dangerous gases
sleep_counter = 0 # Counts how long it has been since the last data point has been recorded
sleep_target = 0 # Determines the feed rate while in sleep mode based upon the highest detected gas concentration
sound_played = False
print_timer = 1 # Counter variable to control frequency of the print statement
time_sleep = 100 # Determines the time between print statements
sensor_data = []
selected_gas = 'CO'

# The gas LEDs and meter LEDs are turned on and then off, signaling the powering on of the device
def on_sequence():
    for item in gas_LED:
        item.on()
    for i in range(len(meter_LED)):
        meter_LED[i].on()
        time.sleep(0.05)
    for i in range(-1, -1*len(meter_LED) - 1, -1):
        meter_LED[i].off()
        time.sleep(0.05)
    for item in gas_LED:
        item.off()
    gas_LED[gas_list.index(selected_gas)].on()
    buttonLED.on()

# Task 1: Status (Uses get_reading(), main() and average_reading())
''' The CO, H2, propane, butane, methane and ethanol gas concentrations are recorded, and appended to the corresponding list that contains that gas's data '''
def get_reading():
    global CO_list, H2_list, propane_list, methane_list, butane_list, ethanol_list
    CO_list.append(sensor.CO_gas())
    H2_list.append(sensor.H2_gas())
    propane_list.append(sensor.propane())
    butane_list.append(sensor.butane())
    methane_list.append(sensor.methane())
    ethanol_list.append(sensor.ethanol())

''' The sensor records a data point, and then the last 10 concentrations of each gas is extracted from the gas's data list. The average of the last 10 concentrations for each gas is calculated, and appended to a list. If there are fewer than 10 data points, then None is returned and the status light is turned off. Otherwise, the list of averages is returned, and the status light is turned on. The danger status, gas concentrations, and LED statuses are printed approximately every 10 seconds while in sleep mode, but are printed every 1 second while in normal mode. '''
def average_reading():
    global total_gas_list, average_gas_list, print_timer, danger
    get_reading()
    average_gas_list = []
    for i in total_gas_list:
        last_10_entries = i[-10:]
        data_sum = sum(last_10_entries)
        average = data_sum / 10
        if len(i) < 10:
            statusLED.off()
            return None
        else:
            average_gas_list.append(round(average,2))
            
    if danger == 0:
        danger_state = 'Normal mode'
    elif danger == 1:
        danger_state = 'Active danger'
    elif danger == 2:
        danger_state = 'Passive danger'
    if print_timer % time_sleep == 0 and sensor_data[0] != 4.38 and sensor_data[1] != 0.73 and sensor_data[2] != 571.16:
        print("CO: " + str(sensor_data[0]) + "   H2: " + str(sensor_data[1]) + "   Propane: " + str(sensor_data[2]) + "   Butane: " + str(sensor_data[3]) + "   Methane: " + str(sensor_data[4]) + "   Ethanol: " + str(sensor_data[5]) + "  Status LED: " + str(statusLED.is_active) + "   Max LED tier: " + str(sleep_compare(sensor_data)) + "  Danger status: " + danger_state + '\n')
        print_timer = 1
        statusLED.on()
    else:
        print_timer += 1
    return average_gas_list

# Task 2: Notification (Uses compare_primary(), turn_on_LED(), turn_off_LED(), cycle_gas() and main())
''' The index of the currently selected gas is obtained, and then a for loop is created which loops through each LED in the meter. For each LED in the meter, the corresponding entry in the list of tier lists is obtained. Then, if the recorded value from the sensor is greater or equal to the tier, then the meter LED is turned on, otherwise the meter LED is turned off. Furthermore, if the meter LED that is being turned on is greater than the danger threshold and danger mode is not already active, then it is enabled. '''
def compare_primary(reading_list):
    global selected_gas, danger
    sensor_value = reading_list[gas_list.index(selected_gas)]
    for i in range(len(meter_LED)):
        item = all_gas_tier_list[gas_list.index(selected_gas)][i] # Finds the i'th tier value for the selected gas
        if item <= sensor_value:
            turn_on_LED(meter_LED, i)
            if i >= danger_threshold and danger == 0:
                danger = 1
        else:
            turn_off_LED(meter_LED, i)

''' This function allows the device to monitor each gas, even if the gas is not currently selected, and checks if any gas is above the danger threshold. The list of average gas concentrations is passed as an argument, and each gas is cycled through using a for loop. If the index of the gas does not match the index of the currently selected gas, then the gas concentration is compared to the danger threshold for that gas. If the concentration is greater than the danger threshold, then the gas's index is added to a list which stores the indexes of the currently danger gases and sleep mode is disabled. If the sensor is still in normal mode, then Active danger mode is activated, otherwise the corresponding gas light is turned off. A part of Task 3 (Escalation)'''
def compare_secondary(reading_list):
    global danger, sleep, dangerous_gases_indexes
    dangerous_gases_indexes = []
    for gas in range(len(gas_list)):
        sensor_value = reading_list[gas]
        if gas != gas_list.index(selected_gas): # Does not need to look at the currently selected gas, as it is handled in compare_primary() 
            if sensor_value >= all_gas_tier_list[gas][danger_threshold]:
                dangerous_gases_indexes.append(gas) # Appends the index of the dangerous gas
                if danger == 0:
                    danger = 1
                sleep = False
            else:
                turn_off_LED(gas_LED, gas)

''' This function provides the mechanism for changing the selected gas, which is initiated by a button press. The index of the currently selected gas is determined, and the gas LED corresponding to the currently selected gas is turned off. The gas LED for the next gas is turned on, and the value of selected_gas is updated to match the currently selected gas. '''
def cycle_gas():
    global selected_gas
    gas_index = gas_list.index(selected_gas)
    if gas_index <= 4:
        next_gas = gas_index + 1
        gas_LED[next_gas].on()
    else:
        next_gas = 0 # Since there are only six gases and gas LEDs, the index needs to be reset back to 0 to switch from the 6th gas back to the 1st
        coLED.on()
    gas_LED[gas_index].off()
    selected_gas = gas_list[next_gas]

''' This function allows the device to determine what gas is the most dangerous based upon the average gas concentrations. Each dangerous gas index is cycled through, and then each tier in the corresponding gas's tier list is cycled through. If the detected gas concentration is greater than the tier value and the tier is greater than the previous largest tier, then the tier is increased and the maximum gas index is set equal to the index of the most dangerous gas. The most dangerous gas is then returned. '''
def danger_level_cycle(reading_list):
    max_gas_index = 0
    for gas_index in dangerous_gases_indexes:
        tier = 0
        for i in range(len(all_gas_tier_list[gas_index])):
            if all_gas_tier_list[gas_index][i] <= reading_list[gas_index] and i > tier: # Checks if the detected gas concentration is greater than the corresponding value in the tier list, and if the current index is greater than the previous largest index
                tier = i
                max_gas_index = gas_index
    return gas_list[max_gas_index - 1] # Returns the most dangerous gas (as a string from gas_list)

# Task 3: Escalation (uses toggle_LED(), danger_level_cycle(), main(), and compare_primary() and compare_secondary() to determine when to enter danger mode)
''' This function controls the blinking of LEDs when in Active or Passive danger mode, and controls the state of the LEDs when in Normal or Sleep mode. If either Active or Passive danger mode is activated, then the button LED and the gas LEDs corresponding to the dangerous gases are toggled on and off. The frequency of the toggling is determined using a counter variable. If the device is in Normal mode, then the button LED is turned on, but if the device is in sleep mode, the button LED is turned off. Finally, the gas LEDs of the dangerous gases are turned off, as the device is operating in Normal mode. '''
def toggle_LED():
    global count, danger
    if danger > 0:
        count += 1
        if count % 10 == 0:
            for item in dangerous_gases_indexes:
                gas_LED[item].toggle()
            buttonLED.toggle()
    else:
        if sleep == False:
            buttonLED.on()
        else:
            buttonLED.off()
        for item in dangerous_gases_indexes:
            gas_LED[item].off()

# Task 4: Sleep Mode (uses sleep_compare() and main())
''' This function allows for the device to find the index of the highest active meter LED, as this value is used to calculate the time between data recordings when in sleep mode. Each gas is cycled through and the data corresponding to that gas is extracted from the list of average gas concentrations, which is passed as an argument to the function. Then each meter LED is cycled through, and if the sensor value is greater than the tier for that LED and if the LED index is greater than the previous highest LED index, then the LED index is increased by 1. This allows the device to determine the maximum number of currently lit meter LEDs. If the highest LED index is greater than the danger threshold, then sleep mode is disabled, Active danger is activated and the danger threshold is returned as the highest LED index. If the highest LED index does not indicate that there is a dangerous gas concentration, then the value of the highest LED index is returned. '''
def sleep_compare(reading_list):
    global sleep, danger
    highest_LED_index = 0
    for gas in range(len(gas_list)):
        sensor_value = reading_list[gas]
        for LED_index in range(len(meter_LED)):
            if all_gas_tier_list[gas][LED_index] <= sensor_value and LED_index > highest_LED_index: # Checks if the LED should be on and if the LED has a higher index than the previous highest LED index
                highest_LED_index = LED_index + 1
    if highest_LED_index >= danger_threshold: # Checks if Active danger should be activated
        sleep = False
        gas_LED[gas_list.index(selected_gas)].on()
        if danger == 0:
            danger = 1
            
        return danger_threshold
    else:
        return highest_LED_index

''' This function turns on the LED in the list and index, which are passed as arguments '''
def turn_on_LED(LED_list, LED_value):
    LED_list[LED_value].on()

''' This function turns off the LED in the list and index, which are passed as arguments '''
def turn_off_LED(LED_list, LED_value):
    LED_list[LED_value].off()

''' This function turns all LEDs off '''
def all_LED_off():
    for i in range(len(meter_LED)):
        turn_off_LED(meter_LED, i)
    for i in range(len(gas_LED)):
        turn_off_LED(gas_LED, i)
    statusLED.off()
    buttonLED.off()


def main():
    global selected_gas, sleep, sleep_target, danger, sleep_counter, dangerous_gases_indexes, sound_played, sensor_data, print_timer, time_sleep
    
    if sleep == True and danger == 0:
        time_sleep = 1
        if button.is_pressed: # If in Sleep mode and the button is pressed, the device switches into Normal mode, the selected gas's LED is turned on, and the sleep counters are reset
            sleep = False
            gas_LED[gas_list.index(selected_gas)].on()
            time.sleep(0.15)
            sleep_counter = 0
            sleep_target = 0

        else:
            if sleep_counter > sleep_target: # When in Sleep mode, the data is collected and compared to determine if there are any dangerous gases
                sensor_data = average_reading()
                sleep_compare_results = sleep_compare(sensor_data)
                sleep_target = danger_threshold - sleep_compare_results
                sleep_counter = 0
            else:
                sleep_counter += 0.2
                time.sleep(0.2)
    
    else: # If the device is not in Sleep mode, data is collected, compared and the corresponding meter LEDs are turned on
        time_sleep = 100
        sensor_data = average_reading()
        try: 
            compare_primary(sensor_data)
            compare_secondary(sensor_data)
        except (IndexError, TypeError): # Catching operations with NoneType Issues
            pass
        
        button_count = 0
        while button.is_pressed: # Counts how long the button has been pressed
            button_count += 0.01
            time.sleep(0.01)

        if button_count < 0.6 and button_count > 0.02:
            if danger == 1:
                try:
                    selected_gas = danger_level_cycle(sensor_data) # If in Active danger mode and button is pressed, skip to most dangerous gas
                except (IndexError, TypeError):
                    pass
                danger = 2
                cycle_gas()
            else:
                time.sleep(0.15)
                cycle_gas()
        
        elif button_count >= 0.6: 
            if danger == 2: # If button is long-pressed and the device is in Passive danger mode, the device enters Normal mode 
                danger = 0
            else:
                sleep = True # If button is long-pressed and the device is not in Passive danger mode, the device enters Sleep mode
                all_LED_off()
            time.sleep(0.2)
        
        if danger == 1: # If in Active danger mode, the device begins playing the song on an infinite loop
            toggle_LED()
            if sound_played == False:
                sound_played = True
                danger_zone.play(-1)
        elif danger == 2: # If in Passive danger mode, the device stops playing the song
            toggle_LED()
            if sound_played == True:
                sound_played = False
                danger_zone.stop()
        else:
            toggle_LED() # Turns off LEDs when the device leaves either Active or Passive danger mode

try:
    on_sequence()
    while True:
        try:
            main()
        except OSError:
            print("\nThe sensor is not responding. Please press the reset button twice.\n")
            statusLED.off()
            time.sleep(1)
        except ValueError:
            pass
        except ZeroDivisionError:
            pass
except KeyboardInterrupt:
    pass
finally:
    all_LED_off() # Whenever the program stops or is quit, all LEDs are turned off and the music stops playing
    danger_zone.stop()
