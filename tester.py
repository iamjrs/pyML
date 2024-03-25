from sb3_contrib.common.maskable.evaluation import evaluate_policy
from loader import Loader


class Tester:

    def __init__(self) -> None:
        Loader(self)


if __name__ == "__main__":

    test = Tester()

    while True:
        result = evaluate_policy(
            test.model, test.env, n_eval_episodes=100, warn=False, deterministic=True
        )
        print(result)
