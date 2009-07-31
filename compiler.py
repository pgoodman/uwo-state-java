
# ----------------------------------------------------------------------
# StateJava: compiler.py
#
# Copyright (C) 2009, 
# Peter Goodman,
# All rights reserved.
#
# Source-to-source compiler for the State Java language. This module
# includes all main type checking routines.
#
# ----------------------------------------------------------------------

from __future__ import with_statement
from sets import Set
from parser import parse_file
import re, os, sys
from java_type import JavaType
from java_method import JavaMethod
from error import JTypeError, JStateError
import shutil

types = None             # string -> JavaType
type_list = None         # List<JavaType>
interface_names = None   # Set<string>
state_ids = None         # string -> int
project_dir = None       # string
method_ids = None        # {JavaMethod -> int}

def compile_project(project_dir):
    """
    compile_project(string) -> void
    
    Compile a state Java project into a Java project.
    """
    try:
        print "Compiling project '%s'..." % project_dir
        if parse_project(project_dir):
            print "Checking Types..."
            check_parents()
            rec_propagate(inherit_states, check_method_states)
            add_method_transitions()
            rec_propagate(inherit_method_transitions)
            check_contracts()
            check_state_reachability()

            print "Generating Code..."
            new_project_dir = compile_classes()
            print "Done; Project saved to: %s/." % new_project_dir
        else:
            print "Done; Please fix parse errors."
    except JStateError, e:
        sys.stdout.flush()
        sys.stderr.write("State Error: %s\n" % e)
    except JTypeError, e:
        sys.stdout.flush()
        sys.stderr.write("Type Error: %s\n" % e)

def state_classes():
    """
    state_classes(void) -> Generator<JavaType>

    Generate java types that have states.
    """
    for klass in type_list:
        if len(klass.states):
            yield klass

def state_methods():
    """
    state_methods(void) -> Generator<JavaMethod>

    Generate java methods that belong to state classes.
    """
    for method in JavaMethod.methods:
        if len(method.klass.states):
            yield method

def parse_project(root_dir):
    """
    parse_project(string) -> void
    
    Begin parsing a Java project. This function expects to be given the
    path to the root directory of the project.
    
    This function will then follow imports until no new Java files to
    parse can be found.
    
    !!! This function expects there to be one and only one class per
        file.
    
    !!! This does not allow two classes to be named the same, regardless 
        of if they are in entirely different sub-packages.
    """    
    global types, type_list, interface_names, state_ids
    global method_ids, project_dir
    
    types = { }
    type_list = [ ]
    interface_names = Set()
    state_ids = { }
    method_ids = { }
    
    is_java_file = re.compile(".*\.java$")
    project_dir = os.path.abspath(root_dir)
    had_errors = False
    
    if not os.path.isdir(project_dir):
        raise Exception("Invalid directory supplied: %s." % project_dir)
    
    # go and discover files to parse
    for dir_name, dir_names, file_names in os.walk(project_dir):            
        for file_name in file_names:
            
            if not is_java_file.match(file_name):
                continue
            
            klass = parse_file(os.path.join(dir_name, file_name))
            if klass:
                if klass.name in types:
                    raise JTypeError(
                        ("Two Java types cannot be named the same; " +
                         "in %s and %s.")
                        % (klass.file, types[klass.name].file)
                    )
                
                types[klass.name] = klass
                type_list.insert(klass.id, klass)
                
                # collect inteface names (for later)
                if klass.is_interface:
                    interface_names.add(klass.name)

                # collect all of the states (for later)
                for state in klass.states:
                    if state not in state_ids:
                        state_ids[state] = len(state_ids)
            else:
                had_errors = True
    return not had_errors

