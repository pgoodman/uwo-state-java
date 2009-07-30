
package test.ChildStateClassMissingConstructor;
import test.ChildStateClassMissingConstructor.Parent;

/**
 * This test is to show that a child class must cover all of its parents
 * constructors.
 */
class Child extends Parent {
    public Child(int a) :A { }
}