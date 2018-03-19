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
        std::string getFeatures(std::string msg);
        std::string getData(std::string msg);

        // ropod info related
        std::vector<std::string> getRopodIDs(std::string message);
        std::string getStatus(std::string msg);
        // ropod info end

    private:
        static void receiveRopodList(zsock_t *pipe, void *args);
        static void receiveFeatures(zsock_t *pipe, void *args);
        static void receiveData(zsock_t *pipe, void *args);

        // ropod info related
        static void receiveRopodIDs(zsock_t *pipe, void *args);
        static void receiveStatus(zsock_t *pipe, void *args);
        // ropod info end


        Json::Value parseMessageJson(std::string msg);
        void shoutMessage(const Json::Value &json_msg);
        zmsg_t* stringToZmsg(std::string msg);

        zyre::node_t *listener_node_;
        zactor_t *ropod_list_actor_;
        zactor_t *feature_query_actor_;
        zactor_t *data_query_actor_;

        // ropod info related
        zactor_t *ropod_id_actor_;
        zactor_t *status_query_actor_;
        // ropod info end


        Json::StreamWriterBuilder json_stream_builder_;

        std::string received_msg_;
        bool ropod_list_received_;
        bool features_received_;
        bool data_received_;
        int timeout_;
        std::vector<std::string> ropod_names_;

        // ropod info related
        bool ropod_ids_received_;
        bool status_received_;

        std::string received_status_;
        std::vector<std::string> ropod_ids_;
        // ropod info end
};

#endif
