package example;
import example.Auto;
import example.SM;
public class Car extends Auto {
	public Car() {
		this.__cs = 3;
		try {
 
        System.out.println("CAR: Off (constructor)"); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
	public void reverse() {
		this.__ps = this.__cs;
		if((this.__cs = SM.trans[this.__cs][3]) < 0) {
			this.__cs = this.__ps;
			super.reverse();
			return;
		}
		try {
 
        System.out.println("CAR: Reverse (from Forward)."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
}
