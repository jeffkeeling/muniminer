import sys
import os
import web
from web import form
import subprocess
import re
import base64
import json

class Parse:


   def __init__(me,txt):
       ## public methods obtain values
       ## and move the pointer
       #me.i = 0
       ## This pointer idea presumed a single pass through the PDF. But, that's obsolete since
       ##  we are making one pass per regular expression now.

       me.txt = txt
   
   def getDollars(me):
      ## looks for dollar amount after possible
      ## white space, returns it
      #me._skip()
      p = me._compile( r"(\$[\d\,]+)" )           
      return me.get_return(p)

   def getRegex(me,regex):
     ## looks for regex 
     #me._skip()
     p = me._compile(regex)
     return me.get_return(p)

   #def _skip(me):
      #p = me._compile(
      #     r"([ \t\n\f]*)"
      #)
      #return me.get_return(p)

   def _compile(me,regex):
       return re.compile(
                    regex,
                    re.IGNORECASE+re.MULTILINE
              )

   # Returns a list of tuples, each representing a match. Each tuple has 1 string for each group in the regex.
   def get_return(me,p):
      tupleList = p.findall(me.txt)
      if tupleList and len(tupleList) > 0:
         print("\tfound " + str(len(tupleList)) + " match(es)")
         matches = []
         # Return a list of strings made up of the 0th entry in each tuple (first group in regex)
         for t in tupleList:
            matches.append(t[0])
         return matches
      else:
         print("\tdidn't find")
         return None 



render = web.template.render('../templates/', base='layout')
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

urls = (
    '/', 'Upload',
    '/upload', 'Upload',
    '/full-text', 'FullText',
    '/display', "Display",
    '/login', 'Login',
    '/about', 'About',
    '/edit-profiles', 'Edit_profiles'
)

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

allowed = {
    'user':'pass'
}

# Notes for user if this data is exposed:
# This is a list of Python regular expression patterns to be applied to document text. 
# Each must have at least one pair of parentheses. Everything matching within the outermost pair will be returned as the match.
# Note that a double backslash sequence \\ is interpreted as a single backslash. So a line break is \\n and a dollar sign is \\$.
#    Pattern for a dollar ammount:  \\$[0-9,]+\\.?[0-9]?[0-9]?"
# To allow line breaks everywhere, \\s+ is used instead of single spaces. And instead of .*? to skip arbitrary text, we use
# the super ugly (.*?\n*?.*?). If we used re.DOTALL, .*? would match newlines, but in testing that it seemed to cause it to act 
# like a greedy match and go to the end of the document.
regs = {
                  # the [)]? at the end handles docs that use parentheses around zero: ($0)
    'Table IV-1': "^(\\s*Table IV ?- ?1\\s*$([^\\$]*?\\n)+(.*?\\$[0-9,]+\\.?[0-9]?[0-9]?[)]?\\s*)+)",

    'Bonds Outstanding': "(as\\s+of\\s+(\\w+\\s+\\d\\d?,?\\s+\\d\\d\\d\\d),?(.*?\n*?.*?)"
                        +"the\\s+(total(.*?\n*?.*?)bonds\\s+outstanding"
                                +"|amount\\s+outstanding(.*?\n*?.*?)bonds"
                                +"|(aggregate\\s+)?(amount\\s+of\\s+)?outstanding\\s+(.*?\n*?.*?)bonds)"
                        +"\\s+(is|are|was|were)\\s+(equal\\s+to\\s+)?\\$[0-9,]+\\.?[0-9]?[0-9]?)",

    # this is the backup plan for docs that don't have bonds outstanding info in paragraph text.
    'Table of Bonds Outstanding': "^(\\s*Table VI ?- ?\\d\\s*"
                                    +"(bonds outstanding"
                                    +"|outstanding.*?bonds)"
                                    +"\\s*$([^\\$]*?\\n)+(.*?\\$[0-9,]+\\.?[0-9]?[0-9]?\\s*)+)"
#Outstanding Series 2003B Bonds
    # todo: add a "Mortgages/Loans" profile to match things like
    #     As of March 31, 2009, the outstanding balance of the Promissory Note was $2,647,368.
    #     As of March 31, 2009, the Company reports that the outstanding balance on the Land Disposition and Development Agreement promissory note is $2,647,368.
    #     As of March 31, 2009, the Company reports that the outstanding balance on the Chesapeake Home Loan is $12,379,130.
    #                            "outstanding\\s+balance(.*?\n*?.*?)promissory\\s+note"
}

