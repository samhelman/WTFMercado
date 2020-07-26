from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.toast import toast
from kivymd.uix.navigationdrawer import NavigationLayout, MDNavigationDrawer
from kivymd.uix.list import OneLineListItem,TwoLineListItem
from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog

import gspread
from google.oauth2.service_account import Credentials

from ast import literal_eval

from datetime import datetime

from random import randint

class MainApp(MDApp):

    def __init__(self, **kwargs):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        self.shopping_list = []
        self.button_list = []
        self.card_dict = {}
        self.num = 0
        self.new_password = ''
        self.view_list = ''
        self.shopping_list_widgets = []
        self.submitted_lists = {}
        self.finished_lists = {}
        self.user_data_widgets = {}
        self.view_list_widgets = {}
        self.last_screen = ''
        self.delete_button = False
        self.price_button = False
        self.popup = False
        self.current_list = ''
        self.user_data_username = ''
        self.user_data_password = ''
        self.nav_drawer = False

        scopes = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file('creds.json', scopes=scopes)
        client = gspread.authorize(creds)
        self.spreadsheet = client.open('wtf_mercado')
        super().__init__(**kwargs)
    
    #method that changes the colours of the shopping list items if clicked
    def button_selected(self, button_id):
        if button_id.md_bg_color == self.theme_cls.bg_normal:
            button_id.md_bg_color = self.theme_cls.primary_color
            button_id.text_color = self.theme_cls.opposite_text_color
            self.button_list.append(button_id)
            self.shopping_list.append(button_id.text)
        else:
            button_id.md_bg_color = self.theme_cls.bg_normal
            button_id.text_color = self.theme_cls.primary_color
            self.button_list.remove(button_id)
            self.shopping_list.remove(button_id.text)

    #method to submit the final shopping list
    def submit_list(self):
        for button_id in self.button_list:
            button_id.md_bg_color = self.theme_cls.bg_normal
            button_id.text_color = self.theme_cls.primary_color
        for key in self.card_dict:
        	self.root.ids.custom_item_grid.remove_widget(self.card_dict[key])
        if len(self.shopping_list) > 0:
            self.add_list(self.username)
            toast('Presentado')
        self.shopping_list = []
        self.card_dict = {}
        self.root.ids.new_list_scrollview.scroll_y = 1
        self.root.ids.screen_manager.current = 'submitted_lists'

    #method that adds the shopping list to the organisation's google sheet
    def add_list(self,username):
        now = datetime.now()
        self.date_time = now.strftime("%b %d, %H:%M:%S")
        self.shopping_list.insert(0, 'Submitted')
        self.shopping_list.insert(0, self.username.upper() + ": " + self.date_time)
        username = self.organisation_data.find(username)
        row = username.row
        col = username.col
        row += 2
        entry = self.organisation_data.cell(row, col)
        dct = literal_eval(entry.value)
        dct[self.shopping_list[0]] = self.shopping_list
        self.organisation_data.update_cell(row,col,str(dct))
        self.add_submitted_list_widget('Submitted')

    #method that adds submitted lists to the submitted lists screen
    def add_submitted_list_widget(self, status):
        new_list = ListWidget(status)
        self.submitted_lists[self.shopping_list[0]] = new_list
        self.root.ids.submitted_lists.add_widget(new_list)

    #method that adds custom item cards to the custom item screen
    def add_custom_item(self, text):
        if len(text) > 0:
            self.shopping_list.append(text)
            new_card = CustomCard(text, self.num)
            self.card_dict[self.num] = new_card
            self.num += 1
            self.root.ids.custom_item_grid.add_widget(new_card)

    #method that removes custom cards from the custom item screen        
    def remove_card(self, root):
        self.shopping_list.remove(root.text)
        self.root.ids.custom_item_grid.remove_widget(self.card_dict[root.id_num])

    #method to change screen to the given screen            
    def set_screen(self, screen):
    	self.root.ids.screen_manager.current = screen

    #method to log in to the main app
    #adds nav_drawer on successful login
    #returns toast if either organisation, username or password are incorrect
    def submit_password(self, organisation, username, password):
        try:
            self.organisation_data = self.spreadsheet.worksheet('%s_data' % organisation)
        except:
            toast("Organización Inválida")
        if self.organisation_data:
            user_pass_dict = literal_eval(self.organisation_data.acell('A2').value)
            if username in user_pass_dict:
                if user_pass_dict[username] == password:
                    self.set_screen('submitted_lists')
                    self.organisation = self.organisation_data.acell('A1').value
                    self.username = username
                    username_cell = self.organisation_data.find(username)
                    row = username_cell.row
                    row += 1
                    col = username_cell.col
                    self.admin = self.organisation_data.cell(row,col).value
                    self.add_nav_drawer()
                    self.get_user_data(self.username)
                else:
                    toast("Contraseña Inválida")
            else:
                toast("Nombre de Usuario Inválida")
        

    def add_nav_drawer(self):
        if self.nav_drawer:
            self.nav_drawer.swipe_edge_width = 20
            self.nav_drawer.ids.nav_drawer_username.text = self.username.upper()
            self.nav_drawer.ids.nav_drawer_organisation.text = self.organisation
        else:
            self.nav_drawer = Navigation_Drawer()
            self.root.add_widget(self.nav_drawer)

    def no_feature(self):
        toast("Feature not added yet")

    def create_account(self, username, password, admin_status):
        if len(username) > 0:
            user_pass_dict = literal_eval(self.organisation_data.acell('A2').value)
            if username not in user_pass_dict:
                user_pass_dict[username] = password
                self.root.ids.admin_switch.active = False
                self.organisation_data.update('A2', str(user_pass_dict))
                row = 3
                col = 1
                entry = self.organisation_data.cell(row, col)
                while entry.value != '':
                    col += 1
                    entry = self.organisation_data.cell(row, col)
                self.organisation_data.update_cell(row,col,username)
                row += 1
                if admin_status == True:
                    self.organisation_data.update_cell(row,col,'admin')
                    self.organisation_data.update('D1', int(self.organisation_data.acell('D1').value) + 1)
                else:
                    self.organisation_data.update_cell(row,col,'user')
                for i in range(3):
                    row += 1
                    self.organisation_data.update_cell(row,col,'{}')
                users = int(self.organisation_data.acell('C1').value)
                self.users = users + 1
                self.organisation_data.update('C1',str(self.users))
                self.root.ids.screen_manager.current = 'accounts_list'
                self.get_user_accounts()
            else:
                toast("Username already in use")
            self.root.ids.new_username_field.text = ''
            self.root.ids.new_username_field.on_focus()
        else:
            toast('Please enter a valid username')

    def open_admin(self):
        if self.admin == 'admin':
            self.nav_drawer.ids.nav_drawer_screen_manager.current = 'nav_screen_admin_options'
        else:
            toast('Admin only')

    def open_list(self, screen, name):
        self.current_list = name
        if self.admin == 'user':
            users = [self.username]
        else:
            users = list(literal_eval(self.organisation_data.acell('A2').value).keys())
        for user in users:
            user_col = self.organisation_data.find(user)
            row = user_col.row
            col = user_col.col
            row += 2
            try:
                entry = literal_eval(self.organisation_data.cell(row,col).value)
                lst = entry[name]
                break
            except:
                try:
                    entry = literal_eval(self.organisation_data.cell(row+1,col).value)
                    lst = entry[name]
                    break
                except:
                    try:
                        entry = literal_eval(self.organisation_data.cell(row+2,col).value)
                        lst = entry[name]
                        break
                    except:
                        pass
        for key in self.view_list_widgets:
            widget = self.view_list_widgets[key]
            self.root.ids.view_list_scrollview.remove_widget(widget)
        self.view_list_widgets = {}
        for item in lst[2:]:
            widget = OneLineListItem(text=item, padding='16dp')
            self.view_list_widgets[item] = widget
            self.root.ids.view_list_scrollview.add_widget(widget)
        if self.delete_button:
            self.root.ids.list_view_buttons.remove_widget(self.delete_button)
            self.delete_button = False
        if self.price_button:
            self.root.ids.list_view_buttons.remove_widget(self.price_button)
            self.delete_button = False
        if self.admin == 'admin':
            self.delete_button = DeleteButton()
            self.price_button = PriceButton()
            self.root.ids.list_view_buttons.add_widget(self.delete_button)
            self.root.ids.list_view_buttons.add_widget(self.price_button)
        self.set_screen(screen)

    def generate_password(self):
        password = ''
        for i in range(0,4):
            password += str(randint(0,9))
        self.root.ids.new_password_field.text = password

    def build(self):
        self.title = 'WTF Groceries'
        return MainLayout()

    def get_user_data(self, username):
        self.users = int(self.organisation_data.acell('C1').value)
        entry = self.organisation_data.find(username)
        row = entry.row
        col = entry.col
        row += 2
        submitted_list_dict = literal_eval(self.organisation_data.cell(row,col).value)
        for key in submitted_list_dict:
            self.shopping_list = submitted_list_dict[key]
            self.add_submitted_list_widget(self.shopping_list[1])
        row += 1
        processing_list_dict = literal_eval(self.organisation_data.cell(row,col).value)
        for key in processing_list_dict:
            self.shopping_list = processing_list_dict[key]
            self.add_submitted_list_widget(self.shopping_list[1])
        row += 1
        finished_list_dict = literal_eval(self.organisation_data.cell(row,col).value)
        for key in finished_list_dict:
            self.shopping_list = finished_list_dict[key]
            self.add_submitted_list_widget(self.shopping_list[1])
        self.shopping_list = []

    def open_shopping_list(self):
        admin_list = literal_eval(self.organisation_data.acell('B1').value)
        list_col = self.organisation_data.acell('A5')
        row = list_col.row
        col = list_col.col
        added = 0
        while added < self.users:
            lists = literal_eval(list_col.value)
            for key in lists:
                lst = lists[key]
                lst[1] = 'Processing'
                for item in lst[2:]:
                    if item in admin_list.keys():
                        admin_list[item] += 1
                    else:
                        admin_list[item] = 1
                row += 1
                processing_lists = literal_eval(self.organisation_data.cell(row,col).value)
                processing_lists[key] = lst
                self.organisation_data.update_cell(row,col,str(processing_lists))
                row -= 1
            self.organisation_data.update_cell(row,col,'{}')
            added += 1
            col += 1
            list_col = self.organisation_data.cell(row,col)
        self.organisation_data.update('B1',str(admin_list))
        for item in self.shopping_list_widgets:
            self.root.ids.shopping_list.remove_widget(item)
        self.shopping_list_widgets = []
        for key in admin_list:
            new_item = AdminShoppingListItem(key,admin_list[key])
            self.shopping_list_widgets.append(new_item)
            self.root.ids.shopping_list.add_widget(new_item)
        self.root.ids.screen_manager.current = 'shopping_list'
        self.nav_drawer.ids.nav_drawer_screen_manager.current = "nav_screen_home"
        self.nav_drawer.set_state()

    def finish_with_admin_list(self):
        self.organisation_data.update('B1', '{}')
        self.root.ids.screen_manager.current = 'archived_lists'
        list_col = self.organisation_data.acell('A6')
        row = list_col.row
        col = list_col.col
        added = 0
        while added < self.users:
            processing_lists = literal_eval(list_col.value)
            row += 1
            finished_lists = literal_eval(self.organisation_data.cell(row,col).value)
            row -= 1
            for key in processing_lists:
                lst = processing_lists[key]
                lst[1] = 'Finished'
                finished_lists[key] = lst
            self.organisation_data.update_cell(row,col, '{}')
            self.organisation_data.update_cell(row + 1,col, str(finished_lists))
            added += 1
            col += 1
            list_col = self.organisation_data.cell(row,col)
        self.get_finished_lists()
        toast('Finished')

    def get_finished_lists(self):
        for lst in self.finished_lists:
            self.root.ids.view_lists.remove_widget(lst)
            self.finished_lists = {}
        user_dict = literal_eval(self.organisation_data.acell('A2').value)
        for user in user_dict:
            user_cell = self.organisation_data.find(user)
            row = user_cell.row
            col = user_cell.col
            row += 4
            finished_lists = self.organisation_data.cell(row,col)
            finished_list_dict = literal_eval(finished_lists.value)
            for key in finished_list_dict:
                self.shopping_list = finished_list_dict[key]
                finished_list_widget = ListWidget('Finished')
                self.finished_lists[key] = finished_list_widget
                self.root.ids.view_lists.add_widget(finished_list_widget)

    def delete_list(self):
        users = list(literal_eval(self.organisation_data.acell('A2').value).keys())
        for user in users:
            user_col = self.organisation_data.find(user)
            row = user_col.row
            col = user_col.col
            row += 2
            for i in range(3):
                list_dict = literal_eval(self.organisation_data.cell(row + i,col).value)
                if self.current_list in list(list_dict.keys()):
                    del list_dict[self.current_list]
                    self.organisation_data.update_cell(row + i, col, str(list_dict))
                    if self.last_screen == 'submitted_lists':
                        widget = self.submitted_lists[self.current_list]
                        self.root.ids.submitted_lists.remove_widget(widget)
                    if self.last_screen == 'archived_lists':
                        widget = self.finished_lists[self.current_list]
                        self.root.ids.archived_lists.remove_widget(widget)
                    break
                else:
                    continue
        self.root.ids.screen_manager.current = self.last_screen

    def get_user_accounts(self):
        for key in self.user_data_widgets:
            widget = self.user_data_widgets[key]
            self.root.ids.accounts_list.remove_widget(widget)
        user_data = literal_eval(self.organisation_data.acell('A2').value)
        usernames = list(user_data.keys())
        usernames.sort()
        for username in usernames:
            password = user_data[username]
            widget = UsernameListWidget(username,password)
            self.user_data_widgets[username] = widget
            self.root.ids.accounts_list.add_widget(widget)

    def open_user_data(self):
        self.set_screen('user_data')
        self.root.ids.user_data_username.text = 'Username: %s' % self.user_data_username
        self.root.ids.user_data_password.text = self.user_data_password

    def delete_user(self):
        username_cell = self.organisation_data.find(self.user_data_username)
        row = username_cell.row
        col = username_cell.col
        username = username_cell.value
        admin_status = self.organisation_data.cell(row+1,col).value
        if admin_status == 'admin' and int(self.organisation_data.acell('D1').value) == 1:
            toast('Only one admin account exists, \ncannot remove final admin account')
        else:
            usernames = literal_eval(self.organisation_data.acell('A2').value)
            del usernames[username]
            self.organisation_data.update('A2', str(usernames))
            user_col = self.organisation_data.find(username)
            row = user_col.row
            col = user_col.col
            for i in range(5):
                self.organisation_data.update_cell(row,col,'')
                row += 1
            self.organisation_data.update('C1', int(self.organisation_data.acell('C1').value) - 1)
            if admin_status == 'admin':
                self.organisation_data.update('D1', int(self.organisation_data.acell('D1').value) - 1)
            widget = self.user_data_widgets[username]
            self.root.ids.accounts_list.remove_widget(widget)
            
    def logout(self):
        self.root.ids.screen_manager.current = 'login'
        self.nav_drawer.set_state()
        self.nav_drawer.swipe_edge_width = 0
        for key in self.submitted_lists:
            self.root.ids.submitted_lists.remove_widget(self.submitted_lists[key])
        self.submitted_lists = {}
        for key in self.finished_lists:
            self.root.ids.archived_lists.remove_widget(self.finished_lists[key])
        self.finished_lists = {} 
    
    def confirm_delete(self):
        self.popup = MDDialog(
            auto_dismiss=False,
            type='custom',
            content_cls=DeleteDialogContent(),
            size_hint=[.75,.25]
        )
        self.popup.open()

    def add_price_popup(self):
        self.popup_content = AddPriceDialogContent()
        self.popup = MDDialog(
            auto_dismiss=False,
            type='custom',
            content_cls=self.popup_content,
            size_hint=[.75,.25]
        )
        self.popup.open()

    def add_price(self, price):
        decimal_index = price.find('.')
        decimal = ''
        for _ in price[decimal_index:]:
            decimal += _
        if len(decimal) > 3:
            self.popup_content.ids.price_field.helper_text = 'Price can only have up to two decimal places'
        else:
            running = True
            while running:
                row = 7
                col = 1
                entry = literal_eval(self.organisation_data.cell(row,col).value)
                if self.current_list in entry:
                    entry[self.current_list].insert(2, price)
                    self.organisation_data.update_cell(row,col,str(entry))
                    running = False
                else:
                    col += 1
            self.popup.dismiss()
            self.root.ids.screen_manager.current = self.last_screen



class Content(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)   	

class CustomCard(MDCard):

    def __init__(self, text, id_num, **kwargs):
        self.text = text
        self.id_num = id_num
        super().__init__(**kwargs)
                
class MainLayout(NavigationLayout):
	pass

class Navigation_Drawer(MDNavigationDrawer):
    pass

class ListWidget(TwoLineListItem):

    def __init__(self, status, **kwargs):
        self.status = status
        super().__init__(**kwargs)

class UsernameListWidget(TwoLineListItem):

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = password
        super().__init__(**kwargs)

class AdminShoppingListItem(GridLayout):
    
    def __init__(self, text, num, **kwargs):
        self.text = text
        self.num = str(num)
        super().__init__(**kwargs)

class DeleteButton(MDRaisedButton):

    def __init__(self, **kwargs):
        self.text = 'Delete List'
        super().__init__(**kwargs)

class PriceButton(MDRaisedButton):

    def __init__(self, **kwargs):
        self.text = 'Add Price'
        super().__init__(**kwargs)

class DeleteDialogContent(BoxLayout):
    pass

class AddPriceDialogContent(BoxLayout):
    pass
        

MainApp().run()

