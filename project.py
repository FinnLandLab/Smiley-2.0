""" Code for running the Lantern experiment.
"""
# import some libraries from PsychoPy
from psychopy import visual, core, event, gui
import os
import sys
import random
from glob import glob
import csv
import time


# ---------------- CONSTANTS --------------------

# The relative directory that data will be saved to.
OUTPUT_LOCATION = "data"

# The names of the variables being recorded for the n-back task. Corresponds to DATA_HEADER_TASK
DATA_NAMES_TASK = ["experiment",
                   "participant id", "age group",
                   "block number", "trial number",
                   "date",
                   "condition",
                   "character", "type",
                   "flanker", "helpful",
                   "expected response",
                   "user response", "reaction time"]


# The header for the csv file being saved for the n-back task
DATA_HEADER_TASK = ",".join(DATA_NAMES_TASK)

# The names of the variables being recorded for the post task. Corresponds to DATA_HEADER_POST
DATA_NAMES_POST = ["experiment",
                   "participant id", "age group",
                   "date",
                   "n-back task", "prime list", "n-back reversed",
                   "prime image", "trial number", "image difficulty",
                   "user response", "reaction time"]

# The header for the csv file being saved for the post task
DATA_HEADER_POST = ",".join(DATA_NAMES_POST)

# For the main task. In seconds
INTERSTIMULUS_INTERVAL = 0.5

# Name will be shown on the pop-up before the experiment
EXPERIMENT_NAME = "Smiley 2.0"

# Go through a practice run?
PRACTICE_RUN = False

# Go through the main task?
TASK = True

# Go through the post task?
POST_TASK = False


# ---------------- VERIFICATION --------------------
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(
    os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)


# ---------------- SETUP --------------------

experiment_info = {'Participant': '', 'Age group': ''}

# Store info about the experiment session
dialogue = gui.DlgFromDict(dictionary=experiment_info, title=EXPERIMENT_NAME)

# User pressed cancel, so cancel!
if dialogue.OK is False:
    core.quit()

# Get the participant number
experiment_info['participant number'] = int("".join([c for c in experiment_info['Participant'] if c.isdigit()]))

# Get the experiment_info['date'] and time
experiment_info['date'] = time.strftime('%c')

# create a window
window = visual.Window(fullscr=True, monitor="testMonitor", units="cm", color=1)


# ---------------- FUNCTIONS --------------------

def save_data():
    """ Saves the data in experiment_info['data'] in the list my_answers into a file with the name:
    "{name}.csv"

    """
    # Get where we will store the data
    age_group = experiment_info["Age group"]
    participant_id = experiment_info["Participant"]

    location = "{}/{}/{}/".format(OUTPUT_LOCATION, age_group, participant_id)

    # Make sure the file directory exists
    if not os.path.exists(location):
        os.makedirs(location)

    # Get what section of the experiment we are in:
    data_name = experiment_info['Section']

    # Get the output file
    output_file = open(location + data_name + ".csv", 'w')

    # Write the header for the csv file
    if data_name == 'task':
        output_file.write(DATA_HEADER_TASK)
    elif data_name == 'post-task':
        output_file.write(DATA_HEADER_POST)
    else:
        raise Exception("Section name is not 'task' or 'post-task'")

    # End the line
    output_file.write("\n")

    # Output the answers, and close the file
    for row in experiment_info['data']:
        row = ",".join(str(entry) for entry in row)
        output_file.write(row)
        output_file.write("\n")
    output_file.close()

def timer_is_running(timer):
    """ Return True if timer is None, otherwise return True iff
    timer.getTime() >= 0

    @param timer: The timer to be checked
    @type timer: CountdownTimer|None
    @rtype: bool
    """
    return timer.getTime() >= 0 if timer is not None else True

def wait_for_prompt(timer=None, key='space', wrong_key=''):
    """ Waits indefinitely until the user strikes the {key}, or until
    esc is pressed exiting the program or until the timer runs out if there
    is one, or until wrong_key is pressed.
    Return True iff the user precessed {key} to exit

    @rtype: bool
    """
    # Clear the key's buffer:
    event.getKeys()

    # Wait for input
    while timer_is_running(timer):
        if len(event.getKeys(keyList=[key.lower(), key.upper()])) != 0:
            return True

        if len(event.getKeys(keyList=[wrong_key.lower(), wrong_key.upper()])) != 0:
            return False

        if len(event.getKeys(keyList=["escape"])) != 0:
            save_data()
            core.quit()
            return False

    return False

def show_images(genre, subgenre, task=None, extension='.png'):
    """ Shows all the instructions which follow the pattern
    '{image}/{task}/{genre}/{subgenre}/*{extension}', in ascending order.

    @param genre:
    @param subgenre:
    @param task:
    @param extension:
    @return:
    """
    if task is None:
        task = experiment_info['Section']
    image_paths = glob("images/{0}/{1}/{2}/*{3}".format(task, genre, subgenre, extension))
    image_paths.sort()

    for image_path in image_paths:
        instruction_image.image = image_path
        instruction_image.draw()
        window.flip()
        wait_for_prompt()

