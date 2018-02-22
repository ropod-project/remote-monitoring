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


// #include <json/json.h>

#include <typeinfo>

#include <jsoncpp/json/json.h>
#include <jsoncpp/json/reader.h>
#include <jsoncpp/json/writer.h>
#include <jsoncpp/json/value.h>
#include <fstream>
// #include <string>

#include <time.h>




class ZyerListener
{
    private:
        ZyreParams zyre_config_params_;
        // zyre::node_t *listener_node_;
        zyre_t *listener_node_;
        zactor_t *actor_;

        const int NUM_SECONDS = 10;
        // actor_ = zactor_new(ZyerListener::newReceiveTask, this);

        std::vector<std::vector<std::string>> ropodLists;

        char* receivedMsg;

    public:
        ZyerListener()
            {

                // creating a node
                listener_node_ = zyre_new ("z_listener_node");

                // zyre_config_params_ = config_params;
                // listener_node_ = new zyre::node_t("z_listener_node");


                // actor is similar to socket
                // actor_ = zactor_new(ZyerListener::newReceiveTask, this);

                // while (!zsys_interrupted) {
                //     std::cout << "Waiting for message" << std::endl;
                //     char message [1024];
                //     if (!fgets (message, 1024, stdin))
                //         break;
                //     message [strlen (message) - 1] = 0;     // Drop the trailing linefeed
                //     zstr_sendx (actor_, "SHOUT", message, NULL);
                // }
                // zclock_sleep(100);
            }


        static void receiveLoop(zsock_t *pipe, void *args);
        static void newReceiveTask(zsock_t *pipe, void *args);
        // static std::vector<std::vector<std::string>> getRopodList();
        std::vector<std::vector<std::string>> getRopodList();

        static void receiveRopodList(zsock_t *pipe, void *args);
        static void receiveQueryResult(zsock_t *pipe, void *args);
        char* getQuery(char* peer, std::string msg, std::string command);

        


};

std::vector<std::vector<std::string>> ZyerListener::getRopodList()
{

    // shout
    // listener_node_ = new zyre::node_t("z_listener_node");

    // zyre_shouts(listener_node_, "ROPOD", "SEND_NAME");
    // zyre_shouts(ZyerListener->listener_node_, "ROPOD", "SEND_NAME");
    // zyre_shouts(ZyerListener.listener_node_, "ROPOD", "SEND_NAME");
    // listener_node_->shout("ROPOD", "SEND_NAME");

    zyre_shouts (listener_node_, "ROPOD", "SEND_NAME");

    // receives all replies
    std::vector< std::vector<std::string> > nodesUuids;

    std::cout << "Inside getRopodList" << std::endl;

    actor_ = zactor_new(ZyerListener::receiveRopodList, listener_node_);

    // char message [1024];
    // if (!fgets (message, 1024, stdin))
    //     break;
    // message [strlen (message) - 1] = 0;     // Drop the trailing linefeed
    // zstr_sendx (actor_, "SHOUT", message, NULL);

    return ropodLists;

}

char* ZyerListener::getQuery(char* peer, std::string msg, std::string command)
{
    char msg_chr[msg.length()+1];
    strcpy(msg_chr, msg.c_str());

    if (!command.compare("GET_FEATURES"))
    {
        zyre_whispers (listener_node_, peer, msg_chr);
        // zyre_whispers (listener_node_, peer, msg.c_str());
        // zyre_whispers (listener_node_, peer, msg);
        // zyre_whisper (ZyerListener->listener_node_, peer, msg);
        
    }
    else
    {
        // if it is not GET_FEATURES then it is get query
        zyre_whispers (listener_node_, peer, msg_chr);

    }

    // receives all replies
    std::vector< std::vector<std::string> > nodesUuids;

    std::cout << "Inside getQuery" << std::endl;

    actor_ = zactor_new(ZyerListener::receiveQueryResult, listener_node_);

    // char message [1024];
    // if (!fgets (message, 1024, stdin))
    //     break;
    // message [strlen (message) - 1] = 0;     // Drop the trailing linefeed
    // zstr_sendx (actor_, "SHOUT", message, NULL);

    return receivedMsg;

}

