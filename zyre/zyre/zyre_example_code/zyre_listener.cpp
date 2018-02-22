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
#include <boost/algorithm/string.hpp>




class ZyerListener
{
    private:
        ZyreParams zyre_config_params_;
        zyre::node_t *listener_node_;
        zactor_t *actor_;

        const int NUM_SECONDS = 10;
        // actor_ = zactor_new(ZyerListener::newReceiveTask, this);

        std::vector<std::vector<std::string>> ropodLists;
        Json::StreamWriterBuilder json_stream_builder_;

        char* receivedMsg;
        bool ropod_list_received;
        bool query_result_received;



    public:
        ZyerListener()
            {
                // zyre_config_params_ = config_params;
                listener_node_ = new zyre::node_t("z_listener_node");
                listener_node_->start();
                listener_node_->join("ROPOD");
                ropod_list_received = false;
                query_result_received = false;
            }


        std::vector<std::vector<std::string>> getRopodList(std::string message);
        static void receiveRopodList(zsock_t *pipe, void *args);

        // char* getQuery(std::string peer, std::string msg);        
        char* getQuery(std::string msg);
        static void receiveQueryResult(zsock_t *pipe, void *args);
        static void receiveQueryResult2(zsock_t *pipe, void *args);


        zmsg_t* string_to_zmsg(std::string msg);
        void shoutMessage(const Json::Value &json_msg);
        Json::Value parseMessageJson(std::string msg);

};

char* ZyerListener::getQuery(std::string msg)
{
    // zmsg_t* zmsg = string_to_zmsg(msg);
    // std::cout << "zmsg before whisper: " << zmsg << std::endl;
    // listener_node_->whisper(peer, zmsg);
    // std::cout << "After whisper " << std::endl;

    Json::Value jmsg =  parseMessageJson(msg);
    std::cout << " jmessage: " << jmsg << std::endl;
    ZyerListener::shoutMessage(jmsg);
    std::cout << " After shout " << std::endl;

    // receives all replies
    actor_ = zactor_new(ZyerListener::receiveQueryResult, this);
    // std::cout << "After zactor_new " << std::endl;


    while (!query_result_received) {}
    query_result_received = false;
    std::cout << "After while loop " << std::endl;


    return receivedMsg;
}


void ZyerListener::receiveQueryResult(zsock_t *pipe, void *args)
{
    ZyerListener *listener = (ZyerListener*)args;

    Json::Value rec_msg;
    std::string null_flag;

    // std::vector<std::string> row;

    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);

    int loopNum = 0;

    while (!terminated) {
        null_flag = "NULL";
        if (loopNum > 5)
            {
                terminated = true;
            }
        loopNum++;

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
            {
                puts ("E: invalid message to actor");
                assert (false);
            }
            free (command);
            zmsg_destroy (&msg);
        }
        else if (which == listener->listener_node_->socket())
        {
            zmsg_t *msg = zmsg_recv (which);
            char *event = zmsg_popstr (msg);
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);

            std::string name_str(name);
            std::cout << name_str << std::endl;
            if (name_str.find("query_interface") == std::string::npos)
            {
                continue;
            }
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            // row.push_back(name);
            // row.push_back(peer);
            // listener->ropodLists.push_back(row);
            // row.clear();
            // std::cout << " received message: " << message << std::endl;

            // std::cout << " null_flag: " << null_flag << std::endl;
            // null_flag = message;
            // std::cout << " null_flag: " << null_flag << std::endl;


            // if (null_flag.compare("NULL") == 0)
            if(message == NULL || ((message != NULL) && (message[0] == '\0')))
            {
                std::cout << "message from: "<< name << " was empty" << std::endl;
                continue;
            }
            // change message to json
            // rec_msg = parseMessageJson(message);
            rec_msg = listener->parseMessageJson(message);
            std::cout << "After pasrsing to json " << std::endl;
            std::cout << "json received message: " << rec_msg << std::endl;
            // null_flag = message;
            // if (!null_flag.compare("NULL"))
            // {
            //     continue;
            // }
            if (!rec_msg["header"]["type"].compare("VARIABLE_QUERY"))
            {
                std::cout << "Inside the if " << std::endl;

                listener->receivedMsg = message;
                listener->query_result_received = true;
                terminated = true;
            }

            free (event);
            free (peer);
            free (name);
            free (group);
            free (message);
            zmsg_destroy (&msg);

        sleep(1);
        }
    }
    listener->query_result_received = true;
    // std::cout << "ropod list received\n";
    zpoller_destroy (&poller);
    zclock_sleep (100);
}









