#include <string>
#include <iostream>

#include <czmq.h>
#include <zmq.hpp>

#include <memory>
#include <sstream>
#include <map>
#include <vector>

#include "node.hpp"
#include "config_params.hpp"

class ZyerListener
{
    private:
        ZyreParams zyre_config_params_;
        zyre::node_t *listener_node_;
        zactor_t *actor_;

    public:
        ZyerListener()
            {
                // zyre_config_params_ = config_params;

                listener_node_ = new zyre::node_t("z_listener_node");
                // for (int i = 0; i < config_params.groups.size(); i++)
                // {
                //     listener_node_->join(config_params.groups[i]);
                // }

                // actor is similar to socket
                // actor_ = zactor_new(ZyerListener::receiveLoop, this);
                actor_ = zactor_new(ZyerListener::newReceiveTask, this);


                    while (!zsys_interrupted) {
                        std::cout << "Waiting for message" << std::endl;
                        char message [1024];
                        if (!fgets (message, 1024, stdin))
                            break;
                        message [strlen (message) - 1] = 0;     // Drop the trailing linefeed
                        zstr_sendx (actor_, "SHOUT", message, NULL);
                    }
                zclock_sleep(100);
            }


        static void receiveLoop(zsock_t *pipe, void *args);
        static void newReceiveTask(zsock_t *pipe, void *args);

};

void ZyerListener::newReceiveTask(zsock_t *pipe, void *args)
{
    zyre_t *node = zyre_new ((char *) args);
    if (!node)
        return;                 //  Could not create new node

    zyre_start (node);
    zyre_join (node, "CHAT");
    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, zyre_socket (node), NULL);
    while (!terminated) {
        void *which = zpoller_wait (poller, -1);
        if (which == pipe) {
            zmsg_t *msg = zmsg_recv (which);
            if (!msg)
                break;              //  Interrupted

            char *command = zmsg_popstr (msg);
            std::cout << "Received message:" << command << std::endl;

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

void ZyerListener::receiveLoop(zsock_t *pipe, void *args)
{
    ZyerListener *z_listener = (ZyerListener*)(args);
    zsock_signal(pipe, 0);
    bool terminated = false;

    // this poller will listen to messages that the node receives
    // AND messages received by this actor on pipe
    zpoller_t *poller = zpoller_new (pipe, z_listener->listener_node_->socket(), NULL);
    while (!terminated)
    {
        void *which = zpoller_wait (poller, -1); // no timeout

        // what is the difference between msg sent to node and actor
        if (which == pipe) // message sent to the actor
        {
            zmsg_t *msg = zmsg_recv (which);
            if (!msg)
                break;              //  Interrupted

            char *command = zmsg_popstr (msg);
            std::cout << "received message is: "<< command << std::endl;
            if (streq (command, "$TERM"))
            {
                terminated = true;
            }
            else
            {
                std::cerr << "received massge: "<< command << std::endl;
                std::cerr << "invalid message to actor" << std::endl;
                assert (false);
            }
            free (command);
            zmsg_destroy (&msg);
        }
        else if (which == z_listener->listener_node_->socket()) // message sent to the node
        {
            zmsg_t *msg = zmsg_recv (which);
            // z_listener->respond(msg);
            std::cout << "msg (inside the else if) is: "<< msg << std::endl;

        }
    }
    zpoller_destroy (&poller);
}

int main(int argc, char const *argv[])
{
    // /* code */
    // std::cout << "Before creating the object "<< std::endl;

    // ZyerListener obj1;
    // std::cout << "After creating the object "<< std::endl;

    // creating the zmq server
    zmq::context_t context(1);
    zmq::socket_t server(context, ZMQ_REP);
    server.bind("tcp://*:5670");

    int i = 0;

    while (true)
    {
        std::cout << "Loop number: " << i << std::endl;
        i++;
        if (i>10)
        {
            break;
        }

    	try
    	{
            zmq::message_t message;
            server.recv(&message);
            std::string contents = std::string(static_cast<char*>(message.data()), message.size());
            std::cout << "received message: " << contents << std::endl;

            // here we call the class for getting the query from the robots
            // if we want to get all the features

            std::cout << "Comparing: " << contents.compare("GET_ROPOD_LIST") << std::endl;

            if (!contents.compare("GET_ROPOD_LIST"))
            {
            	std::cout << "GET ROPOD LIST " << std::endl;

            	//  Send reply back to client
            	zmq::message_t reply (5);
            	memcpy (reply.data (), "World", 5);
            	server.send (reply);
            	std::cout << "Reply sent " << std::endl;

            } else if (!contents.compare("GET_FEATURES"))
            {
                std::cout << "GET_FEATURES" << std::endl;

            	/* code */
            } else if (!contents.compare("GET_QUERY"))
            {
                std::cout << "GET_QUERY" << std::endl;

            	/* code */
            } else {
            	/* code */
            }

            // if we want to get a query from one feature

    	}
    	catch(zmq::error_t exception)
    	{
    		std::cout << zmq_strerror(exception.num()) << std::endl;
    	}

    }

    return 0;
}