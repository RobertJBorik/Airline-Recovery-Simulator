import random
import pandas as pd

from config import Config
from loaders import load_airports, load_aircraft, load_routes
from scheduler import generate_schedule
from simulation import run_simulation
from helper import collect_flight_results


def run_experiment(num_simulations=1000):
    config = Config()

    airports = load_airports("data/airports.json")
    aircraft = load_aircraft("data/aircraft.json")
    routes = load_routes("data/routes.json")

    master_rng = random.Random(config.random_seed)
    simulation_seeds = [master_rng.randint(0, 2**32 - 1) for _ in range(num_simulations)]

    schedule = generate_schedule(aircraft, routes, config)

    sim_results = []
    flight_results = []

    for i, seed in enumerate(simulation_seeds):
        metrics = run_simulation(schedule, aircraft, routes, config, seed)

        sim_results.append(metrics)
        flight_results.extend(collect_flight_results(schedule, i))

    results_df = pd.DataFrame(sim_results)
    flights_df = pd.DataFrame(flight_results)

    return results_df, flights_df


def main():
    results_df, flights_df = run_experiment()

    results_df.to_csv("results/simulation_results.csv", index=False)

    flights_df.to_csv("results/flight_results.csv", index=False)

    print("Simulation complete.")
    print(f"{len(results_df)} simulations")
    print(f"{len(flights_df)} flight records")


if __name__ == "__main__":
    main()