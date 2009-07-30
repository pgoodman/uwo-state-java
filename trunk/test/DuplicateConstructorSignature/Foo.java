
package test.DuplicateConstructorSignature;

/**
 * This test is to show a non-deterministic choice of constructors.
 */
class Foo {
    states { :A, :B }
    public Foo() :A { }
    public Foo() :B { }
}