def check_parents():
    """
    check_parents(void) -> void
    
    Perform very simple type checking. If a class inherits from another
    that is not defined within the set of parsed classes then warn that
    the parent class cannot be checked and remove it from the set of
    parent classes.
    """
    to_remove = Set()
    for klass in type_list:
        for parent in klass.parents:
            if parent not in types:
                to_remove.add(parent)
                sys.stderr.write(
                    "WARNING: type/state participation cannot be " +
                    "enforced for supertype '%s' of type '%s' in %s.\n"
                    % (parent, klass.name, klass.file)
                )
            elif parent == klass.name:
                raise JTypeError(
                    "Type '%s' cannot extend/implement itself in %s."
                    % (parent, klass.file)
                )
        klass.parents.difference_update(to_remove)
        to_remove.clear()

def rec_propagate(each_fn, all_fn = (lambda x: x)):
    """
    rec_propagate(function, function) -> void

    General purpose method to propagate data from a parent class to
    a child class.
    """
    def propagate(klass, unseen_types):
        for parent in klass.parents:
            parent_klass = types[parent]
            if parent_klass.is_interface:
                continue
            if parent_klass in unseen_types:
                unseen_types.remove(parent_klass)
                propagate(parent_klass, unseen_types)
            each_fn(parent_klass, klass)
        all_fn(klass)

    # initialize, make a set of all classes
    unseen_types = Set()
    for t in type_list:
        if not t.is_interface:
            unseen_types.add(t)

    while len(unseen_types):
        klass = unseen_types.pop()
        propagate(klass, unseen_types)

def inherit_states(parent_klass, klass):
    """
    inherit_states(JavaType, JavaType) -> void
    
    Copy states from the parent class into the child class.
    """    
    # not allowed to inherit from a non-state class
    if len(klass.states) and not len(parent_klass.states):
        raise JStateError(
            ("Type '%s' cannot be a subtype of '%s'; " +
             "type has no states in %s.")
            % (klass.name, parent_klass.name, klass.file)
        )
    
    klass.states.update(parent_klass.states)
    
    # make sure that the class has a starting state
    if len(klass.states) and not len(klass.constructor_states):
        raise JStateError(
            ("No starting state for type '%s'; type must have a " +
             "public constructor in %s.") % (klass.name, klass.file)
        )

def check_method_states(klass):
    """
    check_method_states(JavaType) -> void
    
    Check that a class with method state transitions also has class 
    states. This is done after state propogation. Also, check that no
    non-existant states are used in method transitions.
    """
    if not len(klass.states) and len(klass.method_states):
        raise JStateError(
            ("Class '%s' defines state transitions but has no states " +
             "in %s.") % (klass.name, klass.file)
        )
    
    klass.method_states.difference_update(klass.states)
    if len(klass.method_states):
        raise JStateError(
            "Invalid state(s) %s used in %s."
            % (", ".join(klass.method_states), klass.file)
        )
    
    klass.method_states = None

def add_method_transitions():
    """
    add_method_transitions(void) -> void
    
    Add in the transitions to each class. This goes over all methods
    that have state transitions or can have transitions and 
    """
    
    def check_if_method_deterministic(method, other):
        klass.check_if_constructors(method, other)

        # two distinct methods of the same signature have the 
        # same starting state, i.e. non-deterministic
        inter_states = method.from_states & other.from_states        
        if len(inter_states):
            raise JStateError(
                "Non-deterministic transition from state(s) " +
                "%s in %s:%d and %s:%s."
                % (", ".join(inter_states), method.file, 
                   method.line, other.file, other.line)
            )
    
    for klass in state_classes():
        for method_set in klass.method_sets():
            unchecked = method_set.copy()
            
            # add in the transitions.
            for method in method_set:
                unchecked.remove(method)
                
                if method.is_constructor and not len(method.from_states):
                    raise JStateError(
                        "Missing initial state on class "+
                        "constructor in %s:%d." 
                        % (method.file, method.line)
                    )
                
                # go check for non-deterministic transitions, this
                # check is for local class only
                for other in unchecked:
                    check_if_method_deterministic(
                        method,
                        other
                    )
                
                # add in the transitions
                for state in method.from_states:
                    klass.add_transition(state, method)

