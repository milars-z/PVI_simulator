# main.py

from running_mode import run_with_render,run_training

# PED_NUM = 100
# SEED = 42

RUN_MODE = "train"
#RUN_MODE = "render"

def main() -> None:
    if RUN_MODE == "render":
        run_with_render()
    elif RUN_MODE == "train":
        run_training()
    else:
        raise ValueError(f"Unknown RUN_MODE: {RUN_MODE}")

if __name__ == "__main__":
    main()