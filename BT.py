import sys
from tqdm import tqdm, trange
import time
import enum
import random

def charge(i, j):
    if i == 0:
        return j
    return i+1

class State(enum.Enum):
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    RUNNING = "Running"

# convert string to boolean
def String_to_bool(s):
    return s == "TRUE"

# root class for all different type of nodes
class Node:
    Blackboard = {"BATTERY_LEVEL": None,
                  "SPOT_CLEANING": None,
                  "GENERAL_CLEANING": None,
                  "DUSTY_SPOT": None,
                  "HOME_PATH": None
                  }
    # for clean floor task to draw random number from this list
    Random_list = [1, 2, 3, 4, 5]

    def __init__(self, name, order):
        self.children = []
        self.name = name
        self.order = order
        Node.Blackboard[self.name] = State.FAILED

    def __repr__(self):
        return '{' + self.name + '}'

    # add child node to child list
    def add_child(self, child):
        self.children.append(child)

    def run(self):
        return State.FAILED

# sub class of Node, include seq, pri, sel. Which will be differ by "composit"
class Composites(Node):
    def __init__(self, name, order, composit):
        super().__init__(name, order)
        self.composit = composit
        

    def run(self):
        Is_pri = (self.composit == "Priority")
        Is_Seq = (self.composit == "Sequence")
        Is_Sel = (self.composit == "Selector")

        # If this composites is Priority, sort it's children list.
        # and evalute in order
        if Is_pri:
            self.children.sort(key=lambda x: x.order)
            for child in self.children:
                result = child.run()
                if result == State.SUCCEEDED:
                    # this child is SUCCEEDED, update self in the blackboard
                    Node.Blackboard.update({self.name: State.SUCCEEDED})
                    return result
                if result == State.RUNNING:
                    # this child is running, update self in the blackboard
                    Node.Blackboard.update({self.name: State.RUNNING})
                    return result
            return State.FAILED

        # Selection will first if any of their child is RUNNING,
        # if not, evaluated children in order
        elif Is_Sel:
            if Node.Blackboard.get(self.name) == State.RUNNING:
                for child in self.children:
                    if Node.Blackboard.get(child.name) == State.RUNNING:
                        result = child.run()
                        if result == State.SUCCEEDED:
                            # this child finish running and return succeed, 
                            # update self in the blackboard
                            Node.Blackboard.update({self.name: State.SUCCEEDED})
                            return result
                        elif result == State.RUNNING:
                            return result
                        # if the running node is succeed,
                        # we need to go run next node.
                        else: 
                            for Unruned_child in self.children:
                                if child is Unruned_child:
                                    pass
                                else:
                                    result = Unruned_child.run()
                                    if result == State.SUCCEEDED:
                                        return result
                                    elif result == State.RUNNING:
                                        return result
                return State.FAILED
            else:
                for child in self.children:
                    result = child.run()
                    if result == State.SUCCEEDED:
                        print("111111111111")
                        Node.Blackboard.update({self.name: State.SUCCEEDED})
                        return result
                    if result == State.RUNNING:
                        # this child start to running, update self in the blackboard
                        Node.Blackboard.update({self.name: State.RUNNING})
                        return result
                return State.FAILED

        # Seq will first check for any running child,
        # if not evaluate children in order and return as soon as some 
        # child fails or running
        elif Is_Seq:
            is_running = False
            if Node.Blackboard.get(self.name) == State.RUNNING:
                # this value will be set to false when we reach the running node
                is_running = True

            for child in self.children:
                # if this child is running, we want to start run the node
                if Node.Blackboard.get(child.name) == State.RUNNING:
                    is_running = False
                # if we had not reach the running node, we want to skip
                if is_running:
                    continue
                result = child.run()
                if result == State.FAILED:
                    return result
                if result == State.RUNNING:
                    # this child start to running, update self in the blackboard
                    Node.Blackboard.update({self.name: State.RUNNING})
                    return result
            Node.Blackboard.update({self.name: State.SUCCEEDED})
            return State.SUCCEEDED

        else:
            exit(1)

