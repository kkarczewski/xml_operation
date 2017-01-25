#! /usr/bin/env python3.4
#! -*- coding: utf-8 -*-
'''
Created on 27 lip 2015

@author: kamil@justnet.pl
'''

# #############################################################################
# standard modules (moduly z biblioteki standarowej pythona)
# #############################################################################
import os
import sys
import re
import time
import argparse
import subprocess
import pipes
import getpass
import csv
import string
import xml.etree.ElementTree as ET
import datetime
import base64
NAME = __file__
SPLIT_DIR = os.path.dirname(os.path.realpath(NAME))
SCRIPT_DIR = SPLIT_DIR + '/.' + os.path.basename(NAME)
LIB_DIR = SCRIPT_DIR + '/cache/lib/'
TMP_DIR = SPLIT_DIR + '/tmp/'
sys.path.insert(0,LIB_DIR)

#List of lib to install
import_list = [
   ('sqlalchemy','1.0.8','SQLAlchemy-1.0.8.egg-info'),
   ('paramiko','1.15.2','paramiko-1.15.2.dist-info'),
   ('colorama','0.3.3','colorama-0.3.3.egg-info'),
   ('pymysql','0.6.7','PyMySQL-0.6.7.dist-info')]
for line in import_list:
   try:
      if os.path.isdir(LIB_DIR+line[2]):
         pass
#         print('Found installed '+line[0]+line[1]+' in '+line[2])
      else:
         try:
            import pip
         except:
            print("Use sudo apt-get install python3-pip")
            sys.exit(1)
         print('No lib '+line[0]+'-'+line[1])
         os.system("python"+sys.version[0:3]+" -m pip install '"+line[0]+'=='+line[1]+"' --target="+LIB_DIR+" -b "+TMP_DIR)
      module_obj = __import__(line[0])
      globals()[line[0]] = module_obj
   except ImportError as e:
      print(line[0]+' is not installed')

# #############################################################################
# constants, global variables
# #############################################################################
OUTPUT_ENCODING = 'utf-8'
DIRECTORY = './'
TEMP_PATH = SCRIPT_DIR+'/cache/'
LOGGER_PATH = SCRIPT_DIR+'/logfile.xml'
LOG_VERSION = 1.0
# #############################################################################
# functions
# #############################################################################
#CZYTANIE Z PLIKU
def readfile(file_name):
   try:
      with open(file_name, 'r') as file:
         templines = [line.rstrip('\n') for line in file]
         lines=([])
         for line in templines:
            if not line.startswith('#'):
               lines.append(line)
   except (IOError, OSError):
      print >> sys.stderr, "Can't open file."
      sys.exit(1)
   return lines

def writefile(path_to_conf,file_name,data):
   if not os.path.exists(path_to_conf):
      os.mkdir(path_to_conf)    
   try:
      with open(path_to_conf+file_name,'w') as fileout:
         fileout.write(data)
   except(IOError,OSError):
      print_err("Can't write to file.")
      sys.exit(1)

#Kolorowanie ok
def print_ok(output):
   print(colorama.Fore.GREEN+output,colorama.Fore.RESET)

#Kolorowanie błędu
def print_err(error):
   print(colorama.Fore.RED+error,colorama.Fore.RESET)

def print_war(warning):
   print(colorama.Fore.YELLOW+warning,colorama.Fore.RESET)

# pretty print do logowania
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

