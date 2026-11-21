A computer network lets independent machines exchange data reliably, even though the links between them lose, delay, reorder, and corrupt packets. Every web page, video call, and app update depends on a stack of protocols, each solving one part of that problem and relying on the layer below. Understanding the stack lets you reason about why a page loads slowly, why a connection drops, and how data stays private on the way.

This subject works through the layers. It begins with network fundamentals, topologies, and performance measures such as bandwidth, latency, and throughput, then compares the OSI and TCP/IP models. At the physical and data link layers it covers channel capacity, framing, error detection with CRC, error correction, sliding-window protocols, Ethernet, MAC addresses, and switching. The network layer covers routing algorithms, IPv4 subnetting and CIDR, IPv6, ARP, ICMP, DHCP, and inter-domain routing with BGP. The transport layer explains TCP's handshake, flow control, and congestion control alongside UDP. The subject ends with DNS, modern HTTP, TLS, and firewalls.

Many lessons include calculations you can check by hand, such as subnet ranges, CRC remainders, and transmission delays.

## What you will learn
- Describe network topologies and calculate bandwidth, latency, throughput, and delay
- Compare the OSI and TCP/IP models and place each protocol at its layer
- Explain channel capacity and the properties of common transmission media
- Detect errors with parity and CRC, correct them with Hamming codes, and analyse sliding-window protocols
- Explain how Ethernet, MAC addressing, and switches deliver frames on a local network
- Compare distance-vector and link-state routing, and describe how BGP connects autonomous systems
- Divide IPv4 address space with subnetting and CIDR, and explain IPv6, ARP, ICMP, and DHCP
- Trace TCP connection setup, flow control, and congestion control, and decide when UDP is the better choice
- Explain how DNS, HTTP, and TLS work together when a browser loads a secure page

## Prerequisites
- Comfort with binary and hexadecimal numbers
- Basic programming experience helps for the socket and protocol examples
- An outline of operating systems is useful but not required

## Glossary
- **Protocol**: an agreed set of rules for the format and order of messages between devices
- **Packet**: a unit of data carried across a network, with a header and a payload
- **Bandwidth**: the maximum rate at which a link can carry data, in bits per second
- **Latency**: the time a bit takes to travel from sender to receiver
- **Frame**: the data link layer's unit of transmission on a single link
- **MAC address**: a hardware address that identifies a network interface on a local network
- **IP address**: a logical address that identifies a host's interface across networks
- **Subnet**: a block of IP addresses sharing a common prefix, defined by a mask or CIDR length
- **Router**: a device that forwards packets between networks using a routing table
- **TCP**: Transmission Control Protocol; reliable, ordered, connection-oriented byte streams
- **UDP**: User Datagram Protocol; lightweight, connectionless delivery without guarantees
- **Congestion control**: mechanisms that slow senders down when the network is overloaded
- **DNS**: the Domain Name System, which maps names such as example.com to IP addresses
- **TLS**: Transport Layer Security, which encrypts and authenticates connections

## Further reading
- James F. Kurose and Keith W. Ross, *Computer Networking: A Top-Down Approach* (Pearson)
- Andrew S. Tanenbaum, Nick Feamster, and David J. Wetherall, *Computer Networks* (Pearson)
- Larry L. Peterson and Bruce S. Davie, *Computer Networks: A Systems Approach* (Morgan Kaufmann)
- W. Richard Stevens, *TCP/IP Illustrated, Volume 1: The Protocols* (Addison-Wesley)
