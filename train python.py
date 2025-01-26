import os
import sys
os.chdir('C:/Users/Zeddrex Navarra/Desktop/Career/Projects/Train Simulation')
import pandas as pd
from scipy.stats import norm

with open("output.txt","w") as f:
    sys.stdout = f

    train_data = pd.read_csv("train_data.csv").iloc[:,1:6]
    mask = train_data["Day"] == "Weekday"
    train_data = train_data[mask]

    stations = {
        "North Ave": 0,
        "Quezon Ave": 1.2,
        "GMA Kamuning": 2.2,
        "Cubao": 4.1,
        "Santolan": 5.6,
        "Ortigas": 7.9,
        "Shaw Blvd": 8.7,
        "Boni Ave": 9.7,
        "Guadalupe": 10.5,
        "Buendia": 12.5,
        "Ayala Ave": 13.45,
        "Magallanes": 14.65,
        "Taft": 16.7,
        "End of line": 100
    }

    stations_list = list(stations.keys())

    [1.2,1,1.9,1.5,2.3,0.8,1,0.8,2,0.95,1.2,2.05]
    cum_dist = [1.2,2.2,4.1,5.6,7.9,8.7,9.7,10.5,12.5,13.45,14.65,16.7]
    distance_over_time = 0.75

    trains = ["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10"]
    line = [] #this is where the train tracking happens
    pila = {} #this is where the distances are updated
    next_station = {} #target station of the train
    current_station = {} #current station of the train
    parking = {} #to set the parking time of a train

    #Passenger Generation

    station_loop = stations_list[:-1]
    count = 0
    que = {}
    passenger_data = {}

    for station in station_loop:
        
        que = {}
        sample = train_data[train_data["Station"] == station]

        for i in range(1200):

            try:    
                j = 4 + (i//60)
                if i%5 == 0:
                    loc = sample[sample["Hour"] == j]["Mean"].iloc[0]
                    scale = sample[sample["Hour"] == j]["Variance"].iloc[0]

                    passenger = (norm.rvs(loc,scale,1,random_state = i)//12).tolist()[0]
                    
                    if passenger < 0:
                        passenger = 0
                    else:
                        passenger = int(passenger)
                    
                    que[i] = passenger
                    count += 1
                    
            except:
                continue
        
        passenger_data[station] = que

    occupation = {
        "North Ave": "Not occupied",
        "Quezon Ave": "Not occupied",
        "GMA Kamuning": "Not occupied",
        "Cubao": "Not occupied",
        "Santolan": "Not occupied",
        "Ortigas": "Not occupied",
        "Shaw Blvd": "Not occupied",
        "Boni Ave": "Not occupied",
        "Guadalupe": "Not occupied",
        "Buendia": "Not occupied",
        "Ayala Ave": "Not occupied",
        "Magallanes": "Not occupied",
        "Taft": "Not occupied",
        "End of line": "Not occupied"
    }

    alighting = {
        "North Ave": 0,
        "Quezon Ave": 0.1,
        "GMA Kamuning": 0.2,
        "Cubao": 0.6,
        "Santolan": 0.1,
        "Ortigas": 0.3,
        "Shaw Blvd": 0.1,
        "Boni Ave": 0.2,
        "Guadalupe": 0.3,
        "Buendia": 0.1,
        "Ayala Ave": 0.4,
        "Magallanes": 0.3,
        "Taft": 1
    }

    train_cap = {}

    for t in trains:
        train_cap[t] = 1180


    #Passenger boarding mechanics
    train_capacity = {}
    station_queue = {}
    keys_for_removal = {}
    wait_time = []
    i=0

    while i < 1201:
        
        if i%5 == 0:

            try:

                for station in station_loop:
                    
                    if station not in station_queue:
                        station_queue[station] = {}

                    station_queue[station][i] = passenger_data[station][i]

            except:

                break
        
        if i%10 == 0:

            if ((occupation["North Ave"] == "Not occupied") and (len(trains) != 0)):
                #Deploys a train every 10 mins if there are trains to deploy and North Ave does not have a train parked
                train = trains.pop(0)
                line.append(train)
                pila[train] = 0
                current_station[train] = "North Ave"
                next_station[train] = "Quezon Ave"
                parking[train] = 2
                occupation["North Ave"] = "Occupied"
                train_capacity[train] = 0
                available = train_cap[train] - train_capacity[train]

                if sum(list(station_queue["North Ave"].values())) > available:

                    print(f"North Ave queue exceeds train capacity with {sum(list(station_queue['North Ave'].values()))} passengers. Station queue at and train capacity at {train_cap[train]}")

                    tot = 0

                    for key in list(station_queue["North Ave"].keys()):
                        
                        tot = station_queue["North Ave"][key] + tot

                        if tot > available:

                            remainder = station_queue["North Ave"][key] - (available - train_capacity[train])
                            train_capacity[train] = train_capacity[train] + station_queue["North Ave"][key] - remainder
                            station_queue["North Ave"][key] = remainder
                            break

                        else:

                            train_capacity[train] = train_capacity[train] + station_queue["North Ave"][key]
                            wait_time.append((i-key,station_queue[current_station[train]][key]))
                            station_queue[current_station[train]].pop(pops)

                else:

                    train_capacity[train] = int((train_capacity[train])*(1-alighting[current_station[train]])) + sum(station_queue[current_station[train]].copy().values())
                    keys_for_removal[train] = station_queue[current_station[train]].copy()

                    for pops in list(keys_for_removal[train].keys()):

                        wait_time.append((i-pops,station_queue[current_station[train]][pops]))
                        station_queue[current_station[train]].pop(pops)

                print(f"Train {train} is at North Ave at  time {i}, the next station is {next_station[train]}")  
                print(f"Train {train} has {train_capacity[train]} passengers")       

        for t in list(line):

            if parking[t] > 0:
                parking[t] = parking[t]-1
                #print(f"Train {t} is waiting at station {current_station[t]} for {parking[t]} minutes, current time {i}")
                continue

            if parking[t] <= 0 and occupation[next_station[t]] == "Not occupied":

                occupation[current_station[t]] = "Not occupied"
                target_position = stations[next_station[t]]
                new_position = pila[t] + distance_over_time
                
                if (target_position <= new_position):

                    #Distance variable
                    pila[t] = target_position

                    #Station tracker
                    current_station[t] = next_station[t]
                    occupation[current_station[t]] = "Occupied"
                    next_station[t] = stations_list[1 + stations_list.index(next_station[t])]
                    available = train_cap[t] - train_capacity[t]

                    #Handles train capacity limit
                    if sum(list(station_queue[current_station[t]].values())) > available:

                        print(f"{station} queue exceeds train capacity. Station queue at {sum(list(station_queue[current_station[t]].values()))} and train capacity at {train_cap[t]}")

                        tot = 0

                        for key in list(station_queue[current_station[t]].keys()):
                            
                            tot = station_queue[current_station[t]][key] + tot

                            if tot > available:

                                remainder = station_queue[current_station[t]][key] - (available - train_capacity[t])
                                train_capacity[t] = train_capacity[train] + station_queue[current_station[t]][key] - remainder
                                station_queue[current_station[t]][key] = remainder
                                break

                            else:

                                train_capacity[t] = train_capacity[t] + station_queue[current_station[t]][key]
                                wait_time.append((i-key,station_queue[current_station[t]][key]))
                                station_queue[current_station[t]].pop(pops)

                    #Passenger tracker
                    else:

                        train_capacity[t] = int((train_capacity[t])*(1-alighting[current_station[t]])) + sum(station_queue[current_station[t]].copy().values())
                        keys_for_removal[t] = station_queue[current_station[t]].copy()

                        for pops in list(keys_for_removal[t].keys()):

                            wait_time.append((i-pops,station_queue[current_station[t]][pops]))
                            station_queue[current_station[t]].pop(pops)
                    
                    #Parking timer
                    parking[t] = 2

                    #Diagnostic messages
                    print(f"Train {t} has arrived at {current_station[t]} at time {i}, the next station is {next_station[t]}")
                    print([station for station, status in occupation.items() if status == "Occupied"])
                    print(f"Train {t} has {train_capacity[t]} passengers")
                    #break

                else:

                    pila[t] = new_position

                if new_position > 16.7:

                    occupation["Taft"] = "Not occupied"
                    occupation["End of line"] = "Not occupied"
                    trains.append(t)
                    line.pop(0),
                    pila.pop(t),
                    next_station.pop(t)
                    parking.pop(t)
                    current_station.pop(t)
                    print(f"Train {t} will be returning to the terminal station")
        
        i+=1 

sys.stdout = sys.__stdout__
print("Back to terminal")