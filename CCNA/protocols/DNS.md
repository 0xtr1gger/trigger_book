---
created: 2025-11-04 09:28:15
tags:
  - protocols
---
## Configuration

### DNS client

- Enable DNS hostname-to-IP address translation on a router or switch:

```toml
R1(config)# ip domain-lookup
```

- Disable DNS resolution:

```toml
R1(config)# no ip domain-lookup
```

- Configure a DNS server(s) the device would query for hostname resolution:

```toml
R1(config)# ip name-server <dns_server1> <dns_server2>
```

>[!note] You can configure up to 6 severs for redundancy.

- Define the default domain name for the device:

```toml
R1(config)# ip domain-name example.com
```

>[!important] The device's hostname will be appended to that domain name to form an FQDN.

>[!note] This is to simplify hostname resolution by completing partial hostnames automatically. So, `router1` becomes `router1.example.com`. 

- Add more domain suffixes to try when resolving hostnames:

```toml
R1(config)# ip domain-list <domain_name>
```

>[!note] If the first domain doesn't resolve, the router tries subsequent domains in the list. This provides fallback options for hostname resolution across multiple domains.

### DNS server

- Configure a router as a DNS server:

```toml
R1(config)# ip dns server
```

- Manually create static hostname-to-IP address mapping:

```toml
R1(config)# ip host <hostname> <ip_address>
```

For example:

```toml
R1(config)# ip host router1 192.168.1.1
```

### `show` commands

- Display DNS configuration:

```toml
R1# show hosts
```

```toml
R1# show running-config | include domain
```

```toml
R1# show running-config | section ip
```

### Testing connectivity

- Ping a host:

```toml
R1# ping <hostname>
```
