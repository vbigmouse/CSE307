/* 
    109971346 Hung-Ruey Chen
    CSE307 Homework 1 
*/
#include <stdio.h>

int main()
{
    int i,j;
    printf("Input num 1:");
    scanf("%d",&i);
    printf("Input num 2:");
    scanf("%d",&j);
    while(i!=j)
    {
        if(i>j) i-=j;
        else j-=i;
    }
    printf("GCD = %d\n",i);
}
