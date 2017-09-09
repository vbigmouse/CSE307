

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
r=open("booth.txt")
for line in r:
    room,dim,pos,tar = parseline(line)
r.close()
print(room)
print(dim)
print(pos)
print(tar)
dp=[[0] * room[1] for i in range(room[0])]
print(dp)
for bol in pos:
    print(bol)

