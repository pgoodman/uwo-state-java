package test.ConstructorNoState;

/**
 * Test case for a class with states but with a constructor that doesn't
 * define a starting state.
 */
class Foo {
    states { :A }
    public Foo() { }
}