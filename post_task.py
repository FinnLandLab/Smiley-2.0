from random import choice, random


class MultipleChoice:
    """ A class for asking questions"""

    class DataPoint:
        """ A DataPoint for this multiple choice question"""

        def __init__(self, question, options, config):
            """ Initialize a DataPoint"""
            self.question = question
            self.options = options
            self.__parent = config
            self.user_response = None

    def __init__(self, experiment, question, options):
        """ Initializes this Question class with question {question},
        for the experiment {experiment} """
        self.experiment = experiment
        self.window = experiment.window
        self.config = experiment.config

        self.to_save = self.DataPoint(question, options, self.config)

    def ask(self):
        """ Ask this question and record the response"""
        self.to_save.user_response = self.experiment.window.wait_for_choice(self.to_save.question,
                                                                            self.to_save.options, font_size=24)

        self.experiment.push_data(self.to_save)


def random_number():
    return choice("2345678")


def random_letter():
    return choice("ABCDEFGH")


def run(experiment):
    """ Run the post-task for this experiment"""
    # Start a new section of the experiment we are in
    experiment.new_section('post-task')

    # Show some slides before the post-task
    experiment.window.show_image_sequence('instructions', 'start')

    # The answers that people can give
    yes_no_answer = ["Yes", "No"]
    quantity_answer = ["Very little", "A bit", "A lot"]

    prompt = "Did you notice any relationship between the symbols and the letters?"
    noticed_relationship = MultipleChoice(experiment, prompt, yes_no_answer)

    # Create the number questions and alphabetic questions
    number_questions = [MultipleChoice(experiment, "{0} {1} {0}".format(c, random_number()), quantity_answer)
                        for c in "#@*"]
    alpha_questions = [MultipleChoice(experiment, "{0} {1} {0}".format(c, random_letter()), quantity_answer)
                       for c in "#@*"]

    # Half the time number questions should come first,
    # the other half alphabetic questions
    questions = number_questions + alpha_questions if random() > 0.5 else alpha_questions + number_questions

    # Ask if they noticed any relationships
    noticed_relationship.ask()

    # Show some images before the correlation questions
    experiment.window.show_image_sequence('instructions', 'before_corr_questions')

    # Ask the remaining questions
    for question in questions:
        question.ask()

    # Show some slides after the experiment ends
    experiment.window.show_image_sequence('instructions', 'end')

    # Save the gathered data
    experiment.save_data()
