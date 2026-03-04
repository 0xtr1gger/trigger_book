---
created: 20-02-2026
---
## Cmdlets

>A **[cmdlet](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-overview?view=powershell-7.5)** (pronounced *command-let*) is a lightweight, single-function command used in PowerShell environments.

- Cmdlets follow a strict `Verb-Noun` naming convention, such as: [`Get-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-7.5), [`Set-ExecutionPolicy`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-executionpolicy?view=powershell-7.5), [`New-Item`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item?view=powershell-7.5), [`Remove-Item`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/remove-item?view=powershell-7.5), etc.
- Some cmdlets are built-in and come preinstalled with PowerShell, such as `Get-Command`, `Get-Help`, `Get-Service`, `Get-ChildItem`.
- Others are included in modules that are either loaded automatically when needed or can be installed separately. For example, the `ActiveDirectory` module adds cmdlets like `Get-ADUser` and `New-ADGroup`.

- To list available modules, use [`Get-Module`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-module?view=powershell-7.5):

```powershell
Get-Module -ListAvailable
```

- Under the hood, cmdlets are compiled .NET classes. They are executed **within the PowerShell runtime**. 
- PowerShell passes **.NET objects** between commands — not just text. Cmdlets can output objects and accept them as input.
- Many Microsoft products add their own cmdlets, such as:
	- Microsoft Exchange Server
	- Microsoft Azure
	- Windows Server

## PowerShell execution policy

>**PowerShell execution policies** are a safety feature in **PowerShell** that control how scripts are loaded and executed on a system.

- Execution policies are designed to prevent accidental execution of dangerous scripts. But these are **not a security boundary**, and they can be bypassed.

- To get the current execution policy, use [`Get-ExecutionPolicy`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-executionpolicy?view=powershell-7.5):

```powershell 
Get-ExecutionPolicy -List
```

>[!example]+
> ```powershell
> Get-ExecutionPolicy -List
> ```
> 
> ```powershell
>         Scope ExecutionPolicy
>         ----- ---------------
> MachinePolicy    Unrestricted
>    UserPolicy    Unrestricted
>       Process    Unrestricted
>   CurrentUser    Unrestricted
>  LocalMachine    Unrestricted
> ```

- Possible execution policies:


| **Policy**     | **Description**                                                                                                                                                                                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Restricted`   | No scripts are allowed, only interactive commands.<br>`.ps1`, `.psm1`, `.ps1xml`, etc. are all blocked.                                                                                                                                                              |
| `AllSigned`    | Scripts can run, but every script must be **digitally signed**. <br>This applies to both local and remote scripts.<br>Prompts before running scripts signed by new publishers that aren't yet listed as trysted or untrusted.<br>Used in high-security environments. |
| `RemoteSigned` | All local scripts can run, but remote scripts downloaded from the Internet must be signed.                                                                                                                                                                           |
| `Unrestricted` | All scripts can run. Prompts for scripts downloaded from the Internet.<br>The default execution policy for non-Windows computers, and it can't be changed.                                                                                                           |
| `Bypass`       | All scripts, both local and remote, run without restrictions or warnings.                                                                                                                                                                                            |
| `Default`      | This sets the default execution policy, `Restricted` for Windows desktop machines and `RemoteSigned` for Windows servers.                                                                                                                                            |
| `Undefined`    | No execution policy is set for the current scope.<br>If the execution policy for all scopes is set to `Undefined`, then the default execution policy of `Restricted` will be used.                                                                                   |

- To change execution policy for the current process (session), use [`Set-ExecutionPolicy`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5):

```powershell
Set-ExecutionPolicy -Scope Process
```
## PowerShell ISE

>**[PowerShell ISE (Integrated Runtime Scripting Environment)](https://learn.microsoft.com/en-us/powershell/scripting/windows-powershell/ise/introducing-the-windows-powershell-ise?view=powershell-7.5)** is a graphical editor and execution environment for Windows PowerShell. It also has an autocomplete/lookup function for PowerShell commands to make life easier.

PowerShell ISE is now largely replaced by PowerShell extension for Visual Studio Code.

## Useful commands

- Use [`Get-Help`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-help?view=powershell-7.5) to open a help page for a command:

```powershell
Get-Help <cmdlet_name> -Online
```

### Aliases

- [`Get-Alias`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-alias?view=powershell-7.5) lists available aliases:

```powershell
Get-Alias
```

> [!example]+
> ```powershell
> Get-Alias
> ```
> 
> ```powershell
> CommandType     Name                 Version    Source
> -----------     ----                 -------    ------
> Alias           ? -> Where-Object                                             
> Alias           % -> ForEach-Object                                           
> Alias           cd -> Set-Location                                            
> Alias           chdir -> Set-Location                                         
> Alias           clc -> Clear-Content                                          
> Alias           clhy -> Clear-History                                         
> Alias           cli -> Clear-Item                                             
> Alias           clp -> Clear-ItemProperty                                     
> Alias           cls -> Clear-Host                                             
> Alias           clv -> Clear-Variable                                         
> Alias           copy -> Copy-Item                                             
> Alias           cpi -> Copy-Item                                              
> Alias           cvpa -> Convert-Path                                          
> Alias           dbp -> Disable-PSBreakpoint                                   
> Alias           del -> Remove-Item                                            
> Alias           dir -> Get-ChildItem                                          
> Alias           ebp -> Enable-PSBreakpoint                                    
> Alias           echo -> Write-Output                                          
> Alias           epal -> Export-Alias                                          
> Alias           epcsv -> Export-Csv                                           
> Alias           erase -> Remove-Item                                          
> Alias           etsn -> Enter-PSSession 
> ```

- To create an alias, use [`Set-Alias`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/set-alias?view=powershell-7.5):

```powershell
New-Alias -Name "Show-Files" Get-ChildItem
```

## drafts

- To list all installed modules, use [`Get-InstalledModule`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-module?view=powershell-7.5):

```powershell
Get-InstalledModule
```
