#!/usr/bin/env python3

class CommandParse:

    def __init__(self, flag_map, exclusion_map):
        self.fmap = flag_map
        self.exclude = exclusion_map

        print("<command>iqtree")
        self.parseArgs()
        print("</command>")

      

    @staticmethod
    def toName(arg):
        if arg.startswith("--"):
            return arg[2:]

        if arg.startswith("-"):
            return arg[1:]

        print("Error parsing", arg, file=sys.stderr)
        exit(-1)


    def parseArgs(self):
        
        for flag in self.fmap:

            ftype, fdefault, fdescr = self.fmap[flag]
            fname = CommandParse.toName(flag)
           
            if flag in self.exclude:
                #import pdb; pdb.set_trace()
                val = self.exclude[flag]
                if val != False:
                    print("%s %s" % (flag,val))
                    continue
            

            # text, integer, float, file, boolean
            #
            if ftype == "boolean":
                # just print the var name, trueval and falseval fill the gap
                print("$%s" % fname)

            else:
                print('''
#if $%s
%s $%s
#end if'''             % (fname, flag, fname))
                      
