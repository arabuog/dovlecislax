"""Desktop settings panel for the timed loop. No screenshots or detection."""
import json
from dataclasses import asdict
from pathlib import Path
import queue
import sys
import time
import tkinter as tk
from tkinter import ttk
from panel_settings import Settings
from simple_cycle import Cycle


class Panel:
    def __init__(self, root, keys, desktop, keyboard):
        self.root=root
        self.keys=keys
        self.desktop=desktop
        self.events=queue.SimpleQueue()
        self.cycle=None
        self.pending=None
        self.held=set()
        self.closed=False
        self.n_down=False
        self.settings_path=Path(__file__).with_name('panel-settings.json')
        root.title('Dovleci • Panou de control')
        root.geometry('540x600')
        root.minsize(500,580)
        root.configure(bg='#101827')
        style=ttk.Style(root)
        style.theme_use('clam')
        style.configure('TFrame',background='#101827')
        style.configure('TLabel',background='#101827',foreground='#e2e8f0',font=('Segoe UI',11))
        style.configure('Title.TLabel',font=('Segoe UI',20,'bold'))
        style.configure('Hint.TLabel',foreground='#94a3b8',font=('Segoe UI',10))
        style.configure('TButton',font=('Segoe UI',11),padding=10)
        style.configure('TEntry',padding=6)
        body=ttk.Frame(root,padding=24)
        body.pack(fill='both',expand=True)
        ttk.Label(body,text='Mers → tastă → pauză',style='Title.TLabel').pack(anchor='w')
        ttk.Label(body,text='Buclă simplă • N pornește / pune pe pauză',style='Hint.TLabel').pack(anchor='w',pady=(5,20))
        defaults=asdict(Settings())
        self.load_warning=''
        try:
            if self.settings_path.exists():
                defaults=asdict(Settings.parse(json.loads(self.settings_path.read_text()),keys.KEYBOARD_MAPPING))
        except (OSError,ValueError,TypeError):
            self.load_warning='Setările salvate nu au putut fi citite; folosesc valorile inițiale.'
        self.fields={}
        form=ttk.Frame(body)
        form.pack(fill='x')
        form.columnconfigure(1,weight=1)
        labels=[('steps','Număr de pași'),('key','Tastă de apăsat'),('wait','Așteptare după tastă (secunde)'),('step_seconds','Durata unui pas (secunde)')]
        for row,(name,label) in enumerate(labels):
            ttk.Label(form,text=label).grid(row=row,column=0,sticky='w',pady=7,padx=(0,12))
            var=tk.StringVar(value=str(defaults[name]))
            self.fields[name]=var
            if name=='key':
                widget=ttk.Combobox(form,textvariable=var,values=('e','f','g','r','space','enter','1','2'),width=13)
            else:
                widget=ttk.Entry(form,textvariable=var,width=15)
            widget.grid(row=row,column=1,sticky='ew',pady=7)
        ttk.Label(body,text='Pașii sunt aproximați prin timp. Calibrează durata unui pas\nîn joc. Nu există detecție sau schimbare automată de rând.',style='Hint.TLabel').pack(anchor='w',pady=(12,16))
        self.summary=tk.StringVar()
        ttk.Label(body,textvariable=self.summary).pack(anchor='w')
        buttons=ttk.Frame(body)
        buttons.pack(fill='x',pady=(16,12))
        ttk.Button(buttons,text='Pornește în 3 secunde',command=self.prepare).pack(side='left')
        ttk.Button(buttons,text='Oprește',command=lambda:self.stop('Oprit.')).pack(side='right')
        self.status=tk.StringVar(value=self.load_warning or 'Pregătit. Revino în FiveM și apasă N.')
        ttk.Label(body,textvariable=self.status,wraplength=475,style='Hint.TLabel').pack(anchor='w',pady=6)
        for var in self.fields.values():
            var.trace_add('write',self.changed)
        self.changed()
        self.listener=keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        self.listener.start()
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.after(10,self.tick)

    def focused(self):
        window=self.desktop.snapshot()
        return window is not None and window.is_game and window.visible and not window.minimized

    def sync(self, wanted):
        for key in list(self.held-({wanted} if wanted else set())):
            self.keys.keyUp.__wrapped__(key,_pause=False)
            self.held.discard(key)
        if wanted and wanted not in self.held:
            self.held.add(wanted)
            if not self.keys.keyDown(wanted):
                raise RuntimeError('Windows nu a acceptat apăsarea tastei.')

    def stop(self,message):
        self.pending=None
        if self.cycle:
            self.cycle.pause()
        self.sync(None)
        self.status.set(message)

    def read(self):
        return Settings.parse({k:v.get() for k,v in self.fields.items()},self.keys.KEYBOARD_MAPPING)

    def changed(self,*_):
        if self.cycle is not None or self.pending is not None:
            self.stop('Setări modificate; pornește din nou pentru aplicare.')
        try:
            s=self.read()
            self.summary.set(f'W {s.walk_seconds:g}s → {s.key.upper()} o dată → pauză {s.wait:g}s')
        except ValueError:
            self.summary.set('Completează valorile pentru a putea porni.')

    def configure(self):
        try:
            s=self.read()
        except ValueError as error:
            self.status.set(str(error))
            return False
        self.cycle=Cycle(s.walk_seconds,s.wait,s.key)
        try:
            self.settings_path.write_text(json.dumps(asdict(s),indent=2),encoding='utf-8')
        except OSError:
            self.status.set('Setările nu pot fi salvate pe disc; rămân valabile în sesiune.')
        return True

    def prepare(self):
        self.stop('Pregătesc pornirea…')
        if self.configure():
            self.pending=time.monotonic()+3
            self.status.set('Revino în FiveM. Pornire în 3 secunde…')

    def on_press(self,key):
        if (getattr(key,'char',None) or '').lower()=='n' and not self.n_down:
            self.n_down=True
            self.events.put('toggle')

    def on_release(self,key):
        if (getattr(key,'char',None) or '').lower()=='n':
            self.n_down=False

    def tick(self):
        if self.closed:
            return
        try:
            if not self.listener.is_alive():
                self.stop('Ascultarea tastei N s-a oprit. Repornește panoul.')
                return
            while not self.events.empty():
                self.events.get_nowait()
                if self.pending is not None or (self.cycle and self.cycle.phase!='idle'):
                    self.stop('Pauză. Taste eliberate.')
                elif self.focused() and self.configure():
                    self.cycle.start(time.monotonic())
                elif not self.focused():
                    self.status.set('Revino în FiveM înainte să apeși N.')
            now=time.monotonic()
            if self.pending is not None and now>=self.pending:
                self.pending=None
                if self.focused():
                    self.cycle.start(now)
                else:
                    self.stop('Pornire anulată: FiveM nu este în prim-plan.')
            if self.cycle and self.cycle.phase!='idle':
                if not self.focused():
                    self.stop('FiveM nu mai este în prim-plan; pauză.')
                else:
                    self.sync(self.cycle.tick(now))
                    labels={'walk':'Merge înainte…','press':'Apasă tasta o dată…','rest':'Așteaptă…'}
                    self.status.set(f'{labels[self.cycle.phase]} {max(0,self.cycle.deadline-now):.1f}s • N pentru pauză')
        except Exception as error:
            self.stop(f'Oprit din cauza unei erori: {error}')
        self.root.after(10,self.tick)

    def close(self):
        self.closed=True
        try:
            self.stop('Oprit.')
        finally:
            self.listener.stop()
            self.root.destroy()


def main():
    if sys.platform!='win32':
        raise SystemExit('Panoul pentru controlul jocului necesită Windows.')
    import pydirectinput as keys
    from pynput import keyboard
    from game_capture import WindowsDesktop
    keys.PAUSE=0
    root=tk.Tk()
    panel=Panel(root,keys,WindowsDesktop(),keyboard)
    try:
        root.mainloop()
    finally:
        if not panel.closed:
            panel.close()


if __name__=='__main__':
    main()
