
package test.UnreachableStates;

/**
 * This test is to show that the system detects unreachable states, even
 * if they are used. States :B, :C, and :D are unreachable.
 */
class Foo {
    states { :A, :B, :C, :D }
    public Foo() :A { }
    public void bar() :B -> :A { }
    public void baz() :C -> :D { }
    public void baz() :D -> :C { }
}