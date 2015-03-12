#!/usr/bin/env python

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdict
import sys
import urllib2
import json
import re

class WikiContext (GObject.GObject, Gdict.Context):
  local_only = GObject.property(type=bool, default=False)

  def __init__(self):
    GObject.GObject.__init__(self)

  def do_define_word (self, database, word):
    self.emit("lookup-start")

    print 'define_word: ' + word
    resp = urllib2.urlopen('http://en.wiktionary.org/w/api.php?format=json&action=query&titles=' + word + '&prop=revisions&rvprop=content')
    content = resp.read()
    data = json.loads(content)
    for k in data['query']['pages'].keys():
      defs = data['query']['pages'][k]['revisions'][0]['*']

      definition = Gdict.Definition()
      definition.ref_count = 1
      definition.word = word.capitalize()
      definition.total = 1
      definition.database_full = 'Wiktionary'

      text = ''
      sense_cnt = 1
      lines = defs.splitlines()
      for l in lines:
        match = re.search('^# ', l)
        if match:
          sense = str(sense_cnt) + '. ' + l[2:] + '\n'
          text += sense
          sense_cnt += 1

      text = re.sub('\[\[', '{', text)
      text = re.sub('\]\]', '}', text)
      definition.definition = text
      self.emit("definition-found", definition)
      print definition.definition

    self.emit("lookup-end")

class App (Gtk.Application):
  defbox = None

  def __init__(self):
    Gtk.Application.__init__(self,
        application_id="org.gnome.wiktionary",
        flags=Gio.ApplicationFlags.FLAGS_NONE)

  def do_activate(self):
    win = Gtk.Window()
    win.set_default_size(600, 600)
    self.add_window(win)

    vbox = Gtk.VBox()
    entry = Gtk.Entry()
    entry.connect("activate", self.on_entry_activate)
    vbox.pack_start(entry, False, False, 6)

    self.defbox = Gdict.Defbox()
    ctx = WikiContext()
    self.defbox.set_context(ctx)
    vbox.pack_start(self.defbox, True, True, 6)

    win.add(vbox)
    win.show_all()

  def on_entry_activate(self, entry):
    word = entry.get_text()
    print 'activate with word ' + word
    self.defbox.lookup(word)


if __name__ == "__main__":
  app = App()
  app.run(sys.argv)
