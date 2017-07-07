#! /usr/bin/env python

'''
@author: Kamil Karczewski
'''

import os
import sys
import argparse
try:
   from lxml import etree
except ImportError as e:
   print(e)
   print("There is no lxml installation.")

def get_element(path, xpath):
   '''
   @path - path to xml file
   @xpath - xpath to element in xml tree
   Common function. Get xml file from path. Get root then get element from xpath.
   If wrong path there except IOError.
   '''
   try:
      tree = etree.parse(path)
      root = tree.getroot()
      element = root.xpath(xpath)
      if len(element) == 0:
         raise etree.XPathError('lxml.XpathError: Wrong XPath.')
      return element,root
   except IOError as e:
      print('Problem with file or filepath.')
      print(e)

def opt_help():
   '''
   Printing help/manual from argparse.
   '''
   parser.print_help()

def opt_modify(value, xpath, path):
   '''
   @value - new value for mofified element or attribute
   @xpath - xpath to modified element
   @path - path to xml file
   Function to modifing argument's value or element's value on specified xpath.
   '''
   if '@' in xpath:
      key = xpath.split('@')[1]
      element,root = get_element(path, xpath.split('/@')[0])
      element[0].set(key, value)
   else:
      element,root = get_element(path, xpath)
      element[0].text = value
   etree.ElementTree(root).write(path, pretty_print=True)

def opt_add(value, xpath, path):
   '''
   @value - value for new element or attribute
   @xpath - xpath to element with new element at least
   @path - path to xml file
   Function to create argument with value or element with value on specified xpath.
   '''
   if '@' in xpath:
      element,root = get_element(path, xpath.split('/@')[0])
      key = xpath.split('@')[1]
      element[0].set(key, value)
   else:
      name_of_element = xpath[xpath.rfind('/')+1:]
      element,root = get_element(path, xpath[0:xpath.rfind('/')])
      d = etree.SubElement(element[0], name_of_element)
      d.text = value
   etree.ElementTree(root).write(path, pretty_print=True)

def opt_del(xpath, path):
   '''
   @xpath - xpath to deleted element
   @path - path to xml file
   Function to delete argument or element even with subelements on specified xpath.
   '''
   if '@' in xpath:
      key = xpath.split('@')[1]
      element,root = get_element(path, xpath.split('/@')[0])
      element[0].attrib.pop(key)
   else:
      element,root = get_element(path, xpath)
      element[0].getparent().remove(element[0])
   etree.ElementTree(root).write(path, pretty_print=True)

def opt_add_block(value, xpath, path):
   '''
   @value - new value to add, specified as raw xml element
   @xpath - xpath to element, where we adding 
   @path - path to xml file
   Function to add raw xml block in specified xpath.
   '''
   if '@' in xpath:
      raise Exception("You can't add block of raw xml as attribute value.")
   else:
      element,root = get_element(path, xpath)
      parent = element[0].getparent()
      parent.insert(parent.index(element[0])+1, etree.XML(value))
      etree.ElementTree(root).write(path, pretty_print=True)

def opt_rename(value, xpath, path):
   '''
   @value - new tag name of element or attribute
   @xpath - xpath to element or attribute, where we change the name
   @path - path to xml file
   Function to rename element's tag name or attribute name.
   '''
   if '@' in xpath:
      element,root = get_element(path, xpath.split('/@')[0])
      old_key = xpath.split('/@')[1]
      old_value = element[0].attrib[old_key]
      element[0].attrib.pop(old_key)
      element[0].set(value, old_value)
   else:
      element,root = get_element(path, xpath)
      element[0].tag = value
   etree.ElementTree(root).write(path, pretty_print=True)

