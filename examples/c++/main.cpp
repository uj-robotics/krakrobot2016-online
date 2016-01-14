#include <iostream>
#include <string>
#include <map>
#include <cstdlib>
#include <sstream>

using namespace std;

const double TICK_MOVE = 0.01,
			 TICK_ROTATE = 0.002,
			 COLOR_SENSOR_DIST = 0.5;
const int FIELD_SIZE_CM = 22;

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

	friend ostream& operator<<(ostream& os, const Action& action );
};

ostream& operator<<(ostream& os, const Action& action) {
	ACTIONS a = action.a;
	os << ACTIONS_STRING[a];
	if (TURN == a || MOVE == a){
		os << " " << action.par;
	}
	return os;
}


class Robot {
public:
	/*double x, y, angle, steering_noise, distance_noise, forward_steering_drift,
	 speed, turning_speed, execution_cpu_time_limit, M, N;
	 */ // ALL these vars will be in map
	std::map<std::string, double> vars;

	int current_color[3];

	double elapsed_time;

	Robot() {
		current_color[0] = -1;
		current_color[1] = -1;
		current_color[2] = -1;

		elapsed_time = 0;
	}
	Action act() {
		Action a;
		a.a = (rand()%2 == 0) ? TURN : MOVE;
		a.par = (rand()%2 == 0) ? 1 : -1;
		return a;
	}
	void on_sense_color(int r, int g, int b) {
		if (0 <= r && 0 <= g && 0 <= b && r <= 255 && g <= 255 && b <= 255) {
			current_color[0] = r;
			current_color[1] = g;
			current_color[2] = b;
		}

	}

	void on_time(double time) {
		elapsed_time = time;
	}


};

void read_config(Robot& r) {
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

int main(int argc, char* argv[]) {
	srand (time(NULL));
	Robot robot;
	read_config(robot);
	bool running = true;
	string cmd, line;
	while (running) {
		getline(cin, cmd);
		if (cmd == "act") {
			Action response = robot.act();
			if (response.a == FINISH) {
				running = false;
			}
			cout << response << endl;
			// cout << ACTIONS_STRING[response.a] << " " << response.par << endl;
		} else if (cmd == "color") {
			getline(cin, line);

			std::stringstream ss(line);

			int r, g, b;
			ss >> r >> g >> b;
			robot.on_sense_color(r, g, b);
		} else if (cmd == "time") {
			getline(cin, line);
			std::stringstream ss(line);

			double elapsed;
			ss >> elapsed;
			robot.on_time(elapsed);
		} else {
			throw exception();
		}
	}
	return 0;
}

