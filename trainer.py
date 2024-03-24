from sb3_contrib.common.maskable.evaluation import evaluate_policy
import os

from loader import Loader

class Trainer:
    
    model = None
    env = None

    def __init__(self) -> None:
        Loader(self)

    def run(self):
        self.model.learn(total_timesteps=self.model.n_steps * self.env.num_envs, progress_bar=True, reset_num_timesteps=False)
        self.model.save(self.modelName)


if __name__ == "__main__":

    rounds = 0
    while True:
        try:
            trainer = Trainer()
            os.system('cls')
            print(rounds)
            r = evaluate_policy(trainer.model, trainer.env, warn=False, n_eval_episodes=100, deterministic=True)
            print(r)
            trainer.run()
            rounds += 1
            del trainer
        except:
            break

    exit()