
package test.UnusedStates;

/**
 * This test is to show that the system detects unused states as
 * unreachable.
 */
class Foo {
    states { :A, :B, :C, :D }
    public Foo() :A { }
    public void bar() :A -> :B { }
}