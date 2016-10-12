# -*- coding: utf-8 -*-
##j## BOF

"""
JSON.py
JSON parser abstraction layer
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?py;json

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pyJsonVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=invalid-name,undefined-variable

from copy import copy
import json
import re

try:
#
	_PY_STR = unicode.encode
	_PY_UNICODE_TYPE = unicode
#
except NameError:
#
	_PY_STR = bytes.decode
	_PY_UNICODE_TYPE = str
#

class JsonResource(object):
#
	"""
This class provides a bridge between Python and JSON to read JSON on the
fly.

:author:    direct Netware Group
:copyright: (C) direct Netware Group - All rights reserved
:package:   JSON.py
:since:     v0.1.00
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	IMPLEMENTATION_INTERNAL = 1
	"""
Use internal parser for JSON operations
	"""
	IMPLEMENTATION_NATIVE = 2
	"""
Use native Python functions for JSON operations
	"""

	RE_ESCAPED = re.compile("(\\\\+)$")
	"""
RegExp to find escape characters
	"""
	RE_NODE_POSITION = re.compile("^(.+)\\#(\\d+)$")
	"""
RegExp to find node names with a specified position in a list
	"""

	def __init__(self, parse_only = True, struct_type = dict, event_handler = None):
	#
		"""
Constructor __init__(JsonResource)

:param parse_only: Parse data only
:param struct_type: Dict implementation for new struct elements
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

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

	def add_node(self, node_path, data):
	#
		"""
Adds a node with content. Recursion is not supported because both arrays
or objects are possible for numeric path definitions.

:param node_path: Path to the new node - delimiter is space
:param data: Data for the new node

