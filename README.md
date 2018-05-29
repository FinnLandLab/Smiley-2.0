# What file do I run?

Run the "project.py" file. You can open it with psychopy.

# Files

## config.py

This file has all the configurations for the project. Feel free to mess around with different configurations. These will all be saved along with the data output by the experiment. The variables that can be changed are the following, with a description of what they do:

- self.output_location = "data"
	- Output directory for data collected during experiment
- self.practice_run = True
	- Complete a practice run before the main task.
- self.task_no_keyboard_response_time = 0.150
	- Ignore any user input in the first this many seconds. Response time is calculated including this grace period (from when the stimulus is shown)
- self.task_interstimulus_interval = 0
	- How much time to hold on a blank screen between trials in the main task in seconds.
- self.task_feed_back_display_time = 0.150
 	- How long feedback is shown for during the main task. The same for positive and negative feedback
 - self.task_key1
 	- One of the keys to be used to identify letters/numbers. Counterbalanced with self.task_key2. (Half the time pressing task_key1 means identifying a letter, the other half it means identifying a number)
 - self.task_key2
 	- One of the keys to be used to identify letters/numbers. Counterbalanced with self.task_key2. (Half the time pressing task_key2 means identifying a letter, the other half it means identifying a number)


## experiment.py

Contains data about the whole experiment. Contains an instance of config and is accessible from everywhere within the code. Responsible for saving data. The data is saved at a path like "/section/name.csv" in the output_location directory from config.py

## project.py

Ties everything together. Creates an experiment object with all the data about the experiment and its configuration and calls on task.py and post_task.py to run the task and posttask.

## task.py

Runs the main task for the experiment. It is run with the run(experiment) function. The general ideal is that the task contains blocks, which contain trials. So task > block > trial. Each of these object will have an associated run method, where for example task.run runs an experiment which runs many blocks and block.run runs a block which runs many experiments. Along these, there is also the datapoint class. **The only things that will be saved are in the datapoint classes and in the config class**. These are saved using experiment.py's push_data and save_data methods.

In the task participants are shown either a letter (of "ABCDEFGH") or a number (of "23456789"). The letter/number is surrounded by one of "#", "@", "\*" called a flanker (always the same flanker on both sides).

Participants need to identify whether they saw a number or a letter by pressing either task_key1 or task_key2. 

If they are right, partcipants are shown a feed-back image. (/images/task/feedback/correct.jpg or /images/task/feedback/incorrect.jpg).

They are shown this image for task_feed_back_display_time from config.py.

There are 6 blocks total in the task. Each block contains 64 trials, 32 of which contain letters and the remaining 32 containing numbers.

In each block the "#" flanker is shown 16 times, 8 times paired with letters and another 8 with numbers.

The "@" and "\*" flankers are both shown a total of 144 times across the 6 blocks. However in each individual block, a flanker will be shown anywhere between 23 to 25 times. In total these two flankers will be shown 48 times per block.

However, these flankers will be shown at least twice exactly 24 times both in the same block. Additionally, "@" and "\*" will have the same number of blocks where they are showed 23 times. (Also true for blocks where they are shown 25 times).

If letters_corr_at is true: In 4 blocks, the "@" flanker is shown along with letters 21 times and in two blocks it is shown along with letters 22 times. Similarly the "\*" flanker will be shown along with letters 22 times in 4 blocks and in 2 will be shown 21 times.

If letter_corr_at is false, the roles of "@" and "\*" are reversed.

## post_task.py

Will ask the participant to reflect on the experiment and answer a few questions. Follows the same scheme as task.py in regards to datapoints.

## visual.py

Controls how the experiment is displayed. All drawing and visual related functions are here but none of the experiment logic. If you want to change how the experiment looks, try to change how the function is called first as the whole experiment is affected by changing this file.


























