#!/usr/bin/env python

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdict
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
      lines = defs.splitlines()
      for l in lines:
        match = re.search('^# ', l)
        if match:
          defi = Gdict.Definition()
          defi.ref_count = 1
          defi.word = word
          defi.total = len(lines)
          defi.definition = l[2:]
          defi.database_name = 'database'
          self.emit("definition-found", defi)
          print l[2:]

    self.emit("lookup-end")

def on_entry_activate(sender):
  word = sender.get_text()
  print 'activate with word ' + word
  defbox.lookup(word)

if __name__ == "__main__":
  win = Gtk.Window()
  win.set_default_size(600, 600)
  vbox = Gtk.VBox()
  entry = Gtk.Entry()
  entry.connect("activate", on_entry_activate)
  vbox.pack_start(entry, False, False, 6)
  defbox = Gdict.Defbox()
  ctx = WikiContext()
  defbox.set_context(ctx)
  vbox.pack_start(defbox, True, True, 6)
  win.add(vbox)
  win.connect("delete-event", Gtk.main_quit)
  win.show_all()
  Gtk.main()
