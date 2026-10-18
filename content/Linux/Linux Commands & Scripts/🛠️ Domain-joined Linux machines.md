---
created: 2026-09-05
updated: 2026-09-20
---
## Identifying whether a Linux machine is domain-joined

- To determine whether a Linux achine is domain-joined, use the [`realm`](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/windows_integration_guide/cmd-realmd) command:

```bash
realm list
```

| Command                          | Description                                      |
| -------------------------------- | ------------------------------------------------ |
| `realm discover <domain>`        | Discover information about a domain or realm.    |
| `realm list`                     | List configured realms and domain memberships.   |

- In case [`realm`](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/windows_integration_guide/cmd-realmd) is not available, we can also look for other tools used to integrate Linux with Active Directory such as [`sssd`](https://sssd.io/) or [`winbind`](https://www.samba.org/samba/docs/current/man-html/winbindd.8.html).

```bash
ps -ef | grep -i "winbind\|sssd"
```

### Finding kerberos 