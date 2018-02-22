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
        zyre::node_t *listener_node_;
        zactor_t *actor_;

        const int NUM_SECONDS = 10;
        // actor_ = zactor_new(ZyerListener::newReceiveTask, this);

        std::vector<std::vector<std::string>> ropodLists;

        char* receivedMsg;

    public:
        ZyerListener::ZyerListener()
        {
            // zyre_config_params_ = config_params;
            // data_logger_ = data_logger;

            // TODO: the id has to be different for each black box
            query_node_ = new zyre::node_t("black_box_query_interface");
            for (int i = 0; i < config_params.groups.size(); i++)
            {
                query_node_->join(config_params.groups[i]);
            }

            actor_ = zactor_new(QueryInterfaceManager::receiveLoop, this);
            zclock_sleep(100);

            for (std::string data_source : data_sources)
            {
                std::shared_ptr<QueryInterfaceBase> query_interface = QueryInterfaceFactory::getQueryInterface(data_source);
                query_interfaces_[data_source] = query_interface;
            }
        }
    

        static void receiveLoop(zsock_t *pipe, void *args);
        static void newReceiveTask(zsock_t *pipe, void *args);
        // static std::vector<std::vector<std::string>> getRopodList();
        std::vector<std::vector<std::string>> getRopodList();

        static void receiveRopodList(zsock_t *pipe, void *args);
        static void receiveQueryResult(zsock_t *pipe, void *args);
        static char* getQuery(char* peer, std::string msg, std::string command);
};






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