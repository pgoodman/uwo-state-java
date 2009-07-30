
package example;
import example.Auto;

public class Car extends Auto {
   public Car() :Off { System.out.println("CAR: Off (constructor)"); }
      
   /* example of state specialization when overwriting parent class
      methods. */
   public void reverse() :Forward -> :Reverse { System.out.println("CAR: Reverse (from Forward)."); }
}