def processRegex(txt, profileName, profileRegex):
    responseJson = {}
    p = Parse(txt)
    listForCsv = []
    regexName = ''
    regexToUse = '' 
    for r in regs:
        if r == profileName:
            regexName = r
            regexToUse = regs[r]

    if regexName == '':
        regexName = profileName
        regexToUse = r'%s' % profileRegex

    listForCsv.append('\nResults for ' + regexName + ':\n')
    print("searching for " + regexName + ":  " + regexToUse)
    matches = p.getRegex(regexToUse)
    if not matches and regexName == 'Bonds Outstanding':
        print("Didn't find a match in paragraph text, searching for a table instead...")
        matches = p.getRegex(regs['Table of Bonds Outstanding'])

    if matches and len(matches) > 0:
        allmatches = ''
        for m in matches:
            allmatches += m  + "\n"
            listForCsv.append( m  + "\n")
        
        responseJson[regexName] = allmatches
    else:
        responseJson[regexName] = "Text Pattern Not Found"
        listForCsv.append("Not Found")

    print('Creating CSV version of output...')
    csv = ''
    for s in listForCsv:
        print(s)
        if s:
            table_csv = make_csv(s)
            if table_csv:
                csv = csv + "\n" + table_csv
    
    if csv:
        responseJson['CSV Format'] = csv
       
    web.header('Content-Type', 'application/json')
    return json.dumps(responseJson)


def make_csv(txt):
    # remove empty lines that pdftotext seems to always insert
    singleSpaced = re.sub(r"\n\n", "\n", txt)
    # remove existing commas
    noCommas = singleSpaced.replace(',', '')
    cleanLines = noCommas.splitlines()
    foundTable = False
    finishedLines = []
    if len(cleanLines) > 1:
        tableCells = 0.0
        numSkippedLines = 0
        convertedLines = []
        for line in cleanLines:
            # if line stripped of whitespace is empty, skip csv conversion
            if line.isspace():
                convertedLines.append(line)
                numSkippedLines += 1
            else:
                # Split into columns when there are 3 or more spaces. Not sure how robust this rule is.
                column_break = r"[ ]{3}[ ]*"
                convertedLine = re.sub(column_break, ",", line)
                convertedLines.append(convertedLine)
                # Count the number of columns in each row. This is used to detect rows with too many or too few columns
                # which can indicate indentation in the first column (too many) or empty cells in this row (too few columns)
                cols = len(convertedLine.split(','))
                if is_in_table(convertedLine, cols):
                    #print(str(cols) + " columns:     " + convertedLine)
                    tableCells += cols
                else:
                    # don't count this line in the table calculations
                    numSkippedLines += 1

        if numSkippedLines < len(convertedLines):
            foundTable = True
            for line in convertedLines:
                cols = len(line.split(','))
                if is_in_table(line, cols):
                    lineCopy = ''
                    # check for cells that didn't get split (not enough space between them).
                    for cell in line.split(','):
                        if cell.count('$') > 1:
                            # This cell contains multiple dollar signs - split it up!
                            numNewCells = cell.count('$') - 1
                            tableCells += numNewCells
                            cols += numNewCells
                            print("Splitting this cell: " + cell)
                            for newCell in cell.split('$'):
                                if newCell:
                                    lineCopy += '$' + newCell + ','
                        else:
                            lineCopy += cell + ','
                    # drop extra trailing comma from re-assembling the cells
                    lineCopy = lineCopy[0:len(lineCopy)-1]

                    avgCols = tableCells / (len(convertedLines) - numSkippedLines)
                    avgColsRounded = int(round(avgCols))
                    #print("Table columns = " + str(avgCols) + ", rounded to " + str(avgColsRounded))

                    # if its col count > avg and line now starts with a comma, then first column is indented - remove first comma
                    if cols > avgColsRounded and lineCopy.startswith(","):
                        print("Handling indentation in first column of this: " + lineCopy)
                        finishedLines.append(lineCopy[1:len(lineCopy)])
                    # if its col count < avg, there appears to be an empty cell and we can't easily tell where it is.
                    elif cols < avgColsRounded:
                        finishedLines.append(lineCopy + ",,<---- Data misaligned - empty/merged cell(s) in this row?")
                        #TODO: to prevent skipping empty cells, tempting to add some logic during the conversion loop above:
                        #   If the preceding row has a column at the same point but more columns to the left, add empty column(s).
                        #   This would work great for the PDFs that have perfectly aligned column output, but that's rare. 
                    else:
                        finishedLines.append(lineCopy)
                else:
                    finishedLines.append(line)
        else:
            finishedLines = convertedLines
    else:
        finishedLines = cleanLines

    csv = "\n".join(finishedLines)
    #print("CSV OUTPUT:\n" + csv)
    if not foundTable:
        csv = None
        #print("No table data found in this match.")
    return csv

