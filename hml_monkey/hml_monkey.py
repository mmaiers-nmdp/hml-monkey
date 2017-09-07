#i -*- coding: utf-8 -*-

#
#    hml_monkey HML Monkey.
#    Copyright (c) 2017 Be The Match operated by National Marrow Donor Program. All Rights Reserved.
#
#    This library is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or (at
#    your option) any later version.
#
#    This library is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; with out even the implied warranty of MERCHANTABILITY or
#    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#    License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this library;  if not, write to the Free Software Foundation,
#    Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#    > http://www.fsf.org/licensing/licenses/lgpl.html
#    > http://www.opensource.org/licenses/lgpl-license.php
#


import sys
from lxml import etree
from io import StringIO, BytesIO
import re
import gzip
from gl_service import GLservice

glv = GLservice()

target = '3.25.0'
source = '3.20.0'
# local archive of HML
hmldir = "/Volumes/Fat/HML"
# network archive of HML
hmldir = "/home/ec2-user/hml"

# this string seems to accompany elements
schem = "{http://schemas.nmdp.org/spec/hml/1.0.1}"

# extract the first locus from a glstring
m=re.compile("([A-Z0-9-]*)\*")
def getloc(glstring):
    l=m.search(glstring)
    if l.group(1):
        return l.group(1)
    else:
        return "NOLOC"

# table of lab 744 files from first pass
hfiles = {}
firstpassfile = "744.txt"

with open(firstpassfile, "r") as fp:
    
    for line in (fp.readlines()):
        [filenum]= re.split('\t', line.rstrip('\n')) # I miss chomp
        hfiles[filenum]=1
    
# dictionary of results
d={}

#for i in (range(1,3111)):
#for i in (range(35,36)):
for i in (list(hfiles.keys())):
    #if int(i) < 40:
    #    continue
    gzfilename = "{}/{}.hml101.xml.gz".format(hmldir, i)
    fileobject = gzip.open(gzfilename, 'rb')
    print ("open {}".format(gzfilename),file=sys.stderr)
    root = etree.parse(fileobject)

    # reporting center
    reporting_center  = root.find(schem+'reporting-center')
    reporting_center_id = reporting_center.get('reporting-center-id')

    # sample
    for sample in root.findall(schem+'sample'):
        id = sample.get('id')
        # remove hyphens
        id = id.replace("-","")
        # typing
        for typing in sample.findall(schem+'typing'):
            # allele assignment
            allele_assignment = typing.find(schem+'allele-assignment')
            allele_db = allele_assignment.get('allele-db')
            source = allele_assignment.get('allele-version')
            # glstring
            glstring = allele_assignment.find(schem+'glstring')
            gl = None
            if glstring is not None:
                if glstring.text is not None:
                   gl = glstring.text
                   loc = getloc(gl)
            else:
                loc = "NOLOC"

            
            #first validate it
            v = glv.valver(gl, source)
            fixed = 0
            if v.status_code ==400:
                # if its not valid
                # fix it
                fgl = glv.fix(gl)
                vv = glv.valver(fgl, source)
                if vv.status_code ==400:
                    # bailout
                    continue
                else:
                    if fgl != gl:
                        fixed = 1 
                        gl = fgl 
                
            #then lift it over
            lgl = glv.liftover(gl, source, target)
            lifted = 0
            if lgl != gl:
                lifted = 1

            print(",".join(str(j) for j in [i, reporting_center_id, id, loc, gl, lgl,source,lifted, fixed]))

            if i not in d:
                d[i] = {}
            if id not in d[i]:
                d[i][id] = {}
            d[i][id][loc]= gl

#for i in d.keys():
#    for id in d[i].keys():
#        for loc in d[i][id].keys():
#            #print("dump\t{}\t{}\t{}\t{}".format(i, id, loc, d[i][id][loc]))
# make a table of filename index, id, locus
# use this to construct a massive index of all HML
# run it on full archive
# make a table as the source of the 8000 cohort




