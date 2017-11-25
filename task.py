""" A package with the code for the main task"""

from psychopy import core
import random

# -----------------------------------------------------------
# -----------------------  CONSTANTS  -----------------------
# -----------------------------------------------------------

# In seconds
INTERSTIMULUS_INTERVAL = 0


class Trial():
    ''' The trial class'''

    def __init__(self, experiment, character, flanker):
        """ Initializes the Trial class"""
        self.experiment = experiment

        assert isinstance(character, str), "character '{}' is not a string".format(character)
        assert len(character) == 1, "character '{}' must have length 1".format(character)

        assert flanker in '#@*' and len(flanker) == 1, "flanker '{}' is not '#', '@', or '*'".format(flanker)

        # Get the type of the trial
        if character in '23456789':
            self.type = 'numeric'
        elif character.isalpha():
            self.type = 'alphabetic'
        else:
            raise Exception("Character '{}' is not in the allowed set of characters".format(character))

        # Get the correct keys for this trial:
        # Suppose we have that letter_pair_j is true. Then
        if self.type == 'alphabetic':
            self.right_key = 'j'
            self.wrong_key = 'k'
        else:
            self.right_key = 'k'
            self.wrong_key = 'j'
        # If that is not the case, swap them
        if not experiment.letter_pair_j:
            self.right_key, self.wrong_key = self.wrong_key, self.right_key

        # Get the character and flanker for this trial
        self.char = character
        self.flanker = flanker

        # check if the trial is helpful:
        # Suppose that letters_corr_at is true. Then we get:
        if flanker == '#':
            self.helpful = 0
        elif (self.type == 'alphabetic' and self.flanker == '@') or (self.type == 'numeric' and self.flanker == '*'):
            self.helpful = 1
        else:
            self.helpful = -1

        # If letters_corr_at is false, then we have the opposite helpfulness
        if not experiment.letters_corr_at:
            self.helpful = -self.helpful


    def run(self):
        ''' Runs this trial'''
        timer = core.Clock()
        # Experiment with size here!
        self.experiment.window.show_text('{1} {0} {1}'.format(self.char, self.flanker), size=0.5)
        # Don't record responces for the first 150 milliseconds
        core.wait(0.150)
        result = self.experiment.window.wait_for_prompt(keys=[self.right_key, self.wrong_key])
        response_time = timer.getTime()

        return result, response_time


class Block():
    ''' The Block class.
    Each block has 64 trials. 32 trials are numeric, 32 are alphabetic.
    The number of flankers per block will vary.
    '''


    def __init__(self, experiment, type_flanker_amounts, block_num):
        ''' Initializes the block class.'''
        self.experiment = experiment
        # Store the block number
        self.block_num = block_num

        # The numbers and letters to be included
        nums = '23456789'
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
                self.trials.append(Trial(experiment, next(letter_gen), flanker))

            for _ in range(type_flanker_amounts['numeric'][flanker]):
                self.trials.append(Trial(experiment, next(num_gen), flanker))

        # Randomize the trial presentation
        random.shuffle(self.trials)

    def run(self):
        """ Run this block"""
        for i in range(len(self.trials)):
            trial = self.trials[i]
            responce, responce_time = trial.run()

            data_point = [self.experiment.section,
                          self.experiment.participant_num, self.experiment.age_group,
                          self.block_num, i,
                          self.experiment.date,
                          self.experiment.condition,
                          int(self.experiment.letters_corr_at), int(self.experiment.letter_pair_j),
                          trial.char, trial.type,
                          trial.flanker, trial.helpful,
                          trial.right_key,
                          responce, responce_time]

            self.experiment.push_data(data_point)
            if INTERSTIMULUS_INTERVAL != 0:
                core.wait(INTERSTIMULUS_INTERVAL)


def run(experiment):
    """ Run the main experiment task"""
    # Start a new section of the experiment we are in
    experiment.new_section('task')

    # How many trials for each type of character and each type of flanker
    trial_amounts = {'alphabetic': {'#':[8] * 6}, 'numeric':{'#':[8] * 6}}

    # Assume that experiment.letters_corr_at is True
    # Note we know that for each character the trial amounts add up to 32
    trial_amounts['alphabetic']['@'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['alphabetic']['@'])
    trial_amounts['alphabetic']['*'] = [24 - i for i in trial_amounts['alphabetic']['@']]

    trial_amounts['numeric']['*'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['numeric']['*'])
    trial_amounts['numeric']['@'] = [24 - i for i in trial_amounts['numeric']['*']]

    # But if experiment.letters_corr_at is False, switch the occurences
    if not experiment.letters_corr_at:
        trial_amounts['alphabetic'], trial_amounts['numeric'] = trial_amounts['numeric'], trial_amounts['alphabetic']

    # Show some instructions
    if experiment.letter_pair_j:
        experiment.window.show_images('instructions', 'start_j_letter')
    else:
        experiment.window.show_images('instructions', 'start_j_number')

    for i in range(6):
        # Take only the i'th value of the trial_amounts amounts
        type_flanker_amounts = {ctype:{ftype: trial_amounts[ctype][ftype][i] for ftype in trial_amounts[ctype]} for ctype in trial_amounts}
        # Run the block that is represented by the trial amounts
        Block(experiment, type_flanker_amounts, i).run()

        # Give them a break before the next block
        if i < 5:
            experiment.window.show_images('instructions', 'break')

    experiment.save_data()