def inherit_method_transitions(parent_klass, klass):
    """
    inherit_method_transitions(JavaType, JavaType) -> void

    Copy methods from the parent class into the child class.
    """
    
    for trans_from, trans_to, method in parent_klass.method_transitions():                    
        # constructors are not inherited
        if method.is_constructor:
            has_constructor = klass.has_transition(
                trans_from, 
                trans_to, 
                method.name, 
                method.signature
            )
            if not has_constructor:
                raise JTypeError(
                    ("Class '%s' is missing constructor " +
                     "'%s(%s)%s' from '%s'; in %s.")
                    % (klass.name, klass.name, 
                       ", ".join(method.signature[1:]),
                       trans_to, parent_klass.name, klass.file)
                )
        elif method.can_have_states:
            klass.add_transition(trans_from, method, inherit=True)        

def check_contracts():
    """
    check_contracts(void) -> void
    
    Check that each class has all of the methods that each of its
    implemented interfaces require it have for every state.
    """
    missing_methods = [ ]
    
    for klass in state_classes():
        for parent in klass.parents:
            if parent not in interface_names:
                continue
                
            interface = types[parent]

            # go and check that all of the methods from the interface
            # are represented as self-transitions in the current class
            # for *every* state
            for _, _, name, sig in interface.non_state_methods:
                for state in klass.states:
                    if not klass.has_transition(state, state, name, sig):
                        missing_methods.append((name, state))

            # if methods are missing then the class does not follow the
            # interfaces contract and so we have a type error
            if len(missing_methods):
                err_str = [ ]
                for name, state in missing_methods:
                    err_str.append(
                        ("    Missing method %s::%s (%s -> %s) from " +
                         "interface '%s'.\n") 
                        % (klass.name, name, state, state, parent)
                    )

                raise JTypeError(
                    ("Class '%s' is missing methods from interface " +
                     "'%s' in %s:\n%s")
                    % (klass.name, parent, klass.file, "".join(err_str))
                )

def check_state_reachability():
    """
    check_state_reachability(void) -> void
    
    Perform reachability checks on each state of each class.
    """
    newly_reachable = Set()
    
    for klass in state_classes():
        reachable = klass.constructor_states.copy()
        transitions = Set(klass.transitions.keys())
        keep_going = True
        
        # check state reachability by transitivity
        while keep_going and len(transitions):
            keep_going = False
            for from_state, to_state in transitions:
                if from_state in reachable:
                    keep_going = True
                    reachable.add(to_state)
                    newly_reachable.add((from_state, to_state))
            
            # reduce the size of the transitions set if a state was 
            # reached
            if keep_going:
                transitions.difference_update(newly_reachable)
                newly_reachable.clear()
        
        # arr!
        unreachable = klass.states.difference(reachable)
        if len(unreachable):
            raise JStateError(
                "Unreachable state(s) %s in class '%s' in %s."
                % (", ".join(unreachable), klass.name, klass.file)
            )

def make_trans_table():
    """
    make_trans_table(void) -> matrix
    
    Make the state transition table. The table is used as:
    [current-state-id][current-method-id] -> new-state-id
    Each method id represents a method set, and each state id represents
    one of the various states.
    """
    m = [ ]
    num_methods = len(method_ids)
    
    # build the base table
    for _ in state_ids:
        m.append([-1] * num_methods)
    
    # collect the methods. this will collect the same method several
    # times (as a result of inheritance / many start states), but 
    # that's not an issue!
    for klass in state_classes():        
        for from_state, to_state, method in klass.method_transitions():
            j = m[state_ids[from_state]][method_ids[method]]
            m[state_ids[from_state]][method_ids[method]] = state_ids[to_state]
                    
    return m

