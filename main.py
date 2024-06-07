#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import yaml
import random
import atexit
import codecs

from typing import List, Dict
from os.path import join
from psychopy import visual, event, logging, gui, core


@atexit.register
def save_beh_results() -> None:
    """
    Save results of experiment. Decorated with @atexit in order to make sure, that intermediate
    results will be saved even if interpreter will break.

    Returns:
        Nothing.
    """

    file_name = PART_ID + '_' + str(random.choice(range(100, 1000))) + '_beh.csv'
    with open(join('results', file_name), 'w', encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()


def show_image(win: visual.window, file_name: str, size: List[int], key: str = 'f7') -> None:
    """
    Show instructions in a form of an image.
    Args:
        win:
        file_name: Img file.
        size: Img size [width, height].
        key: Key to terminate procedure.

    Returns:
        Nothing.
    """
    image = visual.ImageStim(win=win, image=file_name, interpolate=True, size=size)
    image.draw()
    win.flip()
    clicked = event.waitKeys(keyList=[key, 'return', 'space'])
    if clicked == [key]:
        logging.critical('Experiment finished by user! {} pressed.'.format(key[0]))
        exit(0)
    win.flip()


def read_text_from_file(file_name: str, insert: str = '') -> str:
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    Args:
        file_name: Name of file to read
        insert:

    Returns:
        String to display.
    """
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def check_exit(key: str = 'f7') -> None:
    """
    Check if exit button pressed.

    Returns:
        Nothing.
    """
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error('Experiment finished by user! {} pressed.'.format(key))


def show_info(win: visual.Window, file_name: str, insert: str = '') -> None:
    """
    Clear way to show info message into screen.
    Args:
        win:
        file_name:
        insert:

    Returns:
        Nothing.
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg, height=20, wrapWidth=1000)
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space', 'left', 'right'])
    if key == ['f7']:
        abort_with_error('Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def abort_with_error(err: str) -> None:
    """
    Call if an error occurred.

    Returns:
        Nothing.
    """
    logging.critical(err)
    raise Exception(err)


def run_trial(win, conf, clock, stim):
    """
    Prepare and present single trial of procedure.
    Input (params) should consist all data need for presenting stimuli.
    If some stimulus (eg. text, label, button) will be presented across many trials.
    Should be prepared outside this function and passed for .draw() or .setAutoDraw().
    Returns:
        All behavioral data (reaction time, answer, etc. should be returned from this function).
    """

    # === Prepare trial-related stimulus ===
    # Randomise if needed
    #
    # Examples:
    #
    # que_pos = random.choice([-conf['STIM_SHIFT'], conf['STIM_SHIFT']])
    stim_image = random.choice([("images\\neutr_p.png", 'right'),
                                ("images\\neutr_l.png", 'left'),
                                ("images\\zgdn_l.png", 'left'),
                                ("images\\zgdn_p.png", 'right'),
                                ("images\\nzgdn_p.png", 'right'),
                                ("images\\nzgdn_l.png", 'left')])

    stim.image = stim_image[0]
    correct_key = stim_image[1]
    rbodz = ''
    if stim_image[0] == "images\\neutr_p.png" or stim_image[0] == "images\\neutr_l.png":
        rbodz = "Neutralny"
    elif stim_image[0] == "images\\zgodn_p.png" or stim_image[0] == "images\\zgodn_l.png":
        rbodz = "Zgodny"
    elif stim_image[0] == "images\\nzgdn_p.png" or stim_image[0] == "images\\nzgdn_l.png":
        rbodz = "Niezgodny"
    #

    # === Start pre-trial  stuff (Fixation cross etc.)===

    # === Start trial ===
    # This part is time-crucial. All stims must be already prepared.
    # Only .draw() .flip() and reaction related stuff goes there.
    event.clearEvents()
    # make sure, that clock will be reset exactly when stimuli will be drawn
    win.callOnFlip(clock.reset)

    for _ in range(random.choice(conf['STIM_TIME'])):  # present stimuli
        reaction = event.getKeys(keyList=list(conf['REACTION_KEYS']), timeStamped=clock)
        if reaction:  # break if any button was pressed
            break
        stim.draw()
        win.flip()
    reaction = None
    if not reaction:  # no reaction during stim time, allow to answer after that
        # question_frame.draw()
        # question_label.draw()
        win.flip()
        reaction = event.waitKeys(keyList=list(conf['REACTION_KEYS']), maxWait=conf['REACTION_TIME'], timeStamped=clock)
    # === Trial ended, prepare data for send  ===
    if reaction:
        key_pressed, rt = reaction[0]
        rt = round(rt * 1000)
    else:  # timeout
        key_pressed = 'no_key'
        rt = -1.0

    is_correct = (key_pressed == correct_key)

    return key_pressed, rt, is_correct, rbodz  # return all data collected during trial


# GLOBAL VARIABLES

RESULTS = list()  # list in which data will be collected
RESULTS.append(['Sesja', 'Numer próby', 'Czas reakcji', 'Poprawność', 'Rodzaj bodźca'])  # Results header
PART_ID = ''
SCREEN_RES = []

# === Dialog popup ===
info: Dict = {'Identyfikator': '', 'Płeć': ['M', "F"], 'Wiek': ''}
dict_dlg = gui.DlgFromDict(dictionary=info, title='Test flankowy')
if not dict_dlg.OK:
    abort_with_error('Ni mo.')

clock = core.Clock()
# load config, all params should be there
conf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
frame_rate: int = conf['FRAME_RATE']
SCREEN_RES: List[int] = conf['SCREEN_RES']
# === Scene init ===
win = visual.Window(SCREEN_RES, fullscr=True, monitor='testMonitor', units='pix', color=conf['BACKGROUND_COLOR'])
event.Mouse(visible=False, newPos=None, win=win)  # Make mouse invisible

PART_ID = info['Identyfikator'] + info['Płeć'] + info['Wiek']
logging.LogFile(join('results', f'{PART_ID}.log'), level=logging.INFO)  # errors logging
logging.info('FRAME RATE: {}'.format(frame_rate))
logging.info('SCREEN RES: {}'.format(SCREEN_RES))

# === Prepare stimulus here ===
#
# Examples:
fix_dot = visual.ImageStim(win, image='images\\BlackDot.png', size=[280, 280])
# que = visual.Circle(win, radius=conf['QUE_RADIUS'], fillColor=conf['QUE_COLOR'], lineColor=conf['QUE_COLOR'])
# stim = visual.TextStim(win, text="Press any arrow.", height=conf['STIM_SIZE'], color=conf['STIM_COLOR'])
# mask = visual.ImageStim(win, image='mask4.png', size=(conf['STIM_SIZE'], conf['STIM_SIZE']))
stim = visual.ImageStim(win, image='images\\neutr_p.png', size=(conf['STIM_SIZE1'], conf['STIM_SIZE2']))

# === Training ===
show_image(win, join('.', 'images', 'instrukcja.png'), size=[1550, 1080])

for trial_no in range(conf['TRAINING_TRIALS']):
    key_pressed, rt, corr, rbodz = run_trial(win, conf, clock, stim)

    RESULTS.append(["Trening", trial_no, '-', corr, rbodz])

    # it's a good idea to show feedback during training trials
    feedb = "images\\zielony.png" if corr else "images\\czerwony.png"
    feedb = visual.ImageStim(win, image=feedb, size=[1920, 1080])
    feedb.draw()
    win.flip()
    core.wait(1)
    win.flip()

# === Experiment ===
show_info(win, join('.', 'messages', 'before_experiment.txt'))
trial_no = 0
for _ in range(conf['FIX_CROSS_TIME']):
    fix_dot.draw()
    win.flip()
for _ in range(conf['TRIALS']):
    key_pressed, rt, corr, rbodz = run_trial(win, conf, clock, stim)
    RESULTS.append(["Eksperyment", trial_no, rt, corr, rbodz])
    trial_no += 1
    win.flip()
    core.wait(1)

# === Cleaning time ===
save_beh_results()
logging.flush()
show_info(win, join('.', 'messages', 'end.txt'))
win.close()
