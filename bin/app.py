import sys
import os
import web
from web import form
import subprocess
import re

class Parse:


   def __init__(me,txt):
       ## public methods obtain values
       ## and move the pointer
       me.i = 0
       me.txt = txt
   
   def getDollars(me):
      ## looks for dollar amount after possible
      ## white space, returns it
      me._skip()
      p = me._compile( r"(\$[\d\,]+)" )           
      return me.get_return(p)

   def getRegex(me,regex):
     ## looks for regex 
     me._skip()
     p = me._compile(regex)
     return me.get_return(p)

   def getTable(me):
      ## looks for a table after possible
      ## white space and returns it as an
      ## array of arrays
      pass

   def _skip(me):
      p = me._compile(
           r"([ \t\n\f]*)"
      )
      return me.get_return(p)

   def _compile(me,regex):
       return re.compile(
                    regex,
                    re.IGNORECASE+re.MULTILINE
              )

   def get_return(me,p):
      match_obj = p.search(me.txt[me.i:])
      if match_obj:
         me.i = match_obj.end()
         return match_obj.group(1)
      else:
         return None 


render = web.template.render('../templates/')
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

urls = (
    '/', 'Upload',
    '/upload', 'Upload',
    '/display', "Display"
)

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

def processRegex(txt):
    regs = [ 
        r"^\s*(Table IV-1\s*$([^\$]*?\n)+(.*?\$[0-9,]+\.?[0-9]?[0-9]?\n\s*\n)+)",
        r"(as of (\w+ \d\d?, \d\d\d\d),? the total.*?bonds outstanding was \$[0-9,]+\.?[0-9]?[0-9]?)"
    ]
    p = Parse(txt)
    out = [] 
    for r in regs:
       if r:
           out.append( p.getRegex(r) )
       else:
           # todo: associate a name with each regex so it's clear what was/wasn't found
           out.append("Text Pattern Not Found")
    out.append('\n----------------------- CSV Format -----------------------n')
    csv = ''
    for s in out:
        #print(s)
        if s:
            csv = csv + make_csv(s)
    out.append(csv)
    # TOOD? also append the full PDF text
    return '\n\n'.join(out)

def make_csv(txt):
    txt = txt.replace(',', '')
    # Splits columns when there are 3 or more spaces. Not sure how robust this rule is.
    column_break = r"[ ]{3}[ ]*"
    # tried with /t instead of comma, but still didn't paste into Excel as columns
    csv = re.sub(column_break, ",", txt)
    #remove empty lines?
    empty_row = r"\n{2}\n*"
    csv = re.sub(empty_row, "\n", csv)
    # This is not good enough because 1) many tables use indentation within a column (following cells get shifted right).
    # and 2) empty cells are skipped (following cells get shifted left).
    #   idea: split each comma-delimited row on commas to determine the number of columns in each row and compute the avg
    #           Verify that split() counts a leading , (first string in output is empty)
    #     For each row, 
    #       if its col count > avg and original text of row starts with a space, then INDENTED - remove first comma
    #       if its col count < avg, append an extra column with text "<---- Data misaligned - empty table cell(s) in this row?"
    return csv

class Upload:
    def GET(self):
        web.header('Content-Type', 'text/html; charset=usf-8')
        return render.upload()

    def POST(self):
        x = web.input(myfile={})
        filedir = '../static'
        if 'myfile' in x:  # chck file obj created
            filepath = x.myfile.filename.replace('\\', '/')
            filename = filepath.split('/')[-1]
            fout = open(filedir + '/temp.pdf', 'w')
            fout.write(x.myfile.file.read())
            fout.close()
            subprocess.call([
                'pdftotext', '-table', 'static/temp.pdf', 'static/output.txt'
            ])

            with open('../static/output.txt') as fi: txt=fi.read()
 
            returnval = processRegex(txt)
            return returnval

class Display: 
     def GET(self):
        returnval = 'returnval'
        return render.index(returnval)


def notfound():
    return web.notfound('noooope')

app.notfound = notfound


if __name__ == "__main__":
    app.run()
