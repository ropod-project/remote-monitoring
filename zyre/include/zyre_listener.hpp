#ifndef ZYRE_LISTENER_H
#define ZYRE_LISTENER_H

#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <algorithm>

#include <jsoncpp/json/json.h>
#include <jsoncpp/json/reader.h>
#include <jsoncpp/json/writer.h>
#include <jsoncpp/json/value.h>

#include "extern/zyre/node.hpp"

class ZyreListener
{
    public:
        ZyreListener(int timeout);
        ~ZyreListener();

        std::vector<std::string> getRopodList(std::string message);
        std::string getQuery(std::string msg);
    private:
        static void receiveRopodList(zsock_t *pipe, void *args);
        static void receiveQueryResult(zsock_t *pipe, void *args);

        Json::Value parseMessageJson(std::string msg);
        void shoutMessage(const Json::Value &json_msg);
        zmsg_t* stringToZmsg(std::string msg);

        zyre::node_t *listener_node_;
        zactor_t *ropod_list_actor_;
        zactor_t *query_actor_;

        Json::StreamWriterBuilder json_stream_builder_;

        std::string received_msg_;
        bool ropod_list_received_;
        bool query_result_received_;
        int timeout_;
        std::vector<std::string> ropod_names_;
};

#endif
