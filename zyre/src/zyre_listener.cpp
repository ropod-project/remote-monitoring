#include "zyre_listener.hpp"

ZyreListener::ZyreListener(int timeout)
{
    listener_node_ = new zyre::node_t("z_listener_node");
    listener_node_->start();
    listener_node_->join("ROPOD");
    timeout_ = timeout;
}

ZyreListener::~ZyreListener()
{
    listener_node_->leave("ROPOD");
    listener_node_->stop();
    delete listener_node_;
}

std::vector<std::string> ZyreListener::getQueryInterfaceList(std::string message, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    // shout to all the nodes and ask them to send their name and uuids
    Json::Value jmsg =  parseMessageJson(message);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";
    ZyreListener::shoutMessage(jmsg);
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    ListenerParams listener_params(this, sender_id);
    actors_[sender_id] = zactor_new(ZyreListener::receiveData, &listener_params);
    reply_received_[sender_id] = false;
    node_names_[sender_id] = std::vector<std::string>();

    std::cout << "Waiting for ropod list...\n";
    while (!reply_received_[sender_id]) { }
    reply_received_.erase(sender_id);
    std::cout << "Query interface list received\n\n";

    zactor_destroy(&actors_[sender_id]);
    actors_.erase(sender_id);

    std::vector<std::string> query_interface_names = node_names_[sender_id];
    node_names_.erase(sender_id);
    return query_interface_names;
}

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
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    ListenerParams listener_params(this, sender_id);
    actors_[sender_id] = zactor_new(ZyreListener::receiveData, &listener_params);
    reply_received_[sender_id] = false;
    node_names_[sender_id] = std::vector<std::string>();

    std::cout << "Waiting for ropod IDs...\n";
    while (!reply_received_[sender_id]) { }
    reply_received_.erase(sender_id);
    std::cout << "Ropod IDs received\n\n";

    zactor_destroy(&actors_[sender_id]);
    actors_.erase(sender_id);

    std::vector<std::string> ropod_ids = node_names_[sender_id];
    node_names_.erase(sender_id);
    return ropod_ids;
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
    std::string sender_id = jmsg["payload"]["sender_id"].asString();
    ListenerParams listener_params(this, sender_id);
    actors_[sender_id] = zactor_new(ZyreListener::receiveData, &listener_params);
    reply_received_[sender_id] = false;

    std::cout << "Waiting for status results...\n";
    while (!reply_received_[sender_id]) {}
    reply_received_.erase(sender_id);
    std::cout << "Status result received\n\n";

    zactor_destroy(&actors_[sender_id]);
    actors_.erase(sender_id);

    std::string received_msg;
    if (received_msg_.count(sender_id) > 0)
    {
        received_msg = received_msg_[sender_id];
        received_msg_.erase(sender_id);
    }
    return received_msg;
}

std::string ZyreListener::getFeatures(std::string msg, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    Json::Value jmsg =  parseMessageJson(msg);
    std::cout << "Received a '" << jmsg["header"]["type"].asString() << "' request\n";

    ZyreListener::shoutMessage(jmsg);
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    ListenerParams listener_params(this, sender_id);
    actors_[sender_id] = zactor_new(ZyreListener::receiveData, &listener_params);
    reply_received_[sender_id] = false;

    std::cout << "Waiting for query results...\n";
    while (!reply_received_[sender_id]) {}
    reply_received_.erase(sender_id);
    std::cout << "Query result received\n\n";

    zactor_destroy(&actors_[sender_id]);
    actors_.erase(sender_id);

    std::string received_msg = received_msg_[sender_id];
    if (received_msg_.count(sender_id) > 0)
    {
        received_msg = received_msg_[sender_id];
        received_msg_.erase(sender_id);
    }
    return received_msg;
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
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    ListenerParams listener_params(this, sender_id);
    actors_[sender_id] = zactor_new(ZyreListener::receiveData, &listener_params);
    reply_received_[sender_id] = false;

    std::cout << "Waiting for query results...\n";
    while (!reply_received_[sender_id]) {}
    reply_received_.erase(sender_id);
    std::cout << "Query result received\n\n";

    zactor_destroy(&actors_[sender_id]);
    actors_.erase(sender_id);

    std::string received_msg = received_msg_[sender_id];
    if (received_msg_.count(sender_id) > 0)
    {
        received_msg = received_msg_[sender_id];
        received_msg_.erase(sender_id);
    }
    return received_msg;
}

