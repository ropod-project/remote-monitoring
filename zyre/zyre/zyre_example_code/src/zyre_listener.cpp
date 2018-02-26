#include "zyre_listener.hpp"

ZyreListener::ZyreListener(int timeout)
{
    listener_node_ = new zyre::node_t("z_listener_node");
    listener_node_->start();
    listener_node_->join("ROPOD");
    ropod_list_received_ = false;
    query_result_received_ = false;
    timeout_ = timeout;
}

ZyreListener::~ZyreListener()
{
    listener_node_->leave("ROPOD");
    listener_node_->stop();
    delete listener_node_;
}

std::vector<std::string> ZyreListener::getRopodList(std::string message)
{
    // shout to all the nodes and ask them to send their name and uuids
    Json::Value jmsg =  parseMessageJson(message);
    ropod_list_actor_ = zactor_new(ZyreListener::receiveRopodList, this);

    ZyreListener::shoutMessage(jmsg);

    while (!ropod_list_received_) { }
    ropod_list_received_ = false;

    zactor_destroy(&ropod_list_actor_);
    return ropod_names_;
}

std::string ZyreListener::getQuery(std::string msg)
{
    Json::Value jmsg =  parseMessageJson(msg);
    ZyreListener::shoutMessage(jmsg);

    // receives all replies
    query_actor_ = zactor_new(ZyreListener::receiveQueryResult, this);

    while (!query_result_received_) {}
    query_result_received_ = false;
    zactor_destroy(&query_actor_);

    return received_msg_;
}


void ZyreListener::receiveRopodList(zsock_t *pipe, void *args)
{
    ZyreListener *listener = (ZyreListener*)args;

    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);

    listener->ropod_names_.clear();
    auto start = std::chrono::high_resolution_clock::now();
    while (!terminated)
    {
        void *which = zpoller_wait (poller, -1);
        if (which == pipe)
        {
            zmsg_t *msg = zmsg_recv (which);
            if (!msg)
                break;              //  Interrupted

            char *command = zmsg_popstr (msg);

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

            std::string name_str = std::string(name);
            if (name_str.find("query_interface") != std::string::npos)
            {
                listener->ropod_names_.push_back(name_str);
            }

            free (event);
            free (peer);
            free (name);
            free (group);
            free (message);
            zmsg_destroy (&msg);

            auto now = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> elapsed = now - start;
            if (elapsed.count() > listener->timeout_)
            {
                terminated = true;
            }
        }
    }
    listener->ropod_list_received_ = true;
    zpoller_destroy (&poller);
    zclock_sleep (100);
}

void ZyreListener::receiveQueryResult(zsock_t *pipe, void *args)
{
    ZyreListener *listener = (ZyreListener*)args;

    Json::Value rec_msg;
    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);

    auto start = std::chrono::high_resolution_clock::now();
    while (!terminated)
    {
        void *which = zpoller_wait (poller, -1);
        if (which == pipe)
        {
            zmsg_t *msg = zmsg_recv (which);
            if (!msg)
                break;              //  Interrupted

            char *command = zmsg_popstr (msg);

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
            if (std::string(event) != "SHOUT")
            {
                free (event);
                zmsg_destroy (&msg);
                continue;
            }

            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            if(message == NULL || ((message != NULL) && (message[0] == '\0')))
            {
                free (event);
                free (peer);
                free (name);
                free (group);
                free (message);
                zmsg_destroy (&msg);
                continue;
            }

            std::string name_str(name);
            if (name_str.find("query_interface") == std::string::npos)
            {
                free (event);
                free (peer);
                free (name);
                free (group);
                free (message);
                zmsg_destroy (&msg);
                continue;
            }

            rec_msg = listener->parseMessageJson(message);
            if (!rec_msg["header"]["type"].compare("VARIABLE_QUERY"))
            {
                listener->received_msg_ = std::string(message);
                terminated = true;
            }

            free (event);
            free (peer);
            free (name);
            free (group);
            free (message);
            zmsg_destroy (&msg);

            auto now = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> elapsed = now - start;
            if (elapsed.count() > listener->timeout_)
            {
                terminated = true;
            }
        }
    }
    listener->query_result_received_ = true;
    zpoller_destroy (&poller);
    zclock_sleep (100);
}

/**
 * Converts message to a json message
 *
 * @param msg_params message data
 */
Json::Value ZyreListener::parseMessageJson(std::string msg)
{
    Json::Value jmsg;
    Json::Reader reader;
    bool parsingSuccessful = reader.parse(msg.c_str(), jmsg);
    return jmsg;
}

/**
 * Converts an std::string to a zmsg_t pointer
 *
 * @param msg the string to be converted
 */
zmsg_t* ZyreListener::stringToZmsg(std::string msg)
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
void ZyreListener::shoutMessage(const Json::Value &json_msg)
{
    std::string msg = Json::writeString(json_stream_builder_, json_msg);
    zmsg_t* message = stringToZmsg(msg);
    listener_node_->shout("ROPOD", message);
}
