""" A package with the code for the main task"""

from psychopy import core
import random


class Trial:
    """ A trial in the main task"""

    class DataPoint:
        """ A DataPoint for a trial"""

        def __init__(self, character, flanker, trial_number, block):
            """ Creates a DataPoint for a trial in a blck"""
            # Get the character and flanker for this trial
            self.char = character
            self.flanker = flanker

            # Get the position of the trial within the task
            self.trial_number = trial_number

            self.user_input = None
            self.response_time = None
            self.correct = None

            self.__parent = block.to_save

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
            if not block.config.letter_pair_j:
                self.right_key, self.wrong_key = self.wrong_key, self.right_key

            # Use the same trick here
            if flanker == '#':
                self.helpful = 0
            elif (self.type == 'alphabetic' and self.flanker == '@') or (
                    self.type == 'numeric' and self.flanker == '*'):
                self.helpful = 1
            else:
                self.helpful = -1

            # If letters_corr_at is false, then we have the opposite helpfulness
            if not block.config.letters_corr_at:
                self.helpful = -self.helpful

    def __init__(self, character, flanker, trial_number, block):
        """ Initializes the Trial class"""
        self.experiment = block.experiment
        self.window = block.window
        self.config = block.config

        self.to_save = self.DataPoint(character, flanker, block, trial_number)

    def run(self):
        """ Run this trial"""
        timer = core.Clock()
        # Experiment with size here!
        self.window.show_text('{1} {0} {1}'.format(self.to_save.char, self.to_save.flanker), size=0.5)

        # Don't record responses for the first 150 milliseconds
        core.wait(0.150)

        # Get the user's response
        self.to_save.user_input = self.window.wait_for_prompt(keys=[self.to_save.right_key, self.to_save.wrong_key])
        self.to_save.response_time = timer.getTime()
        self.to_save.correct = (self.to_save.user_input == self.to_save.right_key)


class Block:
    """ The Block class.
    Each block has 64 trials. 32 trials are numeric, 32 are alphabetic.
    The number of flankers per block will vary.
    """

    class DataPoint:
        """ A DataPoint for a Block"""

        def __init__(self, block_num, config):
            """ Create a DataPoint for a block"""
            self.block_num = block_num
            self.__parent = config

    def __init__(self, experiment, type_flanker_amounts, block_num):
        """ Initializes the block class."""
        self.experiment = experiment
        self.window = experiment.window
        self.config = experiment.config

        self.to_save = self.DataPoint(block_num, self.config)

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
                self.trials.append(Trial(experiment, next(letter_gen), flanker, self))

            for _ in range(type_flanker_amounts['numeric'][flanker]):
                self.trials.append(Trial(experiment, next(num_gen), flanker, self))

        # Randomize the trial presentation
        random.shuffle(self.trials)

    def run(self):
        """ Run this block"""
        for i in range(len(self.trials)):
            trial = self.trials[i]
            trial.run()
            self.experiment.push_data(trial.to_save)
            if self.config.interstimulus_interval != 0:
                core.wait(self.config.interstimulus_interval)


def run(experiment):
    """ Run the main experiment task"""
    # Start a new section of the experiment we are in
    experiment.new_section('task')

    # How many trials for each type of character and each type of flanker
    trial_amounts = {'alphabetic': {'#': [8] * 6}, 'numeric':{'#':[8] * 6}}

    # Assume that experiment.letters_corr_at is True
    # Note we know that for each character the trial amounts add up to 32
    trial_amounts['alphabetic']['@'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['alphabetic']['@'])
    trial_amounts['alphabetic']['*'] = [24 - i for i in trial_amounts['alphabetic']['@']]

    trial_amounts['numeric']['*'] = [21] * 4 + [22] * 2
    random.shuffle(trial_amounts['numeric']['*'])
    trial_amounts['numeric']['@'] = [24 - i for i in trial_amounts['numeric']['*']]

    # But if experiment.letters_corr_at is False, switch the occurrences
    if not experiment.letters_corr_at:
        trial_amounts['alphabetic'], trial_amounts['numeric'] = trial_amounts['numeric'], trial_amounts['alphabetic']

    # Show some instructions
    if experiment.letter_pair_j:
        experiment.window.show_image_sequence('instructions', 'start_j_letter')
    else:
        experiment.window.show_image_sequence('instructions', 'start_j_number')

    for block_num in range(6):
        # Take only the i'th value of the trial_amounts amounts
        type_flanker_amounts = {char_type: {flanker_type: trial_amounts[char_type][flanker_type][block_num]
                                            for flanker_type in trial_amounts[char_type]}
                                for char_type in trial_amounts}

        # Run the block that is represented by the trial amounts
        Block(experiment, type_flanker_amounts, block_num).run()

        # Give them a break before the next block, unless it's the last block
        if block_num < 5:
            experiment.window.show_image_sequence('instructions', 'break')

    experiment.save_data()
