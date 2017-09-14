""" Code for running the Lantern experiment.
"""
# import some libraries
from experiment import Experiment
from visual import ask_user_info
import task, post_task


# ---------------- CONSTANTS --------------------

# Name will be shown on the pop-up before the experiment
EXPERIMENT_NAME = "Smiley 2.0"

# Go through a practice run?
PRACTICE_RUN = False

# Go through the main task?
TASK = True

# Go through the post task?
POST_TASK = False

# ---------------- SETUP --------------------
participant, age_group = ask_user_info(EXPERIMENT_NAME)

# Make an Experiment object to store the experiment info
experiment = Experiment(participant, age_group)

# ---------------- MAIN PROGRAM --------------------

if TASK:
    task.run(experiment)

if POST_TASK:
    post_task.run()

# cleanup
experiment.close()