void ZyerListener::receiveQueryResult2(zsock_t *pipe, void *args)
{
    ZyerListener *listener = (ZyerListener*)args;
    Json::Value rec_msg;
    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);

    std::cout << "Call back after zpoller_new" << std::endl;

    int loopNum = 0;

    // while (!terminated) {
    //     if (loopNum > 2)
    //         {
    //             terminated = true;
    //         }
    //     loopNum++; 

        std::cout << "Callback-before zpoller_wait" << std::endl;

        void *which = zpoller_wait (poller, -1);
        if (which == pipe) {
            zmsg_t *msg = zmsg_recv (which);

            char *command = zmsg_popstr (msg);
            std::cout << "Received message:" << command << std::endl;

            if (streq (command, "$TERM"))
                terminated = true;
            else
            {
                puts ("E: invalid message to actor");
                assert (false);
            }
            free (command);
            zmsg_destroy (&msg);
        }
        else if (which == listener->listener_node_->socket())
        {

            std::cout << "Callback-before zmsg_recv" << std::endl;

            zmsg_t *msg = zmsg_recv (which);

            char *event = zmsg_popstr (msg);
            // std::cout << "Callback-after event: "<< event << std::endl;

            char *peer = zmsg_popstr (msg);
            // std::cout << "Callback-after peer: "<< peer << std::endl;

            char *name = zmsg_popstr (msg);
            // std::cout << "Callback-after name: "<< name << std::endl;

            char *group = zmsg_popstr (msg);
            // std::cout << "Callback-after group: "<< group << std::endl;

            char *message = zmsg_popstr (msg);
            std::cout << "Callback-after message: "<< message << std::endl;

            listener->receivedMsg = message;
            listener->query_result_received = true;


            // change message to json
            // rec_msg = listener->parseMessageJson(message);

            // if (!rec_msg["header"]["type"].compare("VARIABLE_QUERY"))
            // {
            //     listener->receivedMsg = message;
            //     listener->query_result_received = true;
            //     terminated = true;
            // }

            free (event);
            free (peer);
            free (name);
            free (group);
            free (message);
            zmsg_destroy (&msg);
        }

    //     sleep(1);
    // }
    zpoller_destroy (&poller);
    zclock_sleep (100);
}


/**
 * Converts message to a json message
 *
 * @param msg_params message data
 */
Json::Value ZyerListener::parseMessageJson(std::string msg)
{
    Json::Value jmsg;   
    Json::Reader reader;
    bool parsingSuccessful = reader.parse(msg.c_str(), jmsg);

    return jmsg;
}

std::vector<std::vector<std::string>> ZyerListener::getRopodList(std::string message)
{
    // shout to all the nodes and ask them to send their name and uuids
    // void ZyerListener::shoutMessage(const Json::Value &json_msg);

    Json::Value jmsg =  parseMessageJson(message);
    std::cout << " jmessage: " << jmsg << std::endl;

    ZyerListener::shoutMessage(jmsg);
    std::cout << " After shout " << std::endl;

    // receives all replies
    std::vector< std::vector<std::string> > nodesUuids;
    actor_ = zactor_new(ZyerListener::receiveRopodList, this);

    while (!ropod_list_received) {}
    ropod_list_received = false;

    return ropodLists;
}

void ZyerListener::receiveRopodList(zsock_t *pipe, void *args)
{
    ZyerListener *listener = (ZyerListener*)args;

    std::vector<std::string> row;

    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);

    int loopNum = 0;

    while (!terminated) {
        if (loopNum > 2)
            {
                terminated = true;
            }
        loopNum++;

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
            {
                puts ("E: invalid message to actor");
                assert (false);
            }
            free (command);
            zmsg_destroy (&msg);
        }
        else if (which == listener->listener_node_->socket())
        {
            zmsg_t *msg = zmsg_recv (which);
            char *event = zmsg_popstr (msg);
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            row.push_back(name);
            row.push_back(peer);

            std::cout << " received name: " << name << std::endl;
            std::cout << " received peer: " << peer << std::endl;
            listener->ropodLists.push_back(row);
            row.clear();

            free (event);
            free (peer);
            free (name);
            free (group);
            free (message);
            zmsg_destroy (&msg);

        sleep(1);
        }
    }
    listener->ropod_list_received = true;
    std::cout << "ropod list received\n";
    zpoller_destroy (&poller);
    zclock_sleep (100);
}

