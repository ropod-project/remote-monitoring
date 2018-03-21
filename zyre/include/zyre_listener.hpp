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

        ///////////////////////////////////////////////////////////////////////
        // data queries
        std::vector<std::string> getQueryInterfaceList(std::string message, double timeout=-1);
        std::string getFeatures(std::string msg, double timeout=-1);
        std::string getData(std::string msg, double timeout=-1);
        ///////////////////////////////////////////////////////////////////////

        ///////////////////////////////////////////////////////////////////////
        // status queries
        std::vector<std::string> getRopodIDs(std::string message, double timeout=-1);
        std::string getStatus(std::string msg, double timeout=-1);
        ///////////////////////////////////////////////////////////////////////

    private:
        static void receiveData(zsock_t *pipe, void *args);
        Json::Value parseMessageJson(std::string msg);
        void shoutMessage(const Json::Value &json_msg);
        zmsg_t* stringToZmsg(std::string msg);

        /**
         * a dictionary in which the keys represent request sender IDs and the
         * values indicate whether a response has been received
         */
        std::map<std::string, bool> reply_received_;

        /**
         * a dictionary in which the keys represent request sender IDs and the
         * values represent lists of node names
         */
        std::map<std::string, std::vector<std::string>> node_names_;

        /**
         * a dictionary in which the keys represent request sender IDs and the
         * values represent the messages received as responses to those requests
         */
        std::map<std::string, std::string> received_msg_;

        std::map<std::string, std::string> query_info_;
        std::map<std::string, std::string> user_ropod_ids_;

        std::vector<std::string> status_node_names_;

        /**
         * message callback timeout
         */
        int timeout_;

        zactor_t* actor_;
        zyre::node_t *listener_node_;
        Json::StreamWriterBuilder json_stream_builder_;
};

struct ListenerParams
{
    ListenerParams(ZyreListener *listener, std::string sender_id)
    {
        this->listener = listener;
        this->sender_id = sender_id;
    }

    ZyreListener *listener;
    std::string sender_id;
};

#endif
