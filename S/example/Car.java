package example;
import example.Auto;
import example.SM;
public class Car extends Auto {
	public Car() {
		this.__ns = 3;
		try {
 
        System.out.println("CAR: Off (constructor)"); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
	public void reverse() {
		boolean __wis = this.__is;
		if(!this.__checkTrans(3)) {
			if(!__wis) {
				this.__is = false;
			}
			super.reverse();
			return;
		}
		try {
 
        System.out.println("CAR: Reverse (from Forward)."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
}