def compile_trans_class_file(package_name, new_project_dir):
    """
    compile_trans_class_file(string, string) -> Bool
    
    Make the state transition class file, SM.java.
    """
    m = make_trans_table()
    if not len(m):
        return False
    
    with open("%s/SM.java" % (new_project_dir), "w") as f:
        f.write("package %s;\n" % package_name)
        f.write("final public class SM {\n")
        f.write(
            "\tfinal static public String[] states = new String[%s];\n" 
            % len(state_ids)
        )
        
        # state name table
        f.write("\tstatic {\n")
        for state, state_id in state_ids.items():
            f.write("\t\tstates[%d] = \"%s\";\n" % (state_id, state))
        f.write("\t}\n")
        
        # transition table
        f.write("\tfinal static public int[][] trans = {\n")
        sep = "\t\t"
        for i in state_ids.values():
            f.write("%s{%s  }" % (sep, ",".join(("%3d" % j) for j in m[i])))
            sep = ",\n\t\t"
        f.write("\n\t};\n")
        
        # error function
        f.write("\tstatic public void error(String method, int state) {\n")
        f.write(
            "\t\tSystem.out.println(\"Error: cannot call method "+
            "'\"+method+\"' from state '\"+states[state]+\"'.\");\n"
        )
        f.write("\t\tSystem.exit(1);\n")
        f.write("\t}\n")
        f.write("}\n")
    return True

def compile_state_method(klass, method_set, nf, old):
    """
    compile_state_method(JavaMethodSet, file, string) -> void
    
    Compile a single method. This takes in a set of methods. If the
    set has many methods in it then those methods will be merged within
    the body of a switch statement.
    """
    method = base_method = method_set.pop()
    nf.write("\t")
    nf.write(old[method.header_span[0]:method.header_span[1]])
    nf.write(" {\n")
    
    # method to generate the call to a parent method. this takes into
    # account the methods return type and deals with it accordingly.
    def call_parent_impl():
        s = "\t\t\treturn super.%s(%s);\n"
        if base_method.signature[0] == "void":
            s = "\t\t\tsuper.%s(%s);\n\t\t\treturn;\n"
        return s % (base_method.name, ", ".join(base_method.param_names))
    
    # if we have many state methods within one state then we need to
    # make sure that each one is being given the proper variable names.
    def normalize_var_names(param_names, type_bounds):
        things = zip(base_method.param_names, param_names, type_bounds)
        for old_param, new_param, param_bounds in things:
            if old_param != new_param:
                nf.write(
                    "\t\t\t\t%s %s = %s;\n" % (
                        old[param_bounds[0]:param_bounds[1]],
                        new_param, 
                        old_param,
                    )
                )
    
    # constructor, initialize the class to a state.
    if method.is_constructor:
        nf.write(
            "\t\tthis.__cs = %d;\n" % state_ids[method.to_state]
        )
    
    # normal state method
    else:
        nf.write("\t\tthis.__ps = this.__cs;\n")
        nf.write(
            "\t\tif((this.__cs = SM.trans[this.__cs][%d]) < 0) {\n" 
            % method_ids[method]            
        )
        
        # defer check to parent class implementation. this mechanism
        # allows for specialization of parent methods on a state level.
        if method_set.has_parent_impl:
            nf.write("\t\t\tthis.__cs = this.__ps;\n")
            nf.write(call_parent_impl())
        
        # base case: no parent, error
        else:
            nf.write(
                "\t\t\tSM.error(\"%s::%s\", __ps);\n" 
                % (klass.name, method.name)
            )
        
        nf.write("\t\t}\n")
    
    nf.write("\t\ttry {\n")
    
    # the method set contains at least two methods, i.e. we need to merge the
    # bodies of many methods into one method.
    if len(method_set):
        method_set.add(method)
        nf.write("\t\t\tswitch(this.__ps) {\n")
        
        for method in method_set:
            nf.write("\t\t\t")
            for from_state in method.from_states:
                nf.write("case %d: " % state_ids[from_state])
            nf.write("\n\t\t\t{\n")
            
            # make sure that method parameter names are adjusted if the
            # various methods use different param names (but with the same
            # types, of course)
            normalize_var_names(method.param_names, method.type_bounds)
            
            nf.write(old[method.body_span[0]:method.body_span[1]][1:])
            nf.write("\n\t\t\t}\n")
            nf.write("\t\t\tbreak;\n")
        nf.write("\t\t\t}\n")
    
    # life is easy, only one method to deal with
    else:
        nf.write(old[method.body_span[0]:method.body_span[1]][1:])
    
    nf.write(
        "\n\t\t} catch(Exception e) {\n\t\t\tSystem.out.println(e);" +
        "\n\t\t\tSystem.exit(1);\n\t\t}\n"
    )
    
    nf.write("\t}\n")

