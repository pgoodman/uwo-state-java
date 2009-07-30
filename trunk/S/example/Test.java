
package example;
import example.Car;

public class Test {
    static public void main(String[] args) {
        Car car = new Car();
        car.turnOn();
        car.forward();
        car.reverse(); /* Car::reverse() specialization */
        car.neutral();
        car.reverse(); /* Auto::reverse() */
        car.turnOff();
    }
}