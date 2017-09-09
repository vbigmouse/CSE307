def gcd(a,b):
    if a==b:
        return a
    else:
        if a>b:
            return gcd(a-b,a)
        else:
            return gcd(a,b-a)

a=input("Input1:")
b=input("Input2:")
print "GCD = %r" %gcd(a,b)