def compile_non_state_method(header_span, body_span, nf, old):
    """
    compile_non_state_method((int, int), (int, int), file, string)
    
    Copy a non-state method into the class.
    """
    nf.write("\t")
    nf.write(old[header_span[0]:header_span[1]])
    nf.write(" {\n")
    nf.write(old[body_span[0]:body_span[1]][1:])
    nf.write("\n\t}\n")

def compile_class_file(klass, package_name, of, nf):
    """
    compile_class_file(JavaType, string, file, file)
    
    Compile a single class file.
    """
    old = of.read()
    
    # import statements
    if klass.import_span:
        nf.write(old[klass.import_span[0]:klass.import_span[1]])
        nf.write("\n")
    nf.write("import %s.SM;\n" % package_name)
    
    nf.write(old[klass.header_span[0]:klass.header_span[1]])
    nf.write("{\n")
    
    # previous and current state parameters
    if not len(klass.parents):
        nf.write("\tprotected int __cs, __ps;\n")
    
    # params
    for name, (start_param, end_param) in klass.params.values():
        nf.write(old[start_param:end_param])
        nf.write("\n")
    
    # state transitioning methods
    for method_set in klass.method_sets():
        compile_state_method(klass, method_set, nf, old)
    
    # non-state methods
    for header_span, body_span, _, _ in klass.non_state_methods:
        compile_non_state_method(header_span, body_span, nf, old)
    
    nf.write("}\n")

def compile_classes():
    """
    compile_classes(void) -> void
    
    Compile a State Java project into a Java project.
    """
    
    # make the set of method sets
    for method in state_methods():
        method_ids[method] = method.set.id()
    
    # resolve and make our new project directory
    package_name = os.path.basename(project_dir)
    new_project_dir = os.path.abspath(
        "%s/../S/%s" % (project_dir, package_name)
    )
    if not os.path.isdir(new_project_dir):
        os.makedirs(new_project_dir)
    
    # make the main state machine class that will allow for simple
    # state inheritence
    use_states = compile_trans_class_file(package_name, new_project_dir)
    
    for klass in type_list:
        
        # figure out our new file name and create the directory
        # structure if it's missing
        new_file = os.path.abspath(
            "%s/%s" % (new_project_dir, klass.file[len(project_dir):])
        )
        new_dir = os.path.dirname(new_file)
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
        
        if not use_states or not len(klass.states):
            shutil.copyfile(klass.file, new_file)
        else:
            with open(klass.file, "r") as old_file:
                with open(new_file, "w") as new_file:
                    compile_class_file(
                        klass, 
                        package_name, 
                        old_file, 
                        new_file
                    )

    return new_project_dir

def test_compiler():
    """
    test_compiler(void) -> void
    
    Run the compiler through the basic failure test cases. Each test should
    result in either a failure or a warning.
    """
    tests = (
        "./test/ConstructorNoState",
        "./test/ChildConstructorNoState",
        "./test/MethodStateNotStateClass",
        "./test/UncheckTypeStateParticipation",
        "./test/StateClassNoConstructor",
        "./test/ChildStateClassNoConstructor",
        "./test/ChildStateClassMissingConstructor",
        "./test/DuplicateConstructorSignature",
        "./test/UnknownState",
        "./test/NonDeterministicTrans",
        "./test/UnusedStates",
        "./test/UnreachableStates",
        "./test/NonStateInherit",
        "./test/FailedContract",
    )
    for test in tests:
        print "\n-------------------------------------------"
        print "Testing: %s" % test
        print "-------------------------------------------\n"
        compile_project(test)
    print "\n-------------------------------------------"
    print "Done testing."

if __name__ == "__main__":
    compile_project("./example/")
    #test_compiler()
