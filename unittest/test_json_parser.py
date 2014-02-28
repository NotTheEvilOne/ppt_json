# -*- coding: utf-8 -*-
##j## BOF

"""
JSON.py
JSON parser abstraction layer
"""
"""n// NOTE
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?py;json

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

from os import path
import sys
import unittest

from dNG.data.json_parser import JsonParser

class TestJsonParser(unittest.TestCase):
#
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

		json_parser = JsonParser()
		json_parser.set_implementation(JsonParser.IMPLEMENTATION_INTERNAL)
		json_data = json_parser.json_to_data(self._get_json_test_data())

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

		json_parser = JsonParser()
		json_data = json_parser.json_to_data(self._get_json_test_data())

		self.assertTrue(json_data != None)

		self.assertTrue("hello" in json_data)
		self.assertEqual("world", json_data['hello'])

		self.assertTrue("more_complex" in json_data)
		self.assertEqual([ "this", "that", True, 1 ], json_data['more_complex'])
	#
#

if (__name__ == "__main__"):
#
	sys.path.append(path.normpath("../src"))
	unittest.main()
#

##j## EOF