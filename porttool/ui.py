from multiprocessing.dummy import DummyProcess
from pathlib import Path
from tkinter import (
    ttk,
    Toplevel,
    scrolledtext,
    StringVar,
    BooleanVar,
    Canvas, END,
)
from tkinter.filedialog import askopenfilename
import sys
from .configs import *
from .utils import portutils


class FileChooser(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Please select the base package's boot, system, and the zip port package")

        self.portzip = StringVar()
        self.basesys = StringVar()
        self.baseboot = StringVar()

        basesys = Path("base/system.img")
        baseboot = Path("base/boot.img")
        if basesys.exists():
            self.basesys.set(basesys.absolute())
        if baseboot.exists():
            self.baseboot.set(baseboot.absolute())

        self.frame = []
        self.__setup_widgets()
        self.focus()

    def __setup_widgets(self):
        def __match(val) -> str:
            match val:
                case 0:
                    return "Port package path"
                case 1:
                    return "Boot image of this device"
                case 2:
                    return "System image of this device"
                case _:
                    return ""

        def __choose_file(val: StringVar):
            val.set(askopenfilename(initialdir=getcwd()))
            self.focus()

        for index, current in enumerate([self.portzip, self.baseboot, self.basesys]):
            frame = ttk.Frame(self)
            label = ttk.Label(frame, text=__match(index), width=16)
            entry = ttk.Entry(frame, textvariable=current, width=40)
            button = ttk.Button(frame, text="Choose File", command=lambda x=current: __choose_file(x))
            self.frame.append([frame, label, entry, button])
        for i in self.frame:
            for index, widget in enumerate(i):
                if index == 0:  # frame
                    widget.pack(side='top', fill='x', padx=5, pady=5)
                    continue
                if index == 2:  # entry
                    widget.pack(side='left', fill='x', padx=5, pady=5)
                    continue
                widget.pack(side='left', padx=5, pady=5)
        bottomframe = ttk.Frame(self)
        bottombutton = ttk.Button(bottomframe, text='OK', command=self.destroy)
        bottombutton.pack(side='right', padx=5, pady=5)
        bottomframe.pack(side='bottom', fill='x', padx=5, pady=5)

    def get(self) -> list:
        """
        Return [boot.img path, system.img path, portzip.zip path]
        """
        self.wait_window(self)
        return [
            self.baseboot.get(),
            self.basesys.get(),
            self.portzip.get(),
        ]


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert(END, string)
        self.text_space.yview('end')

    def flush(self):
        ...


class MyUI(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="MTK Low-End Device Porting Tool")
        self.chipset_select = StringVar(value='mt65')
        self.pack_type = StringVar(value='zip')
        self.item = []
        self.itembox = []  # save Checkbutton widgets

        self.patch_magisk = BooleanVar(value=False)
        self.target_arch = StringVar(value='arm64')
        self.magisk_apk = StringVar(value="magisk.apk")
        self.__setup_widgets()

    def __start_port(self):
        # Check that at least one port item is selected
        if len(self.item) == 0:
            print("Error: No port items selected, please load port items first!")
            return
        files = boot, system, portzip = FileChooser(self).get()
        for i in (boot, system, portzip):
            if not Path(i).exists() or i == '':
                print(f"File {i} not selected or does not exist")
                return
        print(f"Base package boot path is: {boot}\n"
              f"Base package system image path is: {system}\n"
              f"Port package path is: {portzip}")
        # Configure selected items
        newdict = support_chipset_portstep[self.chipset_select.get()]
        for key, tkbool in self.item:
            newdict[key] = tkbool.get()

        # Magisk configuration
        newdict['patch_magisk'] = self.patch_magisk.get()
        newdict['magisk_apk'] = self.magisk_apk.get()
        newdict['target_arch'] = self.target_arch.get()

        # Start porting
        p = portutils(
            newdict, *files, True if self.pack_type.get() == 'img' else False,
        ).start
        DummyProcess(target=p).start()

    def __setup_widgets(self):
        def __scroll_event(event):
            number = int(-event.delta / 2)
            actcanvas.yview_scroll(number, 'units')

        def __scroll_func(event):
            actcanvas.configure(scrollregion=actcanvas.bbox("all"), width=300, height=180)

        def __create_cv_frame():
            self.actcvframe = ttk.Frame(actcanvas)
            actcanvas.create_window(0, 0, window=self.actcvframe, anchor='nw')
            self.actcvframe.bind("<Configure>", __scroll_func)
            actcanvas.update()

        def __load_port_item(select):
            print(f"Selected port scheme is {select}...")
            flags = support_chipset_portstep[select]['flags']
            # Destroy last items
            self.item = []
            self.itembox = []
            if hasattr(self, 'actcvframe'):
                self.actcvframe.destroy()
            __create_cv_frame()

            for index, current in enumerate(flags):
                self.item.append([current, BooleanVar(value=flags[current])])  # [flag_name, BooleanVar]
                self.itembox.append(
                    ttk.Checkbutton(self.actcvframe, text=current, variable=self.item[index][1])
                )

            for i in self.itembox:
                i.pack(side='top', fill='x', padx=5)

        # Frame for chipset selection
        optframe = ttk.Frame(self)
        optlabel = ttk.Label(optframe)

        opttext = ttk.Label(optlabel, text="Chipset Type", anchor='e')
        optmenu = ttk.OptionMenu(
            optlabel,
            self.chipset_select,
            support_chipset[0],
            *support_chipset,
            command=__load_port_item
        )

        opttext.pack(side='left', padx=5, pady=5, expand=False)
        optmenu.pack(side='left', fill='x', padx=5, pady=5, expand=False)

        optlabel.pack(side='top', fill='x')

        # Frame for supported port items
        actframe = ttk.Labelframe(optframe, text="Supported Port Items", height=180)

        actcanvas = Canvas(actframe)
        actscroll = ttk.Scrollbar(actframe, orient='vertical', command=actcanvas.yview)

        actcanvas.configure(yscrollcommand=actscroll.set)
        actcanvas.configure(scrollregion=(0, 0, 300, 180))
        actcanvas.configure(yscrollincrement=1)
        actcanvas.bind("<MouseWheel>", __scroll_event)

        actscroll.pack(side='right', fill='y')
        actcanvas.pack(side='right', fill='x', expand=True, anchor='e')
        actframe.pack(side='top', fill='x', expand=True)
        __create_cv_frame()

        # Buttons and options
        buttonlabel = ttk.Label(optframe)
        buttonport = ttk.Button(optframe, text="One-Click Port", command=self.__start_port)
        buttonport.pack(side='top', fill='both', padx=5, pady=5, expand=True)

        buttoncheck1 = ttk.Checkbutton(
            buttonlabel,
            text="Output as zip flashable package",
            variable=self.pack_type,
            onvalue='zip',
            offvalue='img'
        )
        buttoncheck2 = ttk.Checkbutton(
            buttonlabel,
            text="Output as img image",
            variable=self.pack_type,
            onvalue='img',
            offvalue='zip'
        )

        buttoncheck1.grid(column=0, row=0, padx=5, pady=5)
        buttoncheck2.grid(column=1, row=0, padx=5, pady=5)

        magiskarch = ttk.OptionMenu(
            buttonlabel,
            self.target_arch,
            "arm64",
            *["arm64", "arm", "x86", "x86_64"]
        )

        magiskapkentry = ttk.Entry(buttonlabel, textvariable=self.magisk_apk)
        magiskapkentry.bind("<Button-1>", lambda x: self.magisk_apk.set(askopenfilename()))

        buttonmagisk = ttk.Checkbutton(
            buttonlabel,
            text="Patch Magisk",
            variable=self.patch_magisk,
            onvalue=True,
            offvalue=False,
            command=lambda: (
                magiskapkentry.grid_forget(),
                magiskarch.grid_forget(),
            ) if not self.patch_magisk.get() else (
                magiskapkentry.grid(column=0, row=3, padx=5, pady=5, sticky='nsew', columnspan=2),
                magiskarch.grid(column=0, row=2, padx=5, pady=5, sticky='nsew', columnspan=2)
            )
        )
        buttonmagisk.grid(column=0, row=1, padx=5, pady=5, sticky='w')
        buttonlabel.pack(side='top', padx=5, pady=5, fill='x', expand=True)

        optframe.pack(side='left', padx=5, pady=5, fill='y', expand=False)

        # Log output
        logframe = ttk.Labelframe(self, text="Log Output")
        self.log = scrolledtext.ScrolledText(logframe)
        sys.stderr = StdoutRedirector(self.log)
        sys.stdout = StdoutRedirector(self.log)
        self.log.pack(side='left', fill='both', anchor='center')
        logframe.pack(side='left', padx=5, pady=5, fill='both', expand=True)

        __load_port_item(self.chipset_select.get())