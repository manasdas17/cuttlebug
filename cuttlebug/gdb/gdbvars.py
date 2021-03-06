import gdb
import odict

class ParseError(Exception): pass

UNSPECIFIED = -1

VOID = 0
CHAR = 1
INT = 3
FLOAT = 4
DOUBLE = 5
STRUCT = 6
UNION = 7

SIGNED,UNSIGNED = 1,0

SHORT,LONG = 0,1

TYPES = {"void": VOID, "char":CHAR,"short": SHORT, "float":FLOAT, "int":INT, "long":LONG, "struct":STRUCT, "union":UNION}
SIZES = {"short":SHORT, "long":LONG}

class Type(object):
    @staticmethod
    def parse(type_string):
        parts = type_string.split()
        parts = [part.strip() for part in parts]
        volatile = "volatile" in parts
        static = "static" in parts

        size = UNSPECIFIED
        if "short" in parts: size = SHORT
        if "long" in parts: size = LONG

        pointer = False
        if parts[-1] == '*':
            parts.pop(-1)
            pointer = True

        if 'struct' in parts:
            type = STRUCT
        else:
            try: type = TYPES[parts[-1]]
            except KeyError:
                if size != UNSPECIFIED: type = INT
                else: raise ParseError("Could not parse type '%s'" % type_string)


        signed = UNSPECIFIED
        if type in (INT, CHAR):
            signed = "unsigned" not in parts
        
        return Type(static, volatile, signed, size, pointer, type)

    def __init__(self, static, volatile, signed, size, pointer, type):
        self.static = static
        self.volatile = volatile
        self.signed = signed
        self.size = size
        self.pointer = pointer
        self.type = type
        
    def __str__(self):
        static = "static " if self.static else ""
        volatile = "volatile " if self.volatile else ""
        signed = {SIGNED:"signed ", UNSIGNED:"unsigned ", UNSPECIFIED:""}[self.signed]
        type = {INT:"int ", CHAR:"char ", FLOAT:"float ", DOUBLE:"double ", VOID:"void ", UNSPECIFIED:""}[self.type]
        size = {SHORT:"short ", LONG:"long ", UNSPECIFIED:""}[self.size]
        pointer = "*" if self.pointer else ""
        return "%s%s%s%s%s%s%s" % (static, volatile, signed, size, type, pointer, self.value)

    def __repr__(self):
        return "<Type '%s'>" % str(self)
    
    def __cmp__(self, x):
        return  self.static == x.static and \
                self.volatile == x.volatile and \
                self.signed == x.signed and \
                self.size == x.size and \
                self.pointer == x.pointer and \
                self.type == x.type
                
class Variable(object):
    
    def __init__(self, name, expression, type, children=0, data=None):
        self.type = type
        self.data = data
        self.name = name
        self.expression = expression
        self.children = int(children)
    
    def __str__(self):
        if self.children:
            return "<Variable %s expr='%s' with %d children>" % (self.name, self.expression, self.children)
        else:
            return "<Variable %s %s=%s>" % (self.name, self.expression, self.data)

            
class GDBVarModel(object):

    def __init__(self, parent):
        self.parent = parent
        self.vars = odict.OrderedDict()
        self.exprs = {}

    def __str__(self):
        return "<GDBVarModel managing %d variables>" % len(self.vars)
    @staticmethod
    def parent_name(name):
        parts = name.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        else:
            return None
    
    def __iter__(self):
        return iter(self.vars)
    
    def __get_roots(self):
        return [name for name in self if '.' not in name]
    roots = property(__get_roots)
    
    def get_parent(self, name):
        parent = GDBVarModel.parent_name(name)
        if parent and parent not in self:
            raise Exception("Orphaned variable in GDBVarModel: %s" % name)
        return parent
    
    def add(self, name, variable):
        parent_name = GDBVarModel.parent_name(name)
        if parent_name and parent_name not in self:
            raise Exception("Attempt to add child variable before parent")
        self.vars[name] = variable
        if parent_name:
            parent = self.vars[parent_name]
            if name not in parent.data:
                parent.data.append(name)
        self.exprs[variable.expression] = name
        
    def remove(self, name):
        var = self.vars.pop(name)
        self.exprs.pop(var.expression)
                        
    def name_from_expr(self, expr):
        return self.exprs[expr]
    
    def __contains__(self, name):
        return name in self.vars
    
    def __getitem__(self, name):
        return self.vars[name]
    
    def __str__(self):
        retval = 'GDBVarModel\n'
        for name, var in self.vars.iteritems():
            retval += "%8s   %s\n" % (name, var)
        return retval