import copy
import sys
import time
from itertools import chain
import logging
fmt="[%(levelname)s]%(funcName)s():%(lineno)i: %(message)s "
logging.basicConfig(level=logging.DEBUG, format=fmt)
log = logging.getLogger(__name__)

def parseline(file):
    ''' parse every line in input txt file'''
    r=open(file)
    kind = -1
    dish_wid = []
    dish_num = []
    sep = -1
    hot_num = -1
    tab_wid = -1
    for line in r:
        word = line.split(".")
        for s in word:
            s=s.strip()
            if s.startswith("dishes"):
                kind = int(s[len("dishes("):-1])
            if s.startswith("separation"):
                sep = int(s[len("separation("):-1])
            if s.startswith("dish_width"):
                dish = []
                for w in s[len("dish_width("):-1].split(","):
                    dish.append(int(w))
                dish_wid.append(dish)
            if s.startswith("demand"):
                demand = []
                for w in s[len("demand("):-1].split(","):
                    demand.append(int(w))
                dish_num.append(demand)
            if s.startswith("table_width"):
                tab_wid = int(s[len("table_width("):-1])
            if s.startswith("hot"):
                hot_num = int(s[len("hot("):-1])
    return kind, sep, hot_num, tab_wid, sorted(dish_wid,key=lambda x:x[0]), sorted(dish_num, key=lambda x:x[0]), sum( x[1] for x in dish_num )

class Dish(object):
    ''' dish object contains width/tempature'''
    def __init__(self, width, hot):
        self.width = width
        self.hot = hot

    def __str__(self):
        return  (" hot " if self.hot else " cool") + " wid:" + str(self.width) 



class Table(object):
    ''' define table width/num on table '''

    def __init__(self):
        ''' init with width/num/dishes on table'''
        self.used_width = 0
        self.dishes_on = []

        # test 2nd method
        self.previous_hot = None
    
    def __str__(self):
        ''' print table information'''

        return " table used_wid:" + str(self.used_width) + " dishes:"+str(len(self.dishes_on))



class Buffet(object):
    ''' room for tables'''

    def __init__(self, wid, sep, used=set(), tables=[Table()]):
        self.table_wid = wid
        self.sep = sep
        #self.total_dishes = 0
        #self.min_table = 0
        #self.dishes = dishes
        self.tables = tables 
        self.used_dish = used
        self.state = self.plot_buffet()
        

    def plot_buffet(self):
        slist = [str("h" if dish.hot else "c")+str(dish.width) for table in self.tables for dish in table.dishes_on]
        s = "".join(slist) 
        log.debug(s)
        return s
    

    def put_dish(self, dish):
        ''' judge if current table available for this dish'''
        if self.tables==[]:
            self.tables.append(Table())
        table=self.tables[-1]
        sep = 0 if table.dishes_on == [] or table.dishes_on[-1].hot == dish.hot else self.sep

        if table.used_width + dish.width + sep > self.table_wid:
            self.tables.append(Table())
            table = self.tables[-1]
            log.info(" create_new table " + str(self.tables[-1]))
        table.used_width += dish.width + sep
        table.dishes_on.append(dish)
        self.state = self.plot_buffet()
        log.info(" put " +str(dish)+" success!!")
        

    def remove_dish(self):
        ''' remove dish from dish_top'''
        table = self.tables[-1]
        dish = table.dishes_on[-1]
        table.used_width -= dish.width
        # pop dish on table
        pop_dish = table.dishes_on.pop()
        if table.dishes_on!=[]:
            if pop_dish.hot != table.dishes_on[-1].hot:
                table.used_width -= self.sep
        #self.total_dishes -= 1
        #self.plot_buffet()
        
        log.info("__remove "+str(dish))
        if table.dishes_on==[]:
            log.info('del table')
            del self.tables[-1]
        

    
    def place_dishes(self, dishes):
        ''' try put dish on table '''

        # if all dish already on table compare with min table num
        # reach requried num
        if len(self.used_dish) == len(dishes):
            self.plot_buffet()
            global min_table
            min_table = len(self.tables) if min_table == 0 else min(min_table, len(self.tables)) 
            log.info("min table = "+str(min_table))
            return 'Done' 
        # try every possible order on this table
        for i in range(len(dishes)):
            # if dish not used
            if i in self.used_dish:
                continue

            # force same kind dish placed in one order
            #if i>0 and not used_dish[kind][i-1]:
            #    continue
        
            # try put this dish 
            self.put_dish(dishes[i])
            self.used_dish.add(i)
            self.place_dishes(dishes)
            self.used_dish.remove(i)
            self.remove_dish()
            
            # put dish success
            log.info("set "+str(i)+" True:"+str(self.used_dish))
            # try put next dish
            #self.place_dishes(dishes, used_dish, need_dish)# in {'Done', None}
            #self.remove_dish(self.tables[-1], dishes[i])
            #used_dish[i] = False
            #log.info("set "+str(i)+" False:"+str(used_dish))
    
    def put_dish2(self, dish):
            ''' judge if current table available for this dish'''
            if self.tables==[]:
                self.tables.append(Table())
            table=self.tables[-1]
            sep = 0 if table.previous_hot == None or table.previous_hot == dish.hot else self.sep

            if table.used_width + dish.width + sep > self.table_wid:
                self.tables.append(Table())
                table = self.tables[-1]
                log.info(" create_new table " + str(self.tables[-1]))
            table.used_width += dish.width + sep
            #table.dishes_on.append(dish)
            table.previous_hot = dish.hot
            self.state = self.plot_buffet()
            log.info(" put " +str(dish)+" success!!")

    def next_buffet(self, dishes):
        for dish in range(len(dishes)):
            if dish not in self.used_dish :
                new_buffet = copy.copy(self) 
                new_buffet.used_dish = copy.deepcopy(self.used_dish) 
                new_buffet.tables = copy.deepcopy(self.tables)
                new_buffet.put_dish2(dishes[dish])
                new_buffet.used_dish.add(dish)
                yield new_buffet