:return: (bool) False on error
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.add_node()- (#echo(__LINE__)#)".format(node_path))

		if (self.data is None): self.data = self.struct_type()
		return self.change_node(node_path, data, True)
	#

	def change_node(self, node_path, data, add = False):
	#
		"""
Change the content of a specified node.

:param node_path: Path to the new node - delimiter is space
:param data: Data for the new node
:param add: Add an undefined node

:return: (bool) False on error
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path,"utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.change_node({0})- (#echo(__LINE__)#)".format(node_path))
		_return = False

		if (type(node_path) is str):
		#
			"""
Get the parent node of the target.
			"""

			node_path_list = node_path.split(" ")

			node_path_count = len(node_path_list)
			node_name = (node_path if (node_path_count < 2) else None)

			if (node_path_count > 1 or JsonResource.RE_NODE_POSITION.match(node_path)):
			#
				if (node_path_count > 1):
				#
					node_name = node_path_list.pop()
					node_path = " ".join(node_path_list)

					node_ptr = self._get_node_ptr(node_path)
				#
				else:
				#
					node_path = ""
					node_ptr = self._get_node_ptr(JsonResource.RE_NODE_POSITION.match(node_name).group(1))
				#
			#
			else:
			#
				node_path = ""
				node_ptr = self.data
			#

			"""
Change the node
			"""

			re_result = JsonResource.RE_NODE_POSITION.match(node_name)

			if (re_result is None): node_position = -1
			else:
			#
				node_name = re_result.group(1)
				node_position = int(re_result.group(2))
			#

			if (isinstance(node_ptr, dict) and node_name in node_ptr):
			#
				node_ptr[node_name] = data
				_return = True

				if (self.data_cache_node != ""):
				#
					node_path_changed = ("{0} {1}".format(node_path, node_name) if (len(node_path) > 0) else node_name)
					if (self.data_cache_node == node_path_changed): self.data_cache_ptr = node_ptr[node_name]
				#
			#
			elif (isinstance(node_ptr, list) and node_position >= 0 and node_position < len(node_ptr)):
			#
				node_ptr[node_position] = data
				_return = True

				if (self.data_cache_node != ""):
				#
					node_path_changed = ("{0} {1}".format(node_path, node_name) if (len(node_path) > 0) else node_name)
					node_path_changed += "#{0:d}".format(node_position)

					if (self.data_cache_node == node_path_changed): self.data_cache_ptr = node_ptr[node_position]
				#
			#
		#

		return _return
	#

	def count_node(self, node_path):
	#
		"""
Count the occurrence of a specified node.

:param node_path: Path to the node - delimiter is space

:return: (int) Counted number off matching nodes
:since:  v0.1.00
		"""

		# global:  _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path,"utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.count_node({0})- (#echo(__LINE__)#)".format(node_path))
		_return = 0

		if (type(node_path) is str):
		#
			"""
Get the parent node of the target.
			"""

			node_ptr = (self._get_node_ptr(node_path) if (" " in node_path) else self.data)

			if (node_ptr is not None):
			#
				_return = (len(node_ptr) if (isinstance(node_ptr, dict) or type(node_ptr) is list) else 1)
			#
		#

		return _return
	#

	def data_to_json(self, data):
	#
		"""
Builds recursively a valid JSON ouput reflecting the given data.

:param data: Python data

:return: (str) JSON output string
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.data_to_json()- (#echo(__LINE__)#)")

		_return = ""

		if (self.implementation == JsonResource.IMPLEMENTATION_NATIVE): _return = json.dumps(data)
		else:
		#
			_type = type(data)

			if (_type is bool): _return = ("true" if (data) else "false")
			elif (isinstance(data, dict)):
			#
				_return = ""

				if (len(data) > 0):
				#
					for key in data:
					#
						if (_return != ""): _return += ","
						_return += "{0}:{1}".format(self.data_to_json(str(key)), self.data_to_json(data[key]))
					#
				#

				_return = "{{{0}}}".format(_return)
			#
			elif (isinstance(data, list)):
			#
				_return = ""

				for key in range(0, len(data)):
				#
					if (_return != ""): _return += ","
					_return += self.data_to_json(data[key])
				#

				_return = "[{0}]".format(_return)
			#
			elif (_type in ( float, int )): _return = str(data)
			elif (_type in ( str, _PY_UNICODE_TYPE )):
			#
				if (str != _PY_UNICODE_TYPE and _type == _PY_UNICODE_TYPE): data = _PY_STR(data,"utf-8")
				data = data.replace('"', '\"')
				data = data.replace("\\", "\\\\")
				data = data.replace("\x08", "\\b")
				data = data.replace("\f", "\\f")
				data = data.replace("\n", "\\n")
				data = data.replace("\r", "\\r")
				data = data.replace("\t", "\\t")
				_return = '"{0}"'.format(data)
			#
			else: _return = "null"
		#

		return _return
	#

	def export_cache(self, flush = False):
	#
		"""
Convert the cached JSON PHP data into a JSON string.

:param flush: True to delete the cache content

:return: (str) Result string
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.export_cache()- (#echo(__LINE__)#)")

		if (self.data is None): _return = ""
		else:
		#
			_return = self.data_to_json(self.data)
			if (flush): self.data = None
		#

		return _return
	#

	def get(self):
	#
		"""
This operation just gives back the content of self.data.

:return: (mixed) JSON data; None if not parsed
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.get()- (#echo(__LINE__)#)")
		return self.data
	#

	def get_implementation(self):
	#
		"""
Returns the parser implementation in use.

:return: (int) Implementation identifier
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.get_implementation()- (#echo(__LINE__)#)")
		return self.implementation
	#

	def get_node(self, node_path):
	#
		"""
Read a specified node including all children if applicable.

:param node_path: Path to the node - delimiter is space

:return: (mixed) JSON data; None on error
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path,"utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.get_node({0})- (#echo(__LINE__)#)".format(node_path))
		_return = None

		if (type(node_path) is str):
		#
			node_ptr = self._get_node_ptr(node_path)
			if (node_ptr is not None): _return = (node_ptr.copy() if (type(node_ptr) is dict) else node_ptr)
		#

		return _return
	#

	def _get_node_ptr(self, node_path):
	#
		"""
Returns the pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (dict) JSON tree element; None on error
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json._get_node_ptr({0})- (#echo(__LINE__)#)".format(node_path))
		_return = None

		if (type(node_path) is str):
		#
			if (self.data_cache_node != ""
			    and node_path[:len(self.data_cache_node)].lower() == self.data_cache_node.lower()
			   ):
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

				re_result = JsonResource.RE_NODE_POSITION.match(node_name)

				if (re_result is None): node_position = -1
				else:
				#
					node_name = re_result.group(1)
					node_position = int(re_result.group(2))
				#

				if (isinstance(node_ptr, dict)):
				#
					if (node_name in node_ptr):
					#
						is_valid = True
						node_ptr = node_ptr[node_name]
					#
				#

				if (node_position >= 0 and isinstance(node_ptr, list) and node_position < len(node_ptr)):
				#
					is_valid = True
					node_ptr = node_ptr[node_position]
				#
			#

			if (is_valid): _return = node_ptr
		#

		return _return
	#

	def json_to_data(self, data):
	#
		"""
Converts JSON data into a Python representation.

:param data: Input JSON data

:return: (mixed) JSON data; None on error
:since:  v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.json_to_data()- (#echo(__LINE__)#)")

		try:
		#
			self.parse(data)
			_return = (self.data.copy() if (hasattr(self.data, "copy")) else copy(self.data))
		#
		except Exception: _return = None

		if (not self.data_parse_only): self.data = None

		return _return
	#

	def _json_to_data_walker(self, data, end_tag = ""):
	#
		"""
Converts JSON data recursively into the corresponding PHP data ...

:param data: Input JSON data
:param end_tag: Ending delimiter

:return: (mixed) JSON data; None on error
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json._json_to_data_walker()- (#echo(__LINE__)#)")
		_return = None

		data = data.strip()

		if (end_tag == "]"):
		#
			_return = [ ]

			while (len(data) > 0):
			#
				if (data[0] == "{"): data_part = JsonResource._find_string(data, "}", "{")
				elif (data[0] == "["): data_part = JsonResource._find_string(data, "]", "[")
				else: data_part = JsonResource._find_string(data, ",")

				if (data_part is None): data_part = JsonResource._find_string(data, "]")

				if (data_part is not None):
				#
					data = data[len(data_part) + 1:].strip()

					if (len(data_part) > 0):
					#
						if (data_part[0] == "{"): _return.append(self._json_to_data_walker(data_part[1:], "}"))
						elif (data_part[0] == "["): _return.append(self._json_to_data_walker(data_part[1:], "]"))
						else: _return.append(self._json_to_data_walker(data_part))
					#
				#
				else:
				#
					if (len(data) > 0 and data != "]"): _return = None
					break
				#
			#
		#
		elif (end_tag == "}"):
		#
			_return = self.struct_type()

			while (len(data) > 0):
			#
				if (data == "}"): break
				else:
				#
					if (data[0] == ","): data = data[1:].strip()

					if (data[0] == '"'): key_string_tag = '"'
					elif (data[0] == "'"): key_string_tag = "'"
					else: key_string_tag = None

					key = False

					if (key_string_tag is not None):
					#
						key = JsonResource._find_string(data[1:], key_string_tag)
						if (key is not None): data = data[len(key) + 2:].strip()
					#

					if (key != False and len(key) > 0 and len(data) > 1 and data[0] == ":"):
					#
						data = data[1:].strip()

						if (data[0] == "{"): data_part = JsonResource._find_string(data, "}", "{")
						elif (data[0] == "["): data_part = JsonResource._find_string(data, "]", "[")
						else: data_part = JsonResource._find_string(data, ",")

						if (data_part is None): data_part = JsonResource._find_string(data, "}")

						if (data_part is not None):
						#
							data = data[len(data_part):].strip()

							if (len(data_part) > 0):
							#
								if (data_part[0] == "{"): _return[key] = self._json_to_data_walker(data_part[1:], "}")
								elif (data_part[0] == "["): _return[key] = self._json_to_data_walker(data_part[1:], "]")
								else: _return[key] = self._json_to_data_walker(data_part)
							#
						#
						elif (len(data) > 0 and data != "}"): data = None
						else: data = ""
					#
					else:
					#
						_return = None
						break
					#
				#
			#
		#
		elif (data == "true"): _return = True
		elif (data == "false"): _return = False
		elif (len(data) > 0 and data != "null"):
		#
			if (data[0] == '"'): value_string_tag = '"'
			elif (data[0] == "'"): value_string_tag = "'"
			else: value_string_tag = None

			if (value_string_tag is None):
			#
				try: _return = int(data)
				except ValueError: pass

				if (_return is None):
				#
					try: _return = float(data)
					except ValueError: pass
				#
			#
			else:
			#
				_return = JsonResource._find_string(data[1:], value_string_tag)

				if (_return is not None):
				#
					_return = _return.replace('\"', '"')
					_return = _return.replace("\\\\", "\\")
					_return = _return.replace("\\b", "\x08")
					_return = _return.replace("\\f", "\f")
					_return = _return.replace("\\n", "\n")
					_return = _return.replace("\\r", "\r")
					_return = _return.replace("\\t", "\t")
				#
			#
		#

		return _return
	#

	def parse(self, data):
	#
		"""
Parses the given JSON data.

:param data: Input JSON data

:since: v0.1.03
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.parse()- (#echo(__LINE__)#)")

		if (str is not _PY_UNICODE_TYPE and type(data) is _PY_UNICODE_TYPE): data = _PY_STR(data,"utf-8")
		data = data.strip()

		if (self.implementation == JsonResource.IMPLEMENTATION_NATIVE): self.data = json.loads(data)
		elif (data[0] == "{"): self.data = self._json_to_data_walker(data[1:], "}")
		elif (data[0] == "["): self.data = self._json_to_data_walker(data[1:], "]")
		else: self.data = None
	#

	def remove_node(self, node_path):
	#
		"""
Remove a node and all children if applicable.

:param node_path: Path to the node - delimiter is space

:return: (bool) False on error
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path,"utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.remove_node({0})- (#echo(__LINE__)#)".format(node_path))
		_return = False

		if (type(node_path) is str):
		#
			"""
Get the parent node of the target.
			"""

			node_path_list = node_path.split(" ")

			node_path_count = len(node_path_list)
			node_name = (node_path if (node_path_count < 2) else None)

			if (node_path_count > 1 or JsonResource.RE_NODE_POSITION.match(node_path)):
			#
				if (node_path_count > 1):
				#
					node_name = node_path_list.pop()
					node_ptr = self._get_node_ptr(" ".join(node_path_list))
				#
				else: node_ptr = self._get_node_ptr(JsonResource.RE_NODE_POSITION.match(node_name).group(1))

				if (self.data_cache_node != "" and node_path[:len(self.data_cache_node)] == self.data_cache_node):
				#
					self.data_cache_node = ""
					self.data_cache_ptr = self.data
				#
			#
			else:
			#
				node_ptr = self.data

				self.data_cache_node = ""
				self.data_cache_ptr = self.data
			#

			"""
Delete the node
			"""

			re_result = JsonResource.RE_NODE_POSITION.match(node_name)

			if (re_result is None): node_position = -1
			else:
			#
				node_name = re_result.group(1)
				node_position = int(re_result.group(2))
			#

			if (isinstance(node_ptr, dict) and node_name in node_ptr):
			#
				del(node_ptr[node_name])
				_return = True
			#
			elif (isinstance(node_ptr, list) and node_position >= 0 and node_position < len(node_ptr)):
			#
				del(node_ptr[node_position])
				_return = True
			#
		#

		return _return
	#

	def set(self, _json, overwrite = False):
	#
		"""
"Imports" PHP JSON data into the cache.

:param _json: Input array
:param overwrite: True to overwrite the current (non-empty) cache

:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.set()- (#echo(__LINE__)#)")
		_return = False

		if ((self.data is None or overwrite) and (isinstance(_json, dict) or type(_json) is list)):
		#
			self.data = _json
			_return = True
		#

		return _return
	#

	def set_cached_node(self, node_path):
	#
		"""
Set the cache pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (bool) True on success
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path,"utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.set_cached_node({0})- (#echo(__LINE__)#)".format(node_path))
		_return = False

		if (type(node_path) is str):
		#
			if (node_path == self.data_cache_node): _return = True
			else:
			#
				node_ptr = self._get_node_ptr(node_path)

				if (node_ptr is not None):
				#
					self.data_cache_node = node_path
					self.data_cache_ptr = node_ptr
					_return = True
				#
			#
		#

		return _return
	#

	def set_event_handler(self, event_handler):
	#
		"""
Sets the EventHandler.

:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		self.event_handler = event_handler
	#

	def set_implementation(self, implementation = None):
	#
		"""
Set the parser implementation to use.

:param implementation: Implementation identifier

:since: v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.set_implementation()- (#echo(__LINE__)#)")

		if (implementation is None and self.struct_type == dict): self.implementation = JsonResource.IMPLEMENTATION_NATIVE
		elif (implementation == JsonResource.IMPLEMENTATION_NATIVE and self.struct_type == dict):
		#
			self.implementation = JsonResource.IMPLEMENTATION_NATIVE
		#
		else: self.implementation = JsonResource.IMPLEMENTATION_INTERNAL
	#

	def set_parse_only(self, parse_only = True):
	#
		"""
Changes the object behaviour of deleting cached data after parsing is
completed.

:param parse_only: Parse data only

:since: v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -json.set_parse_only()- (#echo(__LINE__)#)")

		_type = type(parse_only)

		if ((_type is bool and parse_only) or (_type is str and parse_only == "1")): self.data_parse_only = True
		elif (parse_only is None and (not self.data_parse_only)): self.data_parse_only = True
		else: self.data_parse_only = False
	#

	@staticmethod
	def _find_string(data, end_tag, zone_tag = None):
	#
		"""
Searches the given data for a matching end tag. Sub zone end tags are
ignored.

:param data: Input data
:param end_tag: Ending delimiter
:param zone_tag: Zone start tag for sub zones

:return: (str) Matched data; None if not found
:since:  v0.1.00
		"""

		_return = None

		zone_count = 0

		if (zone_tag is None): cache = ""
		else:
		#
			cache = data[0]
			data = data[1:]
		#

		data_list = data.split(end_tag)
		if (zone_tag is not None): re_zone_tag = re.compile("([\\\\]*){0}".format(re.escape(zone_tag)))

		while (_return is None and len(data_list) > 0):
		#
			data = data_list.pop(0)

			if (zone_tag is not None):
			#
				for result in re_zone_tag.finditer(data):
				#
					if (len(result.group(1)) % 2 == 0): zone_count += 1
				#
			#

			re_result = JsonResource.RE_ESCAPED.search(data)

			if (re_result is not None and (len(re_result.group(1)) % 2) == 1): cache += data
			elif (len(data_list) > 0):
			#
				if (zone_count):
				#
					cache += data
					zone_count -= 1
				#
				else: _return = cache + data
			#
			else: cache += data

			if (len(data_list) > 0):
			#
				if (_return is not None and zone_tag is not None): _return += end_tag
				else: cache += end_tag
			#
		#

		return _return
	#
#

##j## EOF