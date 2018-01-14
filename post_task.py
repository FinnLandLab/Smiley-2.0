from random import choice, random

class Question():
    """ A class for asking questions"""

    def __init__(self, experiment, question, options):
        """ Initializes this Question class with question {question},
        for the experiment {experiment} """
        self.experiment = experiment
        self.question = question
        self.options = options

    def ask(self):
        """ Ask this question and record the response"""
        response = self.experiment.window.wait_for_choice(self.question, self.options, size=None)

        data_point = [self.experiment.section,
                      self.experiment.participant_num, self.experiment.age_group,
                      self.experiment.date,
                      self.experiment.condition,
                      int(self.experiment.letters_corr_at), int(self.experiment.letter_pair_j),
                      self.question, response]

        self.experiment.push_data(data_point)


def random_number():
    return choice("2345678")


def random_letter():
    return choice("ABCDEFGH")


def run(experiment):
    """ Run the post-task for this experiment"""
    # Start a new section of the experiment we are in
    experiment.new_section('post-task')

    # Show some slides before the post-task
    experiment.window.show_images('instructions', 'before_all')

    # The answers that people can give
    yes_no_answer = ["Yes", "No"]
    quantity_answer = ["Very little", "A bit", "A lot"]

    prompt = "Did you notice any relationship between the symbols and the letters?"
    noticed_relationship = Question(experiment, prompt, yes_no_answer)

    # Create the number questions and alphabetic questions
    number_questions = [Question(experiment, "{0} {1} {0}".format(c, random_number()), quantity_answer) for c in "#@*"]
    alpha_questions = [Question(experiment, "{0} {1} {0}".format(c, random_letter()), quantity_answer) for c in "#@*"]

    # Half the time number questions should come first,
    # the other half alphabetic questions
    questions = number_questions + alpha_questions if random() > 0.5 else alpha_questions + number_questions

    # Ask if they noticed any relationships
    noticed_relationship.ask()

    # Show some images before the correlation questions
    experiment.window.show_images('instructions', 'before_corr_questions')

    # Ask the remaining questions
    for question in questions:
        question.ask()

    # Save the gathered data
    experiment.save_data()
