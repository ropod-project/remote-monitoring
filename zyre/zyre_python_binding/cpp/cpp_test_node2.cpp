#include <thread>
#include <zyre.h>
#include "zyre.h"
#include <string>
#include <iostream>

using namespace std;


int main(int argc, char* argv[])
{
  zyre_t *node = zyre_new(NULL);
  int rc = zyre_start(node);
  zyre_join (node, "CHAT");

  cout<<"This is rc: "<<rc<<"\n";
  cout<<"This is node: "<<node<<"\n";

  zyre_stop (node);
  zclock_sleep (100);
  zyre_destroy (&node);

  cout<<"hello world"<<"\n";
  return 0;
  }
