import pandas as pd 

df = pd.read_csv("data.csv")

df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M')
df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M')

df['Productivity'] = df.groupby('Date')['Tasks Completed'].transform('sum')

task_productivity = df.groupby('Task')['Productivity'].sum()
most_productive_tasks = task_productivity.sort_values(ascending= False)
print(most_productive_tasks)


df['Hour'] = df['Start Time'].dt.hour
hourly_completion_counts = df.groupby('Hour')['Tasks Completed'].sum()
peak_productivity_hours = hourly_completion_counts.sort_values(ascending = False)
print(peak_productivity_hours)

timetable = {}

allocated_hours = set()
task_index = 0

for hour in peak_productivity_hours.index:
    if task_index >= len(most_productive_tasks):
        break

    task = most_productive_tasks.index[task_index]
    productvity_score = most_productive_tasks.iloc[task_index]

    if hour not in allocated_hours:
        timetable[hour] = task
        allocated_hours.add(hour)
        task_index += 1


df['Task Completion Time'] = (df['End Time'] - df['Start Time'])
avg_completion_time = df.groupby("Task")["Task Completion Time"].mean()

peak_productivity_task_times = df[df['Hour'].isin(peak_productivity_hours.index)]['Task Completion Time']
total_peak_productivity_time = peak_productivity_task_times.sum()

for hour in peak_productivity_hours.index:
    if task_index >= len(most_productive_tasks):
        break

    if hour not in timetable:
        task = most_productive_tasks.index[task_index]
        productvity_score = most_productive_tasks.iloc[task_index]
        completion_time = avg_completion_time[task]

        if completion_time > pd.Timedelta(hours=1) - total_peak_productivity_time:
            continue

        timetable[hour] = task
        task_index += 1

df['Breaks'] = pd.to_timedelta(df['Breaks'])
df['Distractions'] = pd.to_timedelta(df['Distractions'])

average_break_time = df['Breaks'].mean()
average_downtime = df['Distractions'].mean()

for hour in peak_productivity_hours.index:
    if hour in peak_productivity_hours.index:
        # Subtract productivity hours' time from available time in that hour
        available_time = pd.Timedelta(hours=1) - total_peak_productivity_time
    else:
        available_time = pd.Timedelta(hours=1)
    
    if available_time > average_break_time + average_downtime:
        # Add break and downtime to the timetable
        timetable[hour] = (timetable[hour], "Break")
        timetable[(pd.to_datetime(f'2000-01-01 {hour}:00:00') + pd.Timedelta(minutes=average_break_time.seconds/60)).time()] = "Downtime"
print("Personalized Timetable:")
for hour, task in timetable.items():
    if isinstance(task, tuple):
        print(f"{pd.to_datetime(f'2000-01-01 {hour}:00:00').strftime('%H:%M')} - {task[0]} (Break)")
    else:
        print(f"{pd.to_datetime(f'2000-01-01 {hour}:00:00').strftime('%H:%M')} - {task}")
