#!/usr/bin/env python3
import sys

from xml.dom import minidom
doc = minidom.Document()
root = doc.createElement('root')

class Section:

    def __init__(self, title):
        self.title = title
        self.name  = '_'.join(title.split()[:2]).lower()
        self.arg_map = {} # flag :- param
        self.root = doc.createElement('section')
    #    self.isSub = False   # Main params, sub params (DataType,FreqType, etc)

    #def setSubSection(self, name):
    #   self.isSub = True
    #   self.sub_type = name

    def printSection(self, expanded=False):
        sect = self.root
        sect.setAttribute('name',  self.name  )
        sect.setAttribute('title', self.title )
        sect.setAttribute('expanded', "true" if expanded else "false")

        for flag in self.arg_map:
            param = self.makeFlag(flag)
            sect.appendChild( param )

        #print(self.title)
        #import pdb; pdb.set_trace()
        print(sect.toprettyxml())

    
        
		
    def insertFlag(self, flag, flag_params, text):
        flag = flag.strip()
        if flag not in self.arg_map:
            self.arg_map[flag] = []

        self.arg_map[flag].append(  (flag_params, text)  )

        
    def makeFlag(self,flag):
        flag_type, defaultval = self.resolveFlagType(flag)

        if flag_type == "boolean":
            return self.makeBoolean(flag, defaultval)
        if flag_type == "text":
            return self.makeText(flag, defaultval)
        if flag_type == "float":
            return self.makeNumber(flag, "float", defaultval)
        if flag_type == "integer":
            return self.makeNumber(flag, "integer", defaultval)
        if flag_type == "file":
            return self.makeFile(flag)
        if flag_type == "select":
            return self.makeSelect(flag, defaultval)
        
        print("ERROR:", flag_type, flag, self.arg_map[flag] )
        exit(-1)


    @staticmethod
    def getLabel(text):
        return text.split('. ')[0]


    def resolveFlagType(self, flag):
        array = self.arg_map[flag]

        if len(array)>1:
            return ('select',None)

        fparam, text = array[0]
        text = text.lower()
        words = text.split()

        def determineType(words, text):
            if words[0] == "specify":
                if text.find("list of")!=-1:
                    return "text"
    
                for word in words[:10]:
                    if word == "number":
                        return "integer"
                    if word == "file":
                        return "file"
                    if word == "frequency":
                        return "float"
                    if word == "prefix":
                        return "text"

                return "text"  # 'specify' defaults to text        
            

            if words[0] == "Turn" and words[1] == "on":
                return "boolean"

            # No other clues, probably bool.
            return 'boolean'


        def determineDefault(typer, words):

            for w in range(len(words)):
                word = words[w]
                if word[-6:] == "fault:":
                    next_word = words[w+1]
                    if typer == "boolean":
                        if next_word == "on":
                            return "true"
                        elif next_word == "off":
                            return "false"

                    try:
                        res = float(next_word)
                        return res
                    except ValueError:
                        pass

            return None


        type_of = determineType(words,text)
        default = determineDefault(type_of, words )

        if type_of == "integer" and default!=None:
            default = int(default)
        
        return (type_of, str(default))
                        


    def __makeSingle(self,flag):
        flag_params, text = self.arg_map[flag][0] # first and only

        param = doc.createElement('param')
        param.setAttribute('argument', flag )
        param.setAttribute('label', Section.getLabel(text) )
        param.setAttribute('help', text)
        return param

        
    def makeBoolean(self, flag, defaultval = None):
        param = self.__makeSingle(flag)
        param.setAttribute('type', 'boolean')
        param.setAttribute('value', defaultval if defaultval!=None else "false" )
        return param

    def makeText(self, flag, defaultval = None):
        param = self.__makeSingle(flag)
        param.setAttribute('type', 'text')
        if defaultval!=None:
            param.setAttribute('value',defaultval)
        return param


    def makeNumber(self, flag, typer, default=None):
        param = self.__makeSingle(flag)
        param.setAttribute('type', typer)
        if default != None:
            param.setAttribute('value', default)
        return param


    def makeFile(self,flag):
        param = self.__makeSingle(flag)
        param.setAttribute('type', 'data')
        return param


    def __makeSelect(self, title, opts, helper):
        param = doc.createElement('param')
        param.setAttribute('type', 'select')
        param.setAttribute('argument', title)
        param.setAttribute('help', helper)

        #import pdb; pdb.set_trace()
        
        for opt_value in opts:
            option = doc.createElement('option')
            option.setAttribute('value', opt_value)
            #option.setAttribute('help', text)
            texter = doc.createTextNode(opt_value)

            option.appendChild(texter)
            param.appendChild(option)

        return param
            
        

    def makeSelect(self,flag, defaultval = None):

        # Regular section
        opts = [x[0][0] for x in self.arg_map[flag]]
        hlps = '\n'.join([x[0][0]+' : '+x[1] for x in self.arg_map[flag]])

        # Too exhausting to parse everything, give custom and point to man
        param = self.__makeSelect(flag, opts, hlps)
        
        if flag == '-m':
            # <conditional>
            #  <param bool>
            #  <when false><param select /></when>
            #  <when true > <param text  /></when>

            conditional = doc.createElement('conditional')
            conditional.setAttribute('name','cond_model')
            conditional.setAttribute('title', 'Model Parameters')

            param_bool = doc.createElement('param')
            param_bool.setAttribute('name',  'opt_custommodel' )
            param_bool.setAttribute('label', 'Use Custom Model' )
            param_bool.setAttribute('help',  'See http://www.iqtree.org/doc/Substitution-Models')
            param_bool.setAttribute('value', 'false')

            when_false = doc.createElement('when')
            when_false.setAttribute('value', 'false')
            
            when_true = doc.createElement('when')
            when_true.setAttribute('value','true')

            param_true = doc.createElement('param')
            param_true.setAttribute('type', 'text')
            param_true.setAttribute('value', 'Model')
            param_true.setAttribute('argument', '-m')

            when_true.appendChild(param_true)
            when_false.appendChild(param)

            conditional.appendChild(param_bool)
            conditional.appendChild(when_true)
            conditional.appendChild(when_false)

            return conditional
    
        return param

        # Unimplemented -- these are all essentially just custom settings for the -m flag.
        #                  which can be encapsulated by a text box.
        #
        # Subsections
        #if self.sub_type == "DataType":
        #    import pdb; pdb.set_trace()
        #    vals = ""
            #return __makeSelect
        #
        #                      
        #if self.sub_type == "FreqType":
        #    # nani
        #    return "todo"
        #            
        #if self.sub_type == "RateType":
        #    # kore
        #    return "todo"
        #
        #return "Lizards."
