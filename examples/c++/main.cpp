#include <iostream>
#include <string>
#include <map>
#include <cstdlib>
#include <sstream>
using namespace std;
enum ACTIONS {
	TURN, BEEP, MOVE, FINISH
};
string ACTIONS_STRING[] = {
	"TURN", "BEEP", "MOVE", "FINISH"
};
class Action {
public:
	ACTIONS a;
	//std::string par;
	double par;
};
class Robot {
public:
	/*You can use pair instead of action*/

	Action act() {
		Action a;
		a.a = (rand()%2 == 0) ? TURN : MOVE;
		a.par = (rand()%2 == 0) ? 1 : -1;
		return a;
	}
	void onSenseColor(int r, int g, int b) {
		if (0 <= r && 0 <= g && 0 <= b && r <= 255 && g <= 255 && b <= 255) {
			current_color[0] = r;
			current_color[1] = g;
			current_color[2] = b;
		}

	}
	/*double x, y, angle, steering_noise, color_sensor_displacement,
	 distance_noise, speed
	 turning_speed, execution_cpu_time_limit, N, M;
	 */ // ALL these vars will be in map
	std::map<std::string, double> vars;
	int current_color[3];

};
void readConfig(Robot& r) {
	int i = 11;
	string key, line;
	double value;
	while (i--) {
		getline(cin,line);
		line.replace(line.find(":"),1," ");
		stringstream ss(line);
		ss>>key>>value;
		r.vars[key] = value;
		cerr << "Initialize key:" << key << " with:" << value << endl;
	}
}

int main() {
	srand (time(NULL));
	Robot robot;
	readConfig(robot);
	bool running = true;
	string cmd, line;
	while (running) {
		getline(cin, cmd);
		if (cmd == "act") {
			Action response = robot.act();
			if (response.a == FINISH) {
				running = false;
			}
			cout << ACTIONS_STRING[response.a] << " " << response.par << endl;
			cerr << ACTIONS_STRING[response.a] << " " << response.par << endl;
		} else if (cmd == "color") {
			getline(cin, line);

			std::stringstream ss(line);

			int r, g, b;
			ss >> r >> g >> b;
			robot.onSenseColor(r, g, b);
		} else if (cmd == "time") {
			getline(cin, line);
			//TODO
		} else {
			throw exception();
		}
	}
	return 0;
}

