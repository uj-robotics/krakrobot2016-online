import java.lang.reflect.Field;
import java.util.Random;
import java.util.Scanner;

public class RobotWraper {
	/* Possible commands */
	public static final String TURN = "TURN";
	public static final String BEEP = "BEEP";
	public static final String MOVE = "MOVE";
	public static final String FINISH = "FINISH";
	/* Simulation vars, they MUST be named in python_way */
	private double x, y, angle, steering_noise, color_sensor_displacement, distance_noise, speed;
	private double turning_speed, execution_cpu_time_limit, N, M;
	private int[] current_color = new int[3];

	public RobotWraper() {

	}

	class Action {
		public String action;
		public Object arg;

		public String toString() {
			return action + " " + arg;
		}
	}

	public Action act() {
		// Random movement
		Action a = new Action();
		a.action = (new Random().nextInt() < 0) ? MOVE : TURN;
		a.arg = (new Random().nextInt() < 0) ? 1 : -1;
		return a;
	}

	public void on_sense_color(int r, int g, int b) {
		if (0 <= r && 0 <= g && 0 <= b && r <= 255 && g <= 255 && b <= 255) {
			current_color[0] = r;
			current_color[1] = g;
			current_color[2] = b;
		}
	}

	static public RobotWraper robotFromConfig(Scanner sc) {
		RobotWraper robot = new RobotWraper();
		String line, key, value;
		String tmp[];
		Class<?> c = robot.getClass();
		for (int i = 0; i < 11; i++) {// 11 parameters expected
			line = sc.nextLine();
			tmp = line.split(":");
			key = tmp[0];
			value = tmp[1];
			try {
				Field f = c.getDeclaredField(key);
				f.set(robot, Double.parseDouble(value));
				System.err.println("Set field "+key + " with value: "+value);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
		return robot;
	}

	public static void main(String[] args) {
		String cmd,line;
		Scanner sc = new Scanner (System.in);
		RobotWraper robot = robotFromConfig(sc);
		boolean running = true;
		while (running) {
			cmd = sc.nextLine().replaceAll("\\s+", "");
			if (cmd.equalsIgnoreCase("act")) {
				Action response = robot.act();
				if (response.action.equals(FINISH)){
					running=false;
				}
				System.out.println(robot.act());
				System.out.flush();
			} else if (cmd.equalsIgnoreCase("color")) {
				line = sc.nextLine();
				Scanner sc2 = new Scanner(line);
				robot.on_sense_color(sc2.nextInt(), sc2.nextInt(), sc2.nextInt());
				sc2.close();
			} else if (cmd.equalsIgnoreCase("time")) {
				sc.nextLine();
			} else {
				sc.close();
				throw new RuntimeException("Not recognized cmd \"" + cmd + "\" ");
			}
		}
		sc.close();
	}
}
