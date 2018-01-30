""" A package that focuses on the user interaction"""

from psychopy import visual, event, gui, core
import psychopy.tools.monitorunittools
import sys
from glob import glob


def ask_user_info(title):
    """ A method used to ask the user for their participant id and their age group.
        Will quit if the user presses 'cancel'

        @param str title: The title of the pop-up box
        @return (str, str): A tuple with of (participant id, age group)
    """
    info = {'Participant': '', 'Age group': ''}

    # Store info about the experiment session
    dialogue = gui.DlgFromDict(dictionary=info, title=title)

    # User pressed cancel, so quit!
    if dialogue.OK is False:
        sys.exit()

    # Return the results
    return info['Participant'], info['Age group']


def pt_to_cm(pt):
    """ Convert from pt to cm
    @param float pt: pt to be converted
    @return float: cm equivalent
    """
    return pt * 0.035277778


class Window:
    """ A class used to interface the interaction with the user"""

    def __init__(self, experiment):
        """ Initializes the window class"""
        self.experiment = experiment
        # Create the window object we'll use
        self._window = visual.Window(fullscr=True, monitor="testMonitor", units="norm", color=1)

        self._instruction_image = visual.ImageStim(win=self._window, units='norm', size=(2, 2))

    def norm_to_cm(self, norm):
        x = psychopy.tools.monitorunittools.pix2cm(norm[0] * self._window.size[0] / 2.0, self._window.monitor)
        y = psychopy.tools.monitorunittools.pix2cm(norm[1] * self._window.size[1] / 2.0,  self._window.monitor)
        return x, y

    def norm_magn_to_cm_magn(self, norm_magn):
        return self.norm_to_cm((norm_magn, 0))[0]

    def px_to_norm(self, px):
        x = 2.0 * px[0] / self._window.size[0]
        y = 2.0 * px[1] / self._window.size[1]
        return x, y

    def show_image_sequence(self, genre, subgenre='', task=None, extension='.png'):
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
            self.show_image(image_path)
            self.wait_for_prompt()

    def show_image(self, path):
        """ Show the image at the given path.

        @param str path: the path of the image to be shown
        @rtype: None
        """
        self._instruction_image.image = path
        self._instruction_image.draw()
        self._window.flip()

    def show_text(self, text, font_size=24, legend=None, legend_font_size=24):
        """ Shows the text text on the main screen. font size in pt. Optionally shows a legend beneath the text"""
        # convert size to cm
        font_size_cm = pt_to_cm(font_size)
        text_element = visual.TextStim(self._window, text=text, wrapWidth=None, color=-1,
                                       font='Times New Roman', units='cm', height=font_size_cm)
        text_element.draw()

        if legend is not None:
            legend_font_size_cm = pt_to_cm(legend_font_size)
            text_element = visual.TextStim(self._window, text=legend, wrapWidth=None, color=-1, font='Times New Roman',
                                           units='cm', height=legend_font_size_cm, alignVert='bottom',
                                           pos=self.norm_to_cm((0, -1)))
            text_element.draw()
        self._window.flip()

    def wait_for_choice(self, prompt, choices, font_size=24):
        """ Displays the given choices in lst choices with the given str prompt,
            and waits until one is picked. """
        font_size_cm = pt_to_cm(font_size)

        # Display choices
        button_width = 2 / (len(choices) + 1.0)
        buttons = []

        for i in range(len(choices)):
            x_loc = 2 * ((i + 1.0) / (len(choices) + 1)) - 1

            text = visual.TextStim(self._window, text=choices[i], wrapWidth=button_width/1.1,
                                   color=-1, font='Times New Roman', units='cm',
                                   pos=self.norm_to_cm((x_loc, -0.5)), height=font_size_cm)

            # Find the desired box height and width
            text_width, text_height = self.px_to_norm(text.boundingBox)

            # Make a box
            rect = visual.Rect(self._window, min(1.5 * text_width, button_width),
                               1.5 * text_height, lineColor=-1, pos=(x_loc, -0.5))

            # Add the rect to the set of buttons
            buttons += [rect]

            # Draw the button
            rect.draw()
            text.draw()

        # Display the prompt
        text = visual.TextStim(self._window, text=prompt, wrapWidth=self.norm_magn_to_cm_magn(2), color=-1,
                               font='Times New Roman', units='cm', height=font_size_cm)
        text.draw()

        # Tell the user to use their mouse
        text = visual.TextStim(self._window, text="Use your mouse to click:", wrapWidth=self.norm_magn_to_cm_magn(2),
                               color=-1, font='Times New Roman', alignHoriz='left',
                               pos=self.norm_to_cm((-0.9, -text_height)), units='cm', height=font_size_cm)
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

    def get_input_text(self, prompt=None, font_size=24):
        """ Gets user input as text. The prompt

        @return: The text the user inputted until they pressed the key '0'
        @rtype: str
        """
        font_size_cm = pt_to_cm(font_size)

        # Clear the keys buffer
        event.getKeys()

        # Set up a text box for instructions
        prompt = "" if prompt is None or prompt == "" else prompt + ". "
        text = prompt + "Please type in your answer, press the key '0' to submit it:"
        text_instr = visual.TextStim(win=self._window, text=text, color=-1, alignHoriz='left', alignVert='top',
                                     units='cm', pos=self.norm_to_cm((-1, 1)), height=font_size_cm)

        # Set up a textbox for user input
        input_text = ""
        input_box = visual.TextStim(win=self._window, text=input_text, color=-1, units='cm', height=font_size_cm)

        # Get user input
        inputting = True

        while inputting:
            keys = event.getKeys()
            for key in keys:
                if key == '0':
                    inputting = False
                    break
                elif key == 'escape':
                    self.experiment.save_data()
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
            self._window.flip()

        return input_text
