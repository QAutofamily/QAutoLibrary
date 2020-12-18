import tkinter
from functools import partial

# TODO wrap .show() somehow
# TODO bind Enter to input dialogs
# TODO limit width properly
# TODO split message properly

dialog_y=None
dialog_x=None
class __Dialog(tkinter.Toplevel):
    def __init__(self, message, buttons:list = None, choices: list = None, **kwargs):
        """
        inputfield: bool = False, loginfield: bool = False
        inputfield = False
        loginfield = False
        hiddenfield = False
        """
        global dialog_x, dialog_y
        self.__root = tkinter.Tk()

        #TODO: Icon to pip package
        # Icon won't work with borderless, it needs to be set in a column.
        #self.icon = tkinter.PhotoImage('qautorpa.ico')
        #self.__root.wm_iconbitmap(True, self.icon)
        self.__root.withdraw()

        tkinter.Toplevel.__init__(self, self.__root)

        self.title("QAutomate")

        self.minsize(250,50)
        w = self.__root.winfo_screenwidth()
        h = self.__root.winfo_screenheight()
        if not dialog_y or not dialog_x:
            dialog_y = int(h/2)
            dialog_x = int(w/2)
        self.geometry(f'+{dialog_x}+{dialog_y}')

        #TODO: better grip before
        #Borderless, no icon
        #self.overrideredirect(1)

        self.attributes("-topmost", 1)

        self.__result = None
        self.__dropdownmenu=None
        self.__input_field = None
        self.__password_field = None

        frame = tkinter.Frame(self)
        frame.grid(column=0, row=0)

        frame.bind('<ButtonPress-1>', self.__start_move)
        frame.bind('<ButtonRelease-1>', self.__stop_move)
        frame.bind('<B1-Motion>', self.__move_dialog)
        self.bind_all('<Escape>', self.__close)


        self.__extra_rows = round(len(message) / 25) if len(message) > 25 else 1
        self.__colspan = len(buttons) if buttons else 2

        # Hacky way to set max text length, because there's not enough hours in a workday
        #
        # TODO: Split the sentences with spaces, closest space below charlimit
        # This is only a temporal solution to handle overlapping strings
        message_limit = 40

        if len(message) > message_limit:
            temp = []
            num = message.rfind(' ',message_limit-10,message_limit)
            while len(message) > message_limit:
                temp.append(message[0:num] + '\n')
                message = message[num:]
                num = message.rfind(' ', message_limit-10, message_limit)
            temp.append(message)
            message = ''.join(temp)

        self.__current_row = 1
        messagelabel = tkinter.Label(frame, text=message, width=40)
        messagelabel.grid(row=self.__current_row, column=1, columnspan=self.__colspan, rowspan=self.__extra_rows)
        self.__current_row += self.__extra_rows +1

        if choices:

            self.__dropdown_selection = tkinter.StringVar(self.__root)
            self.__dropdownmenu = tkinter.OptionMenu(frame, self.__dropdown_selection, *choices)
            self.__dropdownmenu.grid(row=self.__current_row, column=1, columnspan=self.__colspan, sticky='ew')
            self.__dropdown_selection.set(choices[0])
            self.__current_row += 1

        if 'inputfield' in kwargs:
            self.__input_field = tkinter.Entry(frame, show=None, font=('Arial', 10))
            self.__input_field.grid(row=self.__current_row, column=1, columnspan=self.__colspan, sticky='ew')
            self.__current_row += 1

        if 'loginfield' in kwargs:
            L1 = tkinter.Label(frame, text="Login")
            L2 = tkinter.Label(frame, text="Password")
            L1.grid(row=self.__current_row, column=1, sticky='w')
            L2.grid(row=self.__current_row+1, column=1, sticky='w')
            self.__input_field = tkinter.Entry(frame, show=None, font=('Arial', 14))
            self.__input_field.grid(row=self.__current_row, column=2, columnspan=self.__colspan, sticky='ew')
            self.__password_field = tkinter.Entry(frame, show='*', font=('Arial', 14))
            self.__password_field.grid(row=self.__current_row+1, column=2, columnspan=self.__colspan, sticky='ew')
            self.__current_row += 2


        if 'hiddeninputfield' in kwargs:
            L1 = tkinter.Label(frame, text="Input")
            L1.grid(row=self.__current_row, column=1, sticky='w')
            self.__input_field = tkinter.Entry(frame, show='*', font=('Arial', 14))
            self.__input_field.grid(row=self.__current_row, column=2, columnspan=self.__colspan, sticky='ew')
            self.__current_row += 1

        if buttons:
            bindenter = 'field' in kwargs
            self.__button_factory(frame, buttons, bindenter)

        frame.pack(padx=5, pady=5, expand=1)

    def label_callback(self, label: str):
        truelist = ['yes','ok','pass', 'continue']
        falselist = ['no','cancel','fail', 'stop']
        if label.lower() in truelist:
            self.__result = True
        elif label.lower() in falselist:
            self.__result = False
        else:
            self.__result = label

        if self.__password_field and label.lower() not in falselist:
            self.__result = self.__input_field.get(), self.__password_field.get()
        elif self.__input_field and label.lower() not in falselist:
            self.__result = self.__input_field.get()

        self.__root.destroy()

    def __button_factory(self,frame, buttons, bindenter: bool = False):
        count = 1
        for b in buttons:
            size = len(b)+2 if len(b)+2 > 10 else 10
            button = tkinter.Button(frame, text=b, width=size, command=partial(self.label_callback, b))
            #TODO: Enter for input dialogs
            #if bindenter:
            #    self.bind_all('<Enter>', lambda event

            button.grid(row=self.__current_row, column=count,pady=7)
            count += 1
        self.__current_row += 1


    def __close(self, event=None):
        self.__result = False
        self.__root.destroy()

    def show(self):
        '''
        # for debugging
        self.__root.update()
        print(self.__root.winfo_width(), self.winfo_height())
        '''
        self.wait_window(self)

        if self.__dropdownmenu:
            if self.__result:
                return self.__dropdown_selection.get()

        return self.__result

    def __start_move(self, event):
        self.x = event.x
        self.y = event.y

    def __stop_move(self, event):
        global dialog_y,dialog_x
        dialog_x = self.winfo_x()
        dialog_y = self.winfo_y()

    def __move_dialog(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        dialog_x = self.winfo_x() + deltax
        dialog_y = self.winfo_y() + deltay

        self.geometry(f"+{dialog_x}+{dialog_y}")

class QAutoButtonDialog(__Dialog):
    def __init__(self, message: str, button_labels: list):
        """
        Creates an always on top dialog popup with buttons
        Returns the button label on click or True/False when one of these apply:
                truelist = ['yes','ok','pass','continue']
                falselist = ['no','cancel','fail','stop]
        :param message: Message to display before buttons
        :param button_labels: List of strings to create buttons from

        Example:
        QAutoButtonDialog(message='Click Continue to resume execution', button_labels=['Continue', 'Stop']).show()
        QAutoButtonDialog(message='Select wether to "Continue" step-by-step, "Stop" or "Finish" to the end', button_labels=['Continue','Stop','Finish']).show()
        """
        super().__init__(message,button_labels)

class QAutoDropdownDialog(__Dialog):
    def __init__(self, message: str, choices:list, button_labels: list = None):
        """
        Creates an always on top dialog popup with a dropdown menu with buttons
        Returns the button label on click and selected dropdown value
        True/False when one of these apply:
                truelist = ['yes','ok','pass','continue']
                falselist = ['no','cancel','fail','stop']
        :param message: Message to display before buttons
        :param choices: List of strings for the user to choose from
        :param button_labels: List of strings to create buttons from, Defaults to Ok and Cancel

        Example:
        QAutoDropdownDialog(message='What is your favourite colour?', button_labels=['Set','Cancel'], choices=['Green','Blue','Red']).show()
        """
        if not button_labels :
            button_labels = ['Ok', 'Cancel']
        super().__init__(message=message,buttons=button_labels,choices=choices)

class QAutoUserinputDialog(__Dialog):
    def __init__(self, message: str, button_labels: list = None):

        if not button_labels :
            button_labels = ['Set', 'Cancel']
        super().__init__(message=message,buttons=button_labels,inputfield=True)

class QAutoHiddeninputDialog(__Dialog):
    def __init__(self, message: str, button_labels: list = None):
        if not button_labels :
            button_labels = ['Set', 'Cancel']
        super().__init__(message=message,buttons=button_labels,hiddeninputfield=True)

class QAutoLoginDialog(__Dialog):
    def __init__(self, message: str, button_labels: list = None):
        if not button_labels:
            button_labels = ['Set', 'Cancel']
        super().__init__(message=message, buttons=button_labels, loginfield=True)


"""
Keyword functions for robots
"""


def pause(message: str = "Resume by clicking Continue"):
    """
    Pauses the script until user clicks continue
    :param message: Message to display in the dialog, defaults to "Resume by clicking Continue"
    :return: QAutoButtonDialog, which returns boolean
    """
    return QAutoButtonDialog(message=message, button_labels=['Continue', 'Stop']).show()


def dropdown_dialog(message: str, list_of_choices: list, buttons: list = None):
    """
    Pauses the script and displays a message, with a dropdown list of choices for the user
    :param message: Message to display
    :param list_of_choices: List of choices in string format
    :param list_of_buttons: List of buttons, defaults to Ok,Cancel
    :return: QAutoDropdownDialog, which returns tuple of (button value, str chosen)
    """
    if not buttons:
        buttons = ['Ok', 'Cancel']
    return QAutoDropdownDialog(message=message, button_labels=buttons, choices=list_of_choices).show()


def button_dialog(message: str, buttons: list = None):
    """
    Pauses the script and displays a message with a selection of buttons
    :param message: Message to display
    :param list_of_buttons: List of buttons in string format
    :return: QAutoButtonDialog, which returns str or boolean, based on button
    """
    if not buttons:
        buttons = ['Ok', 'Cancel']
    return QAutoButtonDialog(message=message, button_labels=buttons).show()


def userinput_dialog(message: str, buttons: list = None):
    """
    Dialog with a user input field
    """
    if not buttons:
        buttons = ['Ok', 'Cancel']
    return QAutoUserinputDialog(message, buttons).show()


def hiddeninput_dialog(message: str, buttons: list = None):
    """
    Dialog with a hidden input field
    """
    if not buttons:
        buttons = ['Ok', 'Cancel']
    return QAutoHiddeninputDialog(message, buttons).show()


def login_dialog(message: str, buttons: list = None):
    """
    Dialog with a Username input field and Password hidden input field
    """
    if not buttons:
        buttons = ['Ok', 'Cancel']
    return QAutoLoginDialog(message, buttons).show()
