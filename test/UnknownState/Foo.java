
package test.UnknownState;

/**
 * This test is to show that the system will error when an undefined
 * state is used in a transition.
 */
class Foo {
    states { :A }
    public Foo() :A { }
    public void bar() :B -> :A { }
}