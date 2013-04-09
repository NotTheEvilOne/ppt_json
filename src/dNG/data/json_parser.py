# -*- coding: utf-8 -*-
##j## BOF

"""
JSON (JavaScript Object Notation) is the easiest way to use transfer data
with JavaScript applications.
"""
"""n// NOTE
----------------------------------------------------------------------------
JSON.py
JSON parser abstraction layer
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?php;json

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pyJsonVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

import json, re

try: _unicode_object = { "type": unicode,"str": unicode.encode }
except: _unicode_object = { "type": bytes,"str": bytes.decode }

class direct_json_parser(object):
#
	"""
This class provides a bridge between PHP and JSON to read JSON on the fly.

:author:    direct Netware Group
:copyright: (C) direct Netware Group - All rights reserved
:package:   JSON.py
:since:     v0.1.00
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	INTERNAL = 1
	"""
Use internal parser for JSON operations
	"""
	NATIVE = 2
	"""
Use native Python functions for JSON operations
	"""

	RE_ESCAPED = re.compile("([\\\]+)$")
	"""
RegExp to find escape characters
	"""
	RE_NODE_NUMBER = re.compile("^(.+?)\\#(\\d+)$")
	"""
RegExp to find node names with a specified position in a list
	"""

	def __init__(self, parse_only = True, struct_type = dict, event_handler = None):
	#
		"""
Constructor __init__(direct_json_parser)

:param parse_only: Parse data only
:param struct_type: Dict implementation for new struct elements
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		if (event_handler != None): event_handler.debug("#echo(__FILEPATH__)# -json.__init__()- (#echo(__LINE__)#)")

		self.data = None
		"""
JSON data
		"""
		self.data_cache_node = ""
		"""
Path of the cached node pointer
		"""
		self.data_cache_ptr = ""
		"""
Reference of the cached node pointer (string if unset)
		"""
		self.data_parse_only = parse_only
		"""
Parse data only
		"""
		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.implementation = 0
		"""
Implementation identifier
		"""
		self.struct_type = struct_type
		"""
Dict implementation used to create new struct elements
		"""

		self.set_implementation()
	#

	def cache_export(self, flush = False):
	#
		"""
Convert the cached JSON PHP data into a JSON string.

:param flush: True to delete the cache content

