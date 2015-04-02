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
        r"(as of (\w+ \d\d?, \d\d\d\d), the total.*?bonds outstanding was \$[0-9,]+\.?[0-9]?[0-9]?)"
    ]
    p = Parse(txt)
    out = [] 
    for r in regs:
       out.append( p.getRegex(r) )
    return '\n\n'.join(out)

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
                'pdftotext', '-table', '/Users/jeff/pdfParse/static/temp.pdf', '/Users/jeff/pdfParse/static/output.txt'
            ])

            with open('/Users/jeff/pdfParse/static/output.txt') as fi: txt=fi.read()
 
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
