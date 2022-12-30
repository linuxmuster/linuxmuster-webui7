<h1 align="center">
    Linuxmuster-webui7
</h1>

<p align="center">
    <a href="https://raw.githubusercontent.com/ajenti/ajenti/master/LICENSE">
        <img src="https://img.shields.io/badge/Python-v3-green" alt="Badge License" />
    </a>
    <a href="https://raw.githubusercontent.com/ajenti/ajenti/master/LICENSE"> 
        <img src="https://img.shields.io/github/license/linuxmuster/linuxmuster-webui7?label=License" alt="Badge License" />
    </a>
    <a href="https://ask.linuxmuster.net">
        <img src="https://img.shields.io/discourse/users?logo=discourse&logoColor=white&server=https%3A%2F%2Fask.linuxmuster.net" alt="Community Forum"/>
    </a>
    <a href="https://crowdin.com/project/linuxmusternet">
        <img src="https://badges.crowdin.net/linuxmusternet/localized.svg" />
    </a>
</p>

## Features

Next generation web interface for linuxmuster.net v7, which provides:

 * user management,
 * device management,
 * class and projects management for each teacher,
 * quota and school settings,
 * Linbo management,
 * and much more !

## Maintenance Details

Linuxmuster.net official | ✅  YES
:---: | :---: 
[Community support](https://ask.linuxmuster.net) | ✅  YES*
Actively developed | ✅  YES
Maintainer organisation |  Linuxmuster.net
Primary maintainer | arnaud@linuxmuster.net  / andreas.till@netzint.de  
    
\* The linuxmuster community consits of people who are nice and happy to help. They are not directly involved in the development though, and might not be able to help in all cases.

## Screenshots

<table align="center">
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-login.png">
                <img src="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-login.png" alt="Screenshot Webui Login" width="500px" />
            </a>
        </td>
        <td align="center">
            <a href="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-class.png">
                <img src="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-class.png" alt="Screenshot Webui Session" width="500px" />
            </a>
        </td>
    </tr>
    <tr>
        <td align="center">
            <a href="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-linbo.png">
                <img src="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-linbo.png" alt="Screenshot Webui Linbo" width="500px" />
            </a>
        </td>
        <td align="center">
            <a href="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-user.png">
                <img src="https://raw.githubusercontent.com/linuxmuster/linuxmuster-webui7/release/docs_src/_static/webui-user.png" alt="Screenshot Webui User" width="500px" />
            </a>
        </td>
    </tr>
</table>

## Installation

### 1. Import key:

```bash
wget -qO - "https://deb.linuxmuster.net/pub.gpg" | sudo apt-key add -
```

### 2. Add repo:

##### Linuxmuster 7.2 ( dev )

```bash
sudo sh -c 'echo "deb https://deb.linuxmuster.net/ lmn72 main" > /etc/apt/sources.list.d/lmn7.list'
```

##### Linuxmuster 7.1 ( testing )

```bash
sudo sh -c 'echo "deb https://deb.linuxmuster.net/ lmn71 main" > /etc/apt/sources.list.d/lmn7.list'
```

##### Linuxmuster 7.0 ( stable )

```bash
sudo sh -c 'echo "deb https://deb.linuxmuster.net/ lmn70 main" > /etc/apt/sources.list.d/lmn7.list'
```

### 3. Apt update

```bash
sudo apt update && sudo apt install linuxmuster-webui7
```
