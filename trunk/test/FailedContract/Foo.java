
package test.FailedContract;
import test.FailedContract.Contract;

class Foo implements Contract {
    states { :A }
    public Foo() :A { }
}