import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pathlib
import PIL.Image
import PIL.ImageTk
import json
from ctypes import windll
import copy


class App(tk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.species_file = 'species.json'
        self.hotkeys_file = 'hotkeys.json'
        self.hotkeys = {}
        self.working_directory = None
        self.file_names = []
        self.canvas = None
        self.canvas_image = None
        self.rare_species_options = None
        self.counter = 0
        self.photo = None
        self.species_common = []
        self.species_rare = []
        self.data = {}
        self.choosed_species = tk.StringVar(parent)
        self.current_image_name = tk.StringVar(parent)
        self.new_species_name = tk.StringVar(parent)
        self.grid_top_widgets = 4

        self.init_ui()

    def init_ui(self):
        self.grid()
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=5)
        self.parent.columnconfigure(1, weight=1)
        self.parent.title("Diatom organizer")

        menubar = tk.Menu(self.parent)
        menubar.add_command(label="Open", command=self.on_open)
        menubar.add_command(label="Import", command=self.on_import)
        menubar.add_command(label="Hotkeys", command=self.on_show_hotkeys)
        self.parent.config(menu=menubar)

        label_image_name = tk.Label(
            self.parent, textvariable=self.current_image_name)
        label_image_name.grid(row=0, column=1, sticky=tk.N, pady=1)

        btn_question = tk.Button(
            self.parent, text="?", bg="gold", width=10, command=lambda: self.save_data('_Bizonytalan'))
        btn_question.grid(row=1, column=1, sticky=tk.NW, pady=10)

        btn_next = tk.Button(
            self.parent, text="Next", bg="wheat1", width=10, command=self.display_next_image)
        btn_next.grid(row=1, column=1, sticky=tk.N, pady=10)

        btn_pack = tk.Button(
            self.parent, text="Pack", bg="SeaGreen3", width=10, command=self.pack_files)
        btn_pack.grid(row=1, column=1, sticky=tk.NE, pady=10)

        self.read_species()

        self.canvas = tk.Canvas(self.parent, bg="grey")
        self.canvas.grid(row=0, column=0, rowspan=len(
            self.species_common) + self.grid_top_widgets, sticky=tk.NSEW)

        entry_new_species = tk.Entry(
            self.parent, textvariable=self.new_species_name, width=30)
        entry_new_species.grid(row=2, column=1, sticky=tk.NW, pady=5)

        btn_save_entry = tk.Button(
            self.parent, text="Save", width=10, command=self.save_new_species)
        btn_save_entry.grid(row=2, column=1, padx=60, pady=5, sticky=tk.E)

        self.choosed_species.set('Select other')
        self.rare_species_options = tk.OptionMenu(
            self.parent, self.choosed_species, *self.species_rare,
            command=lambda lab=self.choosed_species: self.save_data(lab))
        self.rare_species_options.config(bg="SkyBlue2")
        self.rare_species_options["menu"].config(bg="LightSkyBlue2")
        self.rare_species_options.grid(row=3, column=1, sticky=tk.NW, pady=5)
        self.create_buttons(self.species_common)

        # Events
        self.canvas.bind("<Configure>", self.resize)
        self.parent.bind('<Control-o>', self.on_open)
        entry_new_species.bind('<FocusIn>', self.unbind_hotkeys)
        entry_new_species.bind('<FocusOut>', self.bind_hotkeys)
        self.import_hotkeys()
        self.bind_hotkeys()

    def import_hotkeys(self):
        if os.path.exists(self.hotkeys_file):
            with open(self.hotkeys_file, 'r') as f:
                self.hotkeys = json.load(f)

    def bind_hotkeys(self, event=None):
        self.parent.bind('<space>', self.display_next_image)
        for hotkey, species in self.hotkeys.items():
            def make_lambda(x):
                return lambda e: self.save_data(x)
            self.parent.bind(hotkey, make_lambda(species))

    def unbind_hotkeys(self, event=None):
        self.parent.unbind('<space>')
        for hotkey in self.hotkeys.keys():
            self.parent.unbind(hotkey)

    def on_open(self, event=None):
        self.counter = 0
        directory = pathlib.Path(filedialog.askdirectory())
        self.file_names = [
            directory / filename for filename in os.listdir(directory)
            if filename.endswith('.tif') or filename.endswith('.bmp')]
        self.working_directory = self.file_names[0].parent
        self.display_next_image()

    def on_import(self):
        import_file = pathlib.Path(
            filedialog.askopenfilename(
                filetypes=(('JSON', '*.json'),)))
        with open(import_file) as json_file:
            self.data = json.load(json_file)
        self.working_directory = import_file.parent

        self.pack_files()

    def on_show_hotkeys(self):
        hotkeys_str = ''
        for key, value in self.hotkeys.items():
            hotkeys_str += '{0}: {1}\r\n'.format(key, value)
        messagebox.showinfo('Hotkeys', hotkeys_str)

    def display_next_image(self, event=None):
        if len(self.file_names) == self.counter:
            try:
                self.pack_files()
            except:
                with open(self.working_directory / 'result.json', 'w') as fp:
                    json.dump(self.data, fp)
            self.clear()
            return
        file_name = self.file_names[self.counter]
        file_name_str = file_name.as_posix()
        with PIL.Image.open(file_name_str) as img:
            self.img = copy.copy(img)
        size = self.img.size

        self.photo = PIL.ImageTk.PhotoImage(self.img)
        if self.counter == 0:
            self.canvas_image = self.canvas.create_image(
                0, 0, image=self.photo, anchor=tk.NW, tags="IMG")
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.current_image_name.set(self.file_names[self.counter].stem)
        self.counter += 1

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.resize(width=canvas_width, height=canvas_height)

    def resize(self, event=None, width=None, height=None):
        if not hasattr(self, 'img'):
            return
        if event:
            size = (event.width, event.height)
        else:
            size = (width, height)
        resized = copy.copy(self.img)
        resized.thumbnail(size, PIL.Image.ANTIALIAS)
        self.photo = PIL.ImageTk.PhotoImage(resized)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)

    def clear(self):
        self.counter = 0
        self.canvas.delete(self.canvas_image)
        self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, anchor=tk.CENTER,
                                text="End", fill="red", font=("Courier", 44))
        self.current_image_name.set('')
        self.data.clear()

    def read_species(self):
        if os.path.exists(self.species_file):
            with open(self.species_file, 'r') as f:
                file = json.load(f)
                self.species_common = file['common_species']
                self.species_rare = file['rare_species']

    def create_buttons(self, species):
        for idx, label in enumerate(species):
            btn = tk.Button(self.parent, text=label)
            btn.config(command=lambda lab=label: self.save_data(lab))
            btn.grid(row=idx + self.grid_top_widgets,
                     column=1, sticky=tk.EW, pady=2)

    def save_data(self, label, event=False):
        self.data[self.file_names[self.counter - 1].stem] = label
        self.display_next_image()

    def save_new_species(self):
        new_species_name = self.new_species_name.get()
        self.new_species_name.set('')
        self.species_rare.append(new_species_name)
        self.species_rare.sort()

        menu = self.rare_species_options["menu"]
        menu.delete(0, "end")
        for species in self.species_rare:
            menu.add_command(
                label=species, command=tk._setit(self.choosed_species, species, self.save_data))

        with open(self.species_file, 'r+') as f:
            data = json.load(f)

            data['rare_species'] = self.species_rare
            f.seek(0)
            json.dump(data, f, indent=2)

        self.canvas.focus_set()

    def pack_files(self):
        try:
            for file, taxon in self.data.items():
                new_folder = self.working_directory / taxon
                if not os.path.isdir(new_folder):
                    os.mkdir(new_folder)

                extension = '.tif'
                new_file = (self.working_directory / (file + extension))
                if not new_file.is_file():
                    extension = '.bmp'
                    new_file = (self.working_directory / (file + extension))
                if not new_file.is_file():
                    continue
                os.rename(new_file, (new_folder / (file + extension)))
        except Exception as e:
            print(e)
            with open(self.working_directory / 'result.json', 'w') as fp:
                json.dump(self.data, fp)
        self.clear()


def main():
    windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.state('zoomed')
    app = App(root)
    root.mainloop()
    print(app.data)


if __name__ == '__main__':
    main()
