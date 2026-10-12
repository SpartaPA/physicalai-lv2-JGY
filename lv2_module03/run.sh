ros2 topic list -t

# /events/read_split [rosbag2_interfaces/msg/ReadSplitEvent]
# /parameter_events [rcl_interfaces/msg/ParameterEvent]
# /rosout [rcl_interfaces/msg/Log]
# /target [geometry_msgs/msg/PointStamped]

ros2 topic info /events/read_split --verbose

# Type: rosbag2_interfaces/msg/ReadSplitEvent

# Publisher count: 1

# Node name: rosbag2_player
# Node namespace: /
# Topic type: rosbag2_interfaces/msg/ReadSplitEvent
# Topic type hash: RIHS01_6f21c9b52d788338b0775ceccb49f38e7a8baad7b954f79dd280baed91145ad7
# Endpoint type: PUBLISHER
# GID: 01.0f.a5.c1.3a.07.4d.54.00.00.00.00.00.00.15.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1)
#   Durability: VOLATILE
#   Lifespan: Infinite
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Subscription count: 0

ros2 topic info /parameter_events --verbose

# Type: rcl_interfaces/msg/ParameterEvent

# Publisher count: 3

# Node name: _ros2cli_daemon_0_49d8cc2df3f046799951c3bd7aff28df
# Node namespace: /
# Topic type: rcl_interfaces/msg/ParameterEvent
# Topic type hash: RIHS01_043e627780fcad87a22d225bc2a037361dba713fca6a6b9f4b869a5aa0393204
# Endpoint type: PUBLISHER
# GID: 01.0f.41.7d.3a.2c.98.5a.00.00.00.00.00.00.04.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1000)
#   Durability: VOLATILE
#   Lifespan: Infinite
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Node name: _ros2cli_daemon_0_10c1e4b6e7a84e619173be1d984e18f6
# Node namespace: /
# Topic type: rcl_interfaces/msg/ParameterEvent
# Topic type hash: RIHS01_043e627780fcad87a22d225bc2a037361dba713fca6a6b9f4b869a5aa0393204
# Endpoint type: PUBLISHER
# GID: 01.0f.5d.3c.ce.39.f7.c5.00.00.00.00.00.00.04.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1000)
#   Durability: VOLATILE
#   Lifespan: Infinite
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Node name: rosbag2_player
# Node namespace: /
# Topic type: rcl_interfaces/msg/ParameterEvent
# Topic type hash: RIHS01_043e627780fcad87a22d225bc2a037361dba713fca6a6b9f4b869a5aa0393204
# Endpoint type: PUBLISHER
# GID: 01.0f.a5.c1.3a.07.4d.54.00.00.00.00.00.00.10.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1)
#   Durability: VOLATILE
#   Lifespan: Infinite
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Subscription count: 1

# Node name: rosbag2_player
# Node namespace: /
# Topic type: rcl_interfaces/msg/ParameterEvent
# Topic type hash: RIHS01_043e627780fcad87a22d225bc2a037361dba713fca6a6b9f4b869a5aa0393204
# Endpoint type: SUBSCRIPTION
# GID: 01.0f.a5.c1.3a.07.4d.54.00.00.00.00.00.00.11.04

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1)
#   Durability: VOLATILE
#   Lifespan: Infinite
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

ros2 topic info /rosout --verbose

# Type: rcl_interfaces/msg/Log

# Publisher count: 3

# Node name: _ros2cli_daemon_0_49d8cc2df3f046799951c3bd7aff28df
# Node namespace: /
# Topic type: rcl_interfaces/msg/Log
# Topic type hash: RIHS01_e28ce254ca8abc06abf92773b74602cdbf116ed34fbaf294fb9f81da9f318eac
# Endpoint type: PUBLISHER
# GID: 01.0f.41.7d.3a.2c.98.5a.00.00.00.00.00.00.03.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1000)
#   Durability: TRANSIENT_LOCAL
#   Lifespan: 10000000000 nanoseconds
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Node name: _ros2cli_daemon_0_10c1e4b6e7a84e619173be1d984e18f6
# Node namespace: /
# Topic type: rcl_interfaces/msg/Log
# Topic type hash: RIHS01_e28ce254ca8abc06abf92773b74602cdbf116ed34fbaf294fb9f81da9f318eac
# Endpoint type: PUBLISHER
# GID: 01.0f.5d.3c.ce.39.f7.c5.00.00.00.00.00.00.03.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1000)
#   Durability: TRANSIENT_LOCAL
#   Lifespan: 10000000000 nanoseconds
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Node name: rosbag2_player
# Node namespace: /
# Topic type: rcl_interfaces/msg/Log
# Topic type hash: RIHS01_e28ce254ca8abc06abf92773b74602cdbf116ed34fbaf294fb9f81da9f318eac
# Endpoint type: PUBLISHER
# GID: 01.0f.a5.c1.3a.07.4d.54.00.00.00.00.00.00.03.03

# QoS profile:
#   Reliability: RELIABLE
#   History (Depth): KEEP_LAST (1)
#   Durability: TRANSIENT_LOCAL
#   Lifespan: 10000000000 nanoseconds
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Subscription count: 0

ros2 topic info /target --verbose

# Type: geometry_msgs/msg/PointStamped

# Publisher count: 1

# Node name: rosbag2_player
# Node namespace: /
# Topic type: geometry_msgs/msg/PointStamped
# Topic type hash: RIHS01_4c0296af86e01e562e9e0405d138a01537247580076c58ea38d7923ac1045897
# Endpoint type: PUBLISHER
# GID: 01.0f.a5.c1.3a.07.4d.54.00.00.00.00.00.00.14.03

# QoS profile:
#   Reliability: BEST_EFFORT
#   History (Depth): KEEP_LAST (1)
#   Durability: VOLATILE
#   Lifespan: Infinite
#   Deadline: Infinite
#   Liveliness: AUTOMATIC
#   Liveliness lease duration: Infinite

# Subscription count: 0