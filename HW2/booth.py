import copy
import sys
import time
import logging
fmt="[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
logging.basicConfig(level=logging.ERROR, format=fmt)
log = logging.getLogger(__name__)

class Booth(object):
    '''define booth function'''
    
    # init with booth size, position and room size
    def __init__(self,ID,size_w,size_h,pos_x,pos_y):
        self.id = ID
        #self.width = size_w
        #self.height = size_h
        self.pos_x1 = pos_x
        self.pos_x2 = pos_x + size_w
        self.pos_y1 = pos_y
        self.pos_y2 = pos_y + size_h
        self.moves = 0



    def booth_area(self):
        ''' return all coordinate blocked by this booth '''
        for w in range(self.width):
            for h in range(self.height):
                yield(self.pos_x1+w,self.pos_y1+h)

    # return if booth can move inside room size
    def can_up(self, room_size):
        self.pos_y1 += 1
        self.pos_y2 += 1
        self.moves += 1
        return self.pos_y2 <=  room_size[1]
        
    def can_down(self, room_size):
        self.pos_y1 -= 1
        self.pos_y2 -= 1
        self.moves += 1
        return self.pos_y1 >= 0

    def can_right(self, room_size):
        self.pos_x1 += 1
        self.pos_x2 += 1
        self.moves += 1
        return self.pos_x2 <= room_size[0]

    def can_left(self, room_size):
        self.pos_x1 -= 1
        self.pos_x2 -= 1
        self.moves += 1
        return self.pos_x1 >= 0

    def get_id(self):
        ''' return booth.id'''
        return self.id 
    


class Room(object):
    ''' define room func, booth in room, check validaty'''

    # init with all booths
    def __init__(self, room_size, booths, moves):
        self.booths = booths # all booths inside
        self.room_size = room_size
        self.booths.sort(key=lambda x:x.id) # sort by id for unique key
        self.moves = moves

        # generate key for room state
        self.state = "".join(str(b.pos_x1)+str(b.pos_y1) for b in self.booths)
           
    def in_block(self, block, booth):
        if block[0] < booth.pos_x2 and block[1] > booth.pos_x1 \
        and  block[3] > booth.pos_y1 and block[2] < booth.pos_y2:
            return True
        return False 

    def check_valid(self):
        ''' check if booths overlap '''
        blocked_area = set() 
        for booth in self.booths:
            for (x1,x2,y1,y2) in blocked_area:
               #if block[0] < booth.pos_x2 and block[1] > booth.pos_x1 \
               #and  block[3] > booth.pos_y1 and block[2] < booth.pos_y2:
               if x1 < booth.pos_x2 and x2 > booth.pos_x1 \
               and  y2 > booth.pos_y1 and y1 < booth.pos_y2:
                  return False
            blocked_area.add((booth.pos_x1, booth.pos_x2,booth.pos_y1, booth.pos_y2))
            # for x, y in booth.booth_area():
            #     if (x, y) in blocked_area:
            #         return False
            #     blocked_area.add((x, y))
        return True

    
    def move_booths(self):
        ''' try to move every booth in four directions
            and return iterator of new room states'''

        # try every booth
        for booth in self.booths:
            # try method on new booth
            for dir in ['can_up','can_down','can_right','can_left']:
                new_booth = copy.copy(booth)
                # skip if this direction out of bound
                if not getattr(new_booth,dir)(self.room_size):
                    continue
                
                # generate new room state
                new_booths = copy.copy(self.booths)
                new_booths[booth.id-1] = new_booth
                new_room = Room(self.room_size, new_booths, self.moves+1)
                # if new state valid, return iterator
                if new_room.check_valid():
                    #new_room.plot_room()
                    yield new_room


    def finish(self, target):
        ''' check if arrive target'''
        booth = self.booths[target[0]-1]
        return booth.pos_x1 == target[1] and booth.pos_y1 == target[2]
            

    def plot_room(self):
        ''' plot room and booth'''
        room_plot = [ [0] * self.room_size[0] for i in range(self.room_size[1])]
        for booth in self.booths:
            for x,y in booth.booth_area():
                room_plot[y][x]=booth.id
        for row in reversed(room_plot):
            log.debug(row)

def arrange_booth(room,target,limit):
    ''' try move booth to target in this room'''
    if not room.check_valid():
        log.error(' wrong data!')
        return

    # try BFS search
    bfs_queue = []
    # use set save every states explored
    explored = set()

    bfs_queue.append(room)
    explored.add(room.state)

    while bfs_queue:
        room = bfs_queue.pop(0)
        # try every possible neighbor states
        for next_state in room.move_booths():
            if next_state.state in explored:
                continue

            # moves exceed limit
            if next_state.moves > limit:
                return -1 

            if next_state.finish(target):
                total_moves = next_state.moves * 2 - next_state.booths[target[0]-1].moves
                # exceed limit
                if total_moves > limit:
                    return -1
                return total_moves 

            bfs_queue.append(next_state)
            explored.add(next_state.state)

    log.debug('Can\'t move to target')
    return -1

def parseline(file):
    ''' parse every line in input txt file'''
    r=open(file)

    room = []
    dimension = []
    position = []
    target = [] 
    horizon = -1
    for line in r:
        word = line.split(".")
        for s in word:
            s=s.strip()
            if s.startswith("room"):
                for w in s[len("room("):-1].split(","):
                    room.append(int(w))
            if s.startswith("dimension"):
                bo=[]
                for w in s[len("dimension("):-1].split(","):
                    bo.append(int(w))
                dimension.append(bo)
            if s.startswith("position"):
                po=[]
                for w in s[len("position("):-1].split(","):
                    po.append(int(w))
                position.append(po)
            if s.startswith("target"):
                for w in s[len("target("):-1].split(","):
                    target.append(int(w))
            if s.startswith("horizon"):
                horizon = s[len("horizon("):-1]
    r.close()
    return room, sorted(dimension, key=lambda x:x[0]), sorted(position, key=lambda x:x[0]), target, horizon

def main():
    log.debug(sys.argv[1])
    start = time.time()
    room, dim, pos, tar, hor = parseline(sys.argv[1])
    booth=[Booth(dim[i][0], dim[i][1], dim[i][2], pos[i][1], pos[i][2]) for i in range(len(dim))]
    print('moves('+ str(arrange_booth(Room(room, booth, 0), tar, int(hor)))+').')
    log.info(time.time()-start)
main()