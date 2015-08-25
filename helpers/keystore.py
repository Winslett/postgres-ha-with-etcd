import json, os, time
import logging
import etcd
import helpers.errors

logger = logging.getLogger(__name__)

class Etcd:
    def __init__(self, config):
        self.scope = config["scope"]
        self.host, self.port = config["host"].split(":")
        self.client = etcd.Client(host=self.host, port=int(self.port))
        self.ttl = config["ttl"]

    def get(self, path, max_attempts=1):
        attempts = 0
        response = None

        while True:
            try:
                logger.debug("GET: /service/%s%s", self.scope, path)
                response = self.client.read("/service/%s%s" % (self.scope, path))
                break
            except (etcd.EtcdKeyNotFound) as e:
                attempts += 1
                if attempts < max_attempts:
                    logger.info("Failed to return %s, trying again. (%s of %s)" % (path, attempts, max_attempts))
                    time.sleep(3)
                else:
                    raise e

        return (response.value or response)

    def set(self, path, value, ttl=None, prevExist=None, prevValue=None):

        additional_params = {}
        if ttl is not None:
            additional_params['ttl'] = ttl
        if prevExist is not None:
            additional_params['prevExist'] = prevExist
        if prevValue is not None:
            additional_params['prevValue'] = prevValue

        logger.debug("SET: /service/%s%s > %s", self.scope, path, value)
        self.client.write("/service/%s%s" % (self.scope, path),
                          value, **additional_params)

    def current_leader(self):
        try:
            hostname = self.get("/leader")
            address = self.get("/members/%s" % hostname)
            return {"hostname": hostname, "address": address}

        except etcd.EtcdKeyNotFound:
            return None

        except Exception:
            raise helpers.errors.CurrentLeaderError("Etcd is not responding properly")

    def members(self):
        try:
            members = []
            members_dir = self.get("/members")
            if members_dir:
                for member in members_dir.children:
                    members.append({"hostname": member.key.split('/')[-1], "address": member.value})

            return members

        except etcd.EtcdKeyNotFound:
            return None

        except Exception:
            raise helpers.errors.CurrentLeaderError("Etcd is not responding properly")

    def touch_member(self, member, connection_string):
        self.set("/members/%s" % member, connection_string, ttl=self.ttl)

    def take_leader(self, value):
        self.set("/leader", value, ttl=self.ttl)

    def attempt_to_acquire_leader(self, value):
        try:
            self.set("/leader", value, ttl=self.ttl, prevExist=False)
            return True

        except etcd.EtcdAlreadyExist:
            logger.info("Could not aquire leader: already exists")
            return False

    def update_leader(self, state_handler):
        try:
            self.set("/leader", state_handler.name, ttl=self.ttl, prevValue=state_handler.name)
            self.set("/optime/leader", state_handler.last_operation())
        except ValueError:
            logger.error("Error updating leader lock and optime on ETCD for primary.")
            return False

    def last_leader_operation(self):
        try:
            return int(self.get("/optime/leader"))

        except etcd.EtcdKeyNotFound:
            logger.error("Error reading TTL on ETCD for primary.")
            return None

    def leader_unlocked(self):
        try:
            self.get("/leader")
            return False

        except etcd.EtcdKeyNotFound:
            return True

        return False

    def am_i_leader(self, value):
        leader = self.get("/leader")
        logger.info("Lock owner: %s; I am %s", leader, value)
        return leader == value

    def race(self, path, value):
        try:
            self.set(path, value, prevExist=False)
            return True
        except etcd.EtcdAlreadyExist:
            return False