#Logowanie
def my_logger(ERROR_FLAG,subcmd,outmsg):
   id_log = 1
   if not os.path.exists(LOGGER_PATH):
      root = ET.Element('root')
      root.set('version','1.0')
   else:
      tree = ET.parse(LOGGER_PATH)
      root = tree.getroot()
      for child in root:
         id_log+=1
   log = ET.SubElement(root, 'log')
   log.set('id_log',str(id_log))
   date = ET.SubElement(log,'date')
   date.text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
   cmdline = str()
   for line in sys.argv:
      cmdline += line+' '
   command = ET.SubElement(log,'command')
   command.set('encoding','plain')
   command.text = cmdline
   subcommands = ET.SubElement(log,'subcommands')
   subcommands.set('error_flag',ERROR_FLAG)
   subcmd_str=str()
   for one in subcmd:
      subcmd_str+=one+','
   subcommands.text = subcmd_str[:-1]
   outmsg_str = str()
   for one in outmsg:
      outmsg_str+=one+','
   msg = (base64.b64encode(outmsg_str.encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
   output = ET.SubElement(log,'output')
   output.set('encoding','base64')
   output.text = msg
   indent(root)
   if not os.path.exists(LOGGER_PATH):
      tree = ET.ElementTree(root)
   tree.write(LOGGER_PATH,encoding=OUTPUT_ENCODING,xml_declaration=True,method='xml')

#Wykonywanie poleceń w terminalu
def os_call(*args,progress_char='*',verbose=1):
   n = 0
   done_cmd = list()
   out = list()
   for cmd in args:
      p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=DIRECTORY)
      (output,err) = p.communicate()
      n = n+1
      ast = progress_char*n
      if err or 'ERROR' in str(output) or 'Exception' in str(output):
         done_cmd.append(cmd)
         ERROR_FLAG = 'T'
#         print_err(cmd)
         if err:
#            print_err(err.decode(OUTPUT_ENCODING))
            out.append(err.decode(OUTPUT_ENCODING))
            break
         else:
#            print_err(output.decode(OUTPUT_ENCODING))
            out.append(output.decode(OUTPUT_ENCODING))
            break
      else:
         ERROR_FLAG = 'F'
         done_cmd.append(cmd)
         out.append(output.decode(OUTPUT_ENCODING))
         if verbose == 2:
            print(ast,end="\r")
            time.sleep(1)
#            print_ok(cmd)
#            print_ok(output.decode(OUTPUT_ENCODING))
         elif verbose == 1:
            print_ok(output.decode(OUTPUT_ENCODING))
         else:
            print(ast,end='\r')
   return ERROR_FLAG,done_cmd,out

# SQLAlchemy simple example
def simple_query(query):
   engine = sqlalchemy.create_engine(engine_text)
#   engine = create_engine(dialect+driver://username:password@host:port/database)
   connection = engine.connect()
   result = connection.execute(query)
   data = str()
   for row in result:
      data+=str(row)+';'
   connection.close()
   data = data[1:-2].split(');(')
   return data

def makedict(args):
   dictionary = dict()
   for one in args:
      one=one.split('=')
      dictionary[one[0]]=one[1]
   return dictionary

def create_data(one):
   one = one.split(', ')
   if len(one) > 2:
      one[1] = (', ').join(one[1:])
   one[1] = one[1].replace('\n','')
   one[1] = one[1].replace('\\n','')
   one[1] = one[1].replace('\\r','')
   one[1] = one[1].replace('  ',' ')
#   print(one[0],one[1])
   return one[0], one[1]
   
# #############################################################################
# operations
# #############################################################################

def opt_validate(table, column, xsd_file, noout, verbose):
   if table == 'archives':
      sql = 'SELECT id, '+column+' FROM '+table+" WHERE name LIKE 'Raporty faktur%%'"
   else:
      sql = 'SELECT id, '+column+' FROM '+table
   data = simple_query(sql)
   for one in data:
      ident,xml_data = create_data(one)
      list_cmd = list()
      file_path = table+'-'+column+'/'
      file_name = str(ident)+'.xml'
      if xml_data == str(None):
         print_err(str(ident)+' have NULL in content.')
         if without == True:
            writefile(file_path,file_name+'_NULL','NULL')
      else:
         try:
            data = ET.fromstring(xml_data[1:-1])
            writefile(file_path,file_name,xml_data[1:-1])
            cmd = 'xmllint --noout -schema '+xsd_file+' '+file_path+file_name
            list_cmd.append(cmd)
            ERROR_FLAG,done_cmd,out = os_call(*list_cmd,progress_char='*',verbose=1)
            if 'fails' in out[0]:
               if verbose == True:
                  print_err(out[0])
               else:
                  print_err(ident+' not validate.')
               if without == False:
                  os.remove(file_path+file_name)
            else:
               os.remove(file_path+file_name)
         except Exception as e:
            if verbose == True:   
               print_err(ident+' '+str(e))
            else:
               print_err(ident+' '+"XML file syntax error.")
            if without == True:
               writefile(file_path,file_name+"_WRONG_XML",xml_data[1:-1]) 

def opt_db_engine(args):
   data = makedict(args)
   global engine_text
   if not 'database' in data:
      sys.exit(print_err("Database is required. Modify config file."))
   if not 'username' in data:
      sys.exit(print_err("Username is required. Modify config file."))
   if not 'table' in data:
      sys.exit(print_err("Table is required. Modify config file."))
   if not 'file' in data:
      sys.exit(print_err("File is required. Modify config file."))
   if not 'port' in data:
      data['port'] = ''
   if not 'hostname' in data:
      data['hostname'] = 'localhost'
   if not 'column' in data:
      data['column'] = 'content'
   temp = string.Template('mysql+pymysql://$username:$password@$hostname$port/$database')
   engine_text = temp.safe_substitute(data)
   if 'localhost' in engine_text:
      engine_text+='?unix_socket=/var/run/mysqld/mysqld.sock'
#   print(engine_text)
   return data['table'], data['column'], data['file']

def opt_help():
   parser.print_help()
   msg = 'Printed help'
   msg = (base64.b64encode(('Printed help').encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
   return msg

# #############################################################################
# main app 
# #############################################################################
if __name__ == '__main__':
# Czytanie arugmentów
   parser = argparse.ArgumentParser(
      prog='check_content.py',
      description='''\nValidation data in content table in database.\n
file_name (required) - file_name with database configuration.''',
      epilog='''Example of usage:
$./check_content.py archives-content.conf
$./check_content.py file1 -v -o
''',
      add_help=True, 
      argument_default=argparse.SUPPRESS,
      formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument('--verbose','-v',
      default = False,
      action = 'store_true',
      help = 'To print explain more about why is not validate.')
   parser.add_argument('--out','-o',
      default = False,
      action = 'store_true',
      help = 'To store content in xml file that is not validate.')
   argv = sys.argv[2:]
   args = parser.parse_args(argv)
#   print(args)
   try:
      if not len(sys.argv) > 1 or '--help' in sys.argv or '-h' in sys.argv:
         opt_help()
      else:
         file_name = sys.argv[1]
         if os.path.exists(file_name):
            data = readfile(file_name)
         else:
            sys.exit(print_err('File not exists.'))
         verbose = args.verbose
         without = args.out
         table, column, xsd_file = opt_db_engine(data)
         opt_validate(table, column, xsd_file, without, verbose)
         print("Done.")
   except Exception as e:
      cmd = str()
      for one_arg in sys.argv:
         cmd+=one_arg+' '
      list_cmd=list()
      list_cmd.append(cmd)
      err_msg = str(e)
      my_logger('T',list_cmd,err_msg)
      print(e)
