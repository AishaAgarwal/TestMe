import pandas as pd 

df = pd.read_csv("data.csv")

df['Productivity'] = df.groupby('Date')['Tasks Completed'].transform('sum')

task_productivity = df.groupby('Task')['Productivity'].sum()
most_productive_tasks = task_productivity.sort_values(ascending= False)
print(most_productive_tasks)
