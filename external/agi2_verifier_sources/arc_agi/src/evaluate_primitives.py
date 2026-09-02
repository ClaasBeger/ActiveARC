import asyncio
import pickle
import os
import argparse
from collections import defaultdict

from devtools import debug

from src.data import eval_challenges, training_challenges, v2_training_challenges, v2_eval_challenges
from src.logic import can_library_solve_challenge
from src import logfire


async def main() -> None:
    # Add argument parser
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    train_keys = list(training_challenges.keys())
    v2_train_keys = list(v2_training_challenges.keys())
    print(f"v2 training set size: {len(v2_train_keys)}")
    logfire.debug(f"v2 training set size: {len(v2_train_keys)}")
    #random.shuffle(v2_train_keys)
    train_ids_to_test = v2_train_keys
    debug(train_ids_to_test)
    logfire.debug(f"train_ids_to_test: {train_ids_to_test}")

    
    eval_ids_to_test = list(v2_eval_challenges.keys())
    print(f"v2 eval set size: {len(eval_ids_to_test)}")
    logfire.debug(f"v2 eval set size: {len(eval_ids_to_test)}")
    # take random 10 sample fro eval_ids_to_test
    debug(eval_ids_to_test)


    from src.models import Library

    # Function to load library
    def load_library(filename="saved_library_eval_90.pkl"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return pickle.load(f)
        else:
            print(f"No library file found at {filename}, creating new library")
            return Library(primitives=[])

    library_path = "saved_library_1000.pkl"
    library = load_library(library_path)

    print(f"library size: {len(library.primitives)}")
    logfire.debug(f"library size: {len(library.primitives)}")

    if len(library.primitives) == 0:
        print("No library found, exiting")
        return

    solved_challenges = []
    # Dictionary to store primitive scores for each challenge (scores don't change across runs)
    challenge_primitive_scores = defaultdict(dict)

    for idx, challenge_id in enumerate(eval_ids_to_test):
        debug(challenge_id)
        challenge = v2_eval_challenges[challenge_id]

        can_solve = await can_library_solve_challenge(
            challenge=challenge,
            library=library,
            challenge_primitive_scores=challenge_primitive_scores,
        )
        if can_solve:
            solved_challenges.append(challenge_id)
        logfire.debug(f"after {idx} challenges, solved {len(solved_challenges)} challenges")
        logfire.debug(f"challenge_primitive_scores size {len(challenge_primitive_scores)}")
        logfire.debug(f"challenge_primitive_scores primitive size {len(challenge_primitive_scores[challenge_id])}")

    with open("challenge_primitive_accuracy_scores.pkl", "wb") as f:
        pickle.dump(challenge_primitive_scores, f)
        
    logfire.debug(f"Solved Challenges: {solved_challenges}")
    print(f"Solved Challenges: {solved_challenges}")
    logfire.debug(f"Correct Percent SO FAR: {len(solved_challenges) / len(eval_ids_to_test)}")
    print(f"Correct Percent SO FAR: {len(solved_challenges) / len(eval_ids_to_test)}")


if __name__ == "__main__":
    asyncio.run(main())
