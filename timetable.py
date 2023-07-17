from ortools.sat.python import cp_model
import pandas as pd 

df = pd.read_csv("data.csv")

df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M')
df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M')


tasks = df['Task'].unique()
day_types = df['Day Type'].unique().tolist()

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
overlap_with_break_vars = {}


for task in tasks:
    for day_type in day_types:
        start_time_var = model.NewIntVar(start_time[task][day_type], end_time[task][day_type],
                                         f"start_time_{task}_{day_type}")
        end_time_var = model.NewIntVar(start_time[task][day_type], end_time[task][day_type],
                                       f"end_time_{task}_{day_type}")
        start_time_vars[(task, day_type)] = start_time_var
        end_time_vars[(task, day_type)] = end_time_var

# ...

# Create a boolean variable for each pair of tasks and day types
overlapping_vars = {}
for task1 in tasks:
    for task2 in tasks:
        if task1 != task2:
            for day_type in day_types:
                overlapping_vars[(task1, task2, day_type)] = model.NewBoolVar(f"overlap_{task1}_{task2}_{day_type}")

# Add constraints to set the overlapping_vars based on the overlapping condition
for task1 in tasks:
    for task2 in tasks:
        if task1 != task2:
            for day_type in day_types:
                model.Add(end_time_vars[(task1, day_type)] <= start_time_vars[(task2, day_type)] + overlapping_vars[(task1, task2, day_type)])
                model.Add(end_time_vars[(task2, day_type)] <= start_time_vars[(task1, day_type)] + overlapping_vars[(task1, task2, day_type)].Not())

# Add constraint to ensure that no two tasks of the same type overlap on the same day
for day_type in day_types:
    for task in tasks:
        overlapping_tasks = [overlapping_vars[(task1, task2, day_type)] for task1 in tasks for task2 in tasks if task1 != task2]
        model.Add(sum(overlapping_tasks) <= 0)

# ...

break_time_slots = {
    'Breakfast': (8, 9),
    'Lunch': (12, 13),
    'Dinner': (19, 20)
}
# ...

# Create a Boolean variable for each task and break time slot to represent if the task overlaps with the break

for task in tasks:
    for break_slot in break_time_slots.values():
        overlap_with_break_vars[(task, break_slot)] = model.NewBoolVar(f"overlap_{task}_{break_slot[0]}_{break_slot[1]}")

# Add constraints to set the overlap_with_break_vars based on the overlapping condition with break time slots
for day_type in day_types:
    for task in tasks:
        for break_slot in break_time_slots.values():
            model.Add(end_time_vars[(task, day_type)] <= break_slot[0] + (1 - overlap_with_break_vars[(task, break_slot)]))
            model.Add(start_time_vars[(task, day_type)] >= break_slot[1] - (1 - overlap_with_break_vars[(task, break_slot)]))

# ...


max_working_hours_per_day = 8
for day_type in day_types:
    daily_working_hours = []
    for task in tasks:
        daily_working_hours.append(end_time_vars[(task, day_type)] - start_time_vars[(task, day_type)])
    model.Add(sum(daily_working_hours) <= max_working_hours_per_day)


tasks_completed = [model.NewBoolVar(f"completed_{task}_{day_type}") for task in tasks for day_type in day_types]
min_tasks_per_day = 3 

for day_type in day_types:
    daily_tasks_completed = [tasks_completed[i] for i in range(len(tasks_completed)) if i % len(day_types) == day_types.index(day_type)]
    model.Add(sum(daily_tasks_completed) >= min_tasks_per_day)
 
model.Maximize(sum(tasks_completed))

solver = cp_model.CpSolver()
status = solver.Solve(model)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    # Retrieve the solution
    timetable = {}
    for task in tasks:
        for day_type in day_types:
            start_time = solver.Value(start_time_vars[(task, day_type)])
            end_time = solver.Value(end_time_vars[(task, day_type)])
            timetable[(task, day_type)] = (start_time, end_time)

    print(timetable)
else:
    print("No feasible solution found.")
