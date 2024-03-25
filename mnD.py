#!/usr/bin/python
import argparse
import json
import docker
import subprocess
##################################################################
Topology={}
##################################################################
def createLink(c1,c2):
    # Use ip command to create a veth pair
    #h1_id=$(docker ps --format '{{.ID}}' --filter name=h1)
    intf1=f"{c1}-{c2}-eth"
    intf2=f"{c2}-{c1}-eth"
    #ip link add 'intf1' type veth peer name 'intf2'
    subprocess.run(["ip", "link", "add", intf1, "type", "veth", "peer", "name", intf2])
    cid1=Topology[c1]['cid']
    cid2=Topology[c2]['cid']

    #ip link set 'intf1' netns 'cid1'
    subprocess.run(["ip", "link", "set", intf1,"netns",cid1])
##################################################################
def deleteLink(c1,c2):
    intf1=f"{c1}-{c2}-eth"
    intf2=f"{c2}-{c1}-eth"
    # Create veth pair
    
    subprocess.run(["ip", "link", "delete", intf1])
##################################################################
def getParams(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    network_settings = container.attrs['NetworkSettings']
    ns_id = network_settings['Networks']['none']['NetworkID']
    pid = container.attrs['State']['Pid']
    #cid=$(docker ps --format '{{.ID}}' --filter name='container_name')
    cid= container.id
    return({'ns_id':ns_id,'pid':pid,'cid':cid})
##################################################################
def createNode(image_name, container_name):
    client = docker.from_env()
    container = client.containers.run(image_name, detach=True, name=container_name, command="sleep infinity",network_mode="none")
    print(f"Container {container_name} created with ID: {container.id}")
    params=getParams(name)
    Topology[name]={'switchType':None,**params}
    #ln -sfT /proc/$h1_pid/ns/net /var/run/netns/$h1_id
    subprocess.run(["ln", "-sfT", f"/proc/{params[pid]}/ns/net", f"/var/run/netns/{params.cid}"])
    return
##################################################################
def createLinks(data):
    for l in data['links']:
        c1=f"mn_{l['src']}"
        c2=f"mn_{l['dest']}"
        createLink(c1,c2)
##################################################################
def createMiddleboxes(data):
    for sw in data['switches']:
        name="mn_"+sw['opts']['hostname']
        Topology[name]={}
        if sw['opts']['switchType'] == "legacySwitch":
            print("Legacy Switch Created:")
            print(sw['opts'])
            c=createNode("mnbase:latest", name)
            Topology[name]['switchType']="legacySwitch"
            #createBlankBridge()
        elif sw['opts']['switchType'] == "legacyRouter":
            print("Legacy Router Created:")
            print(sw['opts'])
            c=createNode("mnbase:latest", name)
            Topology[name]['switchType']="legacyRouter"
            execDocker(name,"sysctl -w net.ipv4.ip_forward=1")
        else:
            print(f"Unknown Type: Therefore {name} Not created.")
    return
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
def createTopology(topology): 
    data=getJSON(filename=topology)
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
def execDocker(container_name, command):
    client = docker.from_env()
    container = client.containers.get(container_name)
    exec_res = container.exec_run(command, tty=True)
    return exec_res
##################################################################
def cleanup(): 
   client = docker.from_env()
   containers = client.containers.list()
   matching_containers = [container.name for container in containers if container.name.startswith("mn_")]
   for cname in matching_containers:
        kill_and_remove_container(cname)
##################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mininet with Dockers instead of Network Namespace")
    parser.add_argument("topology", help="Topology file (i.e. .mn) generated from miniedit.")
    parser.add_argument("dockerMap", help="Docker mapping JSON for each nodes")
    args = parser.parse_args()
    # args = argparse.Namespace(topology="minieditBaseline.mn",dockerMap=None) ## Ipython stub
    ##################################################################
    #def createTopology(topology):
    subprocess.run(["mkdir", "-p", "/var/run/netns/"])
    data=getJSON(topology=args.topology)
    createMiddleboxes(data)



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