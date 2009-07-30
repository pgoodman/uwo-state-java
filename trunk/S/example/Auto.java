package example;
import example.SM;
public class Auto {
	protected int __cs, __ps;
	public void turnOff() {
		this.__ps = this.__cs;
		if((this.__cs = SM.trans[this.__cs][5]) < 0) {
			SM.error("Auto::turnOff", __ps);
		}
		try {
 
        System.out.println("AUTO: Off."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
	public void reverse() {
		this.__ps = this.__cs;
		if((this.__cs = SM.trans[this.__cs][6]) < 0) {
			SM.error("Auto::reverse", __ps);
		}
		try {
 
        System.out.println("AUTO: Reverse."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
	public Auto() {
		this.__cs = 3;
		try {
 
        System.out.println("AUTO: Off (constructor)"); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
	public void forward() {
		this.__ps = this.__cs;
		if((this.__cs = SM.trans[this.__cs][3]) < 0) {
			SM.error("Auto::forward", __ps);
		}
		try {
			switch(this.__ps) {
			case 2: 
			{
 
        System.out.println("AUTO: Forward (from Neutral)."); 
    
			}
			break;
			case 0: 
			{
 
        System.out.println("AUTO: Forward (from Reverse)."); 
    
			}
			break;
			}

		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
	public void neutral() {
		this.__ps = this.__cs;
		if((this.__cs = SM.trans[this.__cs][1]) < 0) {
			SM.error("Auto::neutral", __ps);
		}
		try {
 
        System.out.println("AUTO: Neutral."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
	public void turnOn() {
		this.__ps = this.__cs;
		if((this.__cs = SM.trans[this.__cs][0]) < 0) {
			SM.error("Auto::turnOn", __ps);
		}
		try {
 
        System.out.println("AUTO: On (Neutral)."); 
    
		} catch(Exception e) {
			System.out.println(e);
			System.exit(1);
		}
	}
}