:return: (str) Result string
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.cache_export(flush)- (#echo(__LINE__)#)")

		if (self.data == None): var_return = ""
		else:
		#
			var_return = self.data2json(self.data)
			if (flush): self.data = None
		#

		return var_return
	#

	def data2json(self, data):
	#
		"""
Builds recursively a valid JSON ouput reflecting the given data.

:param data: Python data

:return: (str) JSON output string
:since:  v0.1.00
		"""

		global _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.data2json(data)- (#echo(__LINE__)#)")

		var_return = ""

		if (self.implementation == direct_json_parser.NATIVE): var_return = json.dumps(data)
		else:
		#
			var_type = type(data)

			if (var_type == bool): var_return = ("true" if (data) else "false")
			elif (isinstance(data, dict)):
			#
				var_return = ""

				if (len(data) > 0):
				#
					for key in data:
					#
						if (var_return != ""): var_return += ","
						var_return += "{0}:{1}".format(self.data2json(str(key)), self.data2json(data[key]))
					#
				#

				var_return = "{{{0}}}".format(var_return)
			#
			elif (isinstance(data, list)):
			#
				var_return = ""

				for key in range(0, len(data)):
				#
					if (var_return != ""): var_return += ","
					var_return += self.data2json(data[key])
				#

				var_return = "[{0}]".format(var_return)
			#
			elif (var_type == float or var_type == int): var_return = str(data)
			elif (var_type == str or var_type == _unicode_object['type']):
			#
				if (var_type == _unicode_object['type']): data = _unicode_object['str'](data,"utf-8")
				data = data.replace('"', '\"')
				data = data.replace("\\", "\\\\")
				data = data.replace("\x08", "\\b")
				data = data.replace("\f", "\\f")
				data = data.replace("\n", "\\n")
				data = data.replace("\r", "\\r")
				data = data.replace("\t", "\\t")
				var_return = '"{0}"'.format(data)
			#
			else: var_return = "null"
		#

		return var_return
	#

	def define_parse_only(self, parse_only = True):
	#
		"""
Changes the object behaviour of deleting cached data after parsing is
completed.

:param parse_only: Parse data only

:return: (bool) Accepted state
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.define_parse_only(parse_only)- (#echo(__LINE__)#)")

		var_type = type(parse_only)

		if ((var_type == bool and parse_only) or (var_type == str and parse_only == "1")): self.data_parse_only = True
		elif (parse_only == None and (not self.data_parse_only)): self.data_parse_only = True
		else: self.data_parse_only = False

		return self.data_parse_only
	#

	def find_string(self, data, end_tag, zone_tag = None):
	#
		"""
Searches the given data for a matching end tag. Sub zone end tags are
ignored.

:param data: Input data
:param end_tag: Ending delimiter
:param zone_tag: Zone start tag for sub zones

:return: (str) Matched data; False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.find_string(data, {0}, zone_tag)- (#echo(__LINE__)#)".format(end_tag))
		var_return = False

		zone_count = 0

		if (zone_tag == None): cache = ""
		else:
		#
			cache = data[0]
			data = data[1:]
		#

		data_list = data.split(end_tag)
		if (zone_tag != None): re_zone_tag = re.compile("([\\\]*){0}".format(re.escape(zone_tag)))

		while (var_return == False and len(data_list) > 0):
		#
			data = data_list.pop(0)

			if (zone_tag != None):
			#
				for result in re_zone_tag.finditer(data):
				#
					if (len(result.group(1)) % 2 == 0): zone_count += 1
				#
			#

			re_result = direct_json_parser.RE_ESCAPED.search(data)

			if (re_result != None and (len(re_result.group(1)) % 2) == 1): cache += data
			elif (len(data_list) > 0):
			#
				if (zone_count):
				#
					cache += data
					zone_count -= 1
				#
				else: var_return = cache + data
			#
			else: cache += data

			if (len(data_list) > 0):
			#
				if (var_return != False and zone_tag != None): var_return += end_tag
				else: cache += end_tag
			#
		#

		return var_return
	#

	def get(self):
	#
		"""
This operation just gives back the content of self.data.

:return: (mixed) JSON data; False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.get()- (#echo(__LINE__)#)")
		return (False if (self.data == None) else self.data)
	#

	def get_implementation(self):
	#
		"""
Returns the parser implementation in use.

:return: (int) Implementation identifier
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.get_implementation()- (#echo(__LINE__)#)")
		return self.implementation
	#

	def json2data(self, data):
	#
		"""
Converts JSON data into the corresponding PHP data ...

:param data: Input JSON data

:return: (mixed) JSON data; None on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.json2data(data)- (#echo(__LINE__)#)")

		if (type(data) == _unicode_object['type']): data = _unicode_object['str'](data,"utf-8")
		data = data.strip()

		if (self.implementation == direct_json_parser.NATIVE):
		#
			try: var_return = json.loads(data)
			except: var_return = None
		#
		else:
		#
			var_return = None

			if (data[0] == "{"): var_return = self.json2data_walker(data[1:], "}")
			elif (data[0] == "["): var_return = self.json2data_walker(data[1:], "]")
		#

		if (var_return and (not self.data_parse_only)): self.data = var_return
		return var_return
	#

	def json2data_walker(self, data, end_tag = ""):
	#
		"""
Converts JSON data recursively into the corresponding PHP data ...

:param data: Input JSON data
:param end_tag: Ending delimiter

:access: protected
:return: (mixed) JSON data; False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.json2data_walker(data, end_tag)- (#echo(__LINE__)#)")
		var_return = None

		data = data.strip()

		if (end_tag == "]"):
		#
			var_return = [ ]

			while (len(data) > 0 and var_return != None):
			#
				if (data[0] == "{"): data_part = self.find_string(data, "}", "{")
				elif (data[0] == "["): data_part = self.find_string(data, "]", "[")
				else: data_part = self.find_string(data, ",")

				if (data_part == False): data_part = self.find_string(data, "]")

				if (data_part != False):
				#
					data = data[len(data_part) + 1:].strip()

					if (len(data_part) > 0):
					#
						if (data_part[0] == "{"): var_return.append(self.json2data_walker(data_part[1:], "}"))
						elif (data_part[0] == "["): var_return.append(self.json2data_walker(data_part[1:], "]"))
						else: var_return.append(self.json2data_walker(data_part))
					#
				#
				elif (len(data) > 0 and data != "]"): data = None
				else: data = ""
			#
		#
		elif (end_tag == "}"):
		#
			var_return = self.struct_type()

			while (len(data) > 0 and var_return != None):
			#
				if (data == "}"): data = ""
				else:
				#
					if (data[0] == ","): data = data[1:].strip()

					if (data[0] == '"'): key_string_tag = '"'
					elif (data[0] == "'"): key_string_tag = "'"
					else: key_string_tag = None

					key = False

					if (key_string_tag != None):
					#
						key = self.find_string(data[1:], key_string_tag)
						if (key != False): data = data[len(key) + 2:].strip()
					#

					if (key != False and len(key) > 0 and len(data) > 1 and data[0] == ":"):
					#
						data = data[1:].strip()

						if (data[0] == "{"): data_part = self.find_string(data, "}", "{")
						elif (data[0] == "["): data_part = self.find_string(data, "]", "[")
						else: data_part = self.find_string(data, ",")

						if (data_part == False): data_part = self.find_string(data, "}")

						if (data_part != False):
						#
							data = data[len(data_part):].strip()

							if (len(data_part) > 0):
							#
								if (data_part[0] == "{"): var_return[key] = self.json2data_walker(data_part[1:], "}")
								elif (data_part[0] == "["): var_return[key] = self.json2data_walker(data_part[1:], "]")
								else: var_return[key] = self.json2data_walker(data_part)
							#
						#
						elif (len(data) > 0 and data != "}"): data = None
						else: data = ""
					#
					else: var_return = None
				#
			#
		#
		elif (data == "true"): var_return = True
		elif (data == "false"): var_return = False
		elif (len(data) > 0 and data != "null"):
		#
			if (data[0] == '"'): value_string_tag = '"'
			elif (data[0] == "'"): value_string_tag = "'"
			else: value_string_tag = None

			if (value_string_tag == None):
			# 
				try: var_return = int(data)
				except ValueError: pass

				if (var_return == None):
				#
					try: var_return = float(data)
					except ValueError: pass
				#
			#
			else:
			#
				var_return = self.find_string(data[1:], value_string_tag)

				if (var_return == False): var_return = None
				else:
				#
					var_return = var_return.replace('\"', '"')
					var_return = var_return.replace("\\\\", "\\")
					var_return = var_return.replace("\\b", "\x08")
					var_return = var_return.replace("\\f", "\f")
					var_return = var_return.replace("\\n", "\n")
					var_return = var_return.replace("\\r", "\r")
					var_return = var_return.replace("\\t", "\t")
				#
			#
		#

		return var_return
	#

	def node_add(self, node_path, data):
	#
		"""
Adds a node with content. Recursion is not supported because both arrays
or objects are possible for numeric path definitions.

:param node_path: Path to the new node - delimiter is space
:param data: Data for the new node

:return: (bool) False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_add(node_path, data)- (#echo(__LINE__)#)".format(node_path))

		if (self.data == None): self.data = self.struct_type()
		return self.node_change(node_path, data, True)
	#

	def node_change(self, node_path, data, add = False):
	#
		"""
Change the content of a specified node.

:param node_path: Path to the new node - delimiter is space
:param data: Data for the new node
:param add: Add an undefined node

:return: (bool) False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path,"utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_change({0}, data, add)- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			node_path_list = node_path.split(" ")

			if (len(node_path_list) > 1 or direct_json_parser.RE_NODE_NUMBER.match(node_path)):
			#
				node_name = node_path_list.pop()
				re_result = direct_json_parser.RE_NODE_NUMBER.match(node_name)

				if (re_result != None and self.node_count(re_result.group(0))):
				#
					node_path = re_result.group(1)
					node_name = re_result.group(2)
				#
				else: node_path = node_path_list.join(" ")

				node_ptr = self.node_get_ptr(node_path)

				if (len(self.data_cache_node) > 0 and node_path.find(self.data_cache_node) == 0):
				#
					self.data_cache_node = ""
					self.data_cache_ptr = self.data
				#
			#
			else:
			#
				node_name = node_path
				node_ptr = self.data

				self.data_cache_node = ""
				self.data_cache_ptr = self.data
			#

			if ((isinstance(node_ptr, dict) or type(node_ptr) == list) and (add or node_name in node_ptr)):
			#
				node_ptr[node_name] = data
				var_return = True
			#
		#

		return var_return
	#

	def node_count(self, node_path):
	#
		"""
Count the occurrence of a specified node.

:param node_path: Path to the node - delimiter is space

:return: (int) Counted number off matching nodes
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path,"utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_count({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = 0

		if (type(node_path) == str):
		#
			"""
Get the parent node of the target.
			"""

			if (" " in node_path): node_ptr = self.node_get_ptr(node_path)
			else: node_ptr = self.data

			if (node_ptr != False):
			#
				if (isinstance(node_ptr, dict) or type(node_ptr) == list): var_return = len(node_ptr)
				else: var_return = 1
			#
		#

		return var_return
	#

	def node_get(self, node_path):
	#
		"""
Read a specified node including all children if applicable.

:param node_path: Path to the node - delimiter is space

:return: (mixed) JSON data; False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path,"utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_get({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			node_ptr = self.node_get_ptr(node_path)
			if (node_ptr != False): var_return = node_ptr.copy()
		#

		return var_return
	#

	def node_get_ptr(self, node_path):
	#
		"""
Returns the pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:access: protected
:return: (dict) JSON tree element; False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_get_ptr({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			if (len(self.data_cache_node) > 0 and node_path[:len(self.data_cache_node)].lower() == self.data_cache_node.lower()):
			#
				node_path = node_path[len(self.data_cache_node):].strip()
				node_ptr = self.data_cache_ptr
			#
			else: node_ptr = self.data

			is_valid = True
			node_path_list = (node_path.split(" ") if (len(node_path) > 0) else [ ])

			while (is_valid and len(node_path_list) > 0):
			#
				is_valid = False
				node_name = node_path_list.pop(0)

				if (isinstance(node_ptr, dict) or type(node_ptr) == list):
				#
					re_result = direct_json_parser.RE_NODE_NUMBER.match(node_path)

					if (node_name in node_ptr):
					#
						is_valid = True
						node_ptr = node_ptr[node_name]
					#
					elif (re_result != None):
					#
						node_name = re_result.group(1)
						node_path_list.insert(0, re_result.group(2))

						if (node_name in node_ptr):
						#
							is_valid = True
							node_ptr = node_ptr[node_name]
						#
					#
				#
			#

			if (is_valid): var_return = node_ptr
		#

		return var_return
	#

	def node_remove(self, node_path):
	#
		"""
Remove a node and all children if applicable.

:param node_path: Path to the node - delimiter is space

:return: (bool) False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path,"utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_remove({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			"""
Get the parent node of the target.
			"""

			node_path_list = node_path.split(" ")

			if (len(node_path_list) > 1 or direct_json_parser.RE_NODE_NUMBER.match(node_path)):
			#
				node_name = node_path_list.pop()
				re_result = direct_json_parser.RE_NODE_NUMBER.match(node_name)

				if (re_result != None and self.node_count(re_result.group(0))):
				#
					node_path = re_result.group(1)
					node_name = re_result.group(2)
				#
				else: node_path = node_path_list.join(" ")

				node_ptr = self.node_get_ptr(node_path)

				if (len(self.data_cache_node) > 0 and node_path[:len(self.data_cache_node)] == self.data_cache_node):
				#
					self.data_cache_node = ""
					self.data_cache_ptr = self.data
				#
			#
			else:
			#
				node_name = node_path
				node_ptr = self.data

				self.data_cache_node = ""
				self.data_cache_ptr = self.data
			#

			if ((isinstance(node_ptr, dict) or type(node_ptr) == list) and node_name in node_ptr):
			#
				del(node_ptr[node_name])
				var_return = True
			#
		#

		return var_return
	#

	def node_set_cache_path(self, node_path):
	#
		"""
Set the cache pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (bool) True on success
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path,"utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.node_set_cache_path({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			if (node_path == self.data_cache_node): var_return = True
			else:
			#
				node_ptr = self.node_get_ptr(node_path)

				if (node_ptr != False):
				#
					self.data_cache_node = node_path
					self.data_cache_ptr = node_ptr
					var_return = True
				#
			#
		#

		return var_return
	#

	def set(self, json, overwrite = False):
	#
		"""
"Imports" PHP JSON data into the cache.

:param json: Input array
:param overwrite: True to overwrite the current (non-empty) cache

:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.set(json, overwrite)- (#echo(__LINE__)#)")
		var_return = False

		if ((self.data == None or overwrite) and (isinstance(json, dict) or type(json) == list)):
		#
			self.data = json
			var_return = True
		#

		return var_return
	#

	def set_event_handler(self, event_handler):
	#
		"""
Sets the EventHandler.

:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		if (event_handler != None): event_handler.debug("#echo(__FILEPATH__)# -json.set_event_handler(event_handler)- (#echo(__LINE__)#)")
		self.event_handler = event_handler
	#

	def set_implementation(self, implementation = None):
	#
		"""
Set the parser implementation to use.

:param implementation: Implementation identifier

:since: v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -json.set_implementation(implementation)- (#echo(__LINE__)#)")

		if (implementation == None and self.struct_type == dict): self.implementation = direct_json_parser.NATIVE
		elif (implementation == direct_json_parser.NATIVE and self.struct_type == dict): self.implementation = direct_json_parser.NATIVE
		else: self.implementation = direct_json_parser.INTERNAL
	#
#

##j## EOF