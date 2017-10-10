from idr.widgets import dropdown_widget, textbox_widget, html_widget, progress


class TestWidgets():

    def test_textbox_widget(self):
        idr_username = textbox_widget('int_test',
                                      'Enter Username',
                                      'IDR username:',
                                      False)

        assert idr_username.value == 'int_test'
        assert idr_username.description == 'IDR username:'
        assert idr_username.placeholder == 'Enter Username'

    def test_dropdown_widget(self):

        organisms_list = ['A', 'B', 'C']
        org_sel = dropdown_widget(organisms_list,
                                  'Select Organism:',
                                  False)

        assert org_sel.value == 'A'
        assert org_sel.description == 'Select Organism:'

    def test_html_widget(self):

        text = 'int_test'
        htmlwid = html_widget(text, displaywidget=False)

        assert htmlwid.value == '<b>' + text + '</b>'

    def test_progress(self):

        scid_list = ['1', '2', '3']
        for i, sid in enumerate(set(scid_list)):
            progress(i+1, len(set(scid_list)),
                     status='Iterating through screens')

        assert i == 2
