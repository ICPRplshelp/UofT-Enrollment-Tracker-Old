import logging
import re
import tkinter as tk
import data_plotter_controller as dpc


class TkWindowSystem:
    root: tk.Tk
    textbox_text: tk.StringVar
    check_state: tk.IntVar
    global_font: str
    repeats: int
    _hints: dict[str, str]
    v: tk.IntVar
    check_state_2: tk.IntVar

    def __init__(self) -> None:
        self._hints = {
            'HINT3': 'State a suffix! e.g. H1-F or Y1-Y',
            'HINT2': 'State the campus and the section code! UTSC courses only! e.g H1-F or Y1-Y',
            'HINT1': 'State a session code! F/Y/S'
        }
        self.repeats = 0
        self.global_font = 'Arial'
        self.root = tk.Tk()
        self.root.geometry("500x500")
        self.root.title("Timetable Tracker")
        label = tk.Label(self.root, text="Timetable Tracker", font=(self.global_font, 18))
        label.pack(padx=10, pady=10)

        # textbox = tk.Text(self.root, height=3, padx=10, pady=10, font=(self.global_font, 16))
        # textbox.pack()

        label2 = tk.Label(self.root, text="Type a course offering and press ENTER", font=(self.global_font, 10))
        label2.pack(padx=5, pady=2.5)

        self.textbox_text = tk.StringVar()
        myentry = tk.Entry(self.root, font=(self.global_font, 16), textvariable=self.textbox_text)
        myentry.pack()
        myentry.bind("<KeyPress>", self.on_key_press)

        self.check_state = tk.IntVar()
        check = tk.Checkbutton(self.root,
                               text="Combine lecture sections",
                               variable=self.check_state)
        check.pack()

        self.check_state_2 = tk.IntVar()
        check_2 = tk.Checkbutton(self.root,
                                 text="Hide special lec sections (LEC2000-2999)",
                                 variable=self.check_state_2)
        check_2.pack()

        self.v = tk.IntVar()
        self.v.set(0)
        plot_options = {"matplotlib": 0, "pyplot": 1}
        for tex, val in plot_options.items():
            tk.Radiobutton(self.root, text=tex, variable=self.v,
                           value=val).pack()

        button = tk.Button(self.root, text="Search",
                           command=self.on_search)
        button.pack(pady=5)

        # ALTERNATE CONTROLS START HERE

        self.printinfo = tk.StringVar()
        self.printinfo.set('')
        label5 = tk.Label(self.root, textvariable=self.printinfo)
        label5.pack()
        self.root.mainloop()


    def on_key_press(self, event) -> None:
        # print(event)
        # print(self.check_state.get())
        if event.char == '\r':
            # print('hello')
            self.on_search()
            # code that runs if enter is pressed

    def on_search(self) -> None:
        text_str = self.textbox_text.get().upper()
        text_str = validate_course_regex(text_str)
        if text_str == '':
            self.show_statement('That\'s not a course!')
            return  # do nothing
        if text_str in self._hints:
            self.show_statement(self._hints[text_str])
            return

        combined = self.check_state.get()
        self.textbox_text.set(text_str)
        try:
            pl = ['plt', 'px'][self.v.get()]
            dpc.main(text_str, not combined, pl, self.check_state_2.get() != 0, '20229')
        except FileNotFoundError:
            self.show_statement("Course isn't offered at all or in this term.")
            return
        self.empty_statement()

    def show_statement(self, text: str) -> None:
        if self.repeats == 0 and text != self.printinfo.get():
            self.printinfo.set(text)
        elif self.repeats == 0 and text == self.printinfo.get():
            self.repeats += 1
            self.printinfo.set(f'{text} x{self.repeats}')
        elif self.repeats >= 1 and text == self.printinfo.get()[:self.printinfo.get().rfind('x') - 1]:
            self.repeats += 1
            self.printinfo.set(f'{text} x{self.repeats}')
        else:
            self.printinfo.set(text)

    def empty_statement(self) -> None:
        self.printinfo.set('')


def re_return(reg: str, text: str) -> str:
    if len(re.findall(reg, text)) != 0:
        return re.findall(reg, text)[0]
    else:
        return ''


def validate_course_regex(text: str) -> str:
    """text is a potential course regex.
    always return what is displayed in the
    correct form.

    if it isn't a course, return ''.
    """
    b1 = re_return("[A-Z]{3}[0-5]\\d{2}[HY][01]-[FYS]", text)
    if b1 != '':
        return b1
    b2 = re_return("[A-Z]{3}[0-5]\\d{2}[HY][01][FYS]", text)
    if b2 != '':
        return b2[:-1] + '-' + b2[-1]
    b3 = re_return("[A-Z]{3}[0-5]\\d{2}[HY][01] [FYS]", text)
    if b3 != '':
        return b3.replace(' ', '-')
    b6 = re_return("[A-Z]{3}[0-5]\\d{2}", text)
    if b6 != '':
        b5 = re_return("[A-Z]{3}[0-5]\\d{2}[HY]", text)
        if b5 != '':
            b4 = re_return("[A-Z]{3}[0-5]\\d{2}[HY][01]", text)
            if b4 != '':
                return 'HINT1'
            return 'HINT2'
        return 'HINT3'
    return ''


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')
    TkWindowSystem()
