# Homework 1 for CS131
Behavior Tree

## Usage
```bash
# Install tqdm if you dont have it:
pip install tqdm
# Run the program using:
python3 BT.py

```

## Detail
This program will first ask to fill in all the configuration it need to run the program.
Please follow the rule, only input interger, TRUE / FALSE, string.
I am assuming that for every evaulation, the battery will be decrease by 2%. And there is only 20% chance that the task clean floor could succeed. User will be response to tell the program if there is a dusty spot, and which cleaning task need to be done. Also after it went to dock, the battery level will return to 100%. But for simplicity, I reduce the charging speed to 100% per second and display the process using tqdm. More detail/comment can be find in source code.