void ZyreListener::receiveData(zsock_t *pipe, void *args)
{
    ListenerParams *listener_params = (ListenerParams*)args;
    std::string sender_id = listener_params->sender_id;
    Json::Value rec_msg;
    bool terminated = false;

    zsock_signal (pipe, 0);
    zpoller_t *poller = zpoller_new (pipe, listener_params->listener->listener_node_->socket(), NULL);
    auto start = std::chrono::high_resolution_clock::now();
    while (!terminated)
    {
        void *which = zpoller_wait (poller, 500);
        if (which == pipe)
        {
            zmsg_t *msg = zmsg_recv (which);
            if (!msg)
                break;

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
        else if (which == listener_params->listener->listener_node_->socket())
        {
            zmsg_t *msg = zmsg_recv (which);
            char *event = zmsg_popstr (msg);
            char *peer = zmsg_popstr (msg);
            char *name = zmsg_popstr (msg);
            char *group;
            char *message;
            if (streq(event, "WHISPER"))
            {
                message = zmsg_popstr(msg);
            }
            else
            {
                group = zmsg_popstr(msg);
                message = zmsg_popstr(msg);
            }

            if (((std::string(event) == "SHOUT") || ((std::string(event) == "WHISPER")))
                && (message != NULL) && (message[0] != '\0'))
            {
                std::string name_str = std::string(name);
                std::cout << name_str << std::endl;
                if ((name_str.find("query_interface") != std::string::npos) ||
                    (name_str.find("ropod") != std::string::npos))
                {
                    rec_msg = listener_params->listener->parseMessageJson(message);
                    if (!rec_msg["payload"]["sender_id"].compare(sender_id))
                    {
                        if (!rec_msg["header"]["type"].compare("NAME_QUERY"))
                        {
                            if(std::find(listener_params->listener->node_names_[sender_id].begin(),
                                         listener_params->listener->node_names_[sender_id].end(), name_str) ==
                                         listener_params->listener->node_names_[sender_id].end())
                            {
                                listener_params->listener->node_names_[sender_id].push_back(name_str);
                            }
                        }
                        else if (!rec_msg["header"]["type"].compare("VARIABLE_QUERY"))
                        {
                            listener_params->listener->received_msg_[sender_id] = std::string(message);
                            listener_params->listener->reply_received_[sender_id] = true;
                            terminated = true;
                        }
                        else if (!rec_msg["header"]["type"].compare("DATA_QUERY"))
                        {
                            listener_params->listener->received_msg_[sender_id] = std::string(message);
                            listener_params->listener->reply_received_[sender_id] = true;
                            terminated = true;
                        }
                        else if (!rec_msg["header"]["type"].compare("STATUS"))
                        {
                            listener_params->listener->received_msg_[sender_id] = std::string(message);
                            listener_params->listener->reply_received_[sender_id] = true;
                            terminated = true;
                        }
                    }
                }
            }

            if (std::string(event) == "WHISPER")
            {
                free (message);
            }
            else
            {
                free (group);
                free (message);
            }
            free (event);
            free (peer);
            free (name);
            zmsg_destroy (&msg);
        }

        auto now = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = now - start;
        std::cout << "checking elapsed time\n";
        std::cout << elapsed.count() << " " << listener_params->listener->timeout_ << std::endl << std::endl;
        if (elapsed.count() > listener_params->listener->timeout_)
        {
            terminated = true;
            listener_params->listener->reply_received_[sender_id] = true;
        }
    }
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
