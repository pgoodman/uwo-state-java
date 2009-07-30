
package example;

public class Auto {
    states { :Forward, :Neutral, :Reverse, :Off }
    
    public Auto() :Off { System.out.println("AUTO: Off (constructor)"); }
    
    /* the turnOff method shows a motivation for having the ability to
       remember a previous state. */
    public void turnOn() :Off -> :Neutral { System.out.println("AUTO: On (Neutral)."); }
    
    /* the following methods ass a motivation for having the ability to
       perform set operations, such as difference, on states. */
    
    public void turnOff() :Forward, :Neutral, :Reverse -> :Off { System.out.println("AUTO: Off."); }
    
    /* this will be specialized by Car::reverse() */
    public void reverse() :Forward, :Neutral -> :Reverse { System.out.println("AUTO: Reverse."); }
    
    public void neutral() :Forward, :Reverse -> :Neutral { System.out.println("AUTO: Neutral."); }
    
    /* example of method merging */
    public void forward() :Neutral -> :Forward { System.out.println("AUTO: Forward (from Neutral)."); }
    public void forward() :Reverse -> :Forward { System.out.println("AUTO: Forward (from Reverse)."); }
}