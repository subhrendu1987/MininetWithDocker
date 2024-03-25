#!/usr/bin/python
import argparse
import json
import docker
##################################################################
def create_container(image_name, container_name):
    client = docker.from_env()
    container = client.containers.run(image_name, detach=True, name=container_name, command="sleep infinity")
    print(f"Container {container_name} created with ID: {container.id}")
##################################################################
def getSwitches(data):
    for sw in data['switches']:
        create_container("ubuntu:latest", "mn_"+sw['opts']['hostname'])
##################################################################
def getJSON(filename):
    # Read the .mn/.JSON file
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            #print("Content of the JSON file:")
            #print(data)
    except FileNotFoundError:
        print("Error: File not found.")
        return(None)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the file.")
        return(None)
    return(data)
##################################################################
def getTopology(): 
    data=getJSON(filename=args.topology)
    #Nodes=
##################################################################
def getDockerImages(): 
   client = docker.from_env() 
   images = client.images.list() 
   return images 
##################################################################
def kill_and_remove_container(cname):
    client = docker.from_env()
    container = client.containers.get(cname)
    if container:
        container.kill()  # Stop the container
        container.remove()  # Remove the container
        print(f"Container '{cname}' killed and removed.")
    else:
        print(f"Container '{cname}' not found.")
##################################################################
def cleanup(): 
   client = docker.from_env()
   containers = client.containers.list()
   matching_containers = [container.name for container in containers if container.name.startswith(prefix)]
   for cname in matching_containers:
        kill_and_remove_container(cname)
##################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mininet with Dockers instead of Network Namespace")
    parser.add_argument("topology", help="Topology file (i.e. .mn) generated from miniedit.")
    parser.add_argument("dockerMap", help="Docker mapping JSON for each nodes")
    args = parser.parse_args()
    # args = argparse.Namespace(topology="minieditBaseline.mn",dockerMap="") ## Ipython stub
    ##################################################################
    data=getJSON(filename=args.topology)
    Nodes=



"""
function start_docker_containers
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    for name in $container_names
        gnome-terminal -- sudo docker run -it --rm --privileged \
            -v /lib/modules:/lib/modules:ro \
            -v /usr/src:/usr/src:ro \
            -v /etc/localtime:/etc/localtime:ro \
            --name $name arch-bcc &
    end
    sleep 40
end

function get_container_pids
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    for name in $container_names
        set id (sudo docker ps --format '{{.ID}}' --filter name=$name)
        set pid (sudo docker inspect -f '{{.State.Pid}}' $id)
        set -g $name"_id" $id
        set -g $name"_pid" $pid
    end
end

function configure_network_namespaces
    echo Adding Symbolic links between namespaces......
    sudo mkdir -p /var/run/netns/
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    for name in $container_names
        sudo ln -sfT /proc/(eval echo "\$"$name"_pid")/ns/net /var/run/netns/(eval echo "\$"$name"_id")
    end
end

function create_virtual_ethernet_devices
    sudo ip link add 'c1-eth0' type veth peer name 'r1-eth0'
    sudo ip link add 'c2-eth0' type veth peer name 'r1-eth1'
    sudo ip link add 'c3-eth0' type veth peer name 'r2-eth0'
    sudo ip link add 'c4-eth0' type veth peer name 'r2-eth1'
end

function move_interfaces_to_containers
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    for name in $container_names
        sudo ip link set "$name-eth0" netns (eval echo "\$"$name"_pid")
        if test $name = "r1" -o $name = "r2"
            sudo ip link set "$name-eth1" netns (eval echo "\$"$name"_pid")
        end
    end
end

function rename_interfaces_in_containers
    echo Renaming interfaces........
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    for name in $container_names
        sudo ip netns exec (eval echo "\$"$name"_id") ip link set "$name-eth0" name 'eth0'
        if test $name = "r1" -o $name = "r2"
            sudo ip netns exec (eval echo "\$"$name"_id") ip link set "$name-eth1" name 'eth1'
        end
    end
end

function bring_up_interfaces_in_containers
    echo Bringing up Interfaces.......
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    for name in $container_names
        sudo ip netns exec (eval echo "\$"$name"_id") ip link set 'eth0' up
        sudo ip netns exec (eval echo "\$"$name"_id") ip link set 'lo' up
        if test $name = "r1" -o $name = "r2"
            sudo ip netns exec (eval echo "\$"$name"_id") ip link set 'eth1' up
        end
    end
end

function assign_container_ips
    echo Assigning IPs......
    set container_names "c1" "r1" "c2" "c3" "c4" "r2"
    set container_ips "10.0.0.1/24" "10.0.0.2/24" "10.0.0.3/24" "10.0.0.4/24" "10.0.0.5/24" "10.0.0.6/24"  \
        "10.0.0.7/24" "10.0.0.8/24" "10.0.0.9/24" "10.0.0.10/24"
    set pointer 1

    for name in $container_names
        sudo ip netns exec (eval echo "\$"$name"_id") ip addr add $container_ips[$pointer] dev "eth0"
        set pointer (math $pointer + 1)
    end
end

function adjust_bottleneck_parameters
    echo Reconfiguring bottleneck.....
    set container_name "r1"
    set bandwidth 20
    set latency 100
    set delay 100
    set jitter 20
    set burst 32

    sudo ip netns exec (eval echo "\$"$container_name"_id") tc qdisc add dev eth0 root handle 1: tbf rate $bandwidth"mbit" burst $burst"kbit" latency $latency"ms"
    sudo ip netns exec (eval echo "\$"$container_name"_id") tc qdisc add dev eth0 parent 1:1 handle 10: netem delay $delay"ms" $jitter"ms" distribution normal
end

function main
    build_docker_image
    start_docker_containers
    get_container_pids
    configure_network_namespaces
    create_virtual_ethernet_devices
    move_interfaces_to_containers
    rename_interfaces_in_containers
    bring_up_interfaces_in_containers
    assign_container_ips
end

main
"""