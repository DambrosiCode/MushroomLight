from nicegui import ui
from raver import Raver
from pathlib import Path

raver = Raver()

with ui.dropdown_button('Select Song', auto_close=True):
    # List files in the current directory
    files = [f.name for f in Path('./music').iterdir() if f.is_file() if f.suffix == '.wav']
    for file in files:
        ui.item(file, on_click=lambda file=file: raver.play_music(f'./music/{file}'))

ui.button('STOP', on_click=lambda: raver.stop_music())

def hash_to_rgb(hex_str):
    print(hex_str)
    # Remove the '#' character if it exists
    hex_str = hex_str.lstrip('#')
    # Convert every 2 characters into a base-16 integer
    return list(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

#with ui.button(icon='colorize') as button:
#    ui.color_picker(on_pick=lambda e:  raver.set_color(hash_to_rgb(e.color)[0], hash_to_rgb(e.color)[1], hash_to_rgb(e.color)[2]))





def hash_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return (
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16),
    )

picker = ui.element('q-color').props(
    ''
)

picker.on(
    'update:model-value',
    lambda e: (
        print(e.args),
        raver.set_color(*hash_to_rgb(e.args))
    )
)
ui.run()
