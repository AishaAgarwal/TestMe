import pandas as pd 
import random 

df = pd.read_csv("data.csv")

num_days = 7
tasks_per_day = 3

num_tasks = len(df) # length of chromosome 

max_generations = 100

population_size = 100

mutation_rate = 0.1

class Timetable:
    def __init__(self, schedule):
        self.schedule = schedule

    def fitness(self):
        tasks_completed = self.schedule['Tasks Completed'].apply(lambda x:1 if x == 'Yes' else 0)
        return tasks_completed.sum() - self.schedule['Distractions'].sum()
    
population = []
for _ in range(population_size):
    schedule = pd.DataFrame(columns=df.columns)
    for day in range(num_days):
        day_tasks = df.sample(n=tasks_per_day).reset_index(drop=True)
        schedule = pd.concat([schedule, day_tasks], ignore_index=True)
    individual = Timetable(schedule)
    population.append(individual)

# Iterating over generations 
for generation in range(max_generations):
    fitness_scores = [individual.fitness() for individual in population]

    parents = []
    for _ in range(population_size):
        tournament_size = 5 
        tournament = random.choices(population, k = tournament_size)
        parent = max(tournament, key = lambda x: x.fitness())
        parents.append(parent)

    offspring = []
    for _ in range(population_size):
        parent1, parent2 = random.choices(parents, k=2)
        crossover_point = random.randint(1, num_tasks-1)
        child_schedule = pd.concat([parent1.schedule[:crossover_point], parent2.schedule[crossover_point:]])
        child = Timetable(child_schedule)
        offspring.append(child)

    for individual in offspring:
        if random.random() < mutation_rate:
            mutation_point = random.randint(0, num_tasks-1)
            individual.schedule.loc[mutation_point] = df.sample(1).iloc[0]

    population = offspring

best_timetable = max(population, key = lambda x: x.fitness())

print("Best Timetable:")
for idx, row in best_timetable.schedule.iterrows():
    print(f"Day {idx//tasks_per_day + 1}:")
    print(f"Task: {row['Task']}")
    print(f"Start Time: {row['Start Time']}")
    print(f"End Time: {row['End Time']}")
    print("-----")
