#include<iostream>
using namespace std;

char board[3][3]={{'1','2','3'},{'4','5','6'},{'7','8','9'}};
int row;
int column;
bool tie = false;
char token = 'x';
string n1 = "";
string n2 = "";

void boardPrinter(){
    cout<<"tt     |     |     \n";
    cout<<"tt  "<<board[0][0]<<"  | "<<board[0][1]<<"   |  "<<board[0][2]<<" \n";
    cout<<"tt_____|_____|_____\n";
    cout<<"tt     |     |     \n";
    cout<<"tt  "<<board[1][0]<<"  | "<<board[1][1]<<"   |  "<<board[1][2]<<" \n";
    cout<<"tt_____|_____|_____\n";
    cout<<"tt     |     |     \n";
    cout<<"tt  "<<board[2][0]<<"  | "<<board[2][1]<<"   |  "<<board[2][2]<<" \n";
    cout<<"tt     |     |     \n";
}

void turnTaker(){
    int digit;

    if(token=='x')
    {
        cout<<n1<<" please enter ";
        cin>>digit;
    }
    if(token=='0')
    {
        cout<<n2<<" please enter ";
        cin>>digit;
    }

    if(digit==1)
    {
        row=0;
        column=0;
    }
    if(digit==2)
    {
        row=0;
        column=1;
    }
    if(digit==3)
    {
        row=0;
        column=2;
    }
    if(digit==4)
    {
        row=1;
        column=0;
    }
    if(digit==5)
    {
        row=1;
        column=1;
    }
    if(digit==6)
    {
        row=1;
        column=2;
    }
    if(digit==7)
    {
        row=2;
        column=0;
    }
    if(digit==8)
    {
        row=2;
        column=1;
    }
    if(digit==9)
    {
        row=2;
        column=2;
    }    
    else if(digit<1 || digit >9){
        cout<<"Invalid !!"<<endl;
        turnTaker(); // ask for input again if invalid
        return;
    }

    //checking if the space is open if it's x's turn
    if(token=='x' && board[row][column] != 'x' && board[row][column] != '0'){
        board[row][column]='x';
        token='0';
    }
    //if it's 0's turn and the space isn't taken 
    else if (token=='0' && board[row][column] != 'x' && board[row][column] != '0'){
        board[row][column]='0';
        token='x';
    }
    else{
        cout<<"There is not empty space!"<<endl;
        turnTaker(); // ask for input again if space is not empty
        return;
    }
    //boardPrinter();
}

bool gameOver()
{
    for(int i = 0; i < 3; i++)
    {
        //checking the horizontal and vertical lines 
        if(board[i][0] == board[i][1] && board[i][0] == board[i][2] || board[0][i] == board[1][i] && board[0][i] == board[2][i])
        {
            return true;
        }
    }
    
    //checking the diagonal lines
    if(board[0][0] == board[1][1] && board[1][1] == board[2][2] || board[0][2] == board[1][1] && board[1][1] == board[2][0])
    {
        return true;
    }

    //checking for tie
    for (int i=0; i< 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            if (board[i][j] != 'x' && board[i][j] != '0')
            {
                return false;
            }
        }
    }
    tie = true;
    return false;
}

int main()
{
    cout<<"Enter the name of the first player: ";
    getline(cin,n1);
    cout<<"Enter the name of the second player: ";
    getline(cin,n2);

    cout<<n1<<" is player one so they will play first.\n";
    cout<<n2<<" is player two so they will play second.\n";

    while (!gameOver())
    {
        boardPrinter();
        turnTaker();
    }

    if(token == 'x' && tie == false)
    {
        cout<<n2<<" Wins!\n";
    }
    else if(token == '0' && tie == false)
    {
        cout<<n1<<" Wins!\n";
    }
    else
    {
        cout<<"It's a tie!\n";
    }
    return 0;
}


