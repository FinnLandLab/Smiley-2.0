""" A package that focuses on the user interaction"""

from psychopy import visual, event, gui, core
import sys, os
from glob import glob

# ---------------- VERIFICATION --------------------
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(
    os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)


def ask_user_info(title, info=None):
    """ A method used to ask the user for their participant id and their age group.
        Will quit if the user presses 'cancel'

        @param str title: The title of the pop-up box
        @return (str, str): A tuple with of (participant id, age group)
    """
    if info is None:
        info = {'Participant': '', 'Age group': ''}

    # Store info about the experiment session
    dialogue = gui.DlgFromDict(dictionary=info, title=title)

    # User pressed cancel, so quit!
    if dialogue.OK is False:
        sys.exit()

    # Return the results
    return info['Participant'], info['Age group']


class Window:
    """ A class used to interface the interaction with the user"""

    def __init__(self, experiment):
        """ Initializes the window class"""
        self.experiment = experiment
        # Create the window object we'll use
        self._window = visual.Window(fullscr=True, monitor="testMonitor", units="norm", color=1)

        self._instruction_image = visual.ImageStim(win=self._window, units='norm', size=(2, 2))


    def show_images(self, genre, subgenre='', task=None, extension='.png'):
        """ Shows all the images which follow the pattern
        'image/{task}/{genre}/{subgenre}/*{extension}', in ascending order.

        @param genre:
        @param subgenre:
        @param task:
        @param extension:
        @return:
        """
        if task is None:
            task = self.experiment.section
        image_paths = glob("images/{0}/{1}/{2}/*{3}".format(task, genre, subgenre, extension))
        image_paths.sort()

        for image_path in image_paths:
            self._instruction_image.image = image_path
            self._instruction_image.draw()
            self._window.flip()
            self.wait_for_prompt()

    def show_text(self, text, size=None):
        """ Shows the text text on the main screen"""
        text_element = visual.TextStim(self._window, text=text, wrapWidth=None, color=-1, font='Times New Roman', height=size)
        text_element.draw()
        self._window.flip()

    def wait_for_choice(self, prompt, choices, size=None):
        """ Displays the given choices in lst choices with the given str prompt,
            and waits until one is picked. """
        # Display choices
        button_width = 2 / (len(choices) + 1.0)
        buttons = []
        for i in range(len(choices)):
            x_loc = 2 * ((i + 1.0) / (len(choices) + 1)) - 1

            text = visual.TextStim(self._window, text=choices[i], wrapWidth=button_width/1.1, color=-1, font='Times New Roman', pos=(x_loc, -0.5), height=size)
            textWidth, textHeight = text.boundingBox
            textWidth = 2.0 * textWidth / self._window.size[0]
            textHeight = 2.0 * textHeight / self._window.size[1]
            rect = visual.Rect(self._window, min(1.5 * textWidth, button_width), 1.5 * textHeight, lineColor=-1, pos=(x_loc, -0.5))
            buttons += [rect]
            rect.draw()
            text.draw()

        # Display the prompt
        text = visual.TextStim(self._window, text=prompt, wrapWidth=2, color=-1, font='Times New Roman', height=size)
        text.draw()

        # Tell the user to use their mouse
        text = visual.TextStim(self._window, text="Use your mouse to click:", wrapWidth=2, color=-1, font='Times New Roman', alignHoriz='left', pos=(-0.9, -textHeight), height=size)
        text.draw()


        self._window.flip()

        mouse = event.Mouse(win=self._window)
        # Wait for the user to click on one of them
        while True:
            for i in range(len(buttons)):
                if mouse.isPressedIn(buttons[i], buttons=[0]):
                    return choices[i]

            if len(event.getKeys(keyList=["escape"])) != 0:
                self.experiment.save_data()
                sys.exit()

            core.wait(0.01, hogCPUperiod=0)



    def wait_for_prompt(self, timer=None, keys='space'):
        """ Waits indefinitely until a key in keys is pressed. Return the key that was pressed.

            If a timer is provided, will wait for prompt until the timer runs out. If the timer runs out,
            None will be returned.

            @rtype: str|None
        """
        # Clear the key's buffer:
        event.clearEvents()

        if isinstance(keys, str):
            keys = [keys]

        keys = [k.lower() for k in keys] + [k.upper() for k in keys]

        # Wait for input
        while timer is None or timer.getTime() >= 0:
            # Get the keys that were pressed that we are watching
            keys_pressed = event.getKeys(keyList=keys)
            if len(keys_pressed) != 0:
                return keys_pressed[0]

            if len(event.getKeys(keyList=["escape"])) != 0:
                self.experiment.save_data()
                sys.exit()

        return None

    def close(self):
        """ Closes this window"""
        self._window.close()
