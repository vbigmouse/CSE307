var gcd = function(a,b)
{
    if(!b)
    {
        return a;
    }
    return gcd(b,a%b);

}
console.log("Input1=2154");
console.log("Input2=458");
console.log(gcd(2154,458));
