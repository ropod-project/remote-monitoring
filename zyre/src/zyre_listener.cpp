#include "zyre_listener.hpp"

ZyreListener::ZyreListener(int timeout)
{
    listener_node_ = new zyre::node_t("z_listener_node");
    listener_node_->start();
    listener_node_->join("ROPOD");
    timeout_ = timeout;
    actor_ = zactor_new(ZyreListener::receiveData, this);
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
    std::string query_type = jmsg["header"]["type"].asString();
    std::cout << "Received a '" << query_type << "' request\n";
    ZyreListener::shoutMessage(jmsg);
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    zstr_sendx (actor_, "QUERY_INFO", sender_id.c_str(), query_type.c_str(), NULL);
    reply_received_[sender_id] = false;
    node_names_[sender_id] = std::vector<std::string>();

    std::cout << "Waiting for ropod list...\n";
    auto start = std::chrono::high_resolution_clock::now();
    while (!reply_received_[sender_id])
    {
        auto now = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = now - start;
        if ((elapsed.count() > timeout_))
        {
            break;
        }
    }

    reply_received_.erase(sender_id);
    query_info_.erase(sender_id);
    std::cout << "Query interface list received\n\n";

    std::vector<std::string> query_interface_names = node_names_[sender_id];
    node_names_.erase(sender_id);
    return query_interface_names;
}

std::string ZyreListener::getFeatures(std::string msg, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    Json::Value jmsg =  parseMessageJson(msg);
    std::string query_type = jmsg["header"]["type"].asString();
    std::cout << "Received a '" << query_type << "' request\n";

    ZyreListener::shoutMessage(jmsg);
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    zstr_sendx (actor_, "QUERY_INFO", sender_id.c_str(), query_type.c_str(), NULL);
    reply_received_[sender_id] = false;

    std::cout << "Waiting for query results...\n";
    auto start = std::chrono::high_resolution_clock::now();
    while (!reply_received_[sender_id])
    {
        auto now = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = now - start;
        if ((elapsed.count() > timeout_))
        {
            break;
        }
    }

    reply_received_.erase(sender_id);
    query_info_.erase(sender_id);
    std::cout << "Query result received\n\n";

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
    std::string query_type = jmsg["header"]["type"].asString();
    std::cout << "Received a '" << query_type << "' request\n";

    ZyreListener::shoutMessage(jmsg);
    std::string sender_id = jmsg["payload"]["sender_id"].asString();

    zstr_sendx (actor_, "QUERY_INFO", sender_id.c_str(), query_type.c_str(), NULL);
    reply_received_[sender_id] = false;

    std::cout << "Waiting for query results...\n";
    auto start = std::chrono::high_resolution_clock::now();
    while (!reply_received_[sender_id])
    {
        auto now = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = now - start;
        if ((elapsed.count() > timeout_))
        {
            break;
        }
    }
    reply_received_.erase(sender_id);
    query_info_.erase(sender_id);
    std::cout << "Query result received\n\n";

    std::string received_msg = received_msg_[sender_id];
    if (received_msg_.count(sender_id) > 0)
    {
        received_msg = received_msg_[sender_id];
        received_msg_.erase(sender_id);
    }
    return received_msg;
}

std::vector<std::string> ZyreListener::getRopodIDs(std::string message, double timeout)
{
    Json::Value jmsg =  parseMessageJson(message);
    std::string query_type = jmsg["header"]["type"].asString();
    std::cout << "Received a '" << query_type << "' request\n";
    std::cout << "Returning ropod IDs\n\n";
    return status_node_names_;
}

std::string ZyreListener::getStatus(std::string msg, double timeout)
{
    if (timeout > 0)
    {
        timeout_ = timeout;
    }

    Json::Value jmsg =  parseMessageJson(msg);
    std::string query_type = jmsg["header"]["type"].asString();
    std::string ropod_id = jmsg["payload"]["ropod_id"].asString();
    std::cout << "Received a '" << query_type << "' request\n";

    std::string sender_id = jmsg["payload"]["sender_id"].asString();
    zstr_sendx (actor_, "STATUS_INFO", sender_id.c_str(), query_type.c_str(), ropod_id.c_str(), NULL);
    reply_received_[sender_id] = false;

    std::cout << "Waiting for status results...\n";
    auto start = std::chrono::high_resolution_clock::now();
    while (!reply_received_[sender_id])
    {
        auto now = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = now - start;
        if ((elapsed.count() > timeout_))
        {
            break;
        }
    }

    reply_received_.erase(sender_id);
    query_info_.erase(sender_id);
    user_ropod_ids_.erase(sender_id);
    std::cout << "Status result received\n\n";

    std::string received_msg;
    if (received_msg_.count(sender_id) > 0)
    {
        received_msg = received_msg_[sender_id];
        received_msg_.erase(sender_id);
    }
    return received_msg;
}

