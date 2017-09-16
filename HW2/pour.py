import copy
import sys

import logging
fmt="[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
logging.basicConfig(level=logging.ERROR, format=fmt)
log = logging.getLogger(__name__)

class Cup(object):
    ''' define cup capacity and current amount'''

    def __init__(self, capacity, amount=0):
        self.capacity = capacity
        self.amount = amount
    
    def __str__(self):
        return str(self.amount)+'/'+str(self.capacity)

    def pour_to(self, other_cup):
        space = other_cup.capacity - other_cup.amount

        other_cup.amount += space if self.amount >= space else self.amount
        self.amount -= space if self.amount >= space else self.amount  
        

class Bar(object):
    ''' define container of cups '''

    def __init__(self, cups, step):
        ''' define Bar.cups'''
        self.cups = cups
        self.state = "".join(str(c.amount) + "/" + str(c.capacity) for c in self.cups)
        self.steps = step
    
    def __str__(self):
        return  ''.join( str(cup)+' ' for cup in self.cups)+'step:'+str(self.steps)

    def pour(self, new_cups, cup, other_cup):
        ''' pour from one cup to another cup'''
        # empty space in target cup
        space = self.cups[other_cup].capacity - self.cups[other_cup].amount
        self.cups[other_cup].amount += space if self.cups[cup].amount >= space else self.cups[cup].amount
        self.cups[cup].amount -= space if self.cups[cup].amount >= space else self.cups[cup].amount  
        for new_cup in new_cups:
            log.debug(str(new_cup))
        return cup, other_cup

    def try_pour(self):
        ''' try to pour from every cup to other cups'''
        log.debug(self)
        for cup in range(len(self.cups)):
            # skip empty cup
            if self.cups[cup].amount == 0:
                continue
            for other_cup in range(len(self.cups)):
                # skip same cup and full cups
                if cup == other_cup or self.cups[other_cup].amount == self.cups[other_cup].capacity:
                    continue
                # copy and generate next Bar state
                new_cup, new_other_cup = copy.copy(self.cups[cup]), copy.copy(self.cups[other_cup])
                new_cups = copy.copy(self.cups)
                new_cup.pour_to(new_other_cup)

                new_cups[cup], new_cups[other_cup] = new_cup, new_other_cup

                yield Bar(new_cups, self.steps+1)
    
    def can_split(self, people, target, current_sum=0, ind=0, used=set()):
        ''' judge if current cup state can split for every one equally recursively'''
        log.debug(self)
        log.debug(str(people) +' target:'+ str(target) +' current:'+ str(current_sum) +' ind:' +str(ind) + str(used))

        # if any amount more than target, return
        if current_sum > target:
            return
        if people == 0:
            return 'Done'
        if current_sum == target:
            return self.can_split(people-1, target, 0, ind, used)

        for cup in range(ind, len(self.cups)):
            # if used this cup skip
            if cup in used:
                continue

            amount = self.cups[cup].amount
            if amount > target:
                return False

            # sum this cup and try all other combinations other than this
            log.debug(str(cup) + ' ->'+str(used))
            used.add(cup)
            log.debug(used)
            result =self.can_split(people, target, current_sum + amount, ind+1, used)
            
            if result == 'Done':
                return 'Done'
            elif result == False:
                return False
            
            used.remove(cup)
         



def share(bar, people, limit, source):
    ''' use bfs to search '''
    
    bfs_queue = []
    explored = set()

    bfs_queue.append(bar)
    explored.add(bar.state)

    while bfs_queue:
        bar = bfs_queue.pop(0)
        for next_pour in bar.try_pour():
            # log.debug(next_pour)
            if next_pour.steps > limit:
                break

            if next_pour.state in explored:
                continue
            
            if bar.can_split(people, int(source/people), used=set()) == 'Done':
                return 'yes' 
            bfs_queue.append(next_pour)
            explored.add(next_pour.state)

    return 'no'




def parseline(file):
    ''' parse every line in input txt file'''
    r=open(file)
    vessels = -1
    source = -1
    people = -1
    horizon = -1
    capacity = []
    for line in r:
        word = line.split(".")
        for s in word:
            s=s.strip()
            if s.startswith("vessels"):
                vessels = int(s[len("vessels("):-1])
            if s.startswith("source"):
                source = int(s[len("source("):-1])
            if s.startswith("people"):
                people = int(s[len("people("):-1])
            if s.startswith("capacity"):
                cap = []
                for w in s[len("capacity("):-1].split(","):
                    cap.append(int(w))
                capacity.append(cap)
            if s.startswith("horizon"):
                horizon = int(s[len("horizon("):-1])
    return vessels, source, people, horizon, sorted(capacity,key=lambda x:x[0])

def main():
    log.info(sys.argv[1])
    ves, source, people, horizon, capacity = parseline(sys.argv[1])
    cups = [ Cup(capacity[i][1])  if i!= source-1 else Cup(capacity[i][1], capacity[i][1]) for i in range(len(capacity))]
    bar = Bar(cups, 0)
    print('split(' + str(share(bar, people, horizon, capacity[source-1][1])) + ').')
    
main()