/**
 * Converts an std::string to a zmsg_t pointer
 *
 * @param msg the string to be converted
 */
zmsg_t* ZyerListener::string_to_zmsg(std::string msg)
{
    zmsg_t* message = zmsg_new();
    zframe_t *frame = zframe_new(msg.c_str(), msg.size());
    zmsg_prepend(message, &frame);
    return message;
}

/**
 * Shouts a message to all the groups of which query_node_ is part
 *
 * @param json_msg the json message that should be shouted
 */
void ZyerListener::shoutMessage(const Json::Value &json_msg)
{
    std::string msg = Json::writeString(json_stream_builder_, json_msg);
    zmsg_t* message = string_to_zmsg(msg);

    listener_node_->shout("ROPOD", message);
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

    std::vector<std::string> received_zmq_msgs;
    std::string target_node_uuid;
    Json::Value query_reply;
    std::string query_reply_str;

    size_t data_size;

    bool terminate = true;
// ----------------------------
    // test code for communicating the dict
    while(true)
    {
        zmq::message_t message;
        server.recv(&message);
        std::string contents = std::string(static_cast<char*>(message.data()), message.size());
        std::cout << "received message: " << contents << std::endl;

        boost::split(received_zmq_msgs, contents, boost::is_any_of("++"));
        std::cout << "received command: " << received_zmq_msgs[0] << std::endl;
        std::cout << "received message: " << received_zmq_msgs[2] << std::endl;
        std::cout <<std::endl;
        std::cout <<std::endl;


        for (auto &ii : received_zmq_msgs)
        {
            std::cout << i <<std::endl;
            std::cout << ii <<std::endl;
            i++;
        }



        try
        {
            if (!received_zmq_msgs[0].compare("GET_ROPOD_LIST"))
            // if (terminate)
            {
                // terminate = false;

                std::cout << "received command: " << received_zmq_msgs[0] << std::endl;

                std::vector<std::vector<std::string>> ropodLists;
                
                ropodLists = z_listener_obj.getRopodList(received_zmq_msgs[2]);

                std::string ropods = "[";
                for (size_t i=0; i < ropodLists.size(); i++)
                {
                    ropods = ropods + "[\"" + ropodLists[i][0] + "\", \"" + ropodLists[i][1] + "\"]";
                    if (i != ropodLists.size() - 1)
                        ropods += ", ";
                }
                ropods += "]";

                std::cout << std::endl << "received message in the main(): " << ropods << std::endl;

                data_size = ropods.size();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), ropods.c_str(), ropods.size());
                server.send (reply);
                std::cout << "Reply sent " << std::endl;
            }
            else if (!received_zmq_msgs[0].compare("QUERY"))
            {                
                target_node_uuid = received_zmq_msgs[2];
                std::cout << "target_node_uuid: " << received_zmq_msgs[2] << std::endl;

                // get query via zyre
                // query_reply_str = z_listener_obj.getQuery(received_zmq_msgs[2], received_zmq_msgs[4]);
                query_reply_str = z_listener_obj.getQuery(received_zmq_msgs[2]);

                std::cout << std::endl << "query reply in the main(): " << query_reply_str << std::endl;
                // std::cout << std::endl << "query reply in the main(): " << std::endl;


                // sending the reply to the interface
                data_size = query_reply_str.length();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), query_reply_str.c_str(), query_reply_str.length());
                server.send (reply);
                std::cout << "Reply sent " << std::endl;


            }
            // else if (!received_zmq_msgs[0].compare("WHISPER"))
            // {                
            //     target_node_uuid = received_zmq_msgs[2];
            //     std::cout << "target_node_uuid: " << received_zmq_msgs[2] << std::endl;

            //     // get query via zyre
            //     query_reply_str = z_listener_obj.getQuery(received_zmq_msgs[2], received_zmq_msgs[4]);
            //     std::cout << std::endl << "query reply in the main(): " << query_reply_str << std::endl;
            //     std::cout << std::endl << "query reply in the main(): " << std::endl;


            //     // sending the reply to the interface
            //     data_size = query_reply_str.length();
            //     zmq::message_t reply (data_size);
            //     memcpy(reply.data (), query_reply_str.c_str(), query_reply_str.length());
            //     server.send (reply);
            //     std::cout << "Reply sent " << std::endl;


            // }
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
    }

    return 0;
}