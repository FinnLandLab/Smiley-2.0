""" Code for running the Smiley experiment.
"""
# import some libraries
from experiment import Experiment
from visual import ask_user_info
import task, post_task

# ---------------- SETUP --------------------
participant, age_group = ask_user_info("Smiley 2.0")

# Make an Experiment object to store the experiment info
experiment = Experiment(participant, age_group)

# ---------------- MAIN PROGRAM --------------------

task.run(experiment)

# TODO: Implement post task
# post_task.run(experiment)

# cleanup
experiment.close()
