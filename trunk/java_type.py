
# ----------------------------------------------------------------------
# StateJava: java_type.py
#
# Copyright (C) 2009, 
# Peter Goodman,
# All rights reserved.
#
# Class representing a single Java (TM) type (class or interface).
#
# ----------------------------------------------------------------------

from sets import Set
from error import *
from java_method import JavaMethodSet

class JavaType(object):
    """
    A Java Type. This is used to model interfaces, classes, and abstract 
    classes in Java. Types are stores with any generic properties erased. 
    This is essentially a value object as it is built up as the parser 
    runs its course.
    """
    
    id = 0
    
    def __init__(self, class_file):
        """
        JavaType(string, Bool)
        
        Construct a new Java type.
        """
        
        self.file = class_file
        self.name = None
        
        # dictionary of method sets indexed by method type signature
        # each method set contains methods from the same class with the
        # same type signature
        self.state_methods = { }
        
        # a list of non-state transitioning methods (static, private,
        # protected)
        self.non_state_methods = [ ]

        self.params = { } # instance variables
        self._transitions = { } # dictionary indexed by state transition
        
        # set of all states used in method transitions
        self.method_states = Set()
        self.constructor_states = Set() # set of initialization states
        self.states = Set() # set of all class states
        
        # set of names of parent types. this ends up having any non-type-
        # checkable names removed
        self.parents = Set()
        
        self.is_interface = False
        self.header_span = None # bounds for the header of the class
        self.import_span = None # bounds for the imports / package
        
        self.id = JavaType.id
        JavaType.id += 1
    
    def add_param(self, name, header):
        """
        add_param(string, (int, int)) -> void
        
        Add a class parameter to this type.
        """
        if name in self.params:
            raise JTypeError(
                ("Parameter '%s' in class '%s' cannot be " +
                 "defined more than once in %s.") 
                % (name, self.name, self.file)
            )
            
        self.params[name] = (name, header)
    
    def add_non_state_method(self, *info):
        """
        add_non_state_method(tuple, tuple, string, tuple) -> void
        
        Add a non-state method to the class. These include static,
        protected, and private methods for normal classes, as well as
        all methods for interfaces.
        """
        self.non_state_methods.append(info)
    
    def add_state_method(self, method):
        """
        add_state_method(string, JavaMethod) -> void
        
        Add in a method implementation. Adding in the transitions on
        these methods is deferred until all of a classes states are
        known.
        
        !!! This method assumes that the method being added is from the
            class that it is being added to.
        """            
        # add the method
        if method.name not in self.state_methods:
            self.state_methods[method.name] = { }
        
        # update the method state set
        for from_state, to_state in method.transitions():
            if not method.is_constructor:
                self.method_states.add(from_state)
            self.method_states.add(to_state)
        
        # assume (for now) that no conflicts exist in method/state
        # signatures
        d = self.state_methods[method.name]
        if method.signature not in d:
            d[method.signature] = JavaMethodSet()
        
        d[method.signature].add(method)
    
    def add_transition(self, from_state, to_state, method, inherit=False):
        """
        add_transition(string, string, JavaMethod) -> void
        
        Add a transition to this class. If a method with the same name, 
        signature, and state transition already exists in the current
        class then don't overwrite it.
        """
        key = (from_state, method.name, method.signature)
        if key not in self._transitions:
            self._transitions[key] = [ ]
            self._transitions[key].append((method, to_state))
        
        # check for transition specialization
        elif inherit:
            if method.name in self.state_methods:
                d = self.state_methods[method.name]
                if method.signature in d:
                    d[method.signature].has_parent_impl = True
        
        # check for a non-deterministic transition
        else:
            for o_method, o_to_state in self._transitions[key]:
                if o_method.klass is method.klass and o_to_state != to_state:
                    if method.is_constructor:
                        raise JStateError(
                            "Two constructors with the same type signature "+
                            "initialize to different states in %s:%d and %s:%s."
                            % (method.file, method.line, o_method.file, 
                               o_method.line)
                        )
                    else:
                        raise JStateError(
                            "Non-deterministic transition from state " +
                            "%s in %s:%d and %s:%s." % (from_state, method.file, 
                            method.line, o_method.file, o_method.line)
                        )
    
    def has_transition(self, from_state, to_state, name, signature):
        """
        has_transition(string, string, string, string) -> Bool
        
        Check whether or not the current type has a method that matches
        the type signature of the JavaMethod instance passed in.
        """
        key = (from_state, name, signature)
        if key in self._transitions:
            for _, dest_state in self._transitions[key]:
                if dest_state == to_state:
                    return True
        return False
    
    def transitions(self):
        """
        method_transitions(void) -> Generator<tuple(string, string, JavaMethod)>

        Generate the methods and their state transitions.
        """
        for key in self._transitions:
            for method, to_state in self._transitions[key]:
                yield key[0], to_state, method
        
    def method_sets(self):
        """
        method_sets(void) -> Generator<JavaMethodSet>
        
        Generate this type's method sets.
        """
        for method_sigs in self.state_methods.values():
            for method_set in method_sigs.values():
                yield method_set
    
    def methods(self):
        for method_set in self.method_sets():
            for method in method_set:
                yield method
    