import copy
import sys

import logging
fmt="[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
logging.basicConfig(level=logging.ERROR, format=fmt)
log = logging.getLogger(__name__)


def parseline(file):
    ''' parse every line in input txt file'''
    r=open(file)
    people = -1
    locations = -1
    preferences = -1
    order= []
    for line in r:
        word = line.split(".")
        for s in word:
            s=s.strip()
            if s.startswith("locations"):
                locations = int(s[len("locations("):-1])
            if s.startswith("places"):
                locations = int(s[len("places("):-1])
            if s.startswith("preferences"):
                preferences = int(s[len("preferences("):-1])
            if s.startswith("people"):
                people = int(s[len("people("):-1])
            if s.startswith("order"):
                orde = []
                for w in s[len("order("):-1].split(","):
                    orde.append(int(w))
                order.append(orde)
    return people, locations, preferences, sorted(order, key=lambda x:x[0]) #, -x[1]))

def add_behind(current_list, new_place):
    ''' add one place that is after every place in list'''

    for key, value in current_list.items():
        value.add(new_place)

    current_list[new_place] = set()

def del_behind(current_list, new_place):
    ''' del last place from all set in list'''

    del current_list[new_place]
    for key, value in current_list.items():
        value.remove(new_place)

def check_vio(place_list, orders):
    ''' check how many violations in this order'''
    global min_vio
    vio=0
    log.debug(orders)
    for order in orders:
        for key, value in order.items():
            log.debug(str(value) + 'in' + str (place_list[key]))
            vio += len(value - place_list[key])
    log.debug(str(min_vio) +' ' + str(vio))
    min_vio = vio if min_vio == -1 else min(vio, min_vio)

def travel(place_list, orders, current_list={}, used=set()):
    ''' generate all possible orders and check vios'''

    if len(current_list) == len(place_list):
        # check number of preferences being violated 
        log.debug(current_list)
        check_vio(current_list, orders)
        return

    # try differfent order of place and generate list
    for i in range(0, len(place_list)):
        if i in used:
            continue

        add_behind(current_list, place_list[i])
        used.add(i)
        travel(place_list, orders, current_list, used)
        del_behind(current_list, place_list[i])
        used.remove(i)
    log.debug(current_list)


min_vio = -1


def main():
    log.info(sys.argv[1])
    people, locations, preferences, orders = parseline(sys.argv[1])
    log.debug(str(people)+str(locations)+str(preferences))
    log.debug(orders)
    
    behind = []
    for order in orders:
        if order[0] > len(behind):
            behind.append( { } ) # dic for each person, map element behind "key"

        # order[1]: front, order[2]: after
        # if front is behind some ele, add after to the set 
        for key, value in behind[order[0]-1].items():
            if order[1] in value:
                value.add(order[2])

        # if front appears 1st time add new dic:set(after) 
        if order[1] not in behind[order[0]-1]:
            behind[order[0]-1][order[1]] = set()
            behind[order[0]-1][order[1]].add(order[2])

        # if any ele in after.set, add to front.set
        if order[2] in behind[order[0]-1]:
            behind[order[0]-1][order[1]].update(x for x in behind[order[0]-1][order[2]])
    
    log.debug('behind:'+str(behind))
    travel(range(1, locations+1), behind)
    print('violations(' + str(min_vio) + ').')
    
main()


