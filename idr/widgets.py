import sys
from IPython.html import widgets
from IPython.display import display

def select_organism_dropdown_widget(organisms_list):

    org_sel = widgets.Dropdown(
        options = organisms_list,
        value = 'Homo sapiens',
        description = 'Select Organism:',
        disabled = False,
    )
    display(org_sel)
    return org_sel

def textbox_widget(temp_value, tool_tip, textbox_name):
    
    text_box = widgets.Text(
        value = temp_value,
        placeholder = tool_tip,
        description = textbox_name,
        disabled = False
    )
    
    display(text_box)
    return text_box

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)