# Name: Owen Johnstone
# Date: Jan. 28, 2020
# DP3 Team Number: 33

def read_file(file):
    data = []
    with open(file) as read_file:
        for line in read_file:
            data.append(float(line.strip()))
    return data

def average_value(values, num_points):
    last_n_entries = values[-int(num_points):]
    data_sum = sum(last_n_entries)
    average = data_sum / int(num_points)
    if len(values) < num_points:
        return None
    else:
        return round(average, 2)

def total_above(values, threshold):
    count = 0
    for item in values:
        if item > threshold:
            count += 1
    return count

def percent_change(values, num_data_points, baseline):
    average = average_value(values, num_data_points)
    if len(values) < num_data_points:
        return None
    percent_change = (average - baseline) / baseline * 100
    return round(percent_change, 2)

def main():
    file = 'test.txt'
    number_of_points = 6
    threshold = 5
    baseline = 7
    
    try:
        data_list = read_file(file)
    except IOError:
        print('Please enter the correct file name')

    temp_values = []
    for i in range(len(data_list)):
        try:
            temp_values.append(data_list[i])
            average = average_value(temp_values, number_of_points)
            choice1 = total_above(temp_values, threshold)
            choice2 = percent_change(temp_values, number_of_points, baseline)
            print(data_list[i], '\t', average, '\t', choice1, '\t', choice2)
        except TypeError:
            print('Please enter the correct data type')
            break
        except ZeroDivisionError:
            print('Please enter a non-zero number of points')
            break
        except ValueError:
            print('Please enter the correct type of value')
            break
main()