# sub class of node, Incluse every task. Can be differ by it's name
class Task(Node):

    def __repr__(self):
        return "Task: " + self.name + " is SUCCEEDED !"

    def __str__(self):
        return "Task: " + self.name

    def run(self):
        Spot_is_done = (self.name == "Done_Spot")
        General_is_done = (self.name == "Done_general")
        Docking = (self.name == "Dock")
        if Spot_is_done:
            Node.Blackboard.update({"SPOT_CLEANING": False})
        elif General_is_done:
            Node.Blackboard.update({"GENERAL_CLEANING": False})
        elif Docking:
            charging_start = Node.Blackboard.get("BATTERY_LEVEL")
            for i in trange(charging_start, 100, initial=charging_start
                            ,total = 100, desc ="Charging"):
                time.sleep(0.01)
            Node.Blackboard.update({"BATTERY_LEVEL": 100})
        print(repr(self))
        return State.SUCCEEDED

# condition class for battery check
class Battery_check(Node):
    def run(self):
        print("Current Battery level is : " + str(Node.Blackboard.get("BATTERY_LEVEL")) + "%")
        if Node.Blackboard.get("BATTERY_LEVEL") < 30:
            print("Going home for recharge!")
            return State.SUCCEEDED
        else:
            return State.FAILED

# condition class to check if we need to do spot clean
class Spot_check(Node):
    def run(self):
        print("Checking if need to do a Spot clean!")
        if Node.Blackboard.get("SPOT_CLEANING"):
            return State.SUCCEEDED
        else:
            return State.FAILED

# condition class to check if we need to do general clean
class General_check(Node):
    def run(self):
        print("Checking if need to do a General clean!")
        if Node.Blackboard.get("GENERAL_CLEANING"):
            return State.SUCCEEDED
        else:
            return State.FAILED

# condition class to check if there is a dusty spot
class Dusty_check(Node):
    def run(self):
        print("Checking if there is a Dusty spot!")
        if Node.Blackboard.get("DUSTY_SPOT"):
            return State.SUCCEEDED
        else:
            return State.FAILED

# sub class of Node. Timer will start when been called and request a total time input.
# which will be the total time we need to do the cleaning.
# Every time the run() been call, the total time will decrease by 1
# Since we are assuming 1 second intervals for each call
class Timer(Node):
    def __init__(self, name, order, task, time):
        super().__init__(name, order)
        self.task = task
        self.Total_time = time + 1

    def __repr__(self):
        return str(self.task) + " is " + str(Node.Blackboard.get(self.name)) + " !"

    def run(self):
        self.Total_time -= 1
        if self.Total_time < 1:
            # update self state in black borad
            Node.Blackboard.update({self.name: State.SUCCEEDED})
            print(self)
            return State.SUCCEEDED
        else:
            print("Need " + str(self.Total_time) + " sec for cleaning, please wait!")
            # update self state in black borad
            Node.Blackboard.update({self.name: State.RUNNING})
            print(self)
            return State.RUNNING

# sub class of Node. It will keep been call until it return succeeded
class Until_Succ(Node):
    def __init__(self, name, order, task):
        super().__init__(name, order)
        self.task = task

    def __repr__(self):
        return str(self.task) + " is " + str(Node.Blackboard.get(self.name)) + " !"

    def run(self):
        Random_num = random.choice(Node.Random_list)
        if Random_num == 3:
            # only 1/5 chance to succeed. Once succeed,
            # update self state in black borad
            Node.Blackboard.update({self.name: State.SUCCEEDED})
            print(self)
            return State.SUCCEEDED
        else:
            # We need to keep this running until succeed,
            # update self state in black borad
            Node.Blackboard.update({self.name: State.RUNNING})
            print(self)
            return State.RUNNING

