
package test.ChildStateClassMissingConstructor;

class Parent {
    states { :A, :B }
    public Parent(int a) :A { }
    public Parent() :B { }
}