def place_dish(buffet, dishes):
    
    bfs_queue = [buffet]
    min_table=0
    explored=set()
    while bfs_queue:
        buffet = bfs_queue.pop(0)
        for new_buffet in buffet.next_buffet(dishes):
            
            if new_buffet.state in explored:
                log.debug('explored')
                continue
            # all used
            if len(new_buffet.used_dish) == len(dishes): 
                min_table = len(new_buffet.tables) if min_table == 0 else min(len(new_buffet.tables), min_table) 
                continue
            explored.add(new_buffet.state)
            if min_table == 0 or min_table > (len(new_buffet.tables)):
                bfs_queue.append(new_buffet)
    return min_table

min_table = 0

def main():
    log.debug(sys.argv[1])
    ans=[]
    kind, sep, hot_num, table_wid, dish_wid, dish_num, total_dishes = parseline(sys.argv[1])
    log.info("total:"+str(total_dishes)+" wid:"+str(table_wid)+" sep:"+str(sep))
    #dishes = [[Dish(dish_wid[i][0], dish_wid[i][1], True) for j in range(dish_num[i][1])] for i in range(hot_num)]
    #dishes += [[Dish(dish_wid[i][0], dish_wid[i][1], False) for j in range(dish_num[i][1])] for i in range(hot_num, kind)] 
    dishes = [[Dish(dish_wid[i][1], True) for j in range(dish_num[i][1])] for i in range(hot_num)] 
    dishes += [[Dish(dish_wid[i][1], False) for j in range(dish_num[i][1])] for i in range(hot_num, kind)] 
    
    for dish in dishes:
        for j in dish:
            log.debug(str(j))
    dishes = list(chain.from_iterable(dishes))
    log.debug(dishes)
    #used_dish = [[ False for i in range(dish_num[j][1])] for j in range(len(dish_num))]
    #used_dish = [False for i in range(len(dishes))]
    #log.debug(used_dish)

    buffet=Buffet(table_wid, sep)
    start = time.time()
    #buffet.place_dishes(dishes)
    #print(min_table)
    #print(time.time()-start)
    #start = time.time()
    print(place_dish(buffet, dishes))
    print(time.time()-start)
    #print("tables(" + str(buffet.min_table)+").")
    #print(time.time()-start)
main()