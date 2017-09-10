import copy

class Booth(object):
    '''define booth function'''
    
    # init with booth size, position and room size
    def __init__(self,id,size_w,size_h,pos_x,pos_y):
        self.id = id
        self.width = size_w
        self.height = size_h
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.moves = 0



    def booth_area(self):
        ''' return all coordinate blocked by this booth '''
        for w in range(self.width):
            for h in range(self.height):
                #print(self.pos_x+w,self.pos_y+h)
                yield(self.pos_x+w,self.pos_y+h)

    # return if booth can move inside room size
    def can_up(self, room_size):
        self.pos_y += 1
        self.moves += 1
        return self.pos_y + self.height <=  room_size[1]
        
    def can_down(self, room_size):
        self.pos_y -= 1
        self.moves += 1
        return self.pos_y >= 0

    def can_right(self, room_size):
        self.pos_x += 1
        self.moves += 1
        return self.pos_x + self.width <= room_size[0]

    def can_left(self, room_size):
        self.pos_x -= 1
        self.moves += 1
        return self.pos_x >= 0

    def get_id(self):
        ''' return booth.id'''
        return self.id 
    


class Room(object):
    ''' define room func, booth in room, check validaty'''

    # init with all booths
    def __init__(self, room_size, booths):
        self.booths = booths # all booths inside
        self.room_size = room_size
        self.booths.sort(key=lambda x:x.id) # sort by id for unique key
        # self.moves = 0

        # generate key for room state
        self.state = "".join(str(b.pos_x)+str(b.pos_y) for b in self.booths)
           

    def check_valid(self):
        ''' check if booths overlap '''
        blocked_area = set() 
        for booth in self.booths:
            for x, y in booth.booth_area():
                if (x, y) in blocked_area:
                    return False
                blocked_area.add((x, y))
        return True

    
    def move_booths(self):
        ''' try to move every booth in four directions
            and return iterator of new room states'''

        # try every booth
        for booth in self.booths:
            # try method on new booth
            for dir in ['can_up','can_down','can_right','can_left']:
                new_booth = copy.deepcopy(booth)
                # skip if this direction out of bound
                if not getattr(new_booth,dir)(self.room_size):
                    continue
                
                # generate new room state
                new_booths = copy.deepcopy(self.booths)
                new_booths[booth.id-1] = new_booth
                new_room = Room(self.room_size,new_booths)
                # if new state valid, return iterator
                print("new state", new_room.state)
                if new_room.check_valid():
                    #new_room.plot_room()
                    yield new_room


    def finish(self, target):
        ''' check if arrive target'''
        booth = self.booths[target[0]-1]
        return booth.pos_x == target[1] and booth.pos_y == target[2]
            

    def plot_room(self):
        ''' plot room and booth'''
        room_plot = [ [0] * self.room_size[0] for i in range(self.room_size[1])]
        for booth in self.booths:
            for x,y in booth.booth_area():
                room_plot[y][x]=booth.id
        for row in reversed(room_plot):
            print(row)

def arrange_booth(room,target):
    ''' try move booth to target in this room'''
    if not room.check_valid():
        print(' wrong data!')
        return

    print('room state id=' + room.state)
    room.plot_room()

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

            # next_state.moves += 1
            print(next_state.state)
            next_state.plot_room()

            if next_state.finish(target):
                next_state.plot_room()
                return sum(step.moves*2 for step in next_state.booths) - next_state.booths[target[0]-1].moves

            bfs_queue.append(next_state)
            explored.add(next_state.state)

    print('Can\'t move to target')
    return -1

def parseline(line):
    word = line.split(".")
    room=[]
    dimension=[]
    position=[]
    target=[]
    for s in word:
        s=s.strip()
        if s.startswith("room"):
            for w in s[5:-1].split(","):
                room.append(int(w))
        if s.startswith("dimension"):
            bo=[]
            for w in s[10:-1].split(","):
                bo.append(int(w))
            dimension.append(bo)
        if s.startswith("position"):
            po=[]
            for w in s[9:-1].split(","):
                po.append(int(w))
            position.append(po)
        if s.startswith("target"):
            tar=[]
            for w in s[7:-1].split(","):
                tar.append(int(w))
            target.append(tar)
    return room,dimension,position,target

r=open("HW2/booth.txt")
for line in r:
    room,dim,pos,tar = parseline(line)
# r.close()
# print(room)
# print(dim)
# print(pos)
# print(tar)
# for bol in pos:
#     print(bol)

r=Room([3,3],[Booth(1,2,1,0,1), Booth(2,2,1,1,2), Booth(3,1,1,0,0)])
r.plot_room()
print(arrange_booth(r,[3,0,2]))

r=Room([3,3],[Booth(1,1,1,0,0)])
r.plot_room()
print(arrange_booth(r,[1,2,2]))


print('finished')
