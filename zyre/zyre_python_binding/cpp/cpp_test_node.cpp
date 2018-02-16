#include <string>
#include <iostream>

#include <zyre.h>
// #include "zyre.h"

using namespace std;





//  This actor will listen and publish anything received
//  on the CHAT group

//  This actor will listen and publish anything received
//  on the CHAT group

static void 
chat_actor (zsock_t *pipe, void *args)
{
    zyre_t *node = zyre_new ((char *) args);

    //  Could not create new node
    if (!node)
        return;

    zyre_start (node);
    zyre_join (node, "CHAT");

    //  Signal "ready" to caller
    zsock_signal (pipe, 0);

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, zyre_socket (node), NULL);
    while (!terminated) {
        void *which = zpoller_wait (poller, -1);
        if (which == pipe) {
            zmsg_t *msg = zmsg_recv (which);
            if (!msg)
                break;              //  Interrupted

            char *command = zmsg_popstr (msg);
            if (streq (command, "$TERM"))
                terminated = true;
            else
            if (streq (command, "SHOUT")) { 
                char *string = zmsg_popstr (msg);
                zyre_shouts (node, "CHAT", "%s", string);
            }
            else {
                puts ("E: invalid message to actor");
                assert (false);
            }
            free (command);
            zmsg_destroy (&msg);
        }
        else
        if (which == zyre_socket (node)) {
            zmsg_t *msg = zmsg_recv (which);
            char *event = zmsg_popstr (msg);
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            if (streq (event, "ENTER"))
                printf ("%s has joined the chat\n", name);
            else
            if (streq (event, "EXIT"))
                printf ("%s has left the chat\n", name);
            else
            if (streq (event, "SHOUT"))
                printf ("%s: %s\n", name, message);
            else
            if (streq (event, "EVASIVE"))
                printf ("%s is being evasive\n", name);

            free (event);
            free (peer);
            free (name);
            free (group);
            free (message);
            zmsg_destroy (&msg);
        }
    }
    zpoller_destroy (&poller);
    zyre_stop (node);
    zclock_sleep (100);
    zyre_destroy (&node);
}


int
main (int argc, char *argv [])
{
    if (argc < 2) {
        puts ("syntax: ./chat myname");
        exit (0);
    }
    zactor_t *actor = zactor_new (chat_actor, argv [1]);
    assert (actor);
    
    while (!zsys_interrupted) {
        char message [1024];
        if (!fgets (message, 1024, stdin))
            break;
        message [strlen (message) - 1] = 0;     // Drop the trailing linefeed
        zstr_sendx (actor, "SHOUT", message, NULL);
    }
    zactor_destroy (&actor);
    return 0;
}

// int main(int argc, char const *argv[])
// {
// 	cout<<"hello world"<<"\n";
// 	return 0;
// }