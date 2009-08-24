
package test.FailedParentContract;
import test.FailedParentContract.Contract;

class Foo implements Contract {
    states { :A }
    public Foo() :A { }
    public void bar() :A -> :A { }
}