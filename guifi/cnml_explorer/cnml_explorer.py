#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# cnml_explorer.py - Explore your free network offline! - 21-August-2011
# Copyright (C) 2011 Pablo Castellano <pablo@anche.no>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import xml.dom.minidom as MD
import sys


class CNMLExplorer:
	def __init__(self, cnmlFile="detail"):
		self.ui = gtk.Builder()
		self.ui.add_from_file("cnml_explorer.ui")
		self.ui.connect_signals(self)

		self.window = self.ui.get_object("window1")
		self.treestore = self.ui.get_object("treestore1")
		self.treeview = self.ui.get_object("treeview1")
		self.statusbar = self.ui.get_object("statusbar1")

		self.about_ui = self.ui.get_object("aboutdialog1")
		with open("COPYING") as f:
			self.about_ui.set_license(f.read())

		self.completaArbol(cnmlFile)


	def completaArbol(self, cnmlFile):
		try:
			tree = MD.parse(cnmlFile)
		except IOError:
			self.cnml = None
			self.statusbar.push(0, "CNML file \"%s\" couldn't be loaded" %cnmlFile)
			return

		zones = tree.getElementsByTagName("zone")
		parent = [None]

		n_nodes = 0

		# Bug: no se muestran nodos de la primera zona
		# Lo suyo sería una función que te devolviera los nodos del primer nivel solamente
		for z in zones:
			n_subzones = len(z.getElementsByTagName("zone"))
			nodes = z.getElementsByTagName("node")
			(w, b, t, p) = self.countNodes(nodes)

			col1 = "%s (%d)" %(z.getAttribute("title"), len(nodes))
			p = self.treestore.append(parent[-1], (col1, w, b, t, p, None))

			# Add zone
			if n_subzones > 0:
				parent.append(p)
			else:
				# Add nodes
				for n in nodes:
					self.treestore.append(p, (None, None, None, None, None, n.getAttribute("title")))
					n_nodes += 1

		self.treeview.expand_all()
		self.statusbar.push(0, "Cargadas %d zonas con %d nodos en total." %(len(zones), n_nodes))
		self.cnml = cnmlFile

	def countNodes(self, nodes):
		n_planned = 0
		n_working = 0
		n_testing = 0
		n_building = 0

		for n in nodes:
			st = n.getAttribute("status")

			if st == "Planned":
				n_planned += 1
			elif st == "Working":
				n_working += 1
			elif st == "Testing":
				n_testing += 1
			elif st == "Building":
				n_building += 1
			else:
				print "Unknown node status:", st

		# Working, Building, Testing, Planned.
		return (n_working, n_building, n_testing, n_planned)


	def on_aboutdialog1_close(self, widget, data=None):
		self.about_ui.hide()

	def on_imagemenuitem10_activate(self, widget, data=None):
		self.about_ui.show()

	def gtk_main_quit(self, widget, data=None):
		gtk.main_quit()


if __name__ == "__main__":

	if len(sys.argv) > 1:
		ui = CNMLExplorer(sys.argv[1])
	else:
		ui = CNMLExplorer()

	ui.window.show()
	gtk.main()