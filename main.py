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

    '''
    Funkcja odpowiadająca za zapisywanie pliku wyjściowego w formacie ".csv".
    @atexit zostało użyte, w celu zapisania wyników, nawet w przypadku błędu interpretera.
    '''

    file_name = PART_ID + '_' + str(random.choice(range(100, 1000))) + '_beh.csv'
    with open(join('results', file_name), 'w', encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()


def show_image(win: visual.window, file_name: str, size: List[int], key: str = 'f7') -> None:

    '''
    Funkcja odpowiedzialna za wyświetlenie początkowych instrukcji przy użyciu zdjęcia.
    Przyjmuje argumenty:
    win: okno, na którym będzie wyświetlona instrukcja
    file_name: ścieżka do pliku
    size: wielkość zdjęcia [szerokość, wysokość]
    key: Klawisz, który po naciśnięciu zakończy procedurę

    '''
    image = visual.ImageStim(win=win, image=file_name, interpolate=True, size=size)
    image.draw()
    win.flip()
    clicked = event.waitKeys(keyList=[key, 'space'])
    if clicked == [key]:
        logging.critical('Eksperyment zakończony przez uczestnika! Naciśnięto {}.'.format(key[0]))
        exit(0)
    win.flip()


def read_text_from_file(file_name: str, insert: str = '') -> str:
    """
    Fragment kodu, który czyta plik tekstowy i dodaje do niego informacje wygenerowane w trakcie działania programu
    Argumenty:
        file_name: Nazwa pliku
        insert:

    Funkcja zwraca łańcuch znaków do wyświetlania
    """
    if not isinstance(file_name, str):
        logging.error('Problem z przetworzeniem pliku. Nazwa pliku musi być łańcuchem znaków')
        raise TypeError('file_name musi być łańcuchem znakowym')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'): 
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def check_exit(key: str = 'f7') -> None:
    """
    Sprawdzanie czy przez użytkownika został wciśnięty przycisk wyjścia z programu
    """
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error('Eksperyment został zakończony przez użytkownika! {} pressed.'.format(key))


def show_info(win: visual.Window, file_name: str, insert: str = '') -> None:
    """
    Tworzenie okna, które wyświetla tekst pliku
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg, height=20, wrapWidth=1000)
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space', 'left', 'right'])
    if key == ['f7']:
        abort_with_error('Eksperyment zakończony przez użytkownika! Klawisz F7 został naciśniety.')
    win.flip()


def abort_with_error(err: str) -> None:
    """
    Uruchamia się pdoczas błędu
    """
    logging.critical(err)
    raise Exception(err)


def run_trial(win, conf, clock, stim):
    """
Funkcja, która odpowiada za pojędyńczą próbę eksperymentalną w procedurze

Zwraca klawisz naciśnięty przez użytkownika, czas reakcji, czy naciśnięty klawisz jest zgodny z wyświetlanym bodźcem,   
rodzaj bodźca, czas wyświetlania bodźca
    """

    # Przygotowanie losowego wyświetlania bodźców
    
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
    elif stim_image[0] == "images\\zgdn_p.png" or stim_image[0] == "images\\zgdn_l.png":
        rbodz = "Zgodny"
    elif stim_image[0] == "images\\nzgdn_p.png" or stim_image[0] == "images\\nzgdn_l.png":
        rbodz = "Niezgodny"

    event.clearEvents()
    win.callOnFlip(clock.reset)

    # Przygotowanie losowania czasu dla wyświetlania bodźca
    czasb = ""

    stim_time = random.choice([9, 15, 21])
    if stim_time == 9:
        czasb = "150"
    elif stim_time == 15:
        czasb = "250"
    elif stim_time == 21:
        czasb = "350"

    for _ in range(stim_time):  # present stimuli
        reaction = event.getKeys(keyList=list(conf['REACTION_KEYS']), timeStamped=clock)
        if reaction:  # przerywa pętle jeśli klawisz zostanie naciśnięty
            break
        stim.draw()
        win.flip()
    reaction = None
    if not reaction:  # jeśli użytkownik nie zareagował podczas wyświetlania bodźca program czeka na reakcje
        win.flip()
        reaction = event.waitKeys(keyList=list(conf['REACTION_KEYS']), maxWait=conf['REACTION_TIME'], timeStamped=clock)

    if reaction:
        key_pressed, rt = reaction[0]
        rt = round(rt * 1000) # przeliczanie czasu reakcji na milisekundy
    else:  # program wypisuje -1 w pliku gdzie zapisują się wyniki
        key_pressed = 'no_key'
        rt = -1.0

    is_correct = (key_pressed == correct_key)

    return key_pressed, rt, is_correct, rbodz, czasb  


# Zmienne globalne

RESULTS = list()  # Lista, w której będą zbierane dane
RESULTS.append(['Sesja', 'Numer próby', 'Czas reakcji', 'Poprawność', 'Rodzaj bodźca',"Czas wyświetlania bodźca"])  # Nagłówek w pliku wyjściowym
PART_ID = ''
SCREEN_RES = []

# Otwiera okno, w którym uczestnik wpisuje swoje dane
info: Dict = {'Identyfikator': '', 'Płeć': ['M', "F"], 'Wiek': ''}
dict_dlg = gui.DlgFromDict(dictionary=info, title='Test flankowy')
if not dict_dlg.OK:
    abort_with_error('Ni mo.')

clock = core.Clock()
# Wczytywanie zmiennych z pliku konfiguracyjnego
conf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
frame_rate: int = conf['FRAME_RATE']
SCREEN_RES: List[int] = conf['SCREEN_RES']
# Stworzenie okna
win = visual.Window(SCREEN_RES, fullscr=True, monitor='testMonitor', units='pix', color=conf['BACKGROUND_COLOR'])
event.Mouse(visible=False, newPos=None, win=win)  # Sprawienie, żeby myszka była niewidoczna

PART_ID = info['Identyfikator'] + info['Płeć'] + info['Wiek']
logging.LogFile(join('results', f'{PART_ID}.log'), level=logging.INFO)  # logowanie błędów
logging.info('FRAME RATE: {}'.format(frame_rate))
logging.info('SCREEN RES: {}'.format(SCREEN_RES))

# Przygotowanie punktu fiksacji i bodźca
fix_dot = visual.ImageStim(win, image='images\\BlackDot.png', size=[280, 280])
stim = visual.ImageStim(win, image='images\\neutr_p.png', size=(conf['STIM_SIZE1'], conf['STIM_SIZE2']))

# Sesja treningowa
show_image(win, join('.', 'images', 'instrukcja.png'), size=[1550, 1080])

for trial_no in range(conf['TRAINING_TRIALS']):
    key_pressed, rt, corr, rbodz, czasb = run_trial(win, conf, clock, stim)

    RESULTS.append(["Trening", trial_no, '-', corr, rbodz, czasb])

    # Informacja zwrotna o poprawności udzielonej odpowiedzi
    feedb = "images\\zielony.png" if corr else "images\\czerwony.png"
    feedb = visual.ImageStim(win, image=feedb, size=[1920, 1080])
    feedb.draw()
    win.flip()
    core.wait(1)
    win.flip()

# Sesja eksperymentalna
show_info(win, join('.', 'messages', 'before_experiment.txt'))
trial_no = 0
for _ in range(conf['FIX_CROSS_TIME']):
    fix_dot.draw()
    win.flip()
for _ in range(conf['TRIALS']):
    key_pressed, rt, corr, rbodz, czasb = run_trial(win, conf, clock, stim)
    RESULTS.append(["Eksperyment", trial_no, rt, corr, rbodz, czasb])
    trial_no += 1
    win.flip()
    core.wait(1)


save_beh_results()
logging.flush()
show_info(win, join('.', 'messages', 'end.txt'))
win.close()
