#include "zyre_listener.hpp"

ZyreListener::ZyreListener(int timeout)
{
    listener_node_ = new zyre::node_t("z_listener_node");
    listener_node_->start();
    listener_node_->join("ROPOD");
    ropod_list_received_ = false;
    features_received_ = false;
    data_received_ = false;
    ropod_ids_received_ = false;
    status_received_ = false;
    timeout_ = timeout;
}

ZyreListener::~ZyreListener()
{
    listener_node_->leave("ROPOD");
    listener_node_->stop();
    delete listener_node_;
}

std::vector<std::string> ZyreListener::getRopodList(std::string message, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    // shout to all the nodes and ask them to send their name and uuids
    Json::Value jmsg =  parseMessageJson(message);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";
    ZyreListener::shoutMessage(jmsg);
    ropod_list_actor_ = zactor_new(ZyreListener::receiveRopodList, this);

    std::cout << "Waiting for ropod list...\n";
    while (!ropod_list_received_) { }
    ropod_list_received_ = false;
    std::cout << "Ropod list received\n\n";

    zactor_destroy(&ropod_list_actor_);
    return ropod_names_;
}

// ============================ ropod info related ============================================

std::vector<std::string> ZyreListener::getRopodIDs(std::string message, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    // shout to all the nodes and ask them to send their name and uuids
    Json::Value jmsg =  parseMessageJson(message);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";
    ZyreListener::shoutMessage(jmsg);
    ropod_id_actor_ = zactor_new(ZyreListener::receiveRopodIDs, this);

    std::cout << "Waiting for ropod IDs...\n";
    while (!ropod_ids_received_) { }
    ropod_ids_received_ = false;
    std::cout << "Ropod IDs received\n\n";

    zactor_destroy(&ropod_id_actor_);
    return ropod_ids_;
}

std::string ZyreListener::getStatus(std::string msg, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    Json::Value jmsg =  parseMessageJson(msg);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";

    ZyreListener::shoutMessage(jmsg);
    status_query_actor_ = zactor_new(ZyreListener::receiveStatus, this);

    std::cout << "Waiting for status results...\n";
    while (!status_received_) {}
    status_received_ = false;
    std::cout << "Status result received\n\n";

    zactor_destroy(&status_query_actor_);
    return received_status_;
}

// ========================================================================

std::string ZyreListener::getFeatures(std::string msg, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    Json::Value jmsg =  parseMessageJson(msg);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";

    ZyreListener::shoutMessage(jmsg);
    feature_query_actor_ = zactor_new(ZyreListener::receiveFeatures, this);

    std::cout << "Waiting for query results...\n";
    while (!features_received_) {}
    features_received_ = false;
    std::cout << "Query result received\n\n";

    zactor_destroy(&feature_query_actor_);
    return received_msg_;
}

std::string ZyreListener::getData(std::string msg, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    Json::Value jmsg =  parseMessageJson(msg);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";

    ZyreListener::shoutMessage(jmsg);
    data_query_actor_ = zactor_new(ZyreListener::receiveData, this);

    std::cout << "Waiting for query results...\n";
    while (!data_received_) {}
    data_received_ = false;
    std::cout << "Query result received\n\n";

    zactor_destroy(&data_query_actor_);
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
                if(std::find(listener->ropod_names_.begin(),
                             listener->ropod_names_.end(), name_str) == listener->ropod_names_.end())
                {
                    listener->ropod_names_.push_back(name_str);
                }
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

// ============================ ropod info related ============================================

void ZyreListener::receiveRopodIDs(zsock_t *pipe, void *args)
{
    ZyreListener *listener = (ZyreListener*)args;

    zsock_signal (pipe, 0);     //  Signal "ready" to caller

    bool terminated = false;
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);

    listener->ropod_ids_.clear();
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

            // Filters the received messages based on their senders names and keeps just the messages from ropods
            if (name_str.find("ropod") != std::string::npos)
            {
                if(std::find(listener->ropod_ids_.begin(),
                             listener->ropod_ids_.end(), name_str) == listener->ropod_ids_.end())
                {
                    listener->ropod_ids_.push_back(name_str);
                }
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
    listener->ropod_ids_received_ = true;
    zpoller_destroy (&poller);
    zclock_sleep (100);
}

void ZyreListener::receiveStatus(zsock_t *pipe, void *args)
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
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            // Filters the received messages based on their senders names and header type
            if ((std::string(event) == "SHOUT") && (message != NULL) && (message[0] != '\0'))
            {
                std::string name_str(name);
                if (name_str.find("ropod") != std::string::npos)
                {
                    rec_msg = listener->parseMessageJson(message);
                    if (!rec_msg["header"]["type"].compare("STATUS"))
                    {
                        listener->received_status_ = std::string(message);
                        terminated = true;
                    }
                }
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
    listener->status_received_ = true;
    zpoller_destroy (&poller);
    zclock_sleep (100);
}

// ========================================================================

void ZyreListener::receiveFeatures(zsock_t *pipe, void *args)
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
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            if ((std::string(event) == "SHOUT") && (message != NULL) && (message[0] != '\0'))
            {
                std::string name_str(name);
                if (name_str.find("query_interface") != std::string::npos)
                {
                    rec_msg = listener->parseMessageJson(message);
                    if (!rec_msg["header"]["type"].compare("VARIABLE_QUERY"))
                    {
                        listener->received_msg_ = std::string(message);
                        terminated = true;
                    }
                }
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
    listener->features_received_ = true;
    zpoller_destroy (&poller);
    zclock_sleep (100);
}

void ZyreListener::receiveData(zsock_t *pipe, void *args)
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
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group = zmsg_popstr (msg);
            char *message = zmsg_popstr (msg);

            if ((std::string(event) == "SHOUT") && (message != NULL) && (message[0] != '\0'))
            {
                std::string name_str(name);
                if (name_str.find("query_interface") != std::string::npos)
                {
                    rec_msg = listener->parseMessageJson(message);
                    if (!rec_msg["header"]["type"].compare("DATA_QUERY"))
                    {
                        listener->received_msg_ = std::string(message);
                        terminated = true;
                    }
                }
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
    listener->data_received_ = true;
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