void ZyreListener::receiveData(zsock_t *pipe, void *args)
{
    ZyreListener *listener = (ZyreListener*)args;
    Json::Value rec_msg;
    bool terminated = false;
    std::string sender_id = "";

    zsock_signal (pipe, 0);
    zpoller_t *poller = zpoller_new (pipe, listener->listener_node_->socket(), NULL);
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
            else if (std::string(command) == "QUERY_INFO")
            {
                char *sender_id_cstr = zmsg_popstr(msg);
                char *query_type_cstr = zmsg_popstr(msg);
                std::string sender(sender_id_cstr);
                std::string query_type(query_type_cstr);

                listener->query_info_[sender] = query_type;

                free(sender_id_cstr);
                free(query_type_cstr);
            }
            else if (std::string(command) == "STATUS_INFO")
            {
                char *sender_id_cstr = zmsg_popstr(msg);
                char *query_type_cstr = zmsg_popstr(msg);
                char *ropod_id_cstr = zmsg_popstr(msg);
                std::string sender(sender_id_cstr);
                std::string query_type(query_type_cstr);
                std::string ropod_id(ropod_id_cstr);

                listener->query_info_[sender] = query_type;
                listener->user_ropod_ids_[sender] = ropod_id;

                free(sender_id_cstr);
                free(query_type_cstr);
                free(ropod_id_cstr);
            }
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

            if (streq(event, "JOIN"))
            {
                std::string name_str = std::string(name);
                if (name_str.find("local_status_monitor") != std::string::npos)
                {
                    if (std::find(listener->status_node_names_.begin(),
                                  listener->status_node_names_.end(), name_str) == listener->status_node_names_.end())
                    {
                        listener->status_node_names_.push_back(name_str);
                    }
                }
            }
            else if (streq(event, "LEAVE") || streq(event, "EXIT"))
            {
                std::string name_str = std::string(name);
                if (name_str.find("local_status_monitor") != std::string::npos)
                {
                    listener->status_node_names_.erase(std::remove(listener->status_node_names_.begin(),
                                                                   listener->status_node_names_.end(), name),
                                                                   listener->status_node_names_.end());
                }
            }

            if (((std::string(event) == "SHOUT") || ((std::string(event) == "WHISPER")))
                && (message != NULL) && (message[0] != '\0'))
            {
                std::string name_str = std::string(name);
                if ((name_str.find("query_interface") != std::string::npos) ||
                    (name_str.find("ropod") != std::string::npos))
                {
                    rec_msg = listener->parseMessageJson(message);
                    sender_id = rec_msg["payload"]["sender_id"].asString();
                    if (!rec_msg["header"]["type"].compare("NAME_QUERY") &&
                        !listener->query_info_[sender_id].compare("NAME_QUERY"))
                    {
                        if(std::find(listener->node_names_[sender_id].begin(),
                                     listener->node_names_[sender_id].end(), name_str) ==
                                     listener->node_names_[sender_id].end())
                        {
                            listener->node_names_[sender_id].push_back(name_str);
                        }
                    }
                    else if (!rec_msg["header"]["type"].compare("VARIABLE_QUERY") &&
                             !listener->query_info_[sender_id].compare("VARIABLE_QUERY"))
                    {
                        listener->received_msg_[sender_id] = std::string(message);
                        listener->reply_received_[sender_id] = true;
                    }
                    else if (!rec_msg["header"]["type"].compare("DATA_QUERY") &&
                             !listener->query_info_[sender_id].compare("DATA_QUERY"))
                    {
                        listener->received_msg_[sender_id] = std::string(message);
                        listener->reply_received_[sender_id] = true;
                    }
                    else if (!rec_msg["header"]["type"].compare("STATUS"))
                    {
                        std::string ropod_id = std::string(name);
                        for (auto info : listener->query_info_)
                        {
                            if (info.second == "STATUS" && listener->user_ropod_ids_[info.first] == ropod_id)
                            {
                                sender_id = info.first;
                                listener->received_msg_[sender_id] = std::string(message);
                                listener->reply_received_[sender_id] = true;
                            }
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