if __name__ == '__main__':
   parser = argparse.ArgumentParser(
      prog = 'xml_operation.py',
      description = '''Program to modify xml file.
Specify path to file.
Specify xpath to element or atribute
and then change value.''',
      epilog = '''TEMPLATES:
** add atrribute to element specified in xpath with name as @test in xpath value and value specified in value
./xml_operation.py --path /full_path_to_xml_file -o add --xpath //business/beers/beer[1]/@test --value test_value
** add element with tag name specified in xpath (beer) and text value specified in value
./xml_operation.py --path /full_path_to_xml_file -o add --xpath //business/beers/beer --value test_value

** modify element's text value specified in xpath to new value specified in value
./xml_operation.py --path /full_path_to_xml_file -o modify --xpath //business/beers/beer[4] --value new_value
** modify attribute's value specified in xpath to new value specified in value
./xml_operation.py --path /full_path_to_xml_file -o modify --xpath //business/beers/beer[1]/@test --value new_value

** removing element (in this case 4 child of beers - beer) in //business/beers
./xml_operation.py --path /full_path_to_xml_file -o del --xpath //business/beers/beer[4]
** removing attribute from xpath specified in xpath
./xml_operation.py --path /full_path_to_xml_file -o del --xpath //business/beers/beer[1]/@test

** add raw xml element specified in value after specified xpath
./xml_operation.py --path /full_path_to_xml_file -o addblock --xpath //business/beers/beer[4] --value '<beer>Test value in block of raw xml code</beer>'

** rename element's tag name specified in xpath to new name specified in value
./xml_operation.py --path /full_path_to_xml_file -o rename --xpath //business/beers --value new_value
** rename attribute's name specified in xpath to new name specified in value
./xml_operation.py --path /full_path_to_xml_file -o rename --xpath //business/@test --value new_value
''',
      add_help = True,
      argument_default = argparse.SUPPRESS,
      formatter_class = argparse.RawTextHelpFormatter)
   #Console argument for path to file.
   parser.add_argument('--path', '-p',
      nargs = '?',
      required = True,
      help = '''Absolute path to to xml file.''')
   #Console argument for xpath to place in xml content
   parser.add_argument('--xpath', '-x',
      nargs = '?',
      required = True,
      help = '''XPath to element that will be procceed.''')
   #Console argument for type of operation on xml file
   parser.add_argument('--operation', '-o',
      nargs = '?',
      required = True,
      choices = ['add', 'modify', 'del', 'addblock', 'rename'],
      default = 'modify',
      help = '''Operations. Choose from add, modify, del and addblock.
modify - to modify existing element value or attribute value. Or create new atribute with value
add - to add new element or new atrribute
del - to remove attribute or element with value also with child nodes
rename - to rename element's tag name or attribute name
addblock - to add block of raw xml code into the xml tree !!after!! specified xpath''')
   #Console argument for value input in specified xpath
   parser.add_argument('--value', '-v',
      nargs = '?',
      default = '',
      help = '''Value to input in specified xpath. Default empty string. It useful to remove operation when you dont have to specify value just xpath''')
   args = parser.parse_args()

# MAIN FUNCTIONALITIES
   try:
      if not len(sys.argv) > 1:
         opt_help()
      else:
         if args.operation == 'modify':
            if args.value:
               opt_modify(args.value, args.xpath, args.path)
            else:
               raise Exception("ARGPARSE ERROR: --value argument is required for -o modify") 
         elif args.operation == 'add':
            if args.value:
               opt_add(args.value, args.xpath, args.path)
            else:
               raise Exception("ARGPARSE ERROR: --value argument is required for -o modify") 
         elif args.operation == 'del':
            opt_del(args.xpath, args.path)
         elif args.operation == 'addblock':
            if args.value:
               opt_add_block(args.value, args.xpath, args.path)
            else:
               raise Exception("ARGPARSE ERROR: --value argument is required for -o modify") 
         elif args.operation == 'rename':
            if args.value:
              opt_rename(args.value, args.xpath, args.path)
            else:
               raise Exception("ARGPARSE ERROR: --value argument is required for -o rename")
         else:
            opt_help()
            raise Exception("Wrong operation")
   except Exception as e:
      print(e)
