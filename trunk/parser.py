
# ----------------------------------------------------------------------
# StateJava: parser.py
#
# Copyright (C) 2009, 
# Peter Goodman,
# All rights reserved.
#
# This is the StateJava parser. This parser parses a subset of the Java
# (TM) language. It does not attempt to correctly parse the language
# according to the specification.
#
# ----------------------------------------------------------------------

from __future__ import with_statement
from ply import lex
from sets import Set
from java_type import JavaType
from java_method import JavaMethod
import lexer, sys

# ----------------------------------------------------------------------

look_ahead = [ ]
generic_klass_types = None
java_lexer = lex.lex(module=lexer)
curr_lexer = None
klass = None
seen_klass_states = False
inherited_modifiers = ("public", "protected", )
stateful_modifiers = ("public", )

# ----------------------------------------------------------------------

class NoTokensLeftException(Exception):
    pass

class ParseError(Exception):
    pass

# ----------------------------------------------------------------------

def parse_file(file_path):
    global look_ahead, java_lexer, curr_lexer, klass, klass_id
    global seen_klass_states
    
    del look_ahead[:]
    
    curr_lexer = java_lexer.clone()
    klass = JavaType(file_path)
    
    try:
        with open(file_path) as f:
            curr_lexer.input(f.read())
            seen_klass_states = False
            parse_class_file()
            print "Parsed file:", file_path
    except ParseError, e:
        sys.stderr.write("Parse Error: %s \n" % e)
        return None
    except NoTokensLeftException, e:
        sys.stderr.write(
            "Parse Error: Unexpected end of input in file %s. \n"
            % klass.file
        )
        return None
    return klass

# ----------------------------------------------------------------------

def get_token():
    global look_ahead, curr_lexer
    if len(look_ahead):
        tok = look_ahead.pop()
    else:
        tok = curr_lexer.token()
        if not tok:
            raise NoTokensLeftException()
    
    return tok

def peek_token():
    tok = get_token()
    pushback_token(tok)
    return tok

def pushback_token(tok):
    global look_ahead
    look_ahead.append(tok)

def accept(*types):
    tok = get_token()
    if len(types) and tok.type not in types:
        raise ParseError(
            ("Unexpected token '%s' of type '%s', expected type of " +
             "%s in %s:%d")
            % (tok.value, tok.type, types, klass.file, tok.lineno)
        )
    return tok

def maybe(*types):
    tok = get_token()
    if tok.type not in types:
        pushback_token(tok)
        return False
    return tok

def peek(*types):
    tok = peek_token()
    if not len(types) or tok.type in types:
        return tok
    return False
    
def repeat(predicate):
    while predicate():
        pass

# ----------------------------------------------------------------------

def erase_types(parts, fmt):
    """
    erase_types(list, string) -> dict
    
    This performs very simple recursive type erasure over a list of 
    (name, generic_part) pairs, where generic_part may also be such a
    list. If there is generic_part then the name is not type-erased;
    however, if no such generic part is there then the name is added to
    the dict as the erased value of fmt % i, where i is the ith erased
    type.
    """
    erased_types = { }
    
    i = 0
    while parts and len(parts):
        name, generic_part, _ = parts.pop()
        if not generic_part:
            erased_types[name] = fmt % i
            i += 1
        else:
            parts.extend(generic_part)
    
    return erased_types

def erased_type(type_name, inferred_method_types):
    """
    erased_type(string, {}) -> string

    Return the erased type for type_name.
    """
    global generic_klass_types

    # look at the non-array portion
    if type_name in generic_klass_types:
        return generic_klass_types[type_name]
    elif type_name in inferred_method_types:
        return inferred_method_types[type_name]

    return type_name

# ----------------------------------------------------------------------

def parse_class_file():
    """
    parse_class_file(void) -> void
    
    Parse a Java class file. A class file can contain a series of
    imports followed by either a class or interface definition.
    """
    global klass, generic_klass_types
    
    start_header = end_header = 0
    
    # imports
    start_import = peek("IMPORT", "PACKAGE")
    end_import = None
    while maybe("IMPORT", "PACKAGE"):  
        maybe("DEF_MODIFIER") # static
        repeat(lambda: maybe("PERIOD", "ID", "MUL"))
        end_import = accept("SEMICOLON")
    
    klass.import_span = (
        end_import and (start_import.lexpos, end_import.lexpos+1) or None
    )
    
    # public/private/static/abstract for class/interface
    start_header = peek().lexpos
    repeat(lambda: maybe("DEF_MODIFIER"))
    
    if accept("CLASS", "INTERFACE").type == "INTERFACE":
        klass.is_interface = True
    
    # generic types in the class
    klass.name, generic_part, _, _ = parse_type()
    generic_klass_types = erase_types(generic_part, "$C%d")
    
    # extended classes
    if not klass.is_interface:
        if maybe("EXTENDS"):
            parent_type, _, _, _ = parse_type()
            klass.parents.add(parent_type)
    
    # implemented interfaces
    if maybe(klass.is_interface and "EXTENDS" or "IMPLEMENTS"):
        cont = True
        while cont:
            parent_type, _, _, _ = parse_type()
            klass.parents.add(parent_type)
            cont = maybe("COMMA")
    
    #print "SUPERTYPES:", klass.parents
    end_header = peek().lexpos
    parse_class_body()
    
    klass.header_span = (start_header, end_header)

