---
title: "Extending a Static IP Office Network with a TP-Link C54 Extender"
date: "2026-09-04 10:00:00 +0530"
categories: ["Networking", "Hardware"]
tags: ["TP-Link", "Static IP", "2026"]
description: "A step-by-step guide to configuring a new router and range extender on a static IP network."

---
Setting up network hardware usually feels like a straightforward plug-and-play process. You unbox a router, plug in the WAN cable, and let DHCP handle the rest. It just works. But things get complicated when you are dealing with a static IP office environment. Honestly, bridging a fixed local area connection to a new Wi-Fi ecosystem requires a bit of manual maneuvering. So, let's walk through replacing an aging router and extending its reach using a TP-Link C54, keeping all the original credentials intact.

---

## Configuring the Primary Connection

The first hurdle is getting the primary router to talk to an internet gateway that doesn't hand out IP addresses automatically. If your network mandates specific parameters—say, a fixed WAN IP with a custom subnet—you have to hardcode these into the new hardware.

You simply connect the main office LAN cable to the router's WAN port, log into the admin panel, and swap the connection type from standard automatic assignment to **Static IP**.

| Setting | Required Value |
| --- | --- |
| **WAN IP** | `10.182.12.163` |
| **Subnet Mask** | `255.255.255.192` |
| **Default Gateway** | `10.182.12.129` |
| **Primary DNS** | `164.100.3.1` |
| **Secondary DNS** | `164.100.17.3` |

Punch in your assigned gateway along with your primary and secondary DNS servers. To be fair, missing just one digit here leaves you offline. Accuracy matters.

---

## Replicating the Old Wi-Fi Credentials

Once the primary router is live, you probably want to keep your existing devices connected without typing in a new password on a dozen different machines. You just change the new router's wireless settings to match the old ones.

```text
SSID: Revenue Sec( Finance)
Password: Revenuesec@123
Security: WPA2-PSK

```

Naming the SSID exactly the same and reusing the original password ensures laptops and phones migrate over instantly.

---

## Deploying the Range Extender

Now, covering a dead zone. This is where the TP-Link C54 comes in as a range extender. Instead of running a long ethernet cable across the floor, you can grab the C54 and plug it into a wall outlet near the primary router for the initial setup.

* Connect to the C54's default Wi-Fi network.
* Open your browser and navigate to `192.168.0.1`.
* Switch the operation mode to **Range Extender** mode and reboot.

Once it wakes back up, a quick setup wizard prompts you to scan the area for existing networks. You just select the primary network, type in the password, and let the extender sync up.

The final step is purely physical. Move the C54 halfway between the main router and the area suffering from weak signal. Plug it into the wall, wait for the lights to turn solid, and connect your devices. You are good to go.
