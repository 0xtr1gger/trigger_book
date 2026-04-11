---
created: 2026-03-09
---
- Look for keywords within files such as `passw`, `user`, `token`, `key`, and `secret`.
- Search for files with extensions commonly associated with stored credentials, such as `.ini`, `.cfg`, `.env`, `.xlsx`, `.ps1`, and `.bat`.
- Watch for files with "interesting" names that include terms like `config`, `user`, `passw`, `cred`, or `initial`.
- If you're trying to locate credentials within the `INLANEFREIGHT.LOCAL` domain, it may be helpful to search for files containing the string `INLANEFREIGHT\`.
- Keywords should be localized based on the target; if you are attacking a German company, it's more likely they will reference a `"Benutzer"` than a `"User"`.
- Pay attention to the shares you are looking at, and be strategic. If you scan ten shares with thousands of files each, it's going to take a significant amount of time. Shares used by `IT employees` might be a more valuable target than those used for company photos.

## Snaffler

[[Snaffler _]]

```
Snaffler.exe -s
```

## PowerHuntShares

 [`PowerHuntShares`](https://github.com/NetSPI/PowerHuntShares)
 generates an `HTML report` upon completion

```
Invoke-HuntSMBShares -Threads 100 -OutputDirectory c:\Users\Public
```

## MANSPIDER

from linux


 [MANSPIDER](https://github.com/blacklanternsecurity/MANSPIDER) a

```bash
docker run --rm -v ./manspider:/root/.manspider blacklanternsecurity/manspider 10.129.234.121 -c 'passw' -u 'mendres' -p 'Inlanefreight2025!'
```

## NetExec

```bash
nxc smb 10.129.234.121 -u mendres -p 'Inlanefreight2025!' --spider IT --content --pattern "passw"
```