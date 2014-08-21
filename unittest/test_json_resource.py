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

from os import path
import sys
import unittest

from dNG.data.json_resource import JsonResource

class TestJsonResource(unittest.TestCase):
#
	"""
Unittest for dNG.data.JsonResource

:since: v0.1.00
	"""

	def _get_json_test_data(self):
	#
		"""
Test data with a simple string and a nested list of content.

:return: (str) Test data
		"""

		return """
{
"hello": "world",
"more_complex": [ "this", "that", true, 1 ]
}
		"""
	#

	def test_internal(self):
	#
		"""
Tests the internal JSON parser implementation.
		"""

		json_resource = JsonResource()
		json_resource.set_implementation(JsonResource.IMPLEMENTATION_INTERNAL)
		json_data = json_resource.json_to_data(self._get_json_test_data())

		self.assertTrue(json_data != None)

		self.assertTrue("hello" in json_data)
		self.assertEqual("world", json_data['hello'])

		self.assertTrue("more_complex" in json_data)
		self.assertEqual([ "this", "that", True, 1 ], json_data['more_complex'])
	#

	def test_native(self):
	#
		"""
Tests the native JSON Python parser.
		"""

		json_resource = JsonResource()
		json_data = json_resource.json_to_data(self._get_json_test_data())

		self.assertTrue(json_data != None)

		self.assertTrue("hello" in json_data)
		self.assertEqual("world", json_data['hello'])

		self.assertTrue("more_complex" in json_data)
		self.assertEqual([ "this", "that", True, 1 ], json_data['more_complex'])
	#

	def test_position_change(self):
	#
		"""
Tests a change to a positional entry.
		"""

		json_resource = JsonResource(parse_only = False)
		json_resource.json_to_data(self._get_json_test_data())

		self.assertEqual("world", json_resource.get_node("hello"))
		self.assertEqual("that", json_resource.get_node("more_complex#1"))

		self.assertTrue(json_resource.change_node("more_complex#1", "test"))
		self.assertEqual("test", json_resource.get_node("more_complex#1"))

		json_resource.set_cached_node("more_complex#1")
		self.assertTrue(json_resource.change_node("more_complex#1", { "some": "unittests", "never": "work" }))
		self.assertEqual("work", json_resource.get_node("more_complex#1 never"))

		json_resource.set_cached_node("more_complex#1 never")
		self.assertTrue(json_resource.change_node("more_complex#1 never", "work but sometimes they do"))
		self.assertEqual("work but sometimes they do", json_resource.get_node("more_complex#1 never"))
	#
#

if (__name__ == "__main__"):
#
	sys.path.append(path.normpath("../src"))
	unittest.main()
#

##j## EOF