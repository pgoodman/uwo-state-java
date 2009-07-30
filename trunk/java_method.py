
# ----------------------------------------------------------------------
# StateJava: java_method.py
#
# Copyright (C) 2009, 
# Peter Goodman,
# All rights reserved.
#
# Classes representing a a single method in a file (JavaMethod) and a
# canonical method (JavaMethodSet).
#
# ----------------------------------------------------------------------

from sets import Set

class JavaMethodSet(Set):
    
    id_count = 0
    
    def __init__(self):
        Set.__init__(self)
        self._all_from_states = None
        self.has_parent_impl = False
        self._id = None
    
    def id(self):
        """
        id(void) -> int

        Get this ID of this method. This is put into a function so that
        we don't assign ids to all method instances when they might not
        be used in state classes.
        """
        if not self._id:
            self._id = JavaMethodSet.id_count
            JavaMethodSet.id_count += 1
        return self._id
    
    def add(self, method):
        """
        add(JavaMethod) -> void
        
        Add a method to this method set. Each method in the method set
        has the same name, type signature, and class.
        """
        Set.add(self, method)
        method.set = self
    
class JavaMethod(object):
    
    methods = Set()
    
    def __init__(self, **kargs):
        self.__dict__.update(kargs)
        self.has_parent_method = False
        self.set = None
        JavaMethod.methods.add(self)
    