def parse_class_body():
    """
    parse_class_body(void) -> void
    
    Parse the body of a Java interface or class. This starts from the
    first { and goes until the final }
    """
    accept("LBRACE")
    while not maybe("RBRACE"):
    
        # state list
        if maybe("STATES"):
            global seen_klass_states
            
            if seen_klass_states:
                raise ParseError(
                    "Class state set already defined in %s." % klass.file
                )
            elif klass.is_interface:
                raise ParseError(
                    "Interface cannot have state set in %s." % klass.file
                )
                
            seen_klass_states = True
            accept("LBRACE")
            parse_states(klass.states)
            accept("RBRACE")
            #print "STATES:", klass.states
        
        # method or attribute
        elif peek("DEF_MODIFIER"):
            
            start_header = peek("DEF_MODIFIER").lexpos
            end_header = 0
            
            inherit, can_have_states = parse_modifiers()
            inferred_types = { }
            is_method = False
            can_have_states = can_have_states and not klass.is_interface
            
            # we are looking at a method that has some inferred types
            if peek("LT"):
                is_method = True
                inferred_types = erase_types(
                    parse_parameratization(), 
                    "$M%d"
                )

            # type of param / method
            return_type = erased_type(parse_type()[0], inferred_types)

            # are we looking at a constructor?
            is_constructor = False
            paren = peek("LPAREN")
            if paren:
                if return_type != klass.name:
                    raise ParseError(
                        "Method missing return type in %s:%d."
                        % (klass.file, paren.lineno)
                    )
                is_method = is_constructor = True
                name = return_type
                return_type = "$Self"
            else:
                name = accept("ID").value
                is_constructor = False
            
            if is_method or peek("LPAREN"):
                
                line_num = peek().lineno
                
                # method parameters
                param_types, param_names, type_bounds = parse_method_params(
                    inferred_types
                )
                end_header = peek().lexpos - 1
                
                # state transitions
                transitions = None                
                if can_have_states:
                    # starting state for the class constructor, no trans
                    if is_constructor:
                        if peek("STATE"):
                            state = accept("STATE").value
                            name = "$C" # normalize constructor name
                            klass.constructor_states.add(state)
                            transitions = [(Set(("$0",)), state)]

                    # normal public method
                    else:
                        transitions = parse_method_states()
                
                # method body
                start_body = end_body = 0
                if not klass.is_interface:
                    start_body, end_body = parse_method_body()
                else:
                    accept("SEMICOLON")
                
                # add the method to the type
                types = [return_type,]
                types.extend(param_types or [ ])
                
                if not can_have_states:
                    klass.add_non_state_method(
                        (start_header, end_header),
                        (start_body, end_body),
                        name,
                        tuple(types)
                    )
                else:
                    klass.add_state_method(JavaMethod(
                        name = name,
                        
                        # type signature of this method, this includes
                        # return type and param types
                        signature = tuple(types),
                        
                        # names of the parameters, needed for state
                        # method specialization (when calling parent
                        # method) and for param renaming (when two
                        # methods with the same name/signature need to
                        # by merged but accept different parameter
                        # names)
                        param_names = param_names,
                        
                        # the lexical bounds around the method param
                        # types, needed for param renaming
                        type_bounds = type_bounds, 
                        
                        # positional info
                        line = line_num,
                        file = klass.file,
                        is_constructor = is_constructor,
                        klass = klass,
                        transitions = transitions,
                        can_have_states = can_have_states,
                        
                        # lexical spans of the header and body of this
                        # method
                        header_span = (start_header, end_header),
                        body_span = (start_body, end_body)
                    ))
            
            # go and find the end of this parameter declaration. this
            # does scans until it finds the first semicolon and then
            # accepts it as the end
            else:
                end_header = accept("EQUALS", "SEMICOLON")
                if end_header.type == "EQUALS":
                    repeat(lambda: (not peek("SEMICOLON")) and accept())
                    end_header = accept("SEMICOLON")
                end_header = end_header.lexpos+1
                klass.add_param(name, (start_header, end_header))
        else:
            tok = peek()
            raise ParseError(
                "Unexpected token '%s' of type '%s' found in class body."
                % (tok.value, tok.type)
            )

