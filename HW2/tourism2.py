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
    num_place = -1
    preferences = -1
    places = []
    prefer = []
    for line in r:
        word = line.split(".")
        for s in word:
            s=s.strip()
            if s.startswith("places"):
                num_place = int(s[len("places("):-1])
            if s.startswith("preferences"):
                preferences = int(s[len("preferences("):-1])
            if s.startswith("people"):
                people = int(s[len("people("):-1])
            if s.startswith("place("):
                plac = []
                for w in s[len("place("):-1].split(","):
                    plac.append(int(w))
                places.append(plac)
            if s.startswith("prefer("):
                pref = []
                for w in s[len("prefer("):-1].split(","):
                    pref.append(int(w))
                prefer.append(pref)
    return people, num_place, preferences, sorted(places, key=lambda x:x[0]), sorted(prefer, key=lambda x:x[0]) #, -x[1]))

class Tour(object):
    ''' define tour time , place visited and people in tourism '''

    def __init__(self, people):
        self.people = people
        self.time = 0
        self.visited = set()

    def __str__(self):
        return 'time:' + str(self.time) + ' visit:' + str(self.visited)

    def visit(self, place):
        ''' actually visit place '''
        # if can't visit return
        if self.time + place.duration > place.close:
            return
        # update tourism time and satisfy
        self.time = place.open + place.duration if self.time == 0 else self.time + place.duration
        for person in self.people:
            if place.id in person.prefers:
                person.satisfy += 1

    def plot_people(self):
        ''' plot all people in tour'''
        plot_list(self.people) 

class Person(object):
    ''' define satisfy and prefers'''

    def __init__(self, ID, prefers):
        self.id = ID 
        self.prefers = prefers
        self.satisfy = 0

    def __str__(self):
        return ' person:' + str(self.id) + ' prefer:' + str(self.prefers) + ' satisfy:' +str(self.satisfy)
    

class Place(object):
    ''' define location open hour and duration'''

    def __init__(self, ID, duration, op, cl):
        self.duration = duration
        self.id = ID
        self.open = op
        self.close = cl

    def __str__(self):
        return ' place:' + str(self.id) +' duration:'+str(self.duration)+' in ' + str(self.open) + '~' + str(self.close)


def plot_list(l):
    ''' plot list'''

    s=''
    for i in range(len(l)):
        s+=str(l[i]) 
    log.debug(s)

def check_satisfy(tour, place_list):
    ''' check place order satisfycation and save largest'''

    global max_satify

    # visit place
    for place in place_list:
        tour.visit(place)

    min_satisfy = -1
    for person in tour.people:
        if person.satisfy == len(person.prefers):
            person.satisfy = len(place_list)
        min_satisfy = person.satisfy if min_satisfy == -1 else min(min_satisfy, person.satisfy)
    
    log.debug(min_satisfy)
    max_satify = max(max_satify, min_satisfy)
    tour.plot_people()


def tourism(place_list, current_list, tour, explored=set()):
    ''' try all possible order'''

    if len(current_list) == len(place_list):
        check_satisfy(copy.deepcopy(tour), current_list)
        return

    for i in range(len(place_list)):
        if i in explored:
            continue
        current_list.append(place_list[i])
        explored.add(i)
        tourism(place_list, current_list, tour, explored)
        current_list.pop()
        explored.remove(i)



max_satify = -1

def main():
    log.info(sys.argv[1])
    people, num_place, preferences, places, prefers= parseline(sys.argv[1])
    log.debug(' people:'+str(people)+' place:'+str(places)+' prefer:'+str(prefers))


    place_list = [Place(p[0], p[1], p[2], p[3]) for p in places]
    plot_list(place_list)

    prefers_set = [set() for i in range(people)]
    for s in prefers:
        prefers_set[s[0]-1].add(s[1])

    person_list = [ Person(s+1, prefers_set[s]) for s in range(people) ] 
    plot_list(person_list)

    tourism(place_list, [], Tour(person_list) )
    print('satisfaction(' + str(max_satify) + ').')
    
main()


