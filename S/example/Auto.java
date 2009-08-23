package example;
import example.SM;
public class Auto {
	protected int __cs, __ns;
	protected boolean __is = true;
	protected boolean __checkTrans(int method_id) {
		if(!this.__is) {
			this.__is = true;
			return (this.__ns = SM.trans[this.__cs][method_id]) >= 0;
		}
		return true;
	}
	protected void __doTrans() {
		if(this.__is) {
			this.__is = false;
			this.__cs = this.__ns;
		}
	}
	public void turnOff() {
		if(!this.__checkTrans(2)) {
			SM.error("Auto::turnOff", this.__cs);
		}
		try {
 
        System.out.println("AUTO: Off."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
	public void reverse() {
		if(!this.__checkTrans(4)) {
			SM.error("Auto::reverse", this.__cs);
		}
		try {
 
        System.out.println("AUTO: Reverse."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
	public Auto() {
		this.__ns = 3;
		try {
 
        System.out.println("AUTO: Off (constructor)"); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
	public void forward() {
		if(!this.__checkTrans(1)) {
			SM.error("Auto::forward", this.__cs);
		}
		try {
			switch(this.__cs) {
				case 2: {
 
        System.out.println("AUTO: Forward (from Neutral)."); 
    
					break;
				}
				case 0: {
 
        System.out.println("AUTO: Forward (from Reverse)."); 
    
					break;
				}
			}

		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
	public void neutral() {
		if(!this.__checkTrans(7)) {
			SM.error("Auto::neutral", this.__cs);
		}
		try {
 
        System.out.println("AUTO: Neutral."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
	public void turnOn() {
		if(!this.__checkTrans(0)) {
			SM.error("Auto::turnOn", this.__cs);
		}
		try {
 
        System.out.println("AUTO: On (Neutral)."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		} finally {
			this.__doTrans();
		}
	}
}
