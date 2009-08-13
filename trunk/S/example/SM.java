package example;
final public class SM {
	final static public String[] states = new String[4];
	static {
		states[0] = ":Reverse";
		states[1] = ":Forward";
		states[2] = ":Neutral";
		states[3] = ":Off";
	}
	final static public int[][] trans = {
		{ -1, -1,  1, -1,  2, -1, -1,  3, -1  },
		{  0, -1, -1, -1,  2, -1,  0,  3, -1  },
		{ -1, -1,  1, -1, -1, -1,  0,  3, -1  },
		{ -1,  2, -1,  3, -1,  3, -1, -1, -1  }
	};
	static public void error(String method, int state) {
		System.out.println("Error: cannot call method '"+method+"' from state '"+states[state]+"'.");
		System.exit(1);
	}
}
