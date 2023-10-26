from PIL import Image, ImageTk, ImageSequence
import PySimpleGUI as sg
import time
import json
import output

NULL_CHAR = chr(0)

# Read config
f = open('config.json')
jdata = json.load(f)

# Empty layout lists
title_list = []
buttons_list = []
system_list = []
layout = []

def str2bool(value):
    return value.lower() in ("yes", "true", "t", "1", "y")

def write_keycode(keycode):
    with open('/dev/hidg0', 'rb+') as fd:
        fd.write(keycode.encode())
        fd.close()

# Load theme 
sg.theme(jdata['General']['deck_theme'])

# Import general settings
font = (jdata['General']['deck_font_name'],int(jdata['General']['deck_font_size']))
general_row_max_buttons = int(jdata['General']['row_max_buttons'])
general_image_scale = int(jdata['General']['image_scale'])
general_icons_path = jdata['General']['icons_path'] + '/' + jdata['General']['icons_theme'] + '/'
general_pad = (int(jdata['General']['button_pad_x']), int(jdata['General']['button_pad_y']))
general_button_resize = str2bool(jdata['General']['button_resize'])
general_border_width = int(jdata['General']['border_width'])
general_empty_buttons = str2bool(jdata['General']['empty_buttons'])
general_button_color_overwrite = str2bool(jdata['General']['button_color_overwrite'])
general_button_font_color =  jdata['General']['button_font_color']
general_button_color = general_button_font_color + " on " + sg.theme_background_color() if general_button_color_overwrite else sg.theme_background_color()
general_key_release_delay =  float(jdata['General']['key_release_delay'])

# Generate layout
# Show text on top if defined
if jdata['General']['deck_text'] != "":
    title_list.append(sg.Text(jdata['General']['deck_text'], font=font, pad = general_pad))
    layout.append(title_list)

# Create buttons
for idx,i in enumerate(jdata['DeckButtons']):
    key = i['key_name']
    image_filename = general_icons_path + i['key_icon']
    image_subsample = general_image_scale
    button_text = i['key_text']
    buttons_list.append(sg.Button(key = key, button_color = general_button_color, mouseover_colors=sg.theme_background_color(), border_width=general_border_width, image_filename=image_filename, image_subsample = image_subsample, button_text = button_text, pad = general_pad, expand_x = general_button_resize))
    if (idx + 1 ) % general_row_max_buttons == 0:
        layout.append(list(buttons_list))
        buttons_list.clear()
# Optional: fill empty buttons
if len(buttons_list) > 0 and len(buttons_list) < general_row_max_buttons and general_empty_buttons:
    for i in range(0,(general_row_max_buttons - len(buttons_list))):
        key = "empty_key_" + str(i)
        image_filename = general_icons_path + "target-rect-normal.png"
        button_text = " "
        buttons_list.append(sg.Button(key = key, button_color=sg.theme_background_color(), mouseover_colors=sg.theme_background_color(), border_width=general_border_width, image_filename=image_filename, image_subsample = image_subsample, button_text = button_text, pad = general_pad, expand_x = general_button_resize, disabled = True))
layout.append(list(buttons_list))

for wname in ('A0', 'A1', 'A2'):
    system_list.append(sg.Image(data=output.loadered, key=wname,  enable_events = True, pad = 15))

layout.append(system_list)

# Create Main Window, Enable titlebar and resize option for X11 support
window = sg.Window('Elite PiDeck', layout, no_titlebar=False, element_justification='c', resizable=True).Finalize()
window.Maximize()
window.TKroot["cursor"] = "none"

lasttime = time.time()
while True:
    curtime = time.time()
    event, values = window.read(timeout=100)
    for i in jdata['DeckButtons']:
        if event == i['key_name']:
            write_keycode(NULL_CHAR*2 + chr(int(i['key_code'],16))+NULL_CHAR*5)
            time.sleep(general_key_release_delay)
            write_keycode(NULL_CHAR*8)
            lasttime = time.time()
    if event in (sg.WIN_CLOSED, 'A0', 'A1', 'A2'):
        break
    if(curtime - lasttime < 0.5):
        for wname in ('A0', 'A1', 'A2'):
            window[wname].UpdateAnimation(output.loadered, time_between_frames=1)
    elif lasttime != 0 and (curtime - lasttime) > 0.5:
        for wname in ('A0', 'A1', 'A2'):
            window[wname].update(output.loadered)
        lasttime = 0


window.close()
