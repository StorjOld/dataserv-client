import os
import glob
import lib2to3
from py2exe.build_exe import py2exe as build_exe

class MediaCollector(build_exe):
   """
      This class Adds 
      jsonschema files draft3.json and draft4.json
      lib2to3 files Grammar.txt and PatternGrammar.txt
      to the list of compiled files so it will be included in the zipfile.
   """

   def copy_extensions(self, extensions):
      build_exe.copy_extensions(self, extensions)

      # lib2to3 files Grammar.txt and PatternGrammar.txt

      # Define the data path where the files reside.
      data_path = os.path.join(lib2to3.__path__[0],'*.txt')

      # Create the subdir where the json files are collected.
      media = os.path.join('lib2to3')
      full = os.path.join(self.collect_dir, media)
      self.mkpath(full)

      # Copy the json files to the collection dir. Also add the copied file
      # to the list of compiled files so it will be included in the zipfile.
      for f in glob.glob(data_path):
         name = os.path.basename(f)
         self.copy_file(f, os.path.join(full, name))
         self.compiled_files.append(os.path.join(media, name))

