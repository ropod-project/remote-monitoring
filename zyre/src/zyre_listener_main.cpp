#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <zmq.hpp>

#include <jsoncpp/json/json.h>
#include <jsoncpp/json/reader.h>
#include <jsoncpp/json/writer.h>
#include <jsoncpp/json/value.h>

#include <boost/algorithm/string.hpp>

#include "zyre_listener.hpp"

int main()
{
    std::unique_ptr<ZyreListener> zyre_listener(new ZyreListener(5));

    // creating the zmq server
    zmq::context_t context(1);
    zmq::socket_t server(context, ZMQ_REP);
    server.bind("tcp://*:5670");

    std::vector<std::string> received_zmq_msgs;
    std::string target_node_uuid;
    Json::Value query_reply;
    std::string query_reply_str;

    size_t data_size;

    bool terminate = true;
    while(true)
    {
        zmq::message_t message;
        server.recv(&message);
        std::string contents = std::string(static_cast<char*>(message.data()), message.size());
        boost::split(received_zmq_msgs, contents, boost::is_any_of("++"));

        try
        {
            if (!received_zmq_msgs[0].compare("GET_ROPOD_LIST"))
            {
                std::vector<std::string> ropod_names = zyre_listener->getRopodList(received_zmq_msgs[2]);

                std::string ropods = "[";
                for (size_t i=0; i<ropod_names.size(); i++)
                {
                    ropods = ropods + "[\"" + ropod_names[i] + "\"]";
                    if (i != ropod_names.size() - 1)
                        ropods += ", ";
                }
                ropods += "]";

                data_size = ropods.size();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), ropods.c_str(), ropods.size());
                server.send (reply);
            }
            else if (!received_zmq_msgs[0].compare("VARIABLE_QUERY"))
            {
                query_reply_str = zyre_listener->getFeatures(received_zmq_msgs[2]);

                // sending the reply to the interface
                data_size = query_reply_str.length();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), query_reply_str.c_str(), query_reply_str.length());
                server.send (reply);
            }
            else if (!received_zmq_msgs[0].compare("DATA_QUERY"))
            {
                query_reply_str = zyre_listener->getData(received_zmq_msgs[2]);

                // sending the reply to the interface
                data_size = query_reply_str.length();
                zmq::message_t reply (data_size);
                memcpy(reply.data (), query_reply_str.c_str(), query_reply_str.length());
                server.send (reply);
            }
        }
        catch(zmq::error_t exception)
        {
            std::cout << zmq_strerror(exception.num()) << std::endl;
        }
    }

    return 0;
}
