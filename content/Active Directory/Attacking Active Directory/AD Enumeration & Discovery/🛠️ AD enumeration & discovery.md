---
created: 2026-10-04
updated: 2026-10-11
---
### External (unauthenticated) enumeration

>[!note] See [[External AD & Windows enumeration]].

### Authenticated enumeration

>[!note] See [[🛠️ Authenticated AD & Windows enumeration]].

- Validate a credential and read the default naming context over LDAP:

```bash
ldapsearch -x -H ldap://10.10.11.5 -D 'jdoe@example.com' -w 'passwd123' -s base -b '' '(objectClass=*)' defaultNamingContext
```

- Sweep the subnet with a valid domain account:

```bash
nxc smb 10.10.11.0/24 -u 'jdoe' -p 'passwd123' -d 'example.com'
```

>[!note] For a consolidated command reference across `net`, the AD PowerShell module, PowerView, and SharpHound, see [[🛠️ AD enumeration]].

### Querying LDAP

>[!note] See [[Querying LDAP]].

- Read the RootDSE anonymously to recover naming contexts and the DC name:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b '' -s base '(objectClass=*)'
```

- Enumerate enabled users:

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' sAMAccountName
```

- List accounts with an SPN (Kerberoastable candidates):

```bash
ldapsearch -x -LLL -H ldap://10.10.11.5 -b 'DC=example,DC=com' -s sub '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' sAMAccountName servicePrincipalName
```

### Username enumeration & password spraying

>[!note] See [[Username enumeration in AD]] and [[Password spraying in AD]].

- Enumerate valid usernames over Kerberos without triggering logon failures:

```bash
kerbrute userenum -d example.com --dc 10.10.11.5 /usr/share/wordlists/statistically-likely-usernames/jsmith.txt
```

- Read the domain password and lockout policy before spraying:

```bash
netexec smb 10.10.11.5 -u jdoe -p passwd123 --pass-pol
```

- Spray a single password across validated usernames:

```bash
netexec smb 10.10.11.5 -u valid_usernames.txt -p Welcome1 | grep +
```

### BloodHound

>[!note] See [[🛠️ BloodHound]].

- Collect from a Linux host with a domain credential:

```bash
bloodhound-python -d example.com -u jdoe -p 'Password123' -c All --zip -ns 10.10.11.5
```

- Collect from a domain-joined Windows host:

```powershell
SharpHound.exe -c All
```