def get_input_text():
    """

    @return: The text the user inputted until they pressed the key '0'
    @rtype: str
    """
    # Clear the keys buffer
    event.getKeys()

    # Set up a text box for instructions
    text = "Please type in your answer, press the key '0' to submit it:"
    text_instr = visual.TextStim(win=window, text=text, color=-1, alignHoriz='left', alignVert='top', units='norm', pos=(-1, 1))

    # Set up a textbox for user input
    input_text = ""
    input_box = visual.TextStim(win=window, text=input_text,  color=-1)

    # Get user input
    inputting = True

    while inputting:
        keys = event.getKeys()
        for key in keys:
            if key == '0':
                inputting = False
                break
            elif key == 'escape':
                save_data()
                core.quit()

            elif key == 'space':
                input_text += ' '

            elif key == 'backspace':
                if len(input_text) > 0:
                    input_text = input_text[:-1]
            elif len(key) == 1 and key.isalpha():
                input_text += key
        input_box.text = input_text
        input_box.draw()
        text_instr.draw()
        window.flip()

    return input_text

def show_text(text):
    """ Shows the text text on the main screen"""
    text_element = visual.TextStim(window, text=text, wrapWidth=None, color=-1, font='Times New Roman')
    text_element.draw()
    window.flip()

class Trial():
    ''' The trial class'''

    def __init__(self, character, flanker):
        """ Initializes the Trial class"""

        assert isinstance(character, str), "character '{}' is not a string".format(character)
        assert len(character) == 1, "character '{}' must have length 1".format(character)

        assert flanker in '#@*' and len(flanker) == 1, "flanker '{}' is not '#', '@', or '*'".format(flanker)

        if character in '23456789':
            self.type = 'numeric'
            self.right_key = 'k'
            self.wrong_key = 'j'
        elif character.isalpha():
            self.type = 'alphabetic'
            self.right_key = 'j'
            self.wrong_key = 'k'
        else:
            raise Exception("Character '{}' is not alphabetic or numeric".format(character))

        self.char = character
        self.flanker = flanker


        # check if the trial is helpful
        self.helpful = -1
        if flanker == '#':
            self.helpful = 0
        elif (self.type == 'alphabetic' and self.flanker == '@') or (self.type == 'numeric' and self.flanker == '*'):
            if experiment_info['condition'] == '1':
                self.helpful = 1
        elif experiment_info['condition'] == '0':
            self.helpful = 1

    def run(self):
        ''' Runs this trial'''
        timer = core.Clock()
        show_text('{1} {0} {1}'.format(self.char, self.flanker))
        result = wait_for_prompt(key=self.right_key, wrong_key=self.wrong_key)
        response_time = timer.getTime()

        return result, response_time


class Block():
    ''' The Block class.
    Each block has 64 trials. 32 trials are numeric, 32 are alphabetic.
    The number of flankers per block will vary.
    '''


    def __init__(self, type_flanker_amounts, block_num):
        ''' Initializes the block class.'''
        # Store the block number
        self.block_num = block_num

        # The numbers and letters to be included
        nums = '23456789'  # paper says '1' wasn't included?
        letters = 'ABCDEFGH'

        # All characters to be used in this block
        nums = list(nums * 4)
        letters = list(letters * 4)

        # Shuffle both lists
        random.shuffle(nums)
        random.shuffle(letters)

        # Get iterators for both lists
        num_gen = iter(nums)
        letter_gen = iter(letters)

        # Make a list to store the trials for the block
        self.trials = []

        # Populate the list with trials
        for flanker in type_flanker_amounts['alphabetic']:
            for _ in range(type_flanker_amounts['alphabetic'][flanker]):
                self.trials.append(Trial(next(letter_gen), flanker))

            for _ in range(type_flanker_amounts['numeric'][flanker]):
                self.trials.append(Trial(next(num_gen), flanker))

        # Randomize the trial presentation
        random.shuffle(self.trials)

    def run(self):
        """ Run this block"""
        for i in range(len(self.trials)):
            trial = self.trials[i]
            result, responce_time = trial.run()

            data_point = [experiment_info['Section'],
                          experiment_info['participant number'], experiment_info['Age group'],
                          self.block_num, i,
                          experiment_info['date'],
                          experiment_info['condition'],
                          trial.char, trial.type,
                          trial.flanker, trial.helpful,
                          trial.right_key,
                          result, responce_time]

            experiment_info['data'] += [data_point]


def task():
    """ Run the main experiment task"""
    # Set the experiment section we are in
    experiment_info['Section'] = 'task'

    # Make an array to store the data
    experiment_info['data'] = []

    # Find out what condition we are in (condition 1 means '@' goes with letters, and '*' with numbers. Opposite for 2)
    experiment_info['condition'] = '1' if experiment_info['participant number'] % 2 == 0 else '2'

    # How many trials for each type of character and each type of flanker
    trial_amounts = {'alphabetic': {'#':[8] * 6}, 'numeric':{'#':[8] * 6}}

    # Assume that we have experiment_info['condition'] == '1'. Note we know that for each character the trial amounts add up to 32
    trial_amounts['alphabetic']['@'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['alphabetic']['@'])
    trial_amounts['alphabetic']['*'] = [24 - i for i in trial_amounts['alphabetic']['@']]

    trial_amounts['numeric']['*'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['numeric']['*'])
    trial_amounts['numeric']['@'] = [24 - i for i in trial_amounts['numeric']['*']]

    # If we don't, switch the occurences
    if experiment_info['condition'] == '2':
        trial_amounts['alphabetic'], trial_amounts['numeric'] = trial_amounts['numeric'], trial_amounts['alphabetic']

    for i in range(6):
        # Take only the i'th value of the trial_amounts amounts
        type_flanker_amounts = {ctype:{ftype: trial_amounts[ctype][ftype][i] for ftype in trial_amounts[ctype]} for ctype in trial_amounts}
        Block(type_flanker_amounts, i).run()
    save_data()







# ---------------- MAIN PROGRAM --------------------

if TASK:
    task()

if POST_TASK:
    prime_task()
# cleanup
window.close()
core.quit()