void ZyerListener::receiveQueryResult(zsock_t *pipe, void *args)
{

    std::vector<std::string> row;
    zyre_t *node = zyre_new ((char *) args);
    if (!node)
        return;                 //  Could not create new node

    zyre_start (node);
    zyre_join (node, "ROPOD");
    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;

    // this poller will listen to messages that the node receives
    // AND messages received by this actor on pipe
    // zpoller_t *poller = zpoller_new (pipe, zyre_socket (node), NULL);
    zpoller_t *poller = zpoller_new (pipe, ZyerListener->listener_node_->socket(), NULL);

    for ( int i = 0 ; i < 3 ; i++)
    {
    // while (!terminated) {
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
                zyre_shouts (node, "ROPOD", "%s", string);
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

            node->receivedMsg = message;

            // if (streq (event, "ENTER"))
            //     printf ("%s has joined the chat\n", name);
            // else
            // if (streq (event, "EXIT"))
            //     printf ("%s has left the chat\n", name);
            // else
            // if (streq (event, "SHOUT"))
            //     printf ("%s: %s\n", name, message);
            // else
            // if (streq (event, "EVASIVE"))
            //     printf ("%s is being evasive\n", name);



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

    sleep(1);
}


void ZyerListener::receiveRopodList(zsock_t *pipe, void *args)
{

    std::vector<std::string> row;
    zyre_t *node = zyre_new ((char *) args);
    if (!node)
        return;                 //  Could not create new node

    zyre_start (node);
    zyre_join (node, "ROPOD");
    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, zyre_socket (node), NULL);

    for ( int i = 0 ; i < 3 ; i++)
    {
    // while (!terminated) {
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
                zyre_shouts (node, "ROPOD", "%s", string);
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

            row.push_back(name);
            row.push_back(peer);

            ropodLists.push_back(row);
            row.clear();

            // if (streq (event, "ENTER"))
            //     printf ("%s has joined the chat\n", name);
            // else
            // if (streq (event, "EXIT"))
            //     printf ("%s has left the chat\n", name);
            // else
            // if (streq (event, "SHOUT"))
            //     printf ("%s: %s\n", name, message);
            // else
            // if (streq (event, "EVASIVE"))
            //     printf ("%s is being evasive\n", name);



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

    sleep(1);
}

void ZyerListener::newReceiveTask(zsock_t *pipe, void *args)
{
    zyre_t *node = zyre_new ((char *) args);
    if (!node)
        return;                 //  Could not create new node

    zyre_start (node);
    zyre_join (node, "ROPOD");
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
                zyre_shouts (node, "ROPOD", "%s", string);
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



// -----------------------------------------------------------
int main(int argc, char const *argv[])
{
    std::cout << "Before creating the object "<< std::endl;
    ZyerListener z_listener_obj;
    // std::cout << "After creating the object "<< std::endl;

    // creating the zmq server
    zmq::context_t context(1);
    zmq::socket_t server(context, ZMQ_REP);
    server.bind("tcp://*:5670");

    int i = 0;

    // read a list of dictionaries in the json format as the dummy data
    Json::Value jdata;
    Json::Reader jreader;

    std::ifstream file_data("../data.json", std::ifstream::binary);
    file_data >> jdata;
    std::cout << "jdata: " << jdata << std::endl;
    std::cout << "jdata type" << typeid(jdata).name() <<std::endl;

    // convert json to string
    Json::FastWriter jfwriter;
    std::string jstr_data = jfwriter.write(jdata);
    std::cout << "jstr_data: " << jstr_data << std::endl;
    std::cout << "jstr_data type: " << typeid(jstr_data).name() <<std::endl;    
    std::cout << "jstr_data length: " << jstr_data.length() << std::endl;
    std::cout << "jstr_data size: " << jstr_data.size() << std::endl;




    const char *test2 = jstr_data.c_str();
// ----------------------------
    // test code for communicating the dict
    // while(true)
    // {
        zmq::message_t message;
        server.recv(&message);
        std::string contents = std::string(static_cast<char*>(message.data()), message.size());
        std::cout << "received message: " << contents << std::endl;

        try
        {
            if (!contents.compare("GET_ROPOD_LIST"))
            {
                std::vector<std::vector<std::string>> ropodLists;
                
                ropodLists = z_listener_obj.getRopodList();

                data_size = ropodLists.size();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), ropodLists.data(), data_size);

            }
            else if (!contents.compare("GET_FEATURES"))
            {
                char* received_msg;
                received_msg = z_listener_obj.getQuery();

                data_size = received_msg.size();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), received_msg, data_size);

            }
            else if (!contents.compare("GET_QUERY"))
            {

            }
        }
        catch(zmq::error_t exception)
        {
            std::cout << zmq_strerror(exception.num()) << std::endl;
        }
        //  Send reply back to client
        // int data_size =  jstr_data.size();

        // zmq::message_t reply (5);
        // zmq::message_t reply (data_size);

        // memcpy (reply.data (), "World", 5);
        // memcpy (reply.data (), test2, data_size);

        server.send (reply);
        std::cout << "Reply sent " << std::endl;
    // }

    return 0;
}