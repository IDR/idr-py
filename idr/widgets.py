from IPython.html import widgets
from IPython.display import display

def select_organism_dropdown_widget(organisms_list):

    org_sel = widgets.Dropdown(
        options = organisms_list,
        value = 'Homo Sapiens',
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