# This function will take a root node as input,
#  and build a tree base on the given BT from spec
#  by creating every node and add to perent's child list.
def Build_Tree(Root):
    # 1.0 sequence for battery check, first in priority
    Battery_seq = Composites("Battery check seq", 1, "Sequence")
    # 1.1 Battery condition
    Battery_condition = Battery_check("Battery condition", 0)
    # 1.2 Tasks: Find home, Go home, Dock
    Find_home = Task("Find_Home", 0)
    Go_home = Task("Go_Home", 0)
    Dock = Task("Dock", 0)
    # 1.3 Add condition and Task to sequence
    Battery_seq.add_child(Battery_condition)
    Battery_seq.add_child(Find_home)
    Battery_seq.add_child(Go_home)
    Battery_seq.add_child(Dock)

    # 2.0 seqence for spot clean
    Spot_seq = Composites("Spot clean seq", 0, "Sequence")
    # 2.1 Spot condition
    Spot_condition = Spot_check("Spot condition", 0)
    # 2.2 Tasks: Clean spot, Done spot and Timer 20s
    Clean_spot1 = Task("Clean_Spot", 0)
    Timer1 = Timer("20 sec Clean spot", 0, Clean_spot1, 20)
    Done_spot = Task("Done_Spot", 0)
    # 2.3 Add condition and Task to sequence
    Spot_seq.add_child(Spot_condition)
    Spot_seq.add_child(Timer1)
    Spot_seq.add_child(Done_spot)

    # 3.0 seqence for Dusty spot
    Dusty_seq = Composites("Dusty spot seq", 1, "Sequence")
    # 3.1 Spot condition
    Dust_condition = Dusty_check("Dusty spot check", 0)
    # 3.2 Task: Clean spot and Timer 35s
    Clean_spot2 = Task("Clean_Spot", 0)
    Timer2 = Timer("35 sec Clean spot", 0, Clean_spot2, 35)
    # 3.3 Add condition and Task to sequence
    Dusty_seq.add_child(Dust_condition)
    Dusty_seq.add_child(Timer2)

    # 4.0 Priority for spot clean
    Dusty_pri = Composites("Dusty priority", 0, "Priority")
    # 4.1 Task: clean floor and Until succeeds
    Clean_floor = Task("Clean_floor", 0)
    Until_succeeds = Until_Succ("clean floor until succ", 2 , Clean_floor)
    #4.2 Add dusty spot seq and clean floor until succ
    Dusty_pri.add_child(Dusty_seq)
    Dusty_pri.add_child(Until_succeeds)

    # 5.0 Seqence for Dusty spot priority and Done General
    Done_gen_seq = Composites("Dusty priority and done general", 0, "Sequence")
    # 5.1 Add Dusty spot priority and Done General
    Done_general = Task("Done_general", 0)
    Done_gen_seq.add_child(Dusty_pri)
    Done_gen_seq.add_child(Done_general)

    # 6.0 General cleaning seq
    General_clean_seq = Composites("General clean seq", 0, "Sequence")
    # 6.1 Genreal cleaning condition
    General_clean_condition = General_check("General clean condition", 0)
    # 6.2 Add seqence for Dusty spot priority and Done 
    #       General | and general cleaning condition
    General_clean_seq.add_child(General_clean_condition)
    General_clean_seq.add_child(Done_gen_seq)

    # 7.0 Selector for seq spot and seq general cleaning
    Only_Selector = Composites("the only selector", 2, "Selector")
    # 7.1 Add both seq to selector
    Only_Selector.add_child(Spot_seq)
    Only_Selector.add_child(General_clean_seq)

    # 8.0 Root priority
    
    # 8.1 Task
    Do_Nothing = Task("Do_Nothing", 3)
    # 8.2 Add all three child to root
    Root.add_child(Battery_seq)
    Root.add_child(Only_Selector)
    Root.add_child(Do_Nothing)
    
    return Root

def main():
    # Greating and ask for the input for basic Black borad.
    print("Welcom to Vacuum Cleaning Robot evaluation!")
    inp = input("Please enter the current battery level (0 to 100): ")
    Node.Blackboard.update({"BATTERY_LEVEL": int(inp)})
    inp = input("Do you want to do a Spot clean (TRUE/FALSE): ")
    Node.Blackboard.update({"SPOT_CLEANING": String_to_bool(inp)})
    inp = input("Do you want to do a General clean (TRUE/FALSE): ")
    Node.Blackboard.update({"GENERAL_CLEANING": String_to_bool(inp)})
    inp = input("Do you think there is a Dusty spot (TRUE/FALSE): ")
    Node.Blackboard.update({"DUSTY_SPOT": String_to_bool(inp)})
    inp = input("Please enter the path to home: ")
    Node.Blackboard.update({"HOME_PATH": inp})
    input("Press Enter to start the evaluation!")
    
    # Create root of the BT
    BT = Composites("Root priority", 0, "Priority")
    # Build the BT
    Build_Tree(BT)
    # For keep track of number of evaluation we have done.
    count = 1
    while(1):
        print("=======================================================================")
        print("Evalution No.", count)
        count += 1
        BT.run()
        battery = Node.Blackboard.get("BATTERY_LEVEL")
        # Decrease the battery level for every evalution.
        Node.Blackboard.update({"BATTERY_LEVEL": battery-2})
        time.sleep(1)
    



if __name__ == "__main__":
    main()
