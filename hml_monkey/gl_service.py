# -*- coding: utf-8 -*-

# validate a gl-string against
# https://gl.nmdp.org/imgt-hla/3.25.0/


import requests
import re
import string
import liftovergl

hladb_version = "3.25.0"
service_url = "http://gl.nmdp.org/imgt-hla"
noun = "genotype-list"

class GLservice:
    def __init__(self, ver=hladb_version, service_url=service_url, noun=noun):
        self.ver = ver
        self.service_url = service_url
        self.url = "{}/{}/{}".format(service_url,ver, noun)
        self.history = liftovergl.read_history()
        #self.pattern =re.compile("HLA-[A-Z]*\*[0-9:*]")
        self.pattern =re.compile("(HLA-[A-Z0-9]*)\*([0-9:]*)")
    def valver(self, glstring, version):
        self.ver = version
        #self.url = "{}/{}/{}".format(service_url, self.ver, noun)
        #print(self.url)
        #response = requests.post(self.url, data=glstring)
        r = liftovergl.mk_glids(glstring, version, self.history) 
        return r
    def val(self, glstring):
        #print(self.url)
        response = requests.post(self.url, data=glstring)
        return response
    def liftover(self, glstring, source, target):
        ret = liftovergl.mk_glids(glstring, source, self.history)
        if ret.errorflag:
            return(ret.retstring)   
        else: 
            return (liftovergl.mk_target(ret.retstring, target, self.history))
    def fix(self, glstring):
        r = self.val(glstring)
        if r.status_code == 201:
            # success
            return r.text
        elif r.status_code == 400:
            # failure
            # parse text
            # e.g.: Unable to create genotype list, allele "HLA-DQB1*04:02:01:01" not a valid allele
            s = self.pattern.search(r.text)
            if s is None:
                return("No HLA")
            else: 
                loc = s.group(1)
                anum = s.group(2)
                afields = re.split(':',anum)
                numfields =  len(afields)
                oldallele = "{}*{}".format(loc, anum)
                if numfields == 3:
                     afields.append("01")
                     newanum = ':'.join(afields)
                     newallele = "{}*{}".format(loc, newanum)
                     newglstring = glstring.replace(oldallele, newallele)
                     return self.fix(newglstring)
    
                     # remove the last
                     #del afields[numfields-1]
                     #newanum = ':'.join(afields)
                     #print ("new allele: {}*{}".format(loc, newanum))
                     #newallele = "{}*{}".format(loc, newanum)
                     #newglstring = glstring.replace(oldallele, newallele)
                     #return newglstring
                elif numfields == 2:
                     # add "01:01"
                     afields.append("01")
                     newanum = ':'.join(afields)
                     newallele = "{}*{}".format(loc, newanum)
                     newglstring = glstring.replace(oldallele, newallele)
                     return self.fix(newglstring)
                else:
                     return "can't fix allele: {}*{}".format(loc, anum)
        else:
            # unknown status code
            return "unknown status: {}".format(r.status_code)
   

# run for testint
if __name__ == '__main__':  
    glv = GLservice()

    #do some val
    glstring = "HLA-DQB1*02:02:01:01+HLA-DQB1*04:02:01"
    print("{} {}".format(glstring,glv.val(glstring)))

    #do some valver
    glstring = "HLA-DQB1*02:02:01:01+HLA-DQB1*04:02:01"
    vers = "3.25.0";
    print("{} {} {}".format(glstring, vers, glv.valver(glstring, vers).errorflag))
    vers = "3.20.0";
    print("{} {} {}".format(glstring, vers, glv.valver(glstring, vers).errorflag))



    # do some liftover
    source = "3.20.0"
    target = "3.25.0"
   
    print ("hit1")
    glstring = "HLA-DRB1*08:01:01/HLA-DRB1*08:01:03"
    print("{} {}".format(glstring,glv.liftover(glstring, source, target)))
    print ("hit2")
    glstring = "HLA-DRB1*10:01:01+HLA-DRB1*14:04:01"
    print("{} {}".format(glstring,glv.liftover(glstring, source, target)))

    glstring = "HLA-DQB1*02:02:01:01+HLA-DQB1*04:02:01"
    print("{} {}".format(glstring,glv.fix(glstring)))

    glstring = "HLA-DQB1*02:02:01+HLA-DQB1*04:02:01"
    print("{} {}".format(glstring,glv.fix(glstring)))

    glstring = "HLA-DQB1*02:02+HLA-DQB1*04:02:01"
    print("{} {}".format(glstring,glv.fix(glstring)))

    

    