def is_in_table(line, colCount):
    # if no column breaks found or only 1 due to leading spaces, don't consider this line part of the table
    return colCount > 1 and (not line.startswith(",") or colCount > 2)

class About:
    def GET(self):
        return render.about()

class Edit_profiles:
    def GET(self):
        return render.editProfiles()

class FullText:
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

            # web.header('Content-Type',' application/download')
            # web.header('Content-Transfer-Encoding',' Binary')
            # web.header('Content-disposition', 'attachment; filename=output.txt')
            return

class Upload:
    def GET(self):
        # authentication check
        # if web.ctx.env.get('HTTP_AUTHORIZATION') is not None:
          web.header('Content-Type', 'text/html; charset=usf-8')
          return render.upload(regs)
        # else:
        #     raise web.seeother('/login')

    def POST(self):
        x = web.input(myfile={})
        profileNameInput = web.input(profileName={})
        profileRegexInput = web.input(profileRegex={})
        
        profileName = ''
        profileRegex = ''

        if 'profileName' in profileNameInput:
            profileName = profileNameInput.profileName

        if 'profileRegex' in profileRegexInput:
            profileRegex = profileRegexInput.profileRegex


        filedir = '../static'
        if 'myfile' in x:  # chck file obj created
            filepath = x.myfile.filename.replace('\\', '/')
            filename = filepath.split('/')[-1]
            fout = open(filedir + '/temp.pdf', 'w')
            fout.write(x.myfile.file.read())
            fout.close()
            subprocess.call([
                'pdftotext', '-table', filedir+'temp.pdf', filedir+'output.txt'
            ])

            with open(filedir+'output.txt') as fi: txt=fi.read()
 
            returnval = processRegex(txt, profileName, profileRegex)
            return returnval

class Login:
    def GET(self):
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ','',auth)
            username,password = base64.decodestring(auth).split(':')
            for key in allowed:
                if allowed[key] == password and key == username: 
                    raise web.seeother('/')
                else:
                    authreq = True
        if authreq:
            web.header('WWW-Authenticate','Basic realm="Auth example"')
            web.ctx.status = '401 Unauthorized'
            return


class Display: 
     def GET(self):
        returnval = 'returnval'
        return render.index(returnval)


def notfound():
    return web.notfound('noooope')

app.notfound = notfound


if __name__ == "__main__":
    app.run()
