from ortools.sat.python import cp_model
import pandas as pd 

df = pd.read_csv("data.csv")

tasks = df['Task'].unique()
day_types = df['Day Type'].unique()

start_time = {}
end_time = {}

for task in tasks :
    start_time[task] = {}
    end_time[task] = {}
    for day_type in day_types :
        task_data = df[(df['Task'] == task) & (df['Day Type'] == day_type)]
        start_time[task][day_type] = task_data['Start Time'].dt.hour.min()
        end_time[task][day_type] = task_data['End Time'].dt.hour.max()

model = cp_model.CpModel()

start_time_vars = {}
end_time_vars = {}

for task in tasks:
    for day_type in day_types:
        start_time_var = model.NewIntVar(start_time[task][day_type], end_time[task][day_type],
                                         f"start_time_{task}_{day_type}")
        end_time_var = model.NewIntVar(start_time[task][day_type], end_time[task][day_type],
                                       f"end_time_{task}_{day_type}")
        start_time_vars[(task, day_type)] = start_time_var
        end_time_vars[(task, day_type)] = end_time_var

for task in tasks :
    for day_type in day_types:
        overlapping_tasks = []
        for other_task in tasks :
            if other_task != task:
                if end_time_vars[(task, day_type)] > start_time_vars[(other_task, day_type)] and \
                        start_time_vars[(task, day_type)] < end_time_vars[(other_task, day_type)]:
                    overlapping_tasks.append(start_time_vars[(other_task, day_type)])
                    overlapping_tasks.append(end_time_vars[(other_task, day_type)])

                    model.Add(end_time_vars[(task, day_type)] <= min(overlapping_tasks))

break_time_slots = {
    'Breakfast': (8, 9),
    'Lunch': (12, 13),
    'Dinner': (19, 20)
}
for day_type in day_types:
    for task in tasks:
        if day_type == "W":
            for break_slot in break_time_slots.values():
                model.Add(end_time_vars[(task, day_type)] <= break_slot[0] or
                          start_time_vars[(task, day_type)] >= break_slot[1])
        else:
            model.Add(end_time_vars[(task, day_type)] <= break_time_slots['Breakfast'][0] or
                      (start_time_vars[(task, day_type)] >= break_time_slots['Breakfast'][1] and
                       end_time_vars[(task, day_type)] <= break_time_slots['Dinner'][0]) or
                      start_time_vars[(task, day_type)] >= break_time_slots['Dinner'][1])
            
max_working_hours_per_day = 8
for day_type in day_types:
    daily_working_hours = []
    for task in tasks:
        daily_working_hours.append(end_time_vars[(task, day_type)] - start_time_vars[(task, day_type)])
    model.Add(sum(daily_working_hours) <= max_working_hours_per_day)

for task in tasks:
    for day_type in day_types:
        model.Add(start_time_vars[(task, day_type)] >= start_time[task][day_type])
        model.Add(end_time_vars[(task, day_type)] <= end_time[task][day_type])

tasks_completed = [model.NewBoolVar(f"completed_{task}_{day_type}") for task in tasks for day_type in day_types]
model.Add(sum(tasks_completed) >= min_tasks_completed)  


model.Maximize(sum(tasks_completed))

