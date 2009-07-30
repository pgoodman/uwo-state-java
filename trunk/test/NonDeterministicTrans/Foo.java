
package test.NonDeterministicTrans;

/**
 * This test is to show that the system will error when there exist two
 * distinct methods with the same names and type signatures and the same
 * starting state. In this, the first bar() is an identity transition and
 * thus transitions from :A -> :A and from :B -> :B. The second bar()
 * transitions from :A -> :B, which conflicts with bar() :A -> :A.
 */
class Foo {
    states { :A, :B }
    public Foo() :A { }
    
    
    public void bar() { }
    public void bar() :A -> :B { }
}