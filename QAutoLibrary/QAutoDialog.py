import tkinter
from functools import partial

dialog_y=None
dialog_x=None
class __Dialog(tkinter.Toplevel):
    def __init__(self, message, buttons:list = None, choices: list = None, inputfield: bool = False):
        global dialog_x, dialog_y
        self.__root = tkinter.Tk()

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

        #Borderless, no icon
        self.overrideredirect(1)
        self.attributes("-topmost", 1)

        self.__result = None
        self.__dropdownmenu=None
        self.__input_field = None

        frame = tkinter.Frame(self)
        frame.grid(column=0, row=0)

        frame.bind('<ButtonPress-1>', self.__start_move)
        frame.bind('<ButtonRelease-1>', self.__stop_move)
        frame.bind('<B1-Motion>', self.__move_dialog)
        frame.bind('<Escape>', self.__close) #TODO: FIX

        sarakkeita = len(buttons) if buttons else 2
        self.__riveja = round(len(message) / 25) if len(message)>25 else 1

        if '\n' in message:
            num = message.find('\n')
            message = [ message[start:start+num]+'\n' for start in range(0, len(message), num) ]
            message = ''.join(message)

        messagelabel = tkinter.Label(frame, text=message, width=40)
        messagelabel.grid(row=1,column=1,columnspan=sarakkeita,rowspan=self.__riveja)


        if choices:

            self.__dropdown_selection = tkinter.StringVar(self.__root)
            self.__dropdownmenu = tkinter.OptionMenu(frame, self.__dropdown_selection, *choices)
            self.__dropdownmenu.grid(row=2+self.__riveja,column=1, columnspan=len(buttons) if buttons else 2, sticky='ew')
            self.__dropdown_selection.set(choices[0])

        if inputfield:
            # Not working
            self.__input_field = tkinter.Entry(self.__root)
            self.__input_field.grid(row=2+self.__riveja,column=1, sticky='ew')


        if buttons:
            self.__button_factory(frame, buttons)

        frame.pack(padx=5, pady=5, expand=1)


    def label_callback(self, label: str):
        truelist = ['yes','ok','pass', 'continue']
        falselist = ['no','cancel','fail', 'stop']
        if label.lower() in truelist:
            self.__result = True
        elif label.lower() in falselist:
            self.__result = False
        else:
            if self.__input_field:
                self.__result = self.__input_field.get()
            else:
                self.__result = label

        self.__root.destroy()

    def __button_factory(self,frame, buttons):
        count = 1
        for b in buttons:
            size = len(b)+2 if len(b)+2 > 10 else 10
            button = tkinter.Button(frame, text=b, width=size, command=partial(self.label_callback, b))
            button.grid(row=3+self.__riveja,column=count)
            count += 1



    def __close(self, event=None):
        self.__root.destroy()

    def show(self):
        '''
        # for debugging
        self.__root.update()
        print(self.__root.winfo_width(), self.winfo_height())
        '''
        self.wait_window(self)

        if self.__dropdownmenu:
            return self.__result, self.__dropdown_selection.get()
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
        """
        ---- NOT IMPLEMENTED ----
        :param message:
        :param button_labels:
        """
        raise NotImplemented('Not yet')
        if not button_labels :
            button_labels = ['Set', 'Cancel']
        super().__init__(message=message,buttons=button_labels,inputfield=True)

"""
Example functions

"""
def pause(message: str = "Resume by clicking Continue"):
    """
    Pauses the script until user clicks continue
    :param message: Message to display in the dialog, defaults to "Resume by clicking Continue"
    :return: QAutoButtonDialog, which returns boolean
    """
    return QAutoButtonDialog(message=message, button_labels=['Continue', 'Stop']).show()

def dropdownmenu(message: str, list_of_choices: list, list_of_buttons: list=None):
    """
    Pauses the script and displays a message, with a dropdown list of choices for the user
    :param message: Message to display
    :param list_of_choices: List of choices in string format
    :param list_of_buttons: List of buttons, defaults to Ok,Cancel
    :return: QAutoDropdownDialog, which returns tuple of (button value, str chosen)
    """
    if not list_of_buttons:
        list_of_buttons = ['Ok', 'Cancel']
    return QAutoDropdownDialog(message=message, button_labels=list_of_buttons, choices=list_of_choices).show()

def buttons(message: str, list_of_buttons: list):
    """
    Pauses the script and displays a message with a selection of buttons
    :param message: Message to display
    :param list_of_buttons: List of buttons in string format
    :return: QAutoButtonDialog, which returns str or boolean, based on button
    """
    return QAutoButtonDialog(message=message, button_labels=list_of_buttons).show()

'''

# Another example function that displays an use case for a possible choice between step-by-step execution,
# a continuous execution or stopping the execution

def multibutton():
    state = None
    napit = [
        'Continue',
        'Stop',
        'Continue without pause'
    ]
    for i in range(0, 10):
        if not state:
            retval = QAutoButtonDialog('Select one of the options:\n', napit)
            if retval == 'Stop':
                break
            elif retval == 'Continue without pause':
                state = True
        print('Round ->', i)
'''