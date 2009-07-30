package test.MethodStateNotStateClass;

/**
 * Test case for a class without states but with a method that has a 
 * state transition.
 */
class Foo {
    public void moo() :A -> :B { }
}