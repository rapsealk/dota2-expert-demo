# Author: Mikita Sazanovich

import os
import pickle
import numpy as np
import math

SIGMA = 0.2 * np.array([[1, 0, 0],
                        [0, 1, 0],
                        [0, 0, 1]])


class ReplayProcessor:

    def __init__(self, replay_dir, state_preprocessor):
        self.replay_dir = replay_dir
        self.state_preprocessor = state_preprocessor
        self.demos = []

    def load(self):
        for name in os.listdir(self.replay_dir):
            dump_path = os.path.join(self.replay_dir, name)
            with open(dump_path, 'rb') as dump_file:
                replay = pickle.load(dump_file)
            demo = self.__process_replay(replay)
            self.demos.append(demo)

    def __process_replay(self, replay):
        # Remove consecutive duplicates
        states = []
        for entry in replay:
            if not states or np.any(states[len(states) - 1] != entry):
                states.append(entry)
        demo = []
        for i in range(1, len(states)):
            prev_state = states[i - 1]
            next_state = states[i]
            diff = next_state - prev_state
            angle_pi = math.atan2(diff[1], diff[0])
            if angle_pi < 0:
                angle_pi += 2 * math.pi
            degrees = angle_pi / math.pi * 180
            action = round(degrees / 22.5) % 16
            demo.append((
                self.state_preprocessor.process(prev_state),
                action,
                self.state_preprocessor.process(next_state)))
        return demo

    def get_potential(self, state, action):
        print('get potential for', state, action)
        # Implemented from: https://www.ijcai.org/Proceedings/15/Papers/472.pdf
        best_value = 0
        for demo in self.demos:
            for demo_state, demo_action, _ in demo:
                if demo_action != action:
                    continue
                diff = state - demo_state
                value = math.e ** (-1/2*diff.dot(SIGMA).dot(diff))
                if value > best_value:
                    best_value = value
        print('best value is', best_value)
        return best_value


def main():
    replay_processor = ReplayProcessor('../replays')
    replay_processor.load()
    print(
        replay_processor.get_potential(np.array([-6700, -6700, 0]), 2))


if __name__ == '__main__':
    main()
