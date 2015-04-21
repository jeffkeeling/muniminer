# muniminer
Muniminer is a tool that will allow users to upload PDFs to a server and receive parsed text dictated with their own regular expressions.

##Setup on local machine

###Requirements

1. XPDF command line tool which uses pdftotext (linux binary, tested on OSX 10.9.5)
2. python2.7
3. pip
4. web.py `pip install web.py` (using sudo if needed)

###Starting Muniminer

1. From Muniminer directory `python bin/app.py 127.0.0.1`
2. Go to http://localhost:8080 in your browser
3. Upload pdf

##Background

Muniminer was born during the Hacking iCorruption hackathon hosted at the MIT Media Lab on March 28-29, 2015.
"The Edmond J. Safra Center for Ethics and the MIT Center for Civic Media hosted Hacking iCorruption, a multidisciplinary hackathon to fix the system, legal corruption that is weakening our public institutions around the world. Edmond J. Safra Lab Fellows presented their research and worked with coders, designers, journalists, activists, and others to build tools that are of practical use in solving the problem of institutional corruption as it manifests in different fields. These projects will be developed and presented at our upcoming conference Ending Institutional Corruption on May 1-2, 2015." 

Hackpad from the event:
https://hack-icorruption.hackpad.com/Marys-MuniMiner-CDA-Mining-Project-NWHGIqWmgv6