def parse_method_body():
    """
    perse_method_body(void) -> (int, int)
    
    Consume tokens until what looks like the end of the method is 
    reached. Return the pair of start and end offsets.
    """
    start = accept("LBRACE")
    brace_count = 0
    
    while True:
        tok = accept()
        if tok.type == "LBRACE":
            brace_count += 1
        elif tok.type == "RBRACE":
            brace_count -= 1
            if brace_count < 0:
                pushback_token(tok)
                break
    
    return start.lexpos, accept("RBRACE").lexpos

def parse_method_states():
    """
    parse_method_states() -> (Set | None, string | None)
    
    Parse the state transitions for a method.
    """
    transitions = [ ]
    next_is_state = peek("MUL", "STATE")    
    from_states = klass.states # default for identity
    to_state = None
    found_states = False
    
    while next_is_state:
        found_states = True
        if next_is_state.type == "MUL":
            accept("MUL")
        else:
            from_states = Set()
            parse_states(from_states)
        accept("STATE_TRANS")
        transitions.append((from_states, accept("STATE").value))
        next_is_state = maybe("SEMICOLON") and peek("MUL", "STATE") or False
    
    return transitions

def parse_method_params(inferred_method_types):
    """
    parse_method_params(dict) -> (tuple, tuple)
    
    Parse out the list of method parameters and return the erased base
    types as a tuple. If void is the only type, or there are no types,
    then return an empty tuple.
    """
    global generic_klass_types
    
    accept("LPAREN")
    types = [ ]
    names = [ ]
    bounds = [ ]
    
    next = peek()
    if (next.type == "ID" and next.value != "void") or next.type != "RPAREN":
        cont = True
        while cont:
            type_name, _, array_part, type_bounds = parse_type()
            bounds.append(type_bounds)
            names.append(accept("ID").value)
            type_name = erased_type(type_name, inferred_method_types)
            if array_part:
                type_name += "[]" * len(array_part)
            types.append(type_name)
            cont = maybe("COMMA")
    
    accept("RPAREN")
    
    return tuple(types), tuple(names), bounds

def parse_states(set):
    """
    parse_states(Set) -> void
    
    Parse a list of zero or more comma separated states.
    """
    cont = peek("STATE")
    while cont:
        set.add(accept("STATE").value)
        cont = maybe("COMMA")
    
def parse_modifiers():
    """
    parse_modifiers(void) -> Bool
    
    Consume one or more visibility modifiers (public, private, protected,
    static, abstract) and return whether or not a modifier from the list
    of inherited_modifiers was consumed.
    """
    global inherited_modifiers, stateful_modifiers
    seen = has_stateful = False
    not_static = True
    mod = accept("DEF_MODIFIER")
    while mod:
        not_static = mod.value != "static" and not_static
        seen = seen or mod.value in inherited_modifiers
        has_stateful = (has_stateful or mod.value in stateful_modifiers)
        mod = maybe("DEF_MODIFIER")
        
    return not_static and seen, not_static and has_stateful

def parse_type():
    """
    parse_type(void) -> (string, list | Bool, tuple | Bool)
    
    Parse a Java type. A type is an identifier followed by an optional
    generic component, followed by an optional array component.
    """
    type_ident = accept("ID")
    return (
        type_ident.value,
        peek("LT") and parse_parameratization(),
        peek("LBRACKET") and parse_array_bounds(),
        (type_ident.lexpos, peek().lexpos - 1),
    )
    
def parse_parameratization():
    """
    parse_parameratization(void) -> list
    
    Parse Java type parameters and return a tree of said parameters.
    """
    accept("LT")
    cont = True
    parts = [ ]
    while cont:
        parts.append(parse_type())
        cont = maybe("COMMA")
    accept("GT")
    return parts

def parse_array_bounds():
    """
    parse_array(void) -> tupe
    
    Parse the array component of a type, and record the bounds therein.
    If a part is given no bound then -1 is used, otherwise the integer
    value is recorded.
    """
    bounds = [ ]
    while maybe("LBRACKET"):
        bound = maybe("NUMBER")
        bounds.append(bound and int(bound.value) or -1)
        accept("RBRACKET")
    return tuple(bounds)
