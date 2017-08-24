import sys
from IPython.html import widgets
from IPython.display import display

def select_option_dropdown_widget(organisms_list, dropdown_widget_name):

    org_sel = widgets.Dropdown(
        options = organisms_list,
        value = organisms_list[0],
        description = dropdown_widget_name,
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

def slider_widget(slider_name, tool_tip, minvalue, maxvalue, defaultvalue):

    slider = widgets.IntSlider(
        min = minvalue,
        max = maxvalue,
        value = defaultvalue,
        placeholder = tool_tip,
        description = slider_name,
        disabled = False
    )

    display(slider)
    return slider

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)