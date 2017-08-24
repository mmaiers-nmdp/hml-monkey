import re
s="                                                                                                     HLA-B*27:05:02+HLA-B*39:01:01:03"
s="HLA-B*27:05:02+HLA-B*39:01:01:03"
                                
#m=re.compile("HLA-[A-Z0-9-]*")
m=re.compile("([A-Z0-9-]*)\*")
# extract the first locus from a glstring
def getloc(glstring):
    l=m.search(glstring)
    if l.group(1):
        return l.group(1)
    else:
        return "NOLOC"


print (s)
print ("matches: {}".format(getloc(s)))
