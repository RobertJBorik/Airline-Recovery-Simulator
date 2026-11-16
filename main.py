import random
import pandas as pd
import copy

from config import Config
from loaders import load_airports, load_aircraft, load_routes
from scheduler import generate_schedule
from simulation import run_simulation
from helper import collect_flight_results, print_schedule


def run_experiment(
    num_simulations=50,
    strategies=(
        "none",
        "activateReserve",
        "activateReserveReposition",
        "aircraftSwap",
        "cyclicalAircraftSwap",
    ),
):
    config = Config()

    airports = load_airports("data/airports.json")
    aircraft = load_aircraft("data/aircraft.json")
    routes = load_routes("data/routes.json")

    master_rng = random.Random(config.random_seed)
    simulation_seeds = [master_rng.randint(0, 2**32 - 1) for _ in range(num_simulations)]

    # Generate base schedule
    generate_schedule(airports, aircraft, routes, config)

    sim_results = []
    flight_results = []

    for strategy in strategies:
        config.recovery_strategy = strategy

        for i, seed in enumerate(simulation_seeds):
            if i % 25 == 0:
                print(f"{strategy}: simulation {i} currently running")

            sim_aircraft = copy.deepcopy(aircraft)
            sim_schedule = []

            for plane in sim_aircraft.values():
                sim_schedule.extend(plane.assigned_flights)

            metrics = run_simulation(sim_schedule, sim_aircraft, config, seed, airports=airports)

            simulation_result = metrics.summary()
            simulation_result["simulation_num"] = i
            simulation_result["recovery_strategy"] = strategy
            sim_results.append(simulation_result)

            flight_results.extend(collect_flight_results(sim_schedule, i, strategy))

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