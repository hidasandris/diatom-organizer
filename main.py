import os
import tkinter as tk
from tkinter import filedialog
import pathlib
import cv2
import PIL.Image
import PIL.ImageTk
import json
from ctypes import windll


class App(tk.Frame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.species_file = 'species.json'
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
        self.parent.title("File dialog")

        menubar = tk.Menu(self.parent)
        menubar.add_command(label="Open", command=self.on_open)
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
        self.parent.bind('<space>', self.display_next_image)
        self.parent.bind('a', lambda e: self.save_data('Cyclotella atomus var. atomus'))
        self.parent.bind('d', lambda e: self.save_data('Discostella pseudostelligera'))
        self.parent.bind('e', lambda e: self.save_data('Cyclotella meduanae'))
        self.parent.bind('h', lambda e: self.save_data('Stephanodiscus hantzschii f. hantzschii'))
        self.parent.bind('i', lambda e: self.save_data('Cyclostephanos invisitatus'))
        self.parent.bind('m', lambda e: self.save_data('Stephanodiscus minutulus'))
        self.parent.bind('t', lambda e: self.save_data('Stephanodiscus hantzschii f. tenuis'))

    def on_open(self):
        self.counter = 0
        directory = pathlib.Path(filedialog.askdirectory())
        self.file_names = [
            directory / filename for filename in os.listdir(directory) if filename.endswith('.tif')]
        self.display_next_image()

    def display_next_image(self, event=None):
        if len(self.file_names) == self.counter:
            self.pack_files()
            self.clear()
            return
        file_name = self.file_names[self.counter]
        img = cv2.imread(file_name.as_posix(), 0)
        cv_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # height, width, no_channels = cv_img.shape
        resized_image = cv2.resize(cv_img, (0, 0), fx=0.9, fy=0.9)

        self.photo = PIL.ImageTk.PhotoImage(
            image=PIL.Image.fromarray(resized_image))
        if self.counter == 0:
            self.canvas_image = self.canvas.create_image(
                0, 0, image=self.photo, anchor=tk.NW)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.current_image_name.set(self.file_names[self.counter].stem)
        self.counter += 1

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
                label=species, command=lambda lab=self.choosed_species: self.save_data(lab))

        with open(self.species_file, 'r+') as f:
            data = json.load(f)

            data['rare_species'] = self.species_rare
            f.seek(0)
            json.dump(data, f, indent=2)

    def pack_files(self):
        self.working_directory = self.file_names[0].parent
        for file, taxon in self.data.items():
            new_folder = self.working_directory / taxon
            if not os.path.isdir(new_folder):
                os.mkdir(new_folder)
            new_file = (self.working_directory / file).with_suffix('.tif')
            os.rename(new_file, (new_folder / file).with_suffix('.tif'))
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
