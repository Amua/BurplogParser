#coding: utf-8
import re
import sys
import json
import requests

try:
    from collections import OrderedDict as _default_dict
except ImportError:
    _default_dict = dict

class BurplogParser(object):
    def __init__(self, filename, dict_type=_default_dict):        
        self.dict = dict_type
        self.fp = open(filename)             
            
    def __del__(self):              
        self.close()
            
    def close(self):
        if self.fp:
            self.fp.close()
            self.fp = None 
            
    def next(self):       
        packbag = self.readlog()
        if not packbag:
            raise StopIteration
        return packbag
        
    def readlog(self):
        assert(self.fp is not None) 
        flag = 0  
        request = 0    
        packbag = self.dict()
                    
        while True:
            line = self.fp.readline()   
            if not line:                
                break            
            if not line.strip():
                if packbag.has_key('headers'):
                    flag = 1                                
                continue                                                                    
            if line.find(' ') > 0:               
                cols = line.split()
                if len(cols) >= 2:
                    if re.match(r'am|pm', cols[1], re.I):
                        cols.pop(1)                  
                    regtime = re.match(r'\d{1,2}\:\d{1,2}\:\d{1,2}', cols[0])
                    if regtime:
                        reghost = re.match(r'((http|https)\:\/\/[\w|\W]+)(\:\d{1,5})?', cols[1], re.I)                                       
                        if reghost:
                            request = 1                                                                                                
                            hosts = reghost.group(0).split(':')
                            try:   
                                packbag['host'] = hosts[0] + ':' + hosts[1]                                                                    
                                packbag['schema'] = hosts[0]                                                                 
                                packbag['port'] = int(hosts[2])
                            except Exception:
                                pass 
            if re.match(r'^[a-z].+http\/\d\.\d$', line, re.I):
                cols = line.split()
                packbag['headers'] = self.dict()
                packbag['method'] = cols[0]
                packbag['url'] = packbag['host'] + ':' + str(packbag['port']) + cols[1]                
            elif re.match(r'^\=+$', line):
                if flag: break
            else:                       
                if packbag.has_key('headers'):
                    if not flag: 
                        cols = line.split(':', 1)
                        if len(cols) >= 2:
                            packbag['headers'][cols[0]] = cols[1].rstrip()
                    else:
                        packbag['data'] = line.rstrip()                                     
        return packbag                                
    
    def __iter__(self):
        self.fp.seek(0)
        while True:
            packbag = self.readlog()
            if not packbag:
                return
            yield packbag               
        
if __name__ == '__main__':  
    burplog = BurplogParser("burplog.txt")   
    try:
        while True:
            packbag = next(burplog)
            print packbag
    except StopIteration:
        pass        
    for index, package in enumerate(burplog):
        print package        
    burplog.close()
    
        
    
    
    
    